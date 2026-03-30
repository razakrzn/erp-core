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
        return self.get_company_scoped_employee_queryset().select_related("user", "department", "designation")


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
        return self.get_company_scoped_employee_queryset().select_related("user")

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
