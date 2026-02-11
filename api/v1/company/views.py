from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated

from apps.company.models import Company, CompanyUser
from utils.responses import APIResponse

from .permissions import IsCompanyAdminOrReadOnly
from .serializers import CompanySerializer, CompanyUserSerializer


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
    permission_classes = [IsAuthenticated & IsCompanyAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["-created_at"]
    lookup_field = "code"
    lookup_value_regex = "[^/]+"

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
            status_code=status.HTTP_204_NO_CONTENT,
        )


class CompanyUserViewSet(viewsets.ModelViewSet):
    """
    API v1 CRUD viewset for CompanyUser.

    Features:
    - List / retrieve / create / update / delete company-user links
    - Filterable by company id or company code
    - Uses the same standardized APIResponse wrapper as CompanyViewSet
    """

    queryset = CompanyUser.objects.select_related("company", "user").all()
    serializer_class = CompanyUserSerializer
    permission_classes = [IsAuthenticated & IsCompanyAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "user__username",
        "user__email",
        "company__name",
        "company__code",
    ]
    ordering_fields = ["created_at", "company__name", "user__username"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Optionally filter by company id (?company=<id>) or company code
        (?company_code=<CODE>).
        """
        queryset = super().get_queryset()
        company_id = self.request.query_params.get("company")
        company_code = self.request.query_params.get("company_code")

        if company_id:
            queryset = queryset.filter(company_id=company_id)
        if company_code:
            queryset = queryset.filter(company__code__iexact=company_code)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Company users retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single company user with standardized API response format.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message="Company user retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        """
        Create a company user with standardized API response format.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Company user created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """
        Update a company user (full or partial) with standardized API response
        format.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Company user updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a company user with standardized API response format.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message="Company user deleted successfully.",
            status_code=status.HTTP_204_NO_CONTENT,
        )
