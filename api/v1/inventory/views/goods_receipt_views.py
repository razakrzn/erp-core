import json
import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework import filters, status

from apps.inventory.models import GoodsReceipt, PurchaseOrder
from core.utils.responses import APIResponse

from ..serializers import ApprovedPurchaseOrderForGRNSerializer, GoodsReceiptSerializer
from .shared import BaseInventoryViewSet

logger = logging.getLogger(__name__)


class GoodsReceiptViewSet(BaseInventoryViewSet):
    queryset = GoodsReceipt.objects.select_related("purchase_order").prefetch_related(
        "material_intakes",
        "received_goods_photos",
    )
    serializer_class = GoodsReceiptSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "purchase_order__po_number",
        "purchase_order_no",
        "vendor_name",
        "vendor_invoice_no",
        "delivery_challan_no",
        "overall_quality_status",
    ]
    ordering_fields = ["id", "grn_recording_date", "created_at", "updated_at"]
    ordering = ["-created_at"]
    permission_prefix = "procurement.goods_receipts"

    @staticmethod
    def _normalize_payload(request):
        payload = request.data.copy()
        normalized_payload = {}
        logger.info(
            "GRN create payload received: data_keys=%s file_keys=%s",
            list(request.data.keys()),
            list(request.FILES.keys()),
        )

        data_raw = payload.get("data", None)
        if isinstance(data_raw, str):
            normalized_data = data_raw.strip()
            logger.info("GRN create: data field type=str length=%s", len(normalized_data))
            normalized_payload = json.loads(normalized_data) if normalized_data else {}
        elif isinstance(data_raw, dict):
            logger.info("GRN create: data field type=dict")
            normalized_payload = dict(data_raw)
        else:
            logger.info("GRN create: data field missing or non-json, falling back to request.data copy")
            normalized_payload = dict(payload)

        intakes_raw = payload.get("material_intakes", normalized_payload.get("material_intakes"))
        if isinstance(intakes_raw, str):
            normalized = intakes_raw.strip()
            logger.info("GRN create: material_intakes type=str length=%s", len(normalized))
            normalized_payload["material_intakes"] = json.loads(normalized) if normalized else []
        elif isinstance(intakes_raw, list):
            logger.info("GRN create: material_intakes type=list count=%s", len(intakes_raw))
            normalized_payload["material_intakes"] = intakes_raw
        else:
            logger.info("GRN create: material_intakes missing or unsupported type=%s", type(intakes_raw).__name__)

        if request.FILES.get("vendor_delivery_challan"):
            normalized_payload["vendor_delivery_challan"] = request.FILES.get("vendor_delivery_challan")
        if request.FILES.get("vendor_invoice"):
            normalized_payload["vendor_invoice"] = request.FILES.get("vendor_invoice")
        if request.FILES.getlist("received_goods_photo_files"):
            normalized_payload["received_goods_photo_files"] = request.FILES.getlist("received_goods_photo_files")

        material_intakes = normalized_payload.get("material_intakes", []) or []
        logger.info("GRN create: normalized material_intakes count=%s", len(material_intakes))
        for intake in material_intakes:
            client_line_id = str(intake.get("client_line_id", "") or "").strip()
            if not client_line_id:
                logger.info("GRN create: intake without client_line_id, skipping defect photo mapping")
                continue
            file_key = f"defect_photo_{client_line_id}"
            if request.FILES.get(file_key):
                intake["defect_photo"] = request.FILES.get(file_key)
                logger.info("GRN create: mapped defect photo key=%s", file_key)
            else:
                logger.info("GRN create: no defect photo file for key=%s", file_key)
        normalized_payload["material_intakes"] = material_intakes
        logger.info("GRN create: normalized payload keys=%s", list(normalized_payload.keys()))
        return normalized_payload

    def create(self, request, *args, **kwargs):
        try:
            payload = self._normalize_payload(request)
        except (TypeError, ValueError, json.JSONDecodeError):
            logger.exception("GRN create: payload normalization failed")
            return APIResponse.error(
                message="Invalid payload. Send valid JSON in data and valid JSON array for material_intakes.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=payload)
        if not serializer.is_valid():
            logger.warning("GRN create serializer errors: %s", serializer.errors)
            return APIResponse.error(
                message=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            self.perform_create(serializer)
        except DjangoValidationError as exc:
            logger.warning("GRN create model validation error: %s", exc.message_dict or exc.messages)
            return APIResponse.error(
                message=exc.message_dict if hasattr(exc, "message_dict") else exc.messages,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=serializer.data,
            message="Goods Receipt created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path=r"approved-purchase-orders/(?P<po_id>[^/.]+)")
    def approved_purchase_order(self, request, po_id=None, *args, **kwargs):
        approved_filter = Q(status__iexact="approved") | Q(is_approved=True)
        purchase_order = (
            PurchaseOrder.objects.select_related("vendor")
            .prefetch_related("po_line_items", "po_line_items__purchase_requisition")
            .filter(approved_filter, pk=po_id)
            .first()
        )
        if not purchase_order:
            return APIResponse.error(
                message="Approved Purchase Order not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = ApprovedPurchaseOrderForGRNSerializer(purchase_order)
        return APIResponse.success(
            data=serializer.data,
            message="Approved Purchase Order retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="purchase-orders-dropdown")
    def purchase_orders_dropdown(self, request, *args, **kwargs):
        status_value = (request.query_params.get("status") or "").strip()

        queryset = PurchaseOrder.objects.all()
        if status_value:
            queryset = queryset.filter(status__iexact=status_value)

        options = [
            {
                "id": po.id,
                "label": po.po_number or f"PO-{po.id:06d}",
            }
            for po in queryset.order_by("-created_at")
        ]

        return APIResponse.success(
            data=options,
            message="Purchase Orders retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
