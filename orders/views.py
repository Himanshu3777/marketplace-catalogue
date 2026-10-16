"""Guest checkout + order tracking API. JSON only."""
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from cart.models import Cart
from cart.views import get_or_create_cart

from .models import Order, OrderItem
from .serializers import OrderSerializer


def available_stock(variant):
    inv = getattr(variant, "inventory", None)
    return inv.available if inv else 0


REQUIRED_FIELDS = ["customer_name", "phone", "address_line1", "city",
                   "state", "pincode"]


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
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

    cart = get_or_create_cart(request)
    items = list(
        cart.items.select_related("variant", "variant__product",
                                 "variant__inventory")
        .order_by("id")
    )
    if not items:
        return Response({"error": "Your cart is empty"},
                        status=status.HTTP_400_BAD_REQUEST)

    # Validate stock before charging ahead
    for item in items:
        stock = available_stock(item.variant)
        if item.quantity > stock:
            return Response(
                {"error": f"Only {stock} unit(s) of "
                          f"{item.variant.product.name} available",
                 "available": stock},
                status=status.HTTP_400_BAD_REQUEST,
            )

    with transaction.atomic():
        subtotal = round(sum(item.variant.final_price * item.quantity
                             for item in items), 2)
        delivery_fee = Order.delivery_fee_for(subtotal)
        order = Order.objects.create(
            order_number=Order.generate_order_number(),
            customer_name=data["customer_name"].strip(),
            phone=str(data["phone"]).strip(),
            email=str(data.get("email", "")).strip(),
            address_line1=data["address_line1"].strip(),
            address_line2=str(data.get("address_line2", "")).strip(),
            city=data["city"].strip(),
            state=data["state"].strip(),
            pincode=str(data["pincode"]).strip(),
            payment_method=payment_method,
            notes=str(data.get("notes", "")).strip(),
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total=round(subtotal + delivery_fee, 2),
            session_key=request.session.session_key or "",
        )
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

    return Response(OrderSerializer(order).data,
                    status=status.HTTP_201_CREATED)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"), order_number=order_number
    )
    return Response(OrderSerializer(order).data)
