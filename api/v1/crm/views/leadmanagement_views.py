from rest_framework import filters

from apps.crm.models import LeadManagement

from ..serializers import LeadManagementDetailSerializer, LeadManagementListSerializer
from .shared import BaseCRMViewSet


class LeadManagementViewSet(BaseCRMViewSet):
    queryset = LeadManagement.objects.all()
    serializer_class = LeadManagementDetailSerializer
    search_fields = ["requirment", "contact_name", "company", "email_address", "phone", "lead_source"]
    ordering_fields = ["contact_name", "company", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "sales.leads"


    def get_serializer_class(self):
        if self.action == "list":
            return LeadManagementListSerializer
        return LeadManagementDetailSerializer
