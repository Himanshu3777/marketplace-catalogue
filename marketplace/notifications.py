"""Order email notifications (Gmail SMTP).

Setup (Render dashboard env vars):
- EMAIL_HOST_USER: Gmail address
- EMAIL_HOST_PASSWORD: Gmail App Password (not the login password!
  Generate at myaccount.google.com → Security → App passwords)
- DEFAULT_FROM_EMAIL: "MarketPlace <you@gmail.com>"

Without these, emails fall back to the console backend (logged, not sent)
so checkout never breaks because email is down.
"""
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def _send(to_email, subject, template, context):
    """Send an email; never raise (checkout must not break on email failure)."""
    if not to_email:
        return False
    try:
        html = render_to_string(template, context)
        # Plain-text fallback: strip tags crudely
        import re
        text = re.sub(r"<[^>]+>", "", html)
        text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
        send_mail(
            subject=subject,
            message=text,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL",
                               "MarketPlace <noreply@marketplace.local>"),
            recipient_list=[to_email],
            html_message=html,
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception("Failed to send email '%s' to %s", subject, to_email)
        return False


def order_confirmation(order):
    """Sent right after checkout."""
    items_html = "".join(
        f"<li>{i.product_name} ({i.variant_name}) × {i.quantity} — "
        f"₹{i.price}</li>"
        for i in order.items.all()
    )
    return _send(
        order.email,
        f"Order {order.order_number} confirmed! 🎉",
        "emails/order_confirmation.html",
        {"order": order, "items_html": items_html},
    )


def order_status_update(order):
    """Sent on CONFIRMED / SHIPPED / OUT_FOR_DELIVERY / DELIVERED / CANCELLED."""
    labels = {
        "CONFIRMED": ("Your order is confirmed ✅",
                      "The seller is preparing your items."),
        "SHIPPED": ("Your order has shipped 📦",
                    "It's on its way to you!"),
        "OUT_FOR_DELIVERY": ("Out for delivery 🛵",
                             "Your order arrives today — keep your phone handy."),
        "DELIVERED": ("Delivered! 🎉",
                      "Enjoy! Damaged or wrong item? You have 7 days to "
                      "request a return/replacement."),
        "CANCELLED": ("Order cancelled",
                      "Your order was cancelled. Reserved stock released. "
                      "If you paid online, the refund is being processed."),
    }
    subject, body = labels.get(order.status, ("Order update", ""))
    if not subject:
        return False
    return _send(
        order.email,
        f"{subject} — {order.order_number}",
        "emails/order_status.html",
        {"order": order, "body": body, "subject": subject},
    )


def return_status_update(return_request):
    """Sent when a return/replacement request changes status."""
    order = return_request.order_item.order
    return _send(
        order.email,
        f"Return update — {return_request.get_status_display()}",
        "emails/return_status.html",
        {"rr": return_request, "order": order},
    )
