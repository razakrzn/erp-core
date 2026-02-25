from django.db import models

from .base import ProductionBaseModel


class ProductionPlanning(ProductionBaseModel):
    machine_loading_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    shift_schedule = models.JSONField(default=list, blank=True)
    capacity_notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "prd_planning"
        verbose_name = "Production Planning"
        verbose_name_plural = "Production Planning"


class ProductionOrder(ProductionBaseModel):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("planned", "Planned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    order_no = models.CharField(max_length=50, unique=True)
    planned_quantity = models.PositiveIntegerField(default=0)
    produced_quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "prd_orders"
        verbose_name = "Production Order"
        verbose_name_plural = "Production Orders"


class ShopFloorControl(ProductionBaseModel):
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name="shop_floor_updates",
    )
    machine_code = models.CharField(max_length=60, blank=True, default="")
    bottleneck_flag = models.BooleanField(default=False)
    current_stage = models.CharField(max_length=120, blank=True, default="")
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        db_table = "prd_shop_floor"
        verbose_name = "Shop Floor Control"
        verbose_name_plural = "Shop Floor Control"


class BOMExplosion(ProductionBaseModel):
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name="bom_explosions",
    )
    level = models.PositiveIntegerField(default=1)
    component_code = models.CharField(max_length=100)
    required_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    issued_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)

    class Meta:
        db_table = "prd_bom_explosion"
        verbose_name = "BOM Explosion"
        verbose_name_plural = "BOM Explosion"


class MachineIntegration(ProductionBaseModel):
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="machine_jobs",
    )
    machine_type = models.CharField(max_length=60, blank=True, default="CNC")
    machine_program = models.TextField(blank=True, default="")
    post_processor = models.CharField(max_length=120, blank=True, default="")

    class Meta:
        db_table = "prd_machine_integration"
        verbose_name = "Machine Integration"
        verbose_name_plural = "Machine Integration"


class LaborTracking(ProductionBaseModel):
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="labor_logs",
    )
    worker_name = models.CharField(max_length=120)
    shift_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    productivity_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        db_table = "prd_labor_tracking"
        verbose_name = "Labor Tracking"
        verbose_name_plural = "Labor Tracking"


class WIPTracking(ProductionBaseModel):
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        related_name="wip_logs",
    )
    stage_name = models.CharField(max_length=120)
    stage_quantity = models.PositiveIntegerField(default=0)
    valuation = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "prd_wip_tracking"
        verbose_name = "WIP Tracking"
        verbose_name_plural = "WIP Tracking"


class SubcontractingManagement(ProductionBaseModel):
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcontracting_jobs",
    )
    vendor_name = models.CharField(max_length=200)
    vendor_work_order = models.CharField(max_length=80)
    expected_return_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "prd_subcontracting"
        verbose_name = "Subcontracting Management"
        verbose_name_plural = "Subcontracting Management"


class BatchTracking(ProductionBaseModel):
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="batches",
    )
    batch_no = models.CharField(max_length=80, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "prd_batch_tracking"
        verbose_name = "Batch Tracking"
        verbose_name_plural = "Batch Tracking"


class RejectionReworkManagement(ProductionBaseModel):
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejections",
    )
    rejected_quantity = models.PositiveIntegerField(default=0)
    rework_quantity = models.PositiveIntegerField(default=0)
    scrap_quantity = models.PositiveIntegerField(default=0)
    reason = models.TextField(blank=True, default="")

    class Meta:
        db_table = "prd_rejection_rework"
        verbose_name = "Rejection & Rework Management"
        verbose_name_plural = "Rejection & Rework Management"
