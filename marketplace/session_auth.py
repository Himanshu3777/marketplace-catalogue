"""Session authentication without CSRF enforcement.

The storefront is a same-origin vanilla-JS app; every JSON API endpoint
already bypasses DRF's CSRF via `@authentication_classes([])`. DRF's
default SessionAuthentication would populate `request.user` from the
session cookie, but it also enforces CSRF on POSTs.

This class just populates `request.user` from Django's session (set by
AuthenticationMiddleware) so views can check `is_authenticated`, keeping
the existing no-CSRF JSON-API pattern consistent.
"""
from rest_framework.authentication import BaseAuthentication


class SessionAuthNoCSRF(BaseAuthentication):
    def authenticate(self, request):
        user = getattr(request._request, "user", None)
        if user is not None and user.is_authenticated:
            return (user, None)
        return None
