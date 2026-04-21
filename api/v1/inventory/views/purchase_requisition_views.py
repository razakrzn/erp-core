import json

from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from apps.inventory.models import Product, PurchaseRequisition, PurchaseRequisitionLineItem
from core.permissions.rbac_permission import RBACPermission
from core.utils.responses import APIResponse, build_actions

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
        "job_order_ref",
        "rework_notes",
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

    def get_queryset(self):
        queryset = super().get_queryset()
        status_value = (self.request.query_params.get("status") or "").strip()
        if status_value:
            queryset = queryset.filter(status__iexact=status_value)
        return queryset

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        computed_actions = build_actions(request.user, self.permission_prefix)
        detail_actions = {
            "canApprove": bool(computed_actions.get("canApprove", False)),
            "canReject": bool(computed_actions.get("canReject", False)),
        }

        if isinstance(data, dict):
            data = {**data, "actions": detail_actions}

        return APIResponse.success(
            data=data,
            message=f"{self.queryset.model._meta.verbose_name.title()} retrieved successfully.",
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

        instance.is_approved = value
        if value:
            instance.is_rejected = False
            instance.status = "Approved"
            instance.approved_by = user
            instance.rejected_by = None
            instance.reject_note = ""
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
                "reject_note",
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
        reject_note = (request.data.get("reject_note", "") or "").strip()
        if value and not reject_note:
            raise ValidationError({"reject_note": "This field is required when rejecting Purchase Requisition."})
        user = request.user if request.user and request.user.is_authenticated else None

        instance.is_rejected = value
        if value:
            instance.is_approved = False
            instance.status = "Rejected"
            instance.rejected_by = user
            instance.reject_note = reject_note
            instance.approved_by = None
        else:
            # Cancel rejection only if currently rejected.
            if instance.status == "Rejected":
                instance.status = "Submitted for Approval"
            instance.rejected_by = None
            instance.reject_note = ""

        instance.updated_by = user if user else instance.updated_by
        instance.save(
            update_fields=[
                "is_approved",
                "is_rejected",
                "status",
                "approved_by",
                "rejected_by",
                "reject_note",
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

    @action(detail=False, methods=["get"], url_path="product-names")
    def product_names(self, request, *args, **kwargs):
        product_names = (
            PurchaseRequisitionLineItem.objects.exclude(product_name__isnull=True)
            .exclude(product_name__exact="")
            .order_by("product_name")
            .values_list("product_name", flat=True)
            .distinct()
        )
        return APIResponse.success(
            data=list(product_names),
            message="Product names retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="product-categories")
    def product_categories(self, request, *args, **kwargs):
        product_categories = (
            PurchaseRequisitionLineItem.objects.exclude(product_category__isnull=True)
            .exclude(product_category__exact="")
            .order_by("product_category")
            .values_list("product_category", flat=True)
            .distinct()
        )
        return APIResponse.success(
            data=list(product_categories),
            message="Product categories retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="preferred-vendor-names")
    def preferred_vendor_names(self, request, *args, **kwargs):
        product_ids = (
            PurchaseRequisitionLineItem.objects.exclude(product_id__isnull=True)
            .values_list("product_id", flat=True)
            .distinct()
        )
        preferred_vendor_names = (
            Product.objects.filter(id__in=product_ids)
            .exclude(preferred_supplier__isnull=True)
            .exclude(preferred_supplier__trade_name__isnull=True)
            .exclude(preferred_supplier__trade_name__exact="")
            .order_by("preferred_supplier__trade_name")
            .values_list("preferred_supplier__trade_name", flat=True)
            .distinct()
        )
        return APIResponse.success(
            data=list(preferred_vendor_names),
            message="Preferred vendor names retrieved successfully.",
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


class PurchaseRequisitionProductNameViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, RBACPermission]
    permission_prefix = "procurement.purchase_requisitions"

    def list(self, request, *args, **kwargs):
        product_names = (
            PurchaseRequisitionLineItem.objects.exclude(product_name__isnull=True)
            .exclude(product_name__exact="")
            .order_by("product_name")
            .values_list("product_name", flat=True)
            .distinct()
        )
        return APIResponse.success(
            data=list(product_names),
            message="Product names retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class PurchaseRequisitionProductCategoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, RBACPermission]
    permission_prefix = "procurement.purchase_requisitions"

    def list(self, request, *args, **kwargs):
        product_categories = (
            PurchaseRequisitionLineItem.objects.exclude(product_category__isnull=True)
            .exclude(product_category__exact="")
            .order_by("product_category")
            .values_list("product_category", flat=True)
            .distinct()
        )
        return APIResponse.success(
            data=list(product_categories),
            message="Product categories retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class PurchaseRequisitionPreferredVendorNameViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, RBACPermission]
    permission_prefix = "procurement.purchase_requisitions"

    def list(self, request, *args, **kwargs):
        product_ids = (
            PurchaseRequisitionLineItem.objects.exclude(product_id__isnull=True)
            .values_list("product_id", flat=True)
            .distinct()
        )
        preferred_vendor_names = (
            Product.objects.filter(id__in=product_ids)
            .exclude(preferred_supplier__isnull=True)
            .exclude(preferred_supplier__trade_name__isnull=True)
            .exclude(preferred_supplier__trade_name__exact="")
            .order_by("preferred_supplier__trade_name")
            .values_list("preferred_supplier__trade_name", flat=True)
            .distinct()
        )
        return APIResponse.success(
            data=list(preferred_vendor_names),
            message="Preferred vendor names retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
