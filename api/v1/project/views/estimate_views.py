from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.Projects.models import Labour, Material, Other

from ..serializers import (
    EstimateLabourDetailSerializer,
    EstimateLabourListSerializer,
    EstimateLabourWriteSerializer,
    EstimateMaterialDetailSerializer,
    EstimateMaterialListSerializer,
    EstimateMaterialWriteSerializer,
    EstimateOtherDetailSerializer,
    EstimateOtherListSerializer,
    EstimateOtherWriteSerializer,
)
from .shared import BaseProjectViewSet


class EstimateMaterialViewSet(BaseProjectViewSet):
    queryset = Material.objects.select_related("project", "item", "material", "material__unit")
    # permission_prefix = "projects.estimate_materials"
    permission_prefix = "project.all_projects"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["project", "item", "material"]
    search_fields = [
        "project__job_number",
        "project__project_name",
        "item__name",
        "material__name",
        "material__sku",
        "material__product_code",
    ]
    ordering_fields = ["id", "project__job_number", "item__name", "material__name", "req_qty"]
    ordering = ["project__job_number", "id"]
    serializer_action_classes = {
        "list": EstimateMaterialListSerializer,
        "retrieve": EstimateMaterialDetailSerializer,
        "create": EstimateMaterialWriteSerializer,
        "update": EstimateMaterialWriteSerializer,
        "partial_update": EstimateMaterialWriteSerializer,
    }
    response_serializer_class = EstimateMaterialDetailSerializer

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, EstimateMaterialDetailSerializer)


class EstimateLabourViewSet(BaseProjectViewSet):
    queryset = Labour.objects.select_related("project", "designation", "designation__department")
    # permission_prefix = "projects.estimate_labours"
    permission_prefix = "project.all_projects"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["project", "designation"]
    search_fields = [
        "project__job_number",
        "project__project_name",
        "designation__name",
        "designation__department__name",
    ]
    ordering_fields = ["id", "project__job_number", "designation__name", "hrs", "rate", "amount"]
    ordering = ["project__job_number", "designation__name", "id"]
    serializer_action_classes = {
        "list": EstimateLabourListSerializer,
        "retrieve": EstimateLabourDetailSerializer,
        "create": EstimateLabourWriteSerializer,
        "update": EstimateLabourWriteSerializer,
        "partial_update": EstimateLabourWriteSerializer,
    }
    response_serializer_class = EstimateLabourDetailSerializer

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, EstimateLabourDetailSerializer)


class EstimateOtherViewSet(BaseProjectViewSet):
    queryset = Other.objects.select_related("project")
    #  permission_prefix = "projects.estimate_others"
    permission_prefix = "project.all_projects"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["project"]
    search_fields = ["project__job_number", "project__project_name", "item_description"]
    ordering_fields = ["id", "project__job_number", "item_description", "amount"]
    ordering = ["project__job_number", "item_description", "id"]
    serializer_action_classes = {
        "list": EstimateOtherListSerializer,
        "retrieve": EstimateOtherDetailSerializer,
        "create": EstimateOtherWriteSerializer,
        "update": EstimateOtherWriteSerializer,
        "partial_update": EstimateOtherWriteSerializer,
    }
    response_serializer_class = EstimateOtherDetailSerializer

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, EstimateOtherDetailSerializer)
