from django.db import models

from .base import ProductionBaseModel


class CuttingOptimizationJob(ProductionBaseModel):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    cad_file = models.FileField(upload_to="production/cad/", blank=True, null=True)
    cutlist_pdf_file = models.FileField(upload_to="production/cutlists/", blank=True, null=True)
    cutlist_xlsx_file = models.FileField(upload_to="production/cutlists/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    stock_sheets = models.JSONField(default=list, blank=True)
    extracted_parts = models.JSONField(default=list, blank=True)
    optimization_result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default="")

    class Meta:
        db_table = "prd_cutting_optimization"
        verbose_name = "Cutting Optimization"
        verbose_name_plural = "Cutting Optimization"
