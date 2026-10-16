from django.contrib import admin
from django.utils.html import format_html

from .models import Inventory, Price


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ["sku", "product_name", "quantity", "reserved",
                    "available", "stock_status", "updated_at"]
    list_filter = ["updated_at"]
    search_fields = ["variant__sku", "variant__product__name"]
    readonly_fields = ["updated_at"]
    list_per_page = 50
    actions = ["restock_100"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "variant", "variant__product")

    @admin.display(description="SKU")
    def sku(self, obj):
        return obj.variant.sku

    @admin.display(description="Product")
    def product_name(self, obj):
        return obj.variant.product.name[:50]

    @admin.display(description="Available")
    def available(self, obj):
        return obj.available

    @admin.display(description="Status")
    def stock_status(self, obj):
        if obj.available <= 0:
            return format_html(
                '<span style="color:#fff;background:#dc2626;padding:2px 8px;'
                'border-radius:999px;font-size:11px">OUT OF STOCK</span>')
        if obj.available <= obj.low_stock_threshold:
            return format_html(
                '<span style="color:#92400e;background:#fef3c7;padding:2px 8px;'
                'border-radius:999px;font-size:11px">LOW</span>')
        return format_html(
            '<span style="color:#065f46;background:#d1fae5;padding:2px 8px;'
            'border-radius:999px;font-size:11px">OK</span>')

    @admin.action(description="Restock selected (+100 units)")
    def restock_100(self, request, queryset):
        for inv in queryset:
            inv.quantity += 100
            inv.save(update_fields=["quantity"])


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ["sku", "mrp", "selling_price", "discount_pct",
                    "is_current", "valid_from"]
    list_filter = ["is_current", "currency"]
    search_fields = ["variant__sku", "variant__product__name"]
    readonly_fields = ["valid_from"]
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "variant", "variant__product")

    @admin.display(description="SKU")
    def sku(self, obj):
        return obj.variant.sku

    @admin.display(description="Discount %")
    def discount_pct(self, obj):
        if obj.mrp:
            return round((1 - float(obj.selling_price) / float(obj.mrp)) * 100, 1)
        return 0
