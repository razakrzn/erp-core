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
from .shared import BaseProductionViewSet


class ProductionPlanningViewSet(BaseProductionViewSet):
    queryset = ProductionPlanning.objects.all()
    serializer_class = ProductionPlanningSerializer
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]
    permission_prefix = "production.production_planning"


class ProductionOrderViewSet(BaseProductionViewSet):
    queryset = ProductionOrder.objects.all()
    serializer_class = ProductionOrderSerializer
    search_fields = ["name", "slug", "order_no", "status"]
    ordering_fields = ["name", "created_at", "updated_at", "due_date"]
    permission_prefix = "production.production_orders"


class ShopFloorControlViewSet(BaseProductionViewSet):
    queryset = ShopFloorControl.objects.select_related("production_order")
    serializer_class = ShopFloorControlSerializer
    search_fields = ["name", "slug", "machine_code", "current_stage"]
    ordering_fields = ["name", "created_at", "updated_at", "progress_percent"]
    permission_prefix = "production.shop_floor_control"


class BOMExplosionViewSet(BaseProductionViewSet):
    queryset = BOMExplosion.objects.select_related("production_order")
    serializer_class = BOMExplosionSerializer
    search_fields = ["name", "slug", "component_code"]
    ordering_fields = ["name", "created_at", "updated_at", "level"]
    permission_prefix = "production.bom_explosion"


class MachineIntegrationViewSet(BaseProductionViewSet):
    queryset = MachineIntegration.objects.select_related("production_order")
    serializer_class = MachineIntegrationSerializer
    search_fields = ["name", "slug", "machine_type", "post_processor"]
    ordering_fields = ["name", "created_at", "updated_at"]
    permission_prefix = "production.machine_integration"


class LaborTrackingViewSet(BaseProductionViewSet):
    queryset = LaborTracking.objects.select_related("production_order")
    serializer_class = LaborTrackingSerializer
    search_fields = ["name", "slug", "worker_name"]
    ordering_fields = ["name", "created_at", "updated_at", "shift_hours", "productivity_score"]
    permission_prefix = "production.labor_tracking"


class WIPTrackingViewSet(BaseProductionViewSet):
    queryset = WIPTracking.objects.select_related("production_order")
    serializer_class = WIPTrackingSerializer
    search_fields = ["name", "slug", "stage_name"]
    ordering_fields = ["name", "created_at", "updated_at", "stage_quantity", "valuation"]
    permission_prefix = "production.wip_tracking"


class SubcontractingManagementViewSet(BaseProductionViewSet):
    queryset = SubcontractingManagement.objects.select_related("production_order")
    serializer_class = SubcontractingManagementSerializer
    search_fields = ["name", "slug", "vendor_name", "vendor_work_order"]
    ordering_fields = ["name", "created_at", "updated_at", "expected_return_date"]
    permission_prefix = "production.subcontracting_production"


class BatchTrackingViewSet(BaseProductionViewSet):
    queryset = BatchTracking.objects.select_related("production_order")
    serializer_class = BatchTrackingSerializer
    search_fields = ["name", "slug", "batch_no"]
    ordering_fields = ["name", "created_at", "updated_at", "expiry_date", "quantity"]
    permission_prefix = "production.batch_tracking_production"


class RejectionReworkManagementViewSet(BaseProductionViewSet):
    queryset = RejectionReworkManagement.objects.select_related("production_order")
    serializer_class = RejectionReworkManagementSerializer
    search_fields = ["name", "slug", "reason"]
    ordering_fields = ["name", "created_at", "updated_at", "rejected_quantity", "rework_quantity", "scrap_quantity"]
    permission_prefix = "production.rejection_rework"
