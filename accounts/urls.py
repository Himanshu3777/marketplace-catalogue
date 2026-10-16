from django.urls import path

from .views import (
    login_view, logout_view, me, my_orders, register, save_default_address,
)

urlpatterns = [
    path("accounts/register/", register, name="account-register"),
    path("accounts/login/", login_view, name="account-login"),
    path("accounts/logout/", logout_view, name="account-logout"),
    path("accounts/me/", me, name="account-me"),
    path("accounts/orders/", my_orders, name="account-orders"),
    path("accounts/address/", save_default_address,
         name="account-address"),
]
