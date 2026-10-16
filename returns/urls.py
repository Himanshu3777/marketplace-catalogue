from django.urls import path

from .views import return_request_create, return_request_detail

urlpatterns = [
    path("returns/request/", return_request_create,
         name="return-request-create"),
    path("returns/<int:pk>/", return_request_detail,
         name="return-request-detail"),
]
