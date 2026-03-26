from rest_framework import filters

from apps.crm.models import Enquiry

from ..serializers import EnquiryDetailSerializer, EnquiryListSerializer
from .shared import BaseCRMViewSet


class EnquiryViewSet(BaseCRMViewSet):
    queryset = Enquiry.objects.select_related("existing_client")
    serializer_class = EnquiryDetailSerializer
    search_fields = [
        "enquiry_code",
        "project_name",
        "company_name",
        "phone_number",
        "new_client_name",
        "existing_client__customer_name",
    ]
    ordering_fields = ["enquiry_code", "project_name", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "crm.enquiries"

    def get_serializer_class(self):
        if self.action == "list":
            return EnquiryListSerializer
        return EnquiryDetailSerializer
