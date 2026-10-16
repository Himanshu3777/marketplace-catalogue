"""Customer profile — extends Django's built-in User with shop fields."""
from django.conf import settings
from django.db import models


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    # Default address for one-click checkout
    default_name = models.CharField(max_length=120, blank=True)
    default_address_line1 = models.CharField(max_length=255, blank=True)
    default_address_line2 = models.CharField(max_length=255, blank=True)
    default_city = models.CharField(max_length=80, blank=True)
    default_state = models.CharField(max_length=80, blank=True)
    default_pincode = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
