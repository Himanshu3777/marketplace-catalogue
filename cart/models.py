"""Session-based shopping cart. No customer account required."""
from django.db import models


class Cart(models.Model):
    session_key = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.session_key[:8]}"

    @property
    def item_count(self):
        return sum(i.quantity for i in self.items.all())

    @property
    def subtotal(self):
        return round(sum(i.line_total for i in self.items.all()), 2)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items"
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant", on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "variant"], name="uniq_cart_variant"
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="cartitem_quantity_gte_1",
            ),
        ]
        indexes = [models.Index(fields=["cart"])]

    def __str__(self):
        return f"{self.variant.sku} x {self.quantity}"

    @property
    def line_total(self):
        return round(self.variant.final_price * self.quantity, 2)
