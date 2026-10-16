from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Brand, Category, Product, ProductImage, ProductSpecification,
    ProductVariant, SubCategory,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "display_order"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_active"]
    list_filter = ["is_active", "category"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ["sku", "color", "size", "storage", "price", "discount_pct",
              "is_active"]
    readonly_fields = ["sku"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ["url", "position"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "brand", "category", "is_active", "is_featured",
                    "variant_count", "created_at"]
    list_filter = ["is_active", "is_featured", "category", "brand"]
    search_fields = ["name", "sku", "product_id"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [ProductVariantInline, ProductImageInline]
    list_per_page = 50
    actions = ["activate", "deactivate", "feature", "unfeature"]

    def get_queryset(self, request):
        from django.db.models import Count
        return super().get_queryset(request).select_related(
            "brand", "category").annotate(_vc=Count("variants"))

    @admin.display(description="Variants")
    def variant_count(self, obj):
        return obj._vc

    @admin.action(description="Activate selected products")
    def activate(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected products")
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Mark as featured")
    def feature(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Remove featured")
    def unfeature(self, request, queryset):
        queryset.update(is_featured=False)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["sku", "product", "color", "size", "price",
                    "final_price_display", "stock_available", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["sku", "product__name"]
    readonly_fields = ["variant_id", "sku"]
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "product", "inventory")

    @admin.display(description="Final price")
    def final_price_display(self, obj):
        return f"₹{obj.final_price}"

    @admin.display(description="Stock")
    def stock_available(self, obj):
        inv = getattr(obj, "inventory", None)
        if not inv:
            return "—"
        color = "#dc2626" if inv.available <= 0 else "#059669"
        return format_html(
            f'<span style="color:{color};font-weight:bold">{inv.available}</span>')


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ["product", "name", "value"]
    search_fields = ["product__name", "name", "value"]
