"""Guest checkout + order tracking API. JSON only."""
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes

from marketplace.session_auth import SessionAuthNoCSRF

from marketplace.throttles import CheckoutThrottle
from rest_framework.response import Response

from cart.models import Cart
from cart.views import cart_payload, get_or_create_cart

from .models import Order, OrderItem
from .permissions import get_order_for_request
from .serializers import OrderSerializer


def available_stock(variant):
    inv = getattr(variant, "inventory", None)
    return inv.available if inv else 0


REQUIRED_FIELDS = ["customer_name", "phone", "address_line1", "city",
                   "state", "pincode"]


@api_view(["POST"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
@throttle_classes([CheckoutThrottle])
def checkout(request):
    data = request.data
    missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]
    if missing:
        return Response(
            {"error": f"Missing required fields: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    payment_method = str(data.get("payment_method", Order.PAYMENT_COD)).upper()
    if payment_method not in dict(Order.PAYMENT_CHOICES):
        return Response({"error": "payment_method must be COD or UPI"},
                        status=status.HTTP_400_BAD_REQUEST)

    # ---- Input validation: Indian phone (10 digits) + pincode (6) ----
    phone_digits = "".join(c for c in str(data["phone"]) if c.isdigit())
    # Accept +91 prefix
    if phone_digits.startswith("91") and len(phone_digits) == 12:
        phone_digits = phone_digits[2:]
    if len(phone_digits) != 10 or not phone_digits[0] in "6789":
        return Response(
            {"error": "Enter a valid 10-digit mobile number"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    pincode_digits = "".join(c for c in str(data["pincode"]) if c.isdigit())
    if len(pincode_digits) != 6:
        return Response(
            {"error": "Enter a valid 6-digit pincode"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ---- Idempotency: same key => return the ORIGINAL order, never a 2nd one
    idempotency_key = str(data.get("idempotency_key", "")).strip()
    if not idempotency_key:
        return Response(
            {"error": "idempotency_key is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    existing = Order.objects.filter(
        idempotency_key=idempotency_key).prefetch_related("items").first()
    if existing:
        payload = OrderSerializer(existing).data
        payload["duplicate"] = True
        return Response(payload, status=status.HTTP_200_OK)

    cart = get_or_create_cart(request)
    items = list(
        cart.items.select_related("variant", "variant__product",
                                 "variant__inventory")
        .order_by("id")
    )
    if not items:
        return Response({"error": "Your cart is empty"},
                        status=status.HTTP_400_BAD_REQUEST)

    # ---- Stock re-check (variant-level, right before money moves) ----
    for item in items:
        stock = available_stock(item.variant)
        if item.quantity > stock:
            return Response(
                {"error": f"Only {stock} unit(s) of "
                          f"{item.variant.product.name} available",
                 "available": stock},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # ---- Price-change detection: never silently charge a new price ----
    # NOTE: compare as rounded floats — variant.final_price returns float
    # while price_at_add is Decimal; direct != is always True (float noise).
    changed = []
    for item in items:
        current = round(float(item.variant.final_price), 2)
        snapshot = round(float(item.price_at_add), 2)
        if snapshot != current:
            changed.append({
                "variant_id": item.variant.id,
                "product_name": item.variant.product.name,
                "old_price": snapshot,
                "new_price": current,
            })
    if changed:
        # Refresh the snapshots so the next attempt uses fresh prices
        for item, c in zip(items, changed):
            item.price_at_add = item.variant.final_price
            item.save(update_fields=["price_at_add"])
        return Response(
            {"error": "Prices changed while you were checking out. "
                      "Please review the updated total.",
             "price_changed": True,
             "changes": changed,
             "cart": cart_payload(cart)},
            status=status.HTTP_409_CONFLICT,
        )

    with transaction.atomic():
        subtotal = round(sum(item.variant.final_price * item.quantity
                             for item in items), 2)
        delivery_fee = Order.delivery_fee_for(subtotal)
        try:
            order = Order.objects.create(
                order_number=Order.generate_order_number(),
                idempotency_key=idempotency_key,
                user=request.user if request.user.is_authenticated else None,
                customer_name=data["customer_name"].strip(),
                phone=phone_digits,
                email=str(data.get("email", "")).strip(),
                address_line1=data["address_line1"].strip(),
                address_line2=str(data.get("address_line2", "")).strip(),
                city=data["city"].strip(),
                state=data["state"].strip(),
                pincode=pincode_digits,
                payment_method=payment_method,
                notes=str(data.get("notes", "")).strip(),
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                total=round(subtotal + delivery_fee, 2),
                session_key=request.session.session_key or "",
            )
        except IntegrityError:
            # Race: same key submitted twice concurrently — return original
            existing = Order.objects.filter(
                idempotency_key=idempotency_key
            ).prefetch_related("items").first()
            payload = OrderSerializer(existing).data
            payload["duplicate"] = True
            return Response(payload, status=status.HTTP_200_OK)
        for item in items:
            v = item.variant
            axes = "/".join(a for a in [v.color, v.size, v.storage] if a)
            OrderItem.objects.create(
                order=order,
                variant=v,
                product_name=v.product.name,
                variant_name=axes or "Standard",
                sku=v.sku,
                price=v.final_price,
                quantity=item.quantity,
            )
            # Reserve stock
            inv = getattr(v, "inventory", None)
            if inv:
                inv.reserved = inv.reserved + item.quantity
                inv.save(update_fields=["reserved"])
        cart.items.all().delete()

    # Confirmation email (best-effort: never breaks checkout)
    try:
        from marketplace.notifications import order_confirmation
        order_confirmation(order)
    except Exception:
        pass

    return Response(OrderSerializer(order).data,
                    status=status.HTTP_201_CREATED)


@api_view(["GET"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
def order_detail(request, order_number):
    order = get_order_for_request(request, order_number)
    return Response(OrderSerializer(order).data)


@api_view(["POST"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
@throttle_classes([CheckoutThrottle])
def order_cancel(request, order_number):
    """Customer cancels their own order (PLACED/CONFIRMED only).

    Stock handling (Phase 1):
    - Unpaid order: release the reservation.
    - Paid order: restock the deducted units (they were sold).
    """
    order = get_order_for_request(request, order_number)
    if order.status == Order.STATUS_CANCELLED:
        return Response({"error": "Order is already cancelled"},
                        status=status.HTTP_400_BAD_REQUEST)
    if order.status not in (Order.STATUS_PLACED, Order.STATUS_CONFIRMED):
        return Response(
            {"error": f"Cannot cancel — order is already {order.status.lower()}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    was_paid = order.payment_verified and order.payment_status == Order.PAYMENT_PAID
    order.status = Order.STATUS_CANCELLED
    order.save(update_fields=["status"])
    if was_paid:
        order.restock_on_cancel_after_payment()
    else:
        order.release_reserved_stock()
    return Response(OrderSerializer(order).data)
