from rest_framework import filters

from apps.company.models import Company

from ..serializers import CompanySerializer
from .shared import BaseCompanyViewSet


class CompanyViewSet(BaseCompanyViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "created_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "sales.leads"
