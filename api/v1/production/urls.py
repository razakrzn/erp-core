from rest_framework.routers import DefaultRouter

from .views import (
    BOMExplosionViewSet,
    BatchTrackingViewSet,
    CuttingOptimizationJobViewSet,
    LaborTrackingViewSet,
    MachineIntegrationViewSet,
    ProductionOrderViewSet,
    ProductionPlanningViewSet,
    RejectionReworkManagementViewSet,
    ShopFloorControlViewSet,
    SubcontractingManagementViewSet,
    WIPTrackingViewSet,
)

router = DefaultRouter()
router.register(r"production-planning", ProductionPlanningViewSet, basename="production-planning")
router.register(r"production-orders", ProductionOrderViewSet, basename="production-order")
router.register(r"shop-floor-control", ShopFloorControlViewSet, basename="shop-floor-control")
router.register(r"bom-explosion", BOMExplosionViewSet, basename="bom-explosion")
router.register(r"cutting-optimization", CuttingOptimizationJobViewSet, basename="cutting-optimization")
router.register(r"machine-integration", MachineIntegrationViewSet, basename="machine-integration")
router.register(r"labor-tracking", LaborTrackingViewSet, basename="labor-tracking")
router.register(r"wip-tracking", WIPTrackingViewSet, basename="wip-tracking")
router.register(r"subcontracting", SubcontractingManagementViewSet, basename="subcontracting")
router.register(r"batch-tracking", BatchTrackingViewSet, basename="batch-tracking")
router.register(r"rejection-rework", RejectionReworkManagementViewSet, basename="rejection-rework")

urlpatterns = router.urls
