"""ReturnRequest JSON serialization."""
from rest_framework import serializers

from .models import ReturnRequest


class ReturnRequestSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source="order_item.order.order_number", read_only=True)
    product_name = serializers.CharField(
        source="order_item.product_name", read_only=True)
    sku = serializers.CharField(source="order_item.sku", read_only=True)
    request_type_label = serializers.CharField(
        source="get_request_type_display", read_only=True)
    reason_label = serializers.CharField(
        source="get_reason_display", read_only=True)
    status_label = serializers.CharField(
        source="get_status_display", read_only=True)

    class Meta:
        model = ReturnRequest
        fields = ["id", "order_number", "product_name", "sku",
                  "request_type", "request_type_label", "reason",
                  "reason_label", "description", "status", "status_label",
                  "refund_status", "refund_amount", "gateway_refund_id",
                  "refunded_at",
                  "requested_at", "updated_at"]
        read_only_fields = ["status", "refund_status", "refund_amount",
                            "gateway_refund_id", "refunded_at",
                            "requested_at", "updated_at"]
