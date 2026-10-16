from django.urls import path

from .views import cart_add, cart_clear, cart_detail, cart_remove, cart_update

urlpatterns = [
    path("cart/", cart_detail, name="cart-detail"),
    path("cart/add/", cart_add, name="cart-add"),
    path("cart/update/", cart_update, name="cart-update"),
    path("cart/remove/", cart_remove, name="cart-remove"),
    path("cart/clear/", cart_clear, name="cart-clear"),
]
