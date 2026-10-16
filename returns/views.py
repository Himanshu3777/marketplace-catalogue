"""Return / replacement request API. JSON only."""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from orders.models import OrderItem

from .models import ReturnRequest
from .serializers import ReturnRequestSerializer


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def return_request_create(request):
    order_item_id = request.data.get("order_item_id")
    request_type = str(request.data.get("request_type", "")).upper()
    reason = str(request.data.get("reason", "")).upper()
    description = str(request.data.get("description", "")).strip()

    if request_type not in dict(ReturnRequest.TYPE_CHOICES):
        return Response(
            {"error": "request_type must be RETURN or REPLACEMENT"},
            status=status.HTTP_400_BAD_REQUEST)
    if reason not in dict(ReturnRequest.REASON_CHOICES):
        return Response(
            {"error": "reason must be one of: " +
                      ", ".join(k for k, _ in ReturnRequest.REASON_CHOICES)},
            status=status.HTTP_400_BAD_REQUEST)

    item = get_object_or_404(
        OrderItem.objects.select_related("order"), pk=order_item_id)
    ok, message = ReturnRequest.check_eligible(item)
    if not ok:
        return Response({"error": message},
                        status=status.HTTP_400_BAD_REQUEST)

    rr = ReturnRequest.objects.create(
        order_item=item,
        request_type=request_type,
        reason=reason,
        description=description,
    )
    return Response(ReturnRequestSerializer(rr).data,
                    status=status.HTTP_201_CREATED)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def return_request_detail(request, pk):
    rr = get_object_or_404(
        ReturnRequest.objects.select_related("order_item", "order_item__order"),
        pk=pk,
    )
    return Response(ReturnRequestSerializer(rr).data)
