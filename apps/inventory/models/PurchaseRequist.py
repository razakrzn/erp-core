from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .products import Product


class PurchaseRequisition(models.Model):
    # Header fields
    purchase_request_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        editable=False,
        help_text="Auto-generated unique purchase requisition number.",
    )
    stock_reason_category = models.CharField(
        max_length=150,
        help_text="Category describing the reason for this stock requisition.",
    )
    required_by_date = models.DateField()
    priority = models.CharField(
        max_length=50,
        default="Medium",
        help_text="Priority level e.g. Low, Medium, High, Urgent.",
    )
    delivery_location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Destination delivery location.",
    )
    reason_description = models.TextField(
        blank=True,
        help_text="Provide justification for this purchase requisition.",
    )

    # Notes & meta
    notes_to_purchase_team = models.TextField(
        blank=True,
        help_text="Specific instructions for the procurement department.",
    )
    status = models.CharField(
        max_length=50,
        default="Draft",
        help_text="Current status e.g. Draft, Submitted for Approval, Approved, Rejected.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="purchase_requisitions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Computed totals (stored for performance)
    estimated_subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
    )
    vat_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
    )
    total_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
    )

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
        related_name="line_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="requisition_line_items",
    )

    # Stock snapshot at time of requisition
    stock_on_hand = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Current stock level at time of PR creation.",
    )
    pending_pr_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Quantity in other pending purchase requisitions.",
    )
    pending_po_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Quantity in pending purchase orders.",
    )

    # Quantities
    requested_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Quantity requested by the requester.",
    )
    net_required_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
        help_text="Net quantity needed after accounting for stock and pending orders.",
    )

    line_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
    )

    class Meta:
        verbose_name = "Purchase Requisition Line Item"
        verbose_name_plural = "Purchase Requisition Line Items"

    def __str__(self) -> str:
        return f"{self.purchase_requisition_id} - {self.product_id}"
