from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser

from apps.company.models import Company
from core.utils.responses import APIResponse

from ..serializers import CompanySerializer
from .shared import BaseCompanyViewSet


class CompanyViewSet(BaseCompanyViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    parser_classes = [MultiPartParser, FormParser]
    search_fields = ["name", "code", "email", "phone", "licence_number", "website", "address"]
    ordering_fields = ["name", "code", "email", "phone", "licence_number", "created_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "sales.leads"

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request, *args, **kwargs):
        company = getattr(request.user, "company", None)
        if not company:
            return APIResponse.error(
                message="No company is assigned to the current user.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(company)
        return APIResponse.success(
            data=serializer.data,
            message="Company retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
