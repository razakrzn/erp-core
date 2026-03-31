from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.company.models import Company
from core.utils.responses import APIResponse

from ..serializers import CompanySerializer
from .shared import BaseCompanyViewSet


class CompanyViewSet(BaseCompanyViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    search_fields = ["name", "code", "email", "phone", "licence_number", "trn", "website", "address"]
    ordering_fields = ["name", "code", "email", "phone", "licence_number", "trn", "created_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "sales.leads"

    @action(detail=False, methods=["get", "put", "patch"], url_path="me")
    def me(self, request, *args, **kwargs):
        company = getattr(request.user, "company", None)
        if not company:
            return APIResponse.error(
                message="No company is assigned to the current user.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if request.method in ["PUT", "PATCH"]:
            partial = request.method == "PATCH"
            serializer = self.get_serializer(company, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return APIResponse.success(
                data=serializer.data,
                message="Company updated successfully.",
                status_code=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(company)
        return APIResponse.success(
            data=serializer.data,
            message="Company retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
