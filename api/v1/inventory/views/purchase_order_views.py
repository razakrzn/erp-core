import json

from rest_framework import filters, status

from apps.inventory.models import PurchaseOrder
from core.utils.responses import APIResponse

from ..serializers import PurchaseOrderListSerializer, PurchaseOrderSerializer
from .shared import BaseInventoryViewSet


class PurchaseOrderViewSet(BaseInventoryViewSet):
    queryset = PurchaseOrder.objects.select_related(
        "purchase_requisition",
        "vendor",
        "created_by",
        "updated_by",
        "confirmed_by",
    ).prefetch_related("po_line_items")
    serializer_class = PurchaseOrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "po_number",
        "status",
        "vendor__trade_name",
        "purchase_requisition__purchase_request_number",
        "associated_job",
        "internal_remarks",
    ]
    ordering_fields = [
        "id",
        "po_issued_date",
        "status",
        "net_amount",
        "grand_total",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]
    permission_prefix = "procurement.purchase_orders"

    def get_serializer_class(self):
        if self.action == "list":
            return PurchaseOrderListSerializer
        return PurchaseOrderSerializer

    @staticmethod
    def _normalize_payload(request):
        payload = request.data.copy()
        line_items_raw = payload.get("line_items", None)
        if isinstance(line_items_raw, str):
            normalized = line_items_raw.strip()
            payload["line_items"] = json.loads(normalized) if normalized else []
        return payload

    def create(self, request, *args, **kwargs):
        try:
            payload = self._normalize_payload(request)
        except (TypeError, ValueError, json.JSONDecodeError):
            return APIResponse.error(
                message="Invalid line_items. Send a valid JSON array for line_items.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self._success_created(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        try:
            payload = self._normalize_payload(request)
        except (TypeError, ValueError, json.JSONDecodeError):
            return APIResponse.error(
                message="Invalid line_items. Send a valid JSON array for line_items.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(instance, data=payload, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self._success_updated(serializer.data)

    def _success_created(self, data):
        return APIResponse.success(
            data=data,
            message="Purchase Order created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def _success_updated(self, data):
        return APIResponse.success(
            data=data,
            message="Purchase Order updated successfully.",
            status_code=status.HTTP_200_OK,
        )
