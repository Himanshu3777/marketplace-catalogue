"""Cart JSON serialization."""
from rest_framework import serializers

from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    variant_id = serializers.IntegerField(source="variant.id", read_only=True)
    variant_code = serializers.CharField(source="variant.variant_id", read_only=True)
    sku = serializers.CharField(source="variant.sku", read_only=True)
    product_id = serializers.IntegerField(source="variant.product.id", read_only=True)
    product_name = serializers.CharField(source="variant.product.name", read_only=True)
    product_slug = serializers.CharField(source="variant.product.slug", read_only=True)
    brand_name = serializers.CharField(source="variant.product.brand.name", read_only=True)
    color = serializers.CharField(source="variant.color", read_only=True)
    size = serializers.CharField(source="variant.size", read_only=True)
    storage = serializers.CharField(source="variant.storage", read_only=True)
    price = serializers.FloatField(source="variant.price", read_only=True)
    discount_pct = serializers.FloatField(source="variant.discount_pct", read_only=True)
    final_price = serializers.FloatField(source="variant.final_price", read_only=True)
    image_url = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    line_total = serializers.FloatField(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "variant_id", "variant_code", "sku", "product_id",
                  "product_name", "product_slug", "brand_name", "color",
                  "size", "storage", "price", "discount_pct", "final_price",
                  "image_url", "available", "quantity", "line_total"]

    def get_image_url(self, obj):
        img = obj.variant.images.order_by("position").first()
        if img:
            return img.url
        pimg = obj.variant.product.images.order_by("position").first()
        return pimg.url if pimg else None

    def get_available(self, obj):
        inv = getattr(obj.variant, "inventory", None)
        return inv.available if inv else 0


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    item_count = serializers.IntegerField()
    subtotal = serializers.FloatField()
