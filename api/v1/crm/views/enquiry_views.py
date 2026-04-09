from rest_framework import filters
from django.db.models.functions import Lower

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
        "trn",
        "phone_number",
        "new_client_name",
        "existing_client__customer_name",
    ]
    ordering_fields = ["enquiry_code", "project_name", "trn", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "sales.enquiry"

    def filter_queryset(self, queryset):
        ordering = self.request.query_params.get("ordering", "")
        if "project_name" in ordering:
            queryset = queryset.annotate(project_name_lower=Lower("project_name"))

        queryset = super().filter_queryset(queryset)

        # After OrderingFilter has applied sorting, if it was project_name, 
        # replace it with project_name_lower in the queryset's order_by clause.
        if "project_name" in ordering:
            new_order = []
            for field in queryset.query.order_by:
                if field == "project_name":
                    new_order.append("project_name_lower")
                elif field == "-project_name":
                    new_order.append("-project_name_lower")
                else:
                    new_order.append(field)
            queryset = queryset.order_by(*new_order)

        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        status_value = (self.request.query_params.get("status") or "").strip()
        if status_value:
            queryset = queryset.filter(status__iexact=status_value)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return EnquiryListSerializer
        return EnquiryDetailSerializer
