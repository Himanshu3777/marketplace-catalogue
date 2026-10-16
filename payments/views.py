"""Razorpay payment integration (TEST mode — no KYC needed).

Security model (non-negotiable):
1. The amount ALWAYS comes from our Order.total — never from the frontend.
2. An order is marked PAID only after the backend verifies the Razorpay
   signature with HMAC-SHA256 using the secret key (never exposed).
3. The frontend's "payment successful" callback is UNTRUSTED — it only
   triggers the backend verification call.
4. Delayed/lost callbacks are handled via the webhook endpoint.

Keys come from env vars (set in Render dashboard, never in git):
- RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
"""
import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes, throttle_classes,
)
from rest_framework.response import Response

from marketplace.session_auth import SessionAuthNoCSRF
from marketplace.throttles import CheckoutThrottle
from orders.models import Order
from orders.serializers import OrderSerializer

logger = logging.getLogger(__name__)


def razorpay_client():
    """Build a Razorpay client, or return None if keys aren't configured."""
    key_id = getattr(settings, "RAZORPAY_KEY_ID", "")
    key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
    if not key_id or not key_secret:
        return None
    import razorpay
    return razorpay.Client(auth=(key_id, key_secret))


def verify_signature(order_id, payment_id, signature):
    """HMAC-SHA256 signature check — the ONLY proof of payment."""
    key_secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
    if not key_secret:
        return False
    msg = f"{order_id}|{payment_id}".encode()
    expected = hmac.new(key_secret.encode(), msg,
                        hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@api_view(["POST"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
@throttle_classes([CheckoutThrottle])
def create_razorpay_order(request):
    """Create a Razorpay order for an existing PENDING marketplace order.

    Body: { "order_number": "MC-XXXXXX" }
    Returns: { razorpay_order_id, amount, currency, key_id }
    """
    order_number = str(request.data.get("order_number", "")).strip()
    order = get_object_or_404(Order, order_number=order_number)

    if order.payment_status == Order.PAYMENT_PAID:
        return Response({"error": "Order is already paid."},
                        status=status.HTTP_400_BAD_REQUEST)
    if order.status == Order.STATUS_CANCELLED:
        return Response({"error": "Order is cancelled."},
                        status=status.HTTP_400_BAD_REQUEST)

    client = razorpay_client()
    if client is None:
        return Response(
            {"error": "Online payments are not configured yet. "
                      "Please choose Cash on Delivery."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # Amount in paise, ALWAYS from our Order.total (never frontend input)
    amount_paise = int(round(float(order.total) * 100))
    try:
        rzp_order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": order.order_number,
            "notes": {"order_number": order.order_number},
        })
    except Exception as e:
        logger.exception("Razorpay order creation failed")
        return Response({"error": "Payment gateway error. Please try again."},
                        status=status.HTTP_502_BAD_GATEWAY)

    order.gateway_order_id = rzp_order["id"]
    order.save(update_fields=["gateway_order_id"])
    return Response({
        "razorpay_order_id": rzp_order["id"],
        "amount": amount_paise,
        "currency": "INR",
        "key_id": getattr(settings, "RAZORPAY_KEY_ID", ""),
        "order_number": order.order_number,
    })


@api_view(["POST"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
@throttle_classes([CheckoutThrottle])
def verify_payment(request):
    """Verify a Razorpay payment signature and mark the order PAID.

    Body: { "order_number", "razorpay_order_id",
            "razorpay_payment_id", "razorpay_signature" }

    This is the ONLY path that flips payment_status to PAID.
    """
    data = request.data
    order_number = str(data.get("order_number", "")).strip()
    rzp_order_id = str(data.get("razorpay_order_id", "")).strip()
    rzp_payment_id = str(data.get("razorpay_payment_id", "")).strip()
    signature = str(data.get("razorpay_signature", "")).strip()

    if not all([order_number, rzp_order_id, rzp_payment_id, signature]):
        return Response({"error": "Missing payment details."},
                        status=status.HTTP_400_BAD_REQUEST)

    order = get_object_or_404(Order, order_number=order_number)

    # Idempotent: already verified → return success without re-processing
    if order.payment_verified and order.payment_status == Order.PAYMENT_PAID:
        return Response({"verified": True,
                         "order": OrderSerializer(order).data})

    # The gateway order must be the one WE created for THIS order
    if order.gateway_order_id and order.gateway_order_id != rzp_order_id:
        logger.warning("Gateway order mismatch for %s", order_number)
        return Response({"error": "Payment verification failed."},
                        status=status.HTTP_400_BAD_REQUEST)

    if not verify_signature(rzp_order_id, rzp_payment_id, signature):
        order.payment_status = Order.PAYMENT_FAILED
        order.save(update_fields=["payment_status"])
        logger.warning("Bad signature for order %s", order_number)
        return Response({"error": "Payment verification failed."},
                        status=status.HTTP_400_BAD_REQUEST)

    order.gateway_order_id = rzp_order_id
    order.gateway_payment_id = rzp_payment_id
    order.gateway_signature = signature
    order.payment_status = Order.PAYMENT_PAID
    order.payment_verified = True
    order.payment_verified_at = timezone.now()
    if order.status == Order.STATUS_PLACED:
        order.status = Order.STATUS_CONFIRMED
    order.save()
    return Response({"verified": True,
                     "order": OrderSerializer(order).data})


@csrf_exempt
def razorpay_webhook(request):
    """Handle delayed/async Razorpay events (e.g. slow callbacks).

    Verifies the webhook signature, then marks the order paid.
    Configure in Razorpay dashboard: Settings → Webhooks.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    webhook_secret = getattr(settings, "RAZORPAY_WEBHOOK_SECRET", "")
    if not webhook_secret:
        return JsonResponse({"error": "Webhook not configured"}, status=503)

    signature = request.headers.get("X-Razorpay-Signature", "")
    expected = hmac.new(webhook_secret.encode(), request.body,
                        hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return JsonResponse({"error": "Bad signature"}, status=400)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Bad payload"}, status=400)

    event = payload.get("event", "")
    if event == "payment.captured":
        payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
        rzp_order_id = payment.get("order_id", "")
        order = Order.objects.filter(gateway_order_id=rzp_order_id).first()
        if order and not order.payment_verified:
            order.gateway_payment_id = payment.get("id", "")
            order.payment_status = Order.PAYMENT_PAID
            order.payment_verified = True
            order.payment_verified_at = timezone.now()
            if order.status == Order.STATUS_PLACED:
                order.status = Order.STATUS_CONFIRMED
            order.save()
    return JsonResponse({"ok": True})
