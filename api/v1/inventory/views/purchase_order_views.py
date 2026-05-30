import json

from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from apps.inventory.models import PurchaseOrder
from core.utils.responses import APIResponse

from ..serializers import PurchaseOrderListSerializer, PurchaseOrderSerializer
from .shared import BaseInventoryViewSet


class PurchaseOrderViewSet(BaseInventoryViewSet):
    queryset = PurchaseOrder.objects.select_related(
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

    @staticmethod
    def _parse_boolean_action_value(raw_value, field_name="value"):
        if isinstance(raw_value, bool):
            return raw_value
        if raw_value is None:
            raise ValidationError({field_name: "This field is required and must be true or false."})
        normalized = str(raw_value).strip().lower()
        if normalized in {"true", "1", "yes"}:
            return True
        if normalized in {"false", "0", "no"}:
            return False
        raise ValidationError({field_name: "Invalid boolean value. Use true or false."})

    @action(detail=True, methods=["patch"], url_path="approve")
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        value = self._parse_boolean_action_value(request.data.get("value", None), "value")
        user = request.user if request.user and request.user.is_authenticated else None

        instance.is_confirmed = value
        if value:
            instance.status = "Confirmed"
            instance.confirmed_by = user
        else:
            instance.status = "Pending"
            instance.confirmed_by = None

        instance.updated_by = user if user else instance.updated_by
        instance.save(update_fields=["is_confirmed", "status", "confirmed_by", "updated_by", "updated_at"])

        message = "Purchase Order Approved" if value else "Purchase Order Approval Cancelled"
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"], url_path="reject")
    def reject(self, request, *args, **kwargs):
        instance = self.get_object()
        value = self._parse_boolean_action_value(request.data.get("value", None), "value")
        user = request.user if request.user and request.user.is_authenticated else None

        if value:
            instance.is_confirmed = False
            instance.status = "Rejected"
            instance.confirmed_by = None
        else:
            instance.status = "Pending"

        instance.updated_by = user if user else instance.updated_by
        instance.save(update_fields=["is_confirmed", "status", "confirmed_by", "updated_by", "updated_at"])

        message = "Purchase Order Rejected" if value else "Purchase Order Rejection Cancelled"
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_200_OK,
        )
