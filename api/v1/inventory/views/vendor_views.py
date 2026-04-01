from rest_framework import filters

from apps.inventory.models import Vendor

from ..serializers import VendorSerializer
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

