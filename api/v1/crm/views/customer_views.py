from rest_framework import filters

from apps.crm.models import Customer

from ..serializers import CustomerSerializer
from .shared import BaseCRMViewSet


class CustomerViewSet(BaseCRMViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    search_fields = ["customer_name", "email_address", "company_name", "trn", "phone_number"]
    ordering_fields = ["customer_name", "trn", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "sales.customers"
