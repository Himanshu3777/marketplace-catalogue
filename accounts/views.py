"""Customer authentication API — Django session auth (no tokens to leak).

Security notes:
- Passwords are hashed with Django's PBKDF2 hasher; never stored raw.
- Login/register are throttled per IP (brute-force protection).
- The frontend must never invent auth state — /api/accounts/me/ is the
  single source of truth.
"""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes, throttle_classes,
)

from marketplace.session_auth import SessionAuthNoCSRF
from rest_framework.response import Response

from cart.models import Cart, CartItem
from marketplace.throttles import AuthThrottle
from orders.serializers import OrderSerializer

from .models import CustomerProfile


def user_payload(user):
    profile = getattr(user, "customer_profile", None)
    return {
        "id": user.id,
        "name": user.first_name or user.username,
        "email": user.email,
        "phone": profile.phone if profile else "",
        "default_address": {
            "name": profile.default_name if profile else "",
            "address_line1": profile.default_address_line1 if profile else "",
            "address_line2": profile.default_address_line2 if profile else "",
            "city": profile.default_city if profile else "",
            "state": profile.default_state if profile else "",
            "pincode": profile.default_pincode if profile else "",
        } if profile else {},
    }


def merge_session_cart_into_user(request, user, session_key=None):
    """Move the anonymous session cart into the user's cart on login.

    Quantities are summed per variant (never duplicated). The session cart
    row is removed afterwards.

    NOTE: pass the PRE-login session key — Django's login() rotates
    (cycle_key) the session, so request.session.session_key after login
    is already the new one.
    """
    session_key = session_key or request.session.session_key
    if not session_key:
        return
    try:
        session_cart = Cart.objects.get(session_key=session_key)
    except Cart.DoesNotExist:
        return
    # Don't merge a cart that's already the user's own
    if session_cart.user_id == user.id:
        return
    user_cart, _ = Cart.objects.get_or_create(
        user=user, defaults={"session_key": f"user-{user.id}"})
    with transaction.atomic():
        for item in session_cart.items.select_related("variant").all():
            existing = CartItem.objects.filter(
                cart=user_cart, variant=item.variant).first()
            if existing:
                existing.quantity += item.quantity
                existing.save(update_fields=["quantity"])
            else:
                item.cart = user_cart
                item.save(update_fields=["cart"])
        # Stock re-check happens at cart-add/checkout time; merged qty that
        # exceeds stock is caught at checkout with a clear 400.
        session_cart.delete()
    # Point the session at the user's cart for subsequent requests
    request.session["cart_id"] = user_cart.id


def get_active_cart(request):
    """Cart for the request: user's cart if logged in, else session cart."""
    from cart.views import get_or_create_cart
    return get_or_create_cart(request)


@api_view(["POST"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
@throttle_classes([AuthThrottle])
def register(request):
    data = request.data
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    phone = str(data.get("phone", "")).strip()
    password = str(data.get("password", ""))

    errors = {}
    if not name:
        errors["name"] = "Name is required."
    if not email:
        errors["email"] = "Email is required."
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "Enter a valid email address."
        else:
            if User.objects.filter(email__iexact=email).exists():
                errors["email"] = "An account with this email already exists."
    phone_digits = "".join(c for c in phone if c.isdigit())
    if phone_digits.startswith("91") and len(phone_digits) == 12:
        phone_digits = phone_digits[2:]
    if phone and (len(phone_digits) != 10 or phone_digits[0] not in "6789"):
        errors["phone"] = "Enter a valid 10-digit mobile number."
    if not password:
        errors["password"] = "Password is required."
    else:
        try:
            validate_password(password)
        except ValidationError as e:
            errors["password"] = " ".join(e.messages)
    if errors:
        return Response({"errors": errors},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=email, email=email, password=password,
                first_name=name[:30],
            )
            CustomerProfile.objects.create(
                user=user, phone=phone_digits)
    except IntegrityError:
        return Response(
            {"errors": {"email": "An account with this email already exists."}},
            status=status.HTTP_400_BAD_REQUEST)

    # Capture BEFORE login(): Django's login() rotates the session key,
    # so the post-login session_key would not find the guest cart.
    guest_session_key = request.session.session_key
    login(request, user)
    merge_session_cart_into_user(request, user,
                                 session_key=guest_session_key)
    return Response({"user": user_payload(user)},
                    status=status.HTTP_201_CREATED)


@api_view(["POST"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
@throttle_classes([AuthThrottle])
def login_view(request):
    email = str(request.data.get("email", "")).strip().lower()
    password = str(request.data.get("password", ""))
    if not email or not password:
        return Response({"error": "Email and password are required."},
                        status=status.HTTP_400_BAD_REQUEST)
    # Generic message — never reveal whether the email exists.
    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response({"error": "Invalid email or password."},
                        status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_active:
        return Response({"error": "This account is disabled."},
                        status=status.HTTP_403_FORBIDDEN)
    # Capture BEFORE login(): Django's login() rotates the session key.
    guest_session_key = request.session.session_key
    login(request, user)
    merge_session_cart_into_user(request, user,
                                 session_key=guest_session_key)
    return Response({"user": user_payload(user)})


@api_view(["POST"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
def logout_view(request):
    logout(request)
    return Response({"ok": True})


@api_view(["GET"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
def me(request):
    if not request.user.is_authenticated:
        return Response({"user": None})
    return Response({"user": user_payload(request.user)})


@api_view(["GET"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
def my_orders(request):
    """Orders belonging to the logged-in customer (newest first)."""
    if not request.user.is_authenticated:
        return Response({"error": "Login required."},
                        status=status.HTTP_401_UNAUTHORIZED)
    orders = (request.user.orders.prefetch_related("items")
              .order_by("-created_at")[:50])
    return Response({"orders": OrderSerializer(orders, many=True).data})


@api_view(["POST"])
@authentication_classes([SessionAuthNoCSRF])
@permission_classes([])
def save_default_address(request):
    """Store the customer's default delivery address for fast checkout."""
    if not request.user.is_authenticated:
        return Response({"error": "Login required."},
                        status=status.HTTP_401_UNAUTHORIZED)
    data = request.data
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
    for field in ("default_name", "default_address_line1",
                  "default_address_line2", "default_city", "default_state",
                  "default_pincode"):
        setattr(profile, field, str(data.get(field, "")).strip())
    phone_digits = "".join(c for c in str(data.get("phone", "")) if c.isdigit())
    if phone_digits:
        profile.phone = phone_digits
    profile.save()
    return Response({"user": user_payload(request.user)})
