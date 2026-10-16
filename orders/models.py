"""Guest checkout orders. Customer details are captured per order (no accounts)."""
import random
import string

from django.db import models
from django.utils import timezone

FREE_DELIVERY_THRESHOLD = 499
DELIVERY_FEE = 49


class Order(models.Model):
    STATUS_PLACED = "PLACED"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_SHIPPED = "SHIPPED"
    STATUS_OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    STATUS_DELIVERED = "DELIVERED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_PLACED, "Placed"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_OUT_FOR_DELIVERY, "Out for delivery"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    ]
    # Ordered pipeline shown on the tracking timeline.
    STATUS_PIPELINE = [
        STATUS_PLACED, STATUS_CONFIRMED, STATUS_SHIPPED,
        STATUS_OUT_FOR_DELIVERY, STATUS_DELIVERED,
    ]

    PAYMENT_COD = "COD"
    PAYMENT_UPI = "UPI"
    PAYMENT_CHOICES = [
        (PAYMENT_COD, "Cash on Delivery"),
        (PAYMENT_UPI, "UPI"),
    ]

    order_number = models.CharField(max_length=16, unique=True, db_index=True)

    # Guest customer details
    customer_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    pincode = models.CharField(max_length=10)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PLACED,
        db_index=True,
    )
    payment_method = models.CharField(
        max_length=8, choices=PAYMENT_CHOICES, default=PAYMENT_COD
    )
    notes = models.TextField(blank=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    session_key = models.CharField(max_length=64, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(subtotal__gte=0),
                name="order_subtotal_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(total__gte=0),
                name="order_total_non_negative",
            ),
        ]

    def __str__(self):
        return self.order_number

    @staticmethod
    def generate_order_number():
        """Unique MC-XXXXXX number (6 chars, unambiguous alphabet)."""
        alphabet = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
        for _ in range(20):
            num = "MC-" + "".join(random.choices(alphabet, k=6))
            if not Order.objects.filter(order_number=num).exists():
                return num
        # Extremely unlikely fallback: timestamp-based
        return "MC-" + timezone.now().strftime("%y%m%d%H%M%S")

    @staticmethod
    def delivery_fee_for(subtotal):
        return 0 if float(subtotal) >= FREE_DELIVERY_THRESHOLD else DELIVERY_FEE

    @property
    def timeline(self):
        """Ordered status steps with done/current flags for the tracker UI."""
        if self.status == self.STATUS_CANCELLED:
            return [{"status": s, "label": l, "done": False, "current": False,
                     "cancelled": True}
                    for s, l in self.STATUS_CHOICES if s == self.STATUS_CANCELLED]
        steps = []
        reached = self.STATUS_PIPELINE.index(self.status)
        for i, s in enumerate(self.STATUS_PIPELINE):
            label = dict(self.STATUS_CHOICES)[s]
            steps.append({
                "status": s,
                "label": label,
                "done": i < reached,
                "current": i == reached,
            })
        return steps


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="order_items",
    )
    # Price/product snapshots — the catalogue may change after purchase
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=255, blank=True)
    sku = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [models.Index(fields=["order"])]

    def __str__(self):
        return f"{self.order.order_number}: {self.sku} x {self.quantity}"

    @property
    def line_total(self):
        return round(float(self.price) * self.quantity, 2)
