"""Admin dashboard stats — injected into the Django admin index page."""
from django.db.models import Count, Sum

from inventory.models import Inventory
from orders.models import Order
from returns.models import ReturnRequest


def dashboard_stats():
    """Key business metrics for the admin landing page."""
    paid_orders = Order.objects.filter(payment_status=Order.PAYMENT_PAID)
    revenue = paid_orders.aggregate(
        total=Sum("total"))["total"] or 0

    pending_orders = Order.objects.filter(
        status__in=[Order.STATUS_PLACED, Order.STATUS_CONFIRMED]).count()

    pending_returns = ReturnRequest.objects.filter(
        status=ReturnRequest.STATUS_REQUESTED).count()

    low_stock = Inventory.objects.filter(
        quantity__lte=10).count()  # at/below default threshold
    out_of_stock = sum(1 for inv in
                       Inventory.objects.only("quantity", "reserved")
                       if inv.available <= 0)

    recent_orders = list(
        Order.objects.order_by("-created_at")
        .values("order_number", "customer_name", "status", "total")[:8])

    return {
        "total_orders": Order.objects.count(),
        "revenue": round(float(revenue), 2),
        "pending_orders": pending_orders,
        "pending_returns": pending_returns,
        "low_stock_count": low_stock,
        "out_of_stock_count": out_of_stock,
        "recent_orders": recent_orders,
    }
