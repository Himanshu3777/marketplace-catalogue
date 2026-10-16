from django.urls import path

from .views import create_razorpay_order, razorpay_webhook, verify_payment

urlpatterns = [
    path("payments/create/", create_razorpay_order,
         name="payment-create"),
    path("payments/verify/", verify_payment, name="payment-verify"),
    path("payments/webhook/", razorpay_webhook, name="payment-webhook"),
]
