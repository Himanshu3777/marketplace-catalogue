from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import CustomerProfile


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = [CustomerProfileInline]
    list_display = ["username", "email", "first_name", "is_active",
                    "date_joined"]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "default_city", "updated_at"]
    search_fields = ["user__username", "user__email", "phone"]
