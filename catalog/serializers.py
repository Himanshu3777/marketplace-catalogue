"""API-first serializers. No HTML rendering anywhere in the API."""
from rest_framework import serializers

from .models import (
    Brand, Category, Product, ProductImage, ProductSpecification,
    ProductVariant, SubCategory,
)
from sellers.models import Seller
from inventory.models import Inventory, Price
from reviews.models import ProductReview


class CategorySerializer(serializers.ModelSerializer):
    subcategory_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "image_url",
                  "display_order", "is_active", "subcategory_count"]


class SubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SubCategory
        fields = ["id", "name", "slug", "category", "category_name",
                  "description", "image_url", "is_active", "product_count"]


class BrandSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "description", "logo_url", "product_count"]


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["id", "name", "slug", "description", "rating"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "url", "alt_text", "position"]


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ["id", "name", "value", "position"]


class InventorySerializer(serializers.ModelSerializer):
    available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Inventory
        fields = ["quantity", "reserved", "available", "low_stock_threshold"]


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ["mrp", "selling_price", "currency", "valid_from"]


class ProductVariantSerializer(serializers.ModelSerializer):
    final_price = serializers.FloatField(read_only=True)
    inventory = InventorySerializer(read_only=True)
    current_price = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ["id", "variant_id", "sku", "color", "size", "storage",
                  "price", "discount_pct", "final_price", "is_active",
                  "inventory", "current_price", "images"]

    def get_current_price(self, obj):
        p = obj.prices.filter(is_current=True).first()
        return PriceSerializer(p).data if p else None


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing pages (no N+1)."""
    final_price = serializers.FloatField(read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    subcategory_slug = serializers.CharField(source="subcategory.slug", read_only=True)
    seller_name = serializers.CharField(source="seller.name", read_only=True)
    primary_image = serializers.SerializerMethodField()
    min_variant_price = serializers.FloatField(read_only=True)
    variant_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "product_id", "sku", "name", "slug", "brand_name",
                  "category_slug", "subcategory_slug", "seller_name",
                  "product_type", "short_description", "price", "discount_pct",
                  "final_price", "gst_pct", "rating", "review_count",
                  "availability_status", "primary_image", "min_variant_price",
                  "variant_count", "is_featured"]

    def get_primary_image(self, obj):
        img = obj.images.first()
        return img.url if img else None


class ProductDetailSerializer(ProductListSerializer):
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(read_only=True)
    seller = SellerSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            "brand", "category", "subcategory", "seller",
            "detailed_description", "warranty", "return_policy",
            "weight_kg", "dimensions", "material",
            "images", "specifications", "variants",
            "created_at", "updated_at",
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ["id", "author_name", "rating", "title", "body",
                  "is_verified", "created_at"]
        read_only_fields = ["is_verified", "created_at"]
