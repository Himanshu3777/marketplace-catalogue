"""API-first ViewSets. JSON only — no HTML rendering for CRUD."""
from django.core.cache import cache
from django.db.models import Count, Min, Prefetch
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from marketplace.session_auth import SessionAuthNoCSRF

from .filters import ProductFilter
from .models import (
    Brand, Category, Product, ProductImage, ProductVariant, SubCategory,
)
from .serializers import (
    BrandSerializer, CategorySerializer, ProductDetailSerializer,
    ProductImageSerializer, ProductListSerializer, ProductReviewSerializer,
    ProductVariantSerializer, SubCategorySerializer,
)
from reviews.models import ProductReview


def product_list_queryset():
    """Optimized base queryset: no N+1 on listing pages."""
    return (
        Product.objects.filter(is_active=True)
        .select_related("brand", "category", "subcategory", "seller")
        .prefetch_related(
            Prefetch("images", queryset=ProductImage.objects.order_by("position"))
        )
        .annotate(
            min_variant_price=Min("variants__price"),
            variant_count=Count("variants", distinct=True),
        )
    )


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = "slug"
    queryset = Category.objects.filter(is_active=True).annotate(
        subcategory_count=Count("subcategories")
    )

    def list(self, request, *args, **kwargs):
        # Categories change rarely — cache the serialized tree for 1 hour.
        data = cache.get("category_tree")
        if data is None:
            data = self.serializer_class(self.get_queryset(), many=True).data
            cache.set("category_tree", data, 3600)
        return Response(data)


class SubCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubCategorySerializer
    lookup_field = "slug"

    def get_queryset(self):
        qs = (
            SubCategory.objects.filter(is_active=True)
            .select_related("category")
            .annotate(product_count=Count("products"))
        )
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug__iexact=category)
        return qs


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BrandSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Brand.objects.filter(is_active=True).annotate(
            product_count=Count("products")
        )


class ProductViewSet(viewsets.ModelViewSet):
    """Full CRUD (JSON). List uses the lightweight serializer."""
    authentication_classes = [SessionAuthNoCSRF]
    filterset_class = ProductFilter
    search_fields = ["name", "short_description", "detailed_description",
                     "brand__name", "product_type", "sku"]
    ordering_fields = ["price", "rating", "created_at", "discount_pct", "review_count"]
    ordering = ["-created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        return product_list_queryset()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer

    def get_object(self):
        # Detail view: deep prefetch for variants/images/specs/reviews
        try:
            obj = (
                Product.objects.filter(is_active=True)
                .select_related("brand", "category", "subcategory", "seller")
                .prefetch_related(
                    "images", "specifications",
                    Prefetch("variants",
                             queryset=ProductVariant.objects.prefetch_related(
                                 "images", "inventory", "prices")),
                )
                .annotate(min_variant_price=Min("variants__price"),
                          variant_count=Count("variants", distinct=True))
                .get(slug=self.kwargs["slug"])
            )
        except Product.DoesNotExist:
            raise Http404("Product not found")
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=["get"])
    def variants(self, request, slug=None):
        product = self.get_object()
        variants = product.variants.filter(is_active=True).prefetch_related(
            "images", "inventory", "prices")
        page = self.paginate_queryset(variants)
        ser = ProductVariantSerializer(
            page if page is not None else variants, many=True)
        if page is not None:
            return self.get_paginated_response(ser.data)
        return Response(ser.data)

    @action(detail=True, methods=["get"])
    def reviews(self, request, slug=None):
        product = self.get_object()
        reviews = product.product_reviews.all()
        page = self.paginate_queryset(reviews)
        ser = ProductReviewSerializer(
            page if page is not None else reviews, many=True)
        if page is not None:
            return self.get_paginated_response(ser.data)
        return Response(ser.data)

    @action(detail=True, methods=["post"], url_path="reviews/submit")
    def review_submit(self, request, slug=None):
        """Submit a review (logged-in users only)."""
        from reviews.models import ProductReview

        if not getattr(request.user, "is_authenticated", False):
            return Response({"error": "Please log in to write a review."},
                            status=status.HTTP_401_UNAUTHORIZED)
        product = self.get_object()
        try:
            rating = int(request.data.get("rating", 0))
        except (TypeError, ValueError):
            rating = 0
        title = str(request.data.get("title", "")).strip()
        body = str(request.data.get("body", "")).strip()
        if rating not in (1, 2, 3, 4, 5):
            return Response({"error": "Rating must be 1-5."},
                            status=status.HTTP_400_BAD_REQUEST)
        if not title or not body:
            return Response({"error": "Title and review text are required."},
                            status=status.HTTP_400_BAD_REQUEST)
        author = request.user.get_full_name() or request.user.username
        from catalog.models import ProductVariant
        bought = ProductVariant.objects.filter(
            product=product, order_items__order__user=request.user,
            order_items__order__status="DELIVERED").exists()
        review, created = ProductReview.objects.update_or_create(
            product=product, author_name=author,
            defaults={"rating": rating, "title": title[:255], "body": body,
                      "is_verified": bought},
        )
        from django.db.models import Avg, Count
        agg = product.product_reviews.aggregate(
            avg=Avg("rating"), cnt=Count("id"))
        product.rating = round(agg["avg"] or 0, 2)
        product.review_count = agg["cnt"] or 0
        product.save(update_fields=["rating", "review_count"])
        return Response(ProductReviewSerializer(review).data,
                        status=status.HTTP_201_CREATED if created
                        else status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def related(self, request, slug=None):
        """Related products: same subcategory → category → brand fallback."""
        product = self.get_object()
        seen_ids = {product.id}
        related = []

        def take(qs, n):
            nonlocal related
            for p in qs.exclude(id__in=seen_ids)[:n]:
                related.append(p)
                seen_ids.add(p.id)

        # 1. Same subcategory (most relevant)
        if product.subcategory_id:
            take(product_list_queryset().filter(
                subcategory_id=product.subcategory_id), 8 - len(related))
        # 2. Same category
        if len(related) < 8 and product.category_id:
            take(product_list_queryset().filter(
                category_id=product.category_id), 8 - len(related))
        # 3. Same brand
        if len(related) < 8 and product.brand_id:
            take(product_list_queryset().filter(
                brand_id=product.brand_id), 8 - len(related))

        ser = ProductListSerializer(related, many=True,
                                    context={"request": request})
        return Response(ser.data)
