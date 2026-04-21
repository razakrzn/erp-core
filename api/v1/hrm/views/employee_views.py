from rest_framework import filters, status
from apps.hrm.models.employee import Employee
from core.utils.responses import APIResponse

from ..serializers.employee_serializers import (
    EmployeeLightweightSerializer,
    EmployeeListSerializer,
    EmployeeSerializer,
)
from .shared import BaseHRMViewSet


class CompanyScopedEmployeeQuerysetMixin:
    """Shared company-aware employee queryset logic for employee endpoints."""

    def get_company_scoped_employee_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Employee.objects.all()
        if hasattr(user, "company") and user.company:
            return Employee.objects.filter(company=user.company)
        return Employee.objects.none()

    def apply_user_link_filter(self, queryset):
        """
        Filter employees by whether they are linked to an auth user.

        Supported query params:
        - `has_user=true`
        - `has_user=false`
        """
        has_user = self.request.query_params.get("has_user")
        if has_user is None:
            return queryset

        normalized_value = has_user.strip().lower()
        if normalized_value in {"true", "1", "yes"}:
            return queryset.filter(user__isnull=False)
        if normalized_value in {"false", "0", "no"}:
            return queryset.filter(user__isnull=True)
        return queryset


class EmployeeViewSet(CompanyScopedEmployeeQuerysetMixin, BaseHRMViewSet):
    """
    API v1 CRUD viewset for Employee.

    Features:
    - List / retrieve / create / update / delete employees
    - Authenticated access by default
    - Filtered by company
    """

    queryset = Employee.objects.select_related("user", "department", "designation")
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "user__username", "user__first_name", "user__last_name"]
    ordering_fields = ["created_at", "first_name", "last_name"]
    ordering = ["-created_at"]
    permission_prefix = "hr.employees"

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeListSerializer
        return EmployeeSerializer

    def get_queryset(self):
        queryset = self.get_company_scoped_employee_queryset().select_related("user", "department", "designation")
        return self.apply_user_link_filter(queryset)


class EmployeeLightweightViewSet(CompanyScopedEmployeeQuerysetMixin, BaseHRMViewSet):
    """
    Lightweight employee API (id + full_name).
    Useful for dropdowns/autocomplete.
    """

    queryset = Employee.objects.select_related("user")
    serializer_class = EmployeeLightweightSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "user__first_name", "user__last_name", "email", "user__username"]
    ordering_fields = ["created_at", "first_name", "last_name"]
    ordering = ["first_name", "last_name", "-created_at"]
    permission_prefix = "hr.employees"

    def get_queryset(self):
        queryset = self.get_company_scoped_employee_queryset().select_related("user")
        return self.apply_user_link_filter(queryset)

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
