"""Session cart API. JSON only — no auth, cart is keyed by session."""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes

from marketplace.session_auth import SessionAuthNoCSRF

from marketplace.throttles import CartWriteThrottle
from rest_framework.response import Response

from catalog.models import ProductVariant

from .models import Cart, CartItem
from .serializers import CartItemSerializer


def get_or_create_cart(request):
    """Return the session's cart, creating the session + cart if needed.

    Logged-in users get their persistent user cart (survives sessions);
    guests get the session-keyed cart (merged into the user cart on login).
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(
            user=request.user,
            defaults={"session_key": f"user-{request.user.id}"})
        return cart
    if not request.session.session_key:
        request.session.save()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def cart_payload(cart):
    items = (
        cart.items.select_related(
            "variant", "variant__product", "variant__product__brand"
        )
        .prefetch_related("variant__images", "variant__product__images",
                          "variant__inventory")
        .order_by("id")
    )
    data = CartItemSerializer(items, many=True).data
    return {
        "items": data,
        "item_count": sum(i["quantity"] for i in data),
        "subtotal": round(sum(i["line_total"] for i in data), 2),
    }


def available_stock(variant):
    inv = getattr(variant, "inventory", None)
    return inv.available if inv else 0


@api_view(["GET"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
def cart_detail(request):
    cart = get_or_create_cart(request)
    return Response(cart_payload(cart))


@api_view(["POST"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
@throttle_classes([CartWriteThrottle])
def cart_add(request):
    variant_id = request.data.get("variant_id")
    try:
        quantity = int(request.data.get("quantity", 1))
    except (TypeError, ValueError):
        return Response({"error": "quantity must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST)
    if quantity < 1:
        return Response({"error": "quantity must be at least 1"},
                        status=status.HTTP_400_BAD_REQUEST)
    variant = get_object_or_404(
        ProductVariant.objects.select_related("inventory"),
        pk=variant_id, is_active=True, product__is_active=True,
    )
    stock = available_stock(variant)
    if stock <= 0:
        return Response({"error": "This variant is out of stock"},
                        status=status.HTTP_400_BAD_REQUEST)
    cart = get_or_create_cart(request)
    try:
        item = CartItem.objects.get(cart=cart, variant=variant)
        new_qty = item.quantity + quantity
    except CartItem.DoesNotExist:
        item = None
        new_qty = quantity
    if new_qty > stock:
        return Response(
            {"error": f"Only {stock} unit(s) available", "available": stock},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if item is None:
        item = CartItem.objects.create(
            cart=cart, variant=variant, quantity=quantity,
            price_at_add=variant.final_price)
        created = True
    else:
        item.quantity = new_qty
        # Keep the ORIGINAL price snapshot — checkout compares it against
        # the current price and blocks on drift (409) instead of silently
        # charging more.
        item.save()
        created = False
    return Response(cart_payload(cart), status=status.HTTP_201_CREATED
                    if created else status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
@throttle_classes([CartWriteThrottle])
def cart_update(request):
    item_id = request.data.get("item_id")
    try:
        quantity = int(request.data.get("quantity", 1))
    except (TypeError, ValueError):
        return Response({"error": "quantity must be an integer"},
                        status=status.HTTP_400_BAD_REQUEST)
    if quantity < 1:
        return Response({"error": "quantity must be at least 1"},
                        status=status.HTTP_400_BAD_REQUEST)
    cart = get_or_create_cart(request)
    item = get_object_or_404(
        CartItem.objects.select_related("variant", "variant__inventory"),
        pk=item_id, cart=cart,
    )
    stock = available_stock(item.variant)
    if quantity > stock:
        return Response(
            {"error": f"Only {stock} unit(s) available", "available": stock},
            status=status.HTTP_400_BAD_REQUEST,
        )
    item.quantity = quantity
    item.save()
    return Response(cart_payload(cart))


@api_view(["POST"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
@throttle_classes([CartWriteThrottle])
def cart_remove(request):
    item_id = request.data.get("item_id")
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    return Response(cart_payload(cart))


@api_view(["POST"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
@throttle_classes([CartWriteThrottle])
def cart_clear(request):
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    return Response(cart_payload(cart))
