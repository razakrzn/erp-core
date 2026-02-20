from django.utils import timezone
from django_filters import rest_framework as django_filters
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from apps.hrm.models.attendance import Attendance
from apps.hrm.models.department import Department
from apps.hrm.models.designation import Designation
from apps.hrm.models.employee import Employee
from core.utils.responses import APIResponse

from .serializers.attendance_serializers import AttendanceSerializer
from .serializers.department_serializers import DepartmentDetailsSerializer, DepartmentSerializer
from .serializers.designation_serializers import DesignationSerializer
from .serializers.employee_serializers import (
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


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API v1 CRUD viewset for Department.

    Features:
    - List / retrieve / create / update / delete departments
    - Authenticated access by default
    - Basic search on name and slug
    """

    queryset = Department.objects.select_related('head').prefetch_related('designations')
    serializer_class = DepartmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DepartmentDetailsSerializer
        return DepartmentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Departments retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message="Department retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        if Department.objects.filter(name__iexact=name).exists():
            return APIResponse.error(
                message="Department with this name already exists.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Department created successfully.",
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
            message="Department updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message="Department deleted successfully.",
            status_code=status.HTTP_200_OK,
        )


class DesignationFilter(django_filters.FilterSet):
    department_id = django_filters.NumberFilter(field_name="department_id")

    class Meta:
        model = Designation
        fields = ["department_id"]


class DesignationViewSet(viewsets.ModelViewSet):
    """
    API v1 CRUD viewset for Designation.

    Features:
    - List / retrieve / create / update / delete designations
    - Authenticated access by default
    - Basic search on name and slug
    - Filter by department_id
    """

    queryset = Designation.objects.select_related('department')
    serializer_class = DesignationSerializer
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DesignationFilter
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]
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
            message="Designations retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message="Designation retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        if Designation.objects.filter(name__iexact=name).exists():
            return APIResponse.error(
                message="Designation with this name already exists.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Designation created successfully.",
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
            message="Designation updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message="Designation deleted successfully.",
            status_code=status.HTTP_200_OK,
        )


class AttendanceViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing Attendance.
    Supports check-in, check-out, listing history, and report.
    """

    serializer_class = AttendanceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Attendance.objects.select_related('employee', 'employee__user')

        employee = getattr(user, 'employee_profile', None)
        if employee:
            return Attendance.objects.select_related('employee', 'employee__user').filter(employee=employee)

        return Attendance.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Attendance history retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['post'], url_path='check-in')
    def check_in(self, request):
        employee = getattr(request.user, 'employee_profile', None)
        if not employee:
            return APIResponse.error(
                message="Employee profile not found for this user.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        today = timezone.now().date()
        if Attendance.objects.filter(employee=employee, date=today).exists():
            return APIResponse.error(
                message="Already checked in today.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        attendance = Attendance.objects.create(
            employee=employee,
            date=today,
            check_in=timezone.now().time(),
            status='Present',
        )

        serializer = self.get_serializer(attendance)
        return APIResponse.success(
            data=serializer.data,
            message="Checked in successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['post'], url_path='check-out')
    def check_out(self, request):
        employee = getattr(request.user, 'employee_profile', None)
        if not employee:
            return APIResponse.error(
                message="Employee profile not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        today = timezone.now().date()
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return APIResponse.error(
                message="No check-in record found for today.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if attendance.check_out:
            return APIResponse.error(
                message="Already checked out today.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        attendance.check_out = timezone.now().time()
        attendance.save(update_fields=['check_out'])

        serializer = self.get_serializer(attendance)
        return APIResponse.success(
            data=serializer.data,
            message="Checked out successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='report')
    def report(self, request):
        queryset = self.get_queryset()
        total_days = queryset.count()
        present_days = queryset.filter(status='Present').count()

        return APIResponse.success(
            data={
                "total_days": total_days,
                "present_days": present_days,
            },
            message="Attendance report retrieved successfully.",
            status_code=status.HTTP_200_OK,
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
