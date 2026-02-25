from rest_framework import filters, status, viewsets

from apps.production.models import (
    BOMExplosion,
    BatchTracking,
    LaborTracking,
    MachineIntegration,
    ProductionOrder,
    ProductionPlanning,
    RejectionReworkManagement,
    ShopFloorControl,
    SubcontractingManagement,
    WIPTracking,
)
from core.utils.responses import APIResponse

from ..serializers import (
    BOMExplosionSerializer,
    BatchTrackingSerializer,
    LaborTrackingSerializer,
    MachineIntegrationSerializer,
    ProductionOrderSerializer,
    ProductionPlanningSerializer,
    RejectionReworkManagementSerializer,
    ShopFloorControlSerializer,
    SubcontractingManagementSerializer,
    WIPTrackingSerializer,
)


class BaseProductionViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
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
            message=f"{self.queryset.model._meta.verbose_name_plural.title()} retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.queryset.model._meta.verbose_name.title()} retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.queryset.model._meta.verbose_name.title()} created successfully.",
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
            message=f"{self.queryset.model._meta.verbose_name.title()} updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(self.get_object())
        return APIResponse.success(
            data=None,
            message=f"{self.queryset.model._meta.verbose_name.title()} deleted successfully.",
            status_code=status.HTTP_200_OK,
        )


class ProductionPlanningViewSet(BaseProductionViewSet):
    queryset = ProductionPlanning.objects.all()
    serializer_class = ProductionPlanningSerializer
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]


class ProductionOrderViewSet(BaseProductionViewSet):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    search_fields = ["name", "slug", "order_no", "status"]
    ordering_fields = ["name", "created_at", "updated_at", "due_date"]


class ShopFloorControlViewSet(BaseProductionViewSet):
    queryset = ShopFloorControl.objects.select_related("production_order")
    serializer_class = ShopFloorControlSerializer
    search_fields = ["name", "slug", "machine_code", "current_stage"]
    ordering_fields = ["name", "created_at", "updated_at", "progress_percent"]


class BOMExplosionViewSet(BaseProductionViewSet):
    queryset = BOMExplosion.objects.select_related("production_order")
    serializer_class = BOMExplosionSerializer
    search_fields = ["name", "slug", "component_code"]
    ordering_fields = ["name", "created_at", "updated_at", "level"]


class MachineIntegrationViewSet(BaseProductionViewSet):
    queryset = MachineIntegration.objects.select_related("production_order")
    serializer_class = MachineIntegrationSerializer
    search_fields = ["name", "slug", "machine_type", "post_processor"]
    ordering_fields = ["name", "created_at", "updated_at"]


class LaborTrackingViewSet(BaseProductionViewSet):
    queryset = LaborTracking.objects.select_related("production_order")
    serializer_class = LaborTrackingSerializer
    search_fields = ["name", "slug", "worker_name"]
    ordering_fields = ["name", "created_at", "updated_at", "shift_hours", "productivity_score"]


class WIPTrackingViewSet(BaseProductionViewSet):
    queryset = WIPTracking.objects.select_related("production_order")
    serializer_class = WIPTrackingSerializer
    search_fields = ["name", "slug", "stage_name"]
    ordering_fields = ["name", "created_at", "updated_at", "stage_quantity", "valuation"]


class SubcontractingManagementViewSet(BaseProductionViewSet):
    queryset = SubcontractingManagement.objects.select_related("production_order")
    serializer_class = SubcontractingManagementSerializer
    search_fields = ["name", "slug", "vendor_name", "vendor_work_order"]
    ordering_fields = ["name", "created_at", "updated_at", "expected_return_date"]


class BatchTrackingViewSet(BaseProductionViewSet):
    queryset = BatchTracking.objects.select_related("production_order")
    serializer_class = BatchTrackingSerializer
    search_fields = ["name", "slug", "batch_no"]
    ordering_fields = ["name", "created_at", "updated_at", "expiry_date", "quantity"]


class RejectionReworkManagementViewSet(BaseProductionViewSet):
    queryset = RejectionReworkManagement.objects.select_related("production_order")
    serializer_class = RejectionReworkManagementSerializer
    search_fields = ["name", "slug", "reason"]
    ordering_fields = ["name", "created_at", "updated_at", "rejected_quantity", "rework_quantity", "scrap_quantity"]
