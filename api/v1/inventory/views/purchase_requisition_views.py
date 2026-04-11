import json

from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from apps.inventory.models import PurchaseRequisition, PurchaseRequisitionLineItem
from core.utils.responses import APIResponse

from ..serializers import (
    PurchaseRequisitionLineItemSerializer,
    PurchaseRequisitionListSerializer,
    PurchaseRequisitionSerializer,
)
from .shared import BaseInventoryViewSet


class PurchaseRequisitionViewSet(BaseInventoryViewSet):
    queryset = PurchaseRequisition.objects.select_related("created_by").prefetch_related("line_items")
    serializer_class = PurchaseRequisitionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "purchase_request_number",
        "requisition_type",
        "stock_reason_category",
        "project_site",
        "job_order_ref",
        "priority",
        "status",
        "delivery_location",
        "created_by__username",
    ]
    ordering_fields = [
        "id",
        "requisition_date",
        "required_by_date",
        "priority",
        "status",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]
    permission_prefix = "procurement.purchase_requisitions"

    @staticmethod
    def _normalize_payload(request):
        payload = request.data.copy()
        line_items_raw = payload.get("line_items", None)

        if isinstance(line_items_raw, str):
            normalized = line_items_raw.strip()
            if normalized:
                payload["line_items"] = json.loads(normalized)
            else:
                payload["line_items"] = []

        return payload

    def get_serializer_class(self):
        if self.action == "list":
            return PurchaseRequisitionListSerializer
        return PurchaseRequisitionSerializer

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
        return APIResponse.success(
            data=serializer.data,
            message="Purchase Requisition created successfully.",
            status_code=status.HTTP_201_CREATED,
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

        instance.is_approved = value
        if value:
            instance.is_rejected = False
            instance.status = "Approved"
            instance.approved_by = user
            instance.rejected_by = None
        else:
            # Cancel approval only if currently approved.
            if instance.status == "Approved":
                instance.status = "Submitted for Approval"
            instance.approved_by = None

        instance.updated_by = user if user else instance.updated_by
        instance.save(
            update_fields=[
                "is_approved",
                "is_rejected",
                "status",
                "approved_by",
                "rejected_by",
                "updated_by",
                "updated_at",
            ]
        )

        message = "Purchase Requisition Approved" if value else "Purchase Requisition Approval Cancelled"
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

        instance.is_rejected = value
        if value:
            instance.is_approved = False
            instance.status = "Rejected"
            instance.rejected_by = user
            instance.approved_by = None
        else:
            # Cancel rejection only if currently rejected.
            if instance.status == "Rejected":
                instance.status = "Submitted for Approval"
            instance.rejected_by = None

        instance.updated_by = user if user else instance.updated_by
        instance.save(
            update_fields=[
                "is_approved",
                "is_rejected",
                "status",
                "approved_by",
                "rejected_by",
                "updated_by",
                "updated_at",
            ]
        )

        message = "Purchase Requisition Rejected" if value else "Purchase Requisition Rejection Cancelled"
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_200_OK,
        )


class PurchaseRequisitionLineItemViewSet(BaseInventoryViewSet):
    queryset = PurchaseRequisitionLineItem.objects.select_related("purchase_requisition")
    serializer_class = PurchaseRequisitionLineItemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "purchase_requisition__id",
        "product_name",
        "product_code",
        "product_category",
    ]
    ordering_fields = [
        "id",
        "purchase_requisition_id",
        "product_name",
        "product_code",
        "requested_qty",
        "net_required_qty",
    ]
    ordering = ["id"]
    permission_prefix = "procurement.purchase_requisitions"
