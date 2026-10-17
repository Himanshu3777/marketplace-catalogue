from django.urls import path

from .views import (
    forgot_password, login_view, logout_view, me, my_orders, phone_login,
    register, reset_password_confirm, save_default_address,
)

urlpatterns = [
    path("accounts/register/", register, name="account-register"),
    path("accounts/login/", login_view, name="account-login"),
    path("accounts/phone-login/", phone_login, name="account-phone-login"),
    path("accounts/forgot-password/", forgot_password,
         name="account-forgot-password"),
    path("accounts/reset-password/", reset_password_confirm,
         name="account-reset-password"),
    path("accounts/logout/", logout_view, name="account-logout"),
    path("accounts/me/", me, name="account-me"),
    path("accounts/orders/", my_orders, name="account-orders"),
    path("accounts/address/", save_default_address,
         name="account-address"),
]
