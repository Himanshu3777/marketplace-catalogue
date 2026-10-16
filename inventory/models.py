"""Inventory (stock per variant) and Price (current price per variant + history)."""
from django.db import models


class Inventory(models.Model):
    variant = models.OneToOneField(
        "catalog.ProductVariant", on_delete=models.CASCADE, related_name="inventory"
    )
    quantity = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["quantity"])]

    def __str__(self):
        return f"{self.variant.sku}: {self.available} available"

    @property
    def available(self):
        return max(0, self.quantity - self.reserved)


class Price(models.Model):
    """Current selling price for a variant. History preserved via valid_from/to."""

    variant = models.ForeignKey(
        "catalog.ProductVariant", on_delete=models.CASCADE, related_name="prices"
    )
    mrp = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="INR")
    valid_from = models.DateTimeField(auto_now_add=True, db_index=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-valid_from"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(selling_price__gte=0),
                name="price_selling_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(selling_price__lte=models.F("mrp")),
                name="price_selling_lte_mrp",
            ),
        ]
        indexes = [models.Index(fields=["variant", "is_current"])]

    def __str__(self):
        return f"{self.variant.sku}: {self.selling_price} {self.currency}"
