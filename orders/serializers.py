"""Order JSON serialization."""
from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.FloatField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "variant_name", "sku", "price",
                  "quantity", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    timeline = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ["order_number", "customer_name", "phone", "email",
                  "address_line1", "address_line2", "city", "state",
                  "pincode", "status", "payment_method", "notes",
                  "subtotal", "delivery_fee", "total",
                  "created_at", "updated_at", "items", "timeline"]
