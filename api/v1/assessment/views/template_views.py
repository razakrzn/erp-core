from rest_framework import filters, status
from rest_framework.decorators import action

from apps.assessment.models import Template, TemplateFinish

from ..serializers.template_serializers import (
    TemplateCategoryListSerializer,
    TemplateDetailSerializer,
    TemplateDropdownSerializer,
    TemplateFinishDropdownSerializer,
    TemplateFinishSerializer,
    TemplateListSerializer,
)
from core.utils.responses import APIResponse
from .shared import BaseAssessmentViewSet


class TemplateViewSet(BaseAssessmentViewSet):
    queryset = Template.objects.prefetch_related("finishes").all().order_by("-created_at")
    serializer_class = TemplateDetailSerializer
    search_fields = ["name", "category"]
    ordering_fields = ["name", "category", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "estimation.quatation_template"

    def get_serializer_class(self):
        if self.action == "list":
            return TemplateListSerializer
        if self.action == "dropdown":
            return TemplateDropdownSerializer
        if self.action == "categories":
            return TemplateCategoryListSerializer
        return TemplateDetailSerializer

    @action(detail=False, methods=["get"], url_path="dropdown")
    def dropdown(self, request):
        queryset = self.get_queryset().only("id", "name").order_by("name")
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Template dropdown retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="categories")
    def categories(self, request):
        queryset = self.get_queryset().values("category").distinct().order_by("category")
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Template categories retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class TemplateFinishViewSet(BaseAssessmentViewSet):
    queryset = TemplateFinish.objects.select_related("template").all()
    serializer_class = TemplateFinishSerializer
    search_fields = ["finish_name", "finish_type", "material", "design"]
    ordering_fields = ["finish_name", "finish_type", "material", "design"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "estimation.quatation_template"

    def get_serializer_class(self):
        if self.action == "dropdown":
            return TemplateFinishDropdownSerializer
        return TemplateFinishSerializer

    @action(detail=False, methods=["get"], url_path="dropdown")
    def dropdown(self, request):
        queryset = self.get_queryset().select_related(None).only("id", "finish_name")
        template_id = request.query_params.get("template_id")
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        queryset = queryset.order_by("finish_name")
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Template finish dropdown retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
