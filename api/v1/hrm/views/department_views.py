from django_filters import rest_framework as django_filters
from rest_framework import filters, status

from apps.hrm.models.department import Department
from apps.hrm.models.designation import Designation
from core.utils.responses import APIResponse

from ..serializers.department_serializers import DepartmentDetailsSerializer, DepartmentSerializer
from ..serializers.designation_serializers import DesignationSerializer
from .shared import BaseHRMViewSet


class DepartmentViewSet(BaseHRMViewSet):
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
    permission_prefix = "hr.department"

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DepartmentDetailsSerializer
        return DepartmentSerializer

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        if Department.objects.filter(name__iexact=name).exists():
            return APIResponse.error(
                message="Department with this name already exists.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


class DesignationFilter(django_filters.FilterSet):
    department_id = django_filters.NumberFilter(field_name="department_id")

    class Meta:
        model = Designation
        fields = ["department_id"]


class DesignationViewSet(BaseHRMViewSet):
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
    permission_prefix = "hr.designation"

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        if Designation.objects.filter(name__iexact=name).exists():
            return APIResponse.error(
                message="Designation with this name already exists.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)
