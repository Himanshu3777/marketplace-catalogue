from django.contrib import admin

from .models import ReturnRequest


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "order_item", "request_type", "reason", "status",
                    "requested_at"]
    list_filter = ["request_type", "reason", "status", "requested_at"]
    search_fields = ["order_item__order__order_number", "order_item__sku"]
    readonly_fields = ["requested_at", "updated_at"]
    actions = ["approve_requests", "reject_requests", "mark_refunded",
               "mark_replacement_shipped", "mark_closed"]

    @admin.action(description="Approve selected requests")
    def approve_requests(self, request, queryset):
        queryset.filter(status=ReturnRequest.STATUS_REQUESTED).update(
            status=ReturnRequest.STATUS_APPROVED)

    @admin.action(description="Reject selected requests")
    def reject_requests(self, request, queryset):
        queryset.filter(status=ReturnRequest.STATUS_REQUESTED).update(
            status=ReturnRequest.STATUS_REJECTED)

    @admin.action(description="Mark as REFUNDED")
    def mark_refunded(self, request, queryset):
        queryset.filter(
            status__in=[ReturnRequest.STATUS_APPROVED,
                        ReturnRequest.STATUS_PICKED_UP]).update(
            status=ReturnRequest.STATUS_REFUNDED)

    @admin.action(description="Mark replacement as SHIPPED")
    def mark_replacement_shipped(self, request, queryset):
        queryset.filter(request_type=ReturnRequest.TYPE_REPLACEMENT).update(
            status=ReturnRequest.STATUS_REPLACEMENT_SHIPPED)

    @admin.action(description="Mark as CLOSED")
    def mark_closed(self, request, queryset):
        queryset.update(status=ReturnRequest.STATUS_CLOSED)
