import json

from django.db.models.deletion import ProtectedError
from rest_framework import filters, status
from rest_framework.decorators import action

from apps.inventory.models import Vendor

from core.utils.responses import APIResponse

from ..serializers import VendorDropdownSerializer, VendorSerializer
from .shared import BaseInventoryViewSet


class VendorViewSet(BaseInventoryViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    search_fields = [
        "trade_name",
        "category",
        "license_no",
        "trn_number",
        "phone",
        "email",
        "primary_activity",
        "status",
    ]
    ordering_fields = [
        "id",
        "trade_name",
        "category",
        "license_no",
        "trn_number",
        "status",
    ]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "procurement.vendors"

    @staticmethod
    def _build_vendor_payload(request):
        vendor_data_raw = request.data.get("vendor_data")
        if vendor_data_raw is None:
            return request.data

        if isinstance(vendor_data_raw, dict):
            payload = dict(vendor_data_raw)
        else:
            payload = json.loads(vendor_data_raw)

        if not isinstance(payload, dict):
            raise ValueError("vendor_data must be a JSON object.")

        for file_field in ("trade_license_pdf", "trn_certificate", "bank_documant"):
            if file_field in request.FILES:
                payload[file_field] = request.FILES[file_field]
            elif file_field in request.data and request.data.get(file_field) in ("", "null", "None"):
                payload[file_field] = None

        return payload

    def create(self, request, *args, **kwargs):
        try:
            payload = self._build_vendor_payload(request)
        except (TypeError, ValueError, json.JSONDecodeError):
            return APIResponse.error(
                message="Invalid vendor_data. Send a valid JSON object string in vendor_data.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Vendor created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        try:
            payload = self._build_vendor_payload(request)
        except (TypeError, ValueError, json.JSONDecodeError):
            return APIResponse.error(
                message="Invalid vendor_data. Send a valid JSON object string in vendor_data.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(instance, data=payload, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Vendor updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            linked_po_numbers = list(
                instance.purchase_orders.exclude(po_number__isnull=True).values_list("po_number", flat=True)[:5]
            )
            reference_text = ", ".join(linked_po_numbers) if linked_po_numbers else "existing purchase orders"
            return APIResponse.error(
                message=f"Cannot delete vendor because it is linked to purchase order(s): {reference_text}.",
                status_code=status.HTTP_409_CONFLICT,
            )

        return APIResponse.success(
            data=None,
            message="Vendor deleted successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="dropdown")
    def dropdown(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = VendorDropdownSerializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Vendors retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
