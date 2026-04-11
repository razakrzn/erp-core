from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone




class PurchaseRequisition(models.Model):
    # Header fields
    purchase_request_number = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        editable=False,
        help_text="Auto-generated unique purchase requisition number (MRF Number).",
    )
    requisition_date = models.DateField(
        null=True,
        blank=True,
        default=timezone.localdate,
        help_text="The creation date of the requisition.",
    )
    requisition_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        default="Normal Stock",
        help_text="Requisition mode: Job (Project), Rework, or Normal Stock.",
    )
    stock_reason_category = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        default="",
        help_text="Reason category for normal stock requisitions (e.g., Low Stock, Routine Replenishment).",
    )
    job_order_ref = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Job order reference used for Rework requisitions.",
    )
    rework_notes = models.TextField(
        null=True,
        blank=True,
        help_text="Justification and notes for rework requisitions.",
    )
    required_by_date = models.DateField(null=True, blank=True)
    priority = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        default="Medium",
        help_text="Priority level: High, Medium, or Low.",
    )
    delivery_location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        default="",
        help_text="Destination delivery location.",
    )
    reason_description = models.TextField(
        null=True,
        blank=True,
        help_text="Provide justification for this purchase requisition.",
    )

    # Notes & meta
    notes_to_purchase_team = models.TextField(
        null=True,
        blank=True,
        help_text="Specific instructions for the procurement department.",
    )
    status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        default="Draft",
        help_text="Current status: Draft, Submitted for Approval, Approved, Rejected.",
    )
    is_approved = models.BooleanField(default=False, null=True, blank=True)
    is_rejected = models.BooleanField(default=False, null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="purchase_requisitions",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_purchase_requisitions",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_purchase_requisitions",
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_purchase_requisitions",
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    VAT_RATE = Decimal("0.05")

    class Meta:
        verbose_name = "Purchase Requisition"
        verbose_name_plural = "Purchase Requisitions"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.purchase_request_number:
            self.purchase_request_number = f"PR-{self.pk:06d}"
            super().save(update_fields=["purchase_request_number"])

    def __str__(self) -> str:
        pr_number = self.purchase_request_number or f"PR-{self.pk or 'NEW'}"
        return f"{pr_number} ({self.status})"


class PurchaseRequisitionLineItem(models.Model):
    purchase_requisition = models.ForeignKey(
        PurchaseRequisition,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="line_items",
    )
    product_code = models.CharField(max_length=100, null=True, blank=True, default="")
    product_name = models.CharField(max_length=255, null=True, blank=True, default="")
    product_category = models.CharField(max_length=100, null=True, blank=True, default="")
    unit = models.CharField(max_length=50, null=True, blank=True, default="")

    # Stock snapshot at time of requisition
    stock_on_hand = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0.00"),
        help_text="Current stock level at time of PR creation.",
    )
    pending_pr_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0.00"),
        help_text="Quantity in other pending purchase requisitions.",
    )
    pending_po_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0.00"),
        help_text="Quantity in pending purchase orders.",
    )

    # Quantities
    requested_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Quantity requested by the requester.",
    )
    net_required_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0.00"),
        editable=False,
        help_text="Net quantity needed after accounting for stock and pending orders.",
    )


    class Meta:
        verbose_name = "Purchase Requisition Line Item"
        verbose_name_plural = "Purchase Requisition Line Items"

    def save(self, *args, **kwargs):
        requested_qty = self.requested_qty or Decimal("0.00")
        stock_on_hand = self.stock_on_hand or Decimal("0.00")
        pending_po_qty = self.pending_po_qty or Decimal("0.00")
        calculated_net = requested_qty - (stock_on_hand + pending_po_qty)
        self.net_required_qty = max(Decimal("0.00"), calculated_net)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.purchase_requisition_id} - {self.product_name}"
