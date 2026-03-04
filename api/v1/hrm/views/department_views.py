from django_filters import rest_framework as django_filters
from rest_framework import filters, status, viewsets
from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.hrm.models.department import Department
from apps.hrm.models.designation import Designation
from core.utils.responses import APIResponse

from ..serializers.department_serializers import DepartmentDetailsSerializer, DepartmentSerializer
from ..serializers.designation_serializers import DesignationSerializer


@extend_schema_view(
    list=extend_schema(tags=["HRM"], summary="List departments", description="Paginated list of departments with search and ordering."),
    retrieve=extend_schema(tags=["HRM"], summary="Get department", description="Retrieve a department by ID with head and designations."),
    create=extend_schema(tags=["HRM"], summary="Create department", description="Create a new department."),
    update=extend_schema(tags=["HRM"], summary="Update department", description="Full update of a department."),
    partial_update=extend_schema(tags=["HRM"], summary="Partial update department", description="Partial update of a department."),
    destroy=extend_schema(tags=["HRM"], summary="Delete department", description="Delete a department."),
)
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
