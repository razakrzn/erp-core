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
        "license_no",
        "trn_number",
        "status",
    ]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "procurement.vendors"

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
