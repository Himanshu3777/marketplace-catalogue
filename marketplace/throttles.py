"""Shared DRF throttles for money-moving endpoints.

All throttles key on client IP for anonymous (session) users, which is
what this marketplace uses — there is no customer login yet.
"""
from rest_framework.throttling import AnonRateThrottle


class CheckoutThrottle(AnonRateThrottle):
    scope = "checkout"


class CartWriteThrottle(AnonRateThrottle):
    scope = "cart_write"


class ReturnsThrottle(AnonRateThrottle):
    scope = "returns"


class AuthThrottle(AnonRateThrottle):
    scope = "auth"
