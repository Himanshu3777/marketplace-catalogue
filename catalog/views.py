"""API-first ViewSets. JSON only — no HTML rendering for CRUD."""
from django.core.cache import cache
from django.db.models import Count, Min, Prefetch
from django.http import Http404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
