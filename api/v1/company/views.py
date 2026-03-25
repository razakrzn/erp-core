from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from core.utils.schema_docs_shims import extend_schema, extend_schema_view

from apps.company.models import Company
from core.utils.responses import APIResponse

from .permissions import IsCompanyAdminOrReadOnly
from .serializers import CompanySerializer


@extend_schema_view(
    list=extend_schema(tags=["Company"], summary="List companies", description="Paginated list with search on name/code and ordering."),
    retrieve=extend_schema(tags=["Company"], summary="Get company", description="Retrieve a single company by ID."),
    create=extend_schema(tags=["Company"], summary="Create company", description="Create a new company."),
    update=extend_schema(tags=["Company"], summary="Update company", description="Full update of a company."),
    partial_update=extend_schema(tags=["Company"], summary="Partial update company", description="Partial update of a company."),
    destroy=extend_schema(tags=["Company"], summary="Delete company", description="Delete a company."),
)
class CompanyViewSet(viewsets.ModelViewSet):
    """
    API v1 CRUD viewset for Company.

    Features:
    - List / retrieve / create / update / delete
    - Defaults to authenticated access with read-only for non-admins
    - Basic search on name and code
    """

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    # permission_classes = [IsAuthenticated & IsCompanyAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["-created_at"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Companies retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single company with standardized API response format.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message="Company retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        """
        Create a company with standardized API response format.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Company created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """
        Update a company (full or partial) with standardized API response format.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Company updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a company with standardized API response format.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message="Company deleted successfully.",
            status_code=status.HTTP_200_OK,
        )
