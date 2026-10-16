from django.contrib import admin

from .models import ReturnRequest


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "order_item", "request_type", "reason", "status",
                    "requested_at"]
    list_filter = ["request_type", "reason", "status", "requested_at"]
    search_fields = ["order_item__order__order_number", "order_item__sku"]
    readonly_fields = ["requested_at", "updated_at"]
