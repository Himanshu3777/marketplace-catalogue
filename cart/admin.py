from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ["line_total"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["session_key", "item_count", "subtotal", "updated_at"]
    search_fields = ["session_key"]
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["cart", "variant", "quantity", "line_total", "updated_at"]
    list_filter = ["created_at"]
