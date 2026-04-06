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
        "legal_trade_name",
        "trade_license_number",
        "tax_registration_number",
        "phone_number",
        "email_address",
        "business_activity",
        "status",
    ]
    ordering_fields = [
        "id",
        "legal_trade_name",
        "trade_license_number",
        "tax_registration_number",
        "status",
    ]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "procurement.vendors"

    @action(detail=False, methods=["get"], url_path="dropdown")
    def dropdown(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = VendorDropdownSerializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Vendors retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
