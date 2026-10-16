from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["line_total"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "customer_name", "phone", "status",
                    "payment_method", "total", "created_at"]
    list_filter = ["status", "payment_method", "created_at"]
    search_fields = ["order_number", "customer_name", "phone"]
    readonly_fields = ["order_number", "subtotal", "delivery_fee", "total",
                       "created_at", "updated_at"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product_name", "sku", "quantity", "price",
                    "line_total"]
    search_fields = ["order__order_number", "sku", "product_name"]
