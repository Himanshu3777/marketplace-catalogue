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
