from django.contrib import admin

from .models import (
    BOMExplosion,
    BatchTracking,
    CuttingOptimizationJob,
    LaborTracking,
    MachineIntegration,
    ProductionOrder,
    ProductionPlanning,
    RejectionReworkManagement,
    ShopFloorControl,
    SubcontractingManagement,
    WIPTracking,
)


@admin.register(ProductionPlanning)
class ProductionPlanningAdmin(admin.ModelAdmin):
    list_display = ("name", "machine_loading_percent", "is_active", "updated_at")
    search_fields = ("name", "slug")


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ("name", "order_no", "status", "planned_quantity", "produced_quantity", "updated_at")
    search_fields = ("name", "order_no", "slug")
    list_filter = ("status", "is_active")


@admin.register(ShopFloorControl)
class ShopFloorControlAdmin(admin.ModelAdmin):
    list_display = ("name", "production_order", "machine_code", "progress_percent", "bottleneck_flag")
    search_fields = ("name", "machine_code", "slug")
    list_filter = ("bottleneck_flag", "is_active")


@admin.register(BOMExplosion)
class BOMExplosionAdmin(admin.ModelAdmin):
    list_display = ("name", "production_order", "component_code", "level", "required_quantity")
    search_fields = ("name", "component_code", "slug")


@admin.register(CuttingOptimizationJob)
class CuttingOptimizationJobAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "cad_file", "updated_at")
    search_fields = ("name", "slug")
    list_filter = ("status", "is_active")


@admin.register(MachineIntegration)
class MachineIntegrationAdmin(admin.ModelAdmin):
    list_display = ("name", "machine_type", "post_processor", "updated_at")
    search_fields = ("name", "machine_type", "slug")


@admin.register(LaborTracking)
class LaborTrackingAdmin(admin.ModelAdmin):
    list_display = ("name", "worker_name", "shift_hours", "productivity_score")
    search_fields = ("name", "worker_name", "slug")


@admin.register(WIPTracking)
class WIPTrackingAdmin(admin.ModelAdmin):
    list_display = ("name", "stage_name", "stage_quantity", "valuation")
    search_fields = ("name", "stage_name", "slug")


@admin.register(SubcontractingManagement)
class SubcontractingManagementAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor_name", "vendor_work_order", "expected_return_date")
    search_fields = ("name", "vendor_name", "vendor_work_order", "slug")


@admin.register(BatchTracking)
class BatchTrackingAdmin(admin.ModelAdmin):
    list_display = ("name", "batch_no", "quantity", "expiry_date")
    search_fields = ("name", "batch_no", "slug")


@admin.register(RejectionReworkManagement)
class RejectionReworkManagementAdmin(admin.ModelAdmin):
    list_display = ("name", "rejected_quantity", "rework_quantity", "scrap_quantity")
    search_fields = ("name", "slug")
