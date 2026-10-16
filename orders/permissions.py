"""Order access control.

Rules:
- Guest orders (user=None): accessible by order number (capability URL,
  like a tracking link). The number is unguessable (MC-XXXXXX, 31^6 combos).
- User orders (user set): only the owner (or staff) may view/pay/cancel.
  Another logged-in user gets 404 (not 403 — don't reveal existence).
"""
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

from orders.models import Order


def get_order_for_request(request, order_number, prefetch_items=True):
    """Fetch order + enforce ownership. Raises 404 on any violation."""
    qs = Order.objects
    if prefetch_items:
        qs = qs.prefetch_related("items")
    order = get_object_or_404(qs, order_number=order_number)
    if order.user_id is not None:
        # Owned order: must be the owner (or staff via admin, which
        # doesn't use this helper).
        req_user = getattr(request, "user", None)
        if not getattr(req_user, "is_authenticated", False):
            raise NotFound("No Order matches the given query.")
        if req_user.id != order.user_id:
            raise NotFound("No Order matches the given query.")
    return order
