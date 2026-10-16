from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["line_total"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "customer_name", "phone", "status",
                    "payment_method", "payment_status", "payment_verified",
                    "total", "created_at"]
    list_filter = ["status", "payment_method", "payment_status",
                   "payment_verified", "created_at"]
    search_fields = ["order_number", "customer_name", "phone",
                     "gateway_order_id", "gateway_payment_id"]
    readonly_fields = ["order_number", "idempotency_key", "subtotal",
                       "delivery_fee", "total", "payment_verified",
                       "payment_verified_at", "created_at", "updated_at"]
    inlines = [OrderItemInline]
    actions = ["mark_confirmed", "mark_shipped", "mark_delivered",
               "mark_cancelled"]

    @admin.action(description="Mark selected as CONFIRMED")
    def mark_confirmed(self, request, queryset):
        queryset.update(status=Order.STATUS_CONFIRMED)

    @admin.action(description="Mark selected as SHIPPED")
    def mark_shipped(self, request, queryset):
        queryset.update(status=Order.STATUS_SHIPPED)

    @admin.action(description="Mark selected as DELIVERED")
    def mark_delivered(self, request, queryset):
        # COD orders are collected on delivery — auto-mark paid+verified.
        # Online payments must ONLY be marked paid via gateway webhook.
        for order in queryset.prefetch_related("items"):
            order.status = Order.STATUS_DELIVERED
            if order.payment_method == Order.PAYMENT_COD:
                order.payment_status = Order.PAYMENT_PAID
                order.payment_verified = True
            order.save()
            order.deduct_stock_on_delivery()

    @admin.action(description="Mark selected as CANCELLED")
    def mark_cancelled(self, request, queryset):
        for order in queryset.prefetch_related("items"):
            if order.status != Order.STATUS_CANCELLED:
                order.status = Order.STATUS_CANCELLED
                order.save()
                order.release_reserved_stock()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product_name", "sku", "quantity", "price",
                    "line_total"]
    search_fields = ["order__order_number", "sku", "product_name"]
