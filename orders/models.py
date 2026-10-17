"""Guest checkout orders. Customer details are captured per order (no accounts)."""
import random
import string
import uuid

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

    # ---- Payment verification (backend is the ONLY source of truth) ----
    # The frontend must NEVER mark an order paid. Only a verified
    # gateway webhook/signature check may flip payment_status to PAID.
    PAYMENT_PENDING = "PENDING"
    PAYMENT_PAID = "PAID"
    PAYMENT_FAILED = "FAILED"
    PAYMENT_REFUNDED = "REFUNDED"
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, "Pending"),
        (PAYMENT_PAID, "Paid"),
        (PAYMENT_FAILED, "Failed"),
        (PAYMENT_REFUNDED, "Refunded"),
    ]
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_PENDING, db_index=True,
    )
    # Gateway references (Razorpay) — set only after backend verification.
    gateway_order_id = models.CharField(max_length=64, blank=True, db_index=True)
    gateway_payment_id = models.CharField(max_length=64, blank=True)
    gateway_signature = models.CharField(max_length=128, blank=True)
    payment_verified = models.BooleanField(default=False)
    payment_verified_at = models.DateTimeField(null=True, blank=True)

    # ---- Idempotency: refresh/double-click must never create 2 orders ----
    # The checkout page generates one UUID per page load and sends it with
    # the request. A repeated request with the same key returns the
    # ORIGINAL order instead of creating a duplicate.
    # NOTE: default=uuid4 is migration-only (for pre-existing rows);
    # the view ALWAYS supplies an explicit key.
    idempotency_key = models.CharField(
        max_length=36, unique=True, db_index=True, default=uuid.uuid4,
    )

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    session_key = models.CharField(max_length=64, blank=True, db_index=True)
    # Customer who placed the order (null = guest checkout).
    # Required before payment-gateway integration: every paid order must
    # be traceable to a verified account.
    user = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders", db_index=True,
    )

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

    def release_reserved_stock(self):
        """Return reserved units to available pool (order cancelled)."""
        from django.db import transaction
        with transaction.atomic():
            for item in self.items.select_related("variant").all():
                if not item.variant_id:
                    continue
                inv = getattr(item.variant, "inventory", None)
                if inv and inv.reserved >= item.quantity:
                    inv.reserved -= item.quantity
                    inv.save(update_fields=["reserved"])

    def deduct_stock_on_payment(self):
        """Convert reservation into a real sale (payment successful).

        Phase 1 rule: successful payment → stock decreases immediately.
        Idempotent: if already deducted (reserved < quantity), skips.
        Uses SELECT FOR UPDATE to prevent concurrent double-deduction.
        """
        from django.db import transaction
        from inventory.models import Inventory
        with transaction.atomic():
            variant_ids = list(self.items.exclude(variant_id=None)
                               .values_list("variant_id", flat=True))
            # Lock inventory rows for the duration of this transaction.
            # order_by ensures consistent lock acquisition order across
            # concurrent transactions, preventing deadlocks.
            locked = {inv.variant_id: inv for inv in
                      Inventory.objects.select_for_update()
                      .filter(variant_id__in=variant_ids)
                      .order_by("variant_id")}
            for item in self.items.select_related("variant").all():
                if not item.variant_id:
                    continue
                inv = locked.get(item.variant_id)
                if inv:
                    take = min(item.quantity, inv.reserved)
                    inv.reserved -= take
                    # Only deduct what was reserved (prevents double-deduct)
                    inv.quantity = max(0, inv.quantity - take)
                    inv.save(update_fields=["reserved", "quantity"])

    def restock_on_cancel_after_payment(self):
        """Return sold units to stock (paid order cancelled)."""
        from django.db import transaction
        from inventory.models import Inventory
        with transaction.atomic():
            variant_ids = list(self.items.exclude(variant_id=None)
                               .values_list("variant_id", flat=True))
            # order_by ensures consistent lock acquisition order across
            # concurrent transactions, preventing deadlocks.
            locked = {inv.variant_id: inv for inv in
                      Inventory.objects.select_for_update()
                      .filter(variant_id__in=variant_ids)
                      .order_by("variant_id")}
            for item in self.items.select_related("variant").all():
                if not item.variant_id:
                    continue
                inv = locked.get(item.variant_id)
                if inv:
                    inv.quantity += item.quantity
                    inv.save(update_fields=["quantity"])

    def deduct_stock_on_delivery(self):
        """Convert reservation into a real sale (order delivered).

        Safety net: for COD orders (no payment verification step) or if
        payment-time deduction was missed. Idempotent via reserved check.
        """
        from django.db import transaction
        with transaction.atomic():
            for item in self.items.select_related("variant").all():
                if not item.variant_id:
                    continue
                inv = getattr(item.variant, "inventory", None)
                if inv:
                    take = min(item.quantity, inv.reserved)
                    inv.reserved -= take
                    inv.quantity = max(0, inv.quantity - take)
                    inv.save(update_fields=["reserved", "quantity"])

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
