from rest_framework import filters, status, viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.hrm.models.employee import Employee
from core.utils.responses import APIResponse

from ..serializers.employee_serializers import (
    EmployeeLightweightSerializer,
    EmployeeListSerializer,
    EmployeeSerializer,
)


class CompanyScopedEmployeeQuerysetMixin:
    """Shared company-aware employee queryset logic for employee endpoints."""

    def get_company_scoped_employee_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Employee.objects.all()
        if hasattr(user, 'company') and user.company:
            return Employee.objects.filter(company=user.company)
        return Employee.objects.none()


@extend_schema_view(
    list=extend_schema(tags=["HRM-Employee"], summary="List employees", responses={200: EmployeeListSerializer(many=True)}),
    retrieve=extend_schema(tags=["HRM-Employee"], summary="Get employee details", responses={200: EmployeeSerializer}),
    create=extend_schema(tags=["HRM-Employee"], summary="Create employee", request=EmployeeSerializer, responses={201: EmployeeSerializer}),
    update=extend_schema(tags=["HRM-Employee"], summary="Update employee", request=EmployeeSerializer, responses={200: EmployeeSerializer}),
    partial_update=extend_schema(tags=["HRM-Employee"], summary="Partial update employee", request=EmployeeSerializer, responses={200: EmployeeSerializer}),
    destroy=extend_schema(tags=["HRM-Employee"], summary="Delete employee", responses={200: None}),
)
class EmployeeViewSet(CompanyScopedEmployeeQuerysetMixin, viewsets.ModelViewSet):
    """
    API v1 CRUD viewset for Employee.

    Features:
    - List / retrieve / create / update / delete employees
    - Authenticated access by default
    - Filtered by company
    """

    queryset = Employee.objects.select_related('user', 'department', 'designation')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "user__username", "user__first_name", "user__last_name"]
    ordering_fields = ["created_at", "first_name", "last_name"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeSerializer

    def get_queryset(self):
        return self.get_company_scoped_employee_queryset().select_related('user', 'department', 'designation')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Employees retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message="Employee details retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Employee created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Employee updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message="Employee deleted successfully.",
            status_code=status.HTTP_200_OK,
        )


class EmployeeLightweightViewSet(CompanyScopedEmployeeQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    """
    Lightweight employee API (id + full_name).
    Useful for dropdowns/autocomplete.
    """

    queryset = Employee.objects.select_related('user')
    serializer_class = EmployeeLightweightSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "user__first_name", "user__last_name", "email", "user__username"]
    ordering_fields = ["created_at", "first_name", "last_name"]
    ordering = ["first_name", "last_name", "-created_at"]

    def get_queryset(self):
        return self.get_company_scoped_employee_queryset().select_related('user')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return APIResponse.success(
                data={
                    "items": serializer.data,
                    "pagination": {
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                    },
                },
                message="Employees retrieved successfully.",
                status_code=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Employees retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message="Employee details retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
