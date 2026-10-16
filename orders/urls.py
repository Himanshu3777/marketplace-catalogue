from django.urls import path

from .views import checkout, order_detail

urlpatterns = [
    path("orders/checkout/", checkout, name="order-checkout"),
    path("orders/<str:order_number>/", order_detail, name="order-detail"),
]
