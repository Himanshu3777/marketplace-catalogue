"""Return / replacement requests for delivered order items."""
from datetime import timedelta

from django.db import models
from django.utils import timezone

# Policy: requests allowed within 7 days of delivery.
RETURN_WINDOW_DAYS = 7


class ReturnRequest(models.Model):
    TYPE_RETURN = "RETURN"
    TYPE_REPLACEMENT = "REPLACEMENT"
    TYPE_CHOICES = [
        (TYPE_RETURN, "Return (refund)"),
        (TYPE_REPLACEMENT, "Replacement"),
    ]

    REASON_DAMAGED = "DAMAGED_IN_TRANSIT"
    REASON_DEFECTIVE = "DEFECTIVE"
    REASON_WRONG_ITEM = "WRONG_ITEM"
    REASON_SIZE_FIT = "SIZE_FIT_ISSUE"
    REASON_QUALITY = "QUALITY_NOT_AS_EXPECTED"
    REASON_OTHER = "OTHER"
    REASON_CHOICES = [
        (REASON_DAMAGED, "Damaged in transit"),
        (REASON_DEFECTIVE, "Defective / not working"),
        (REASON_WRONG_ITEM, "Wrong item delivered"),
        (REASON_SIZE_FIT, "Size / fit issue"),
        (REASON_QUALITY, "Quality not as expected"),
        (REASON_OTHER, "Other"),
    ]

    STATUS_REQUESTED = "REQUESTED"
    STATUS_APPROVED = "APPROVED"
    STATUS_PICKUP_SCHEDULED = "PICKUP_SCHEDULED"
    STATUS_PICKED_UP = "PICKED_UP"
    STATUS_REFUNDED = "REFUNDED"
    STATUS_REPLACEMENT_SHIPPED = "REPLACEMENT_SHIPPED"
    STATUS_CLOSED = "CLOSED"
    STATUS_REJECTED = "REJECTED"
    STATUS_CHOICES = [
        (STATUS_REQUESTED, "Requested"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_PICKUP_SCHEDULED, "Pickup scheduled"),
        (STATUS_PICKED_UP, "Picked up"),
        (STATUS_REFUNDED, "Refunded"),
        (STATUS_REPLACEMENT_SHIPPED, "Replacement shipped"),
        (STATUS_CLOSED, "Closed"),
        (STATUS_REJECTED, "Rejected"),
    ]
    # Terminal states: no further action; a new request may be filed.
    TERMINAL_STATUSES = {STATUS_REJECTED, STATUS_CLOSED, STATUS_REFUNDED}

    order_item = models.ForeignKey(
        "orders.OrderItem", on_delete=models.CASCADE,
        related_name="return_requests",
    )
    request_type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    reason = models.CharField(max_length=32, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=24, choices=STATUS_CHOICES, default=STATUS_REQUESTED,
        db_index=True,
    )
    # ---- Actual money movement (tracked SEPARATELY from the request) ----
    # A return REQUEST is just paperwork. The REFUND is a separate gateway
    # operation — never confuse the two. refund_status tracks real money.
    REFUND_NOT_STARTED = "NOT_STARTED"
    REFUND_INITIATED = "INITIATED"
    REFUND_PROCESSED = "PROCESSED"
    REFUND_FAILED = "FAILED"
    REFUND_STATUS_CHOICES = [
        (REFUND_NOT_STARTED, "Not started"),
        (REFUND_INITIATED, "Initiated"),
        (REFUND_PROCESSED, "Processed"),
        (REFUND_FAILED, "Failed"),
    ]
    refund_status = models.CharField(
        max_length=16, choices=REFUND_STATUS_CHOICES,
        default=REFUND_NOT_STARTED, db_index=True,
    )
    refund_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    gateway_refund_id = models.CharField(max_length=64, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-requested_at"]
        indexes = [models.Index(fields=["order_item", "status"])]

    def __str__(self):
        return f"{self.get_request_type_display()} #{self.id} ({self.status})"

    @property
    def is_active(self):
        return self.status not in self.TERMINAL_STATUSES

    def initiate_gateway_refund(self):
        """Initiate the ACTUAL money refund via Razorpay.

        Only for paid orders. Returns (ok, message). This is separate from
        the return request status — money movement is tracked in
        refund_status, never inferred from request status.
        """
        from django.utils import timezone as tz
        from orders.models import Order
        import logging
        logger = logging.getLogger(__name__)

        order = self.order_item.order
        if order.payment_status != Order.PAYMENT_PAID:
            return False, "Order was not paid online — no gateway refund needed."
        if not order.gateway_payment_id:
            return False, "No gateway payment recorded for this order."
        if self.refund_status == self.REFUND_PROCESSED:
            return False, "Refund already processed."
        if self.refund_status == self.REFUND_INITIATED:
            return False, "Refund already initiated — check gateway dashboard."

        from django.conf import settings
        key_id = getattr(settings, "RAZORPAY_KEY_ID", "")
        key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
        if not key_id or not key_secret:
            return False, "Payment gateway not configured."

        import razorpay
        client = razorpay.Client(auth=(key_id, key_secret))
        # Refund the single item's price (not the whole order)
        amount_paise = int(round(float(self.order_item.price)
                                 * self.order_item.quantity * 100))
        try:
            refund = client.payment.refund(
                order.gateway_payment_id,
                {"amount": amount_paise,
                 "notes": {"return_request": str(self.id)}})
        except Exception as e:
            logger.exception("Razorpay refund failed for return #%s", self.id)
            self.refund_status = self.REFUND_FAILED
            self.save(update_fields=["refund_status"])
            return False, f"Gateway refund failed: {e}"

        self.gateway_refund_id = refund.get("id", "")
        self.refund_amount = self.order_item.price * self.order_item.quantity
        self.refund_status = self.REFUND_PROCESSED
        self.refunded_at = tz.now()
        self.status = self.STATUS_REFUNDED
        self.save()
        # Also reflect on the order
        if order.payment_status == Order.PAYMENT_PAID:
            order.payment_status = Order.PAYMENT_REFUNDED
            order.save(update_fields=["payment_status"])
        return True, f"Refund processed: {self.gateway_refund_id}"

    @staticmethod
    def check_eligible(order_item):
        """Return (ok, message) for the return/replacement policy.

        Policy:
        - Only items of DELIVERED orders.
        - Within RETURN_WINDOW_DAYS of delivery. The Order model tracks
          status changes via updated_at, so order.updated_at is used as a
          proxy for the delivered date (documented limitation: no separate
          delivered_at field exists).
        - At most one active (non-terminal) request per order item.
        """
        from orders.models import Order

        order = order_item.order
        if order.status != Order.STATUS_DELIVERED:
            return False, "Returns are allowed only for delivered orders."
        delivered_at = order.updated_at  # proxy for delivered date
        if timezone.now() - delivered_at > timedelta(days=RETURN_WINDOW_DAYS):
            return False, (
                f"Return window expired — requests are accepted within "
                f"{RETURN_WINDOW_DAYS} days of delivery."
            )
        if order_item.return_requests.exclude(
                status__in=ReturnRequest.TERMINAL_STATUSES).exists():
            return False, "A return/replacement request is already open for this item."
        return True, "Eligible."
