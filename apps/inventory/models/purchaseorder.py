from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .PurchaseRequist import PurchaseRequisition
from .vendor import Vendor


class PurchaseOrder(models.Model):
    # Auto-generated PO number e.g. PO-000001
    po_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        editable=False,
        help_text="Auto-generated unique purchase order number.",
    )

    # Link to originating PR (nullable — PO can be raised without a PR)
    purchase_requisition = models.ForeignKey(
        PurchaseRequisition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_orders",
        help_text="The Purchase Requisition this PO was raised from.",
    )

    # Header fields
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="purchase_orders",
        help_text="Vendor / supplier.",
    )
    associated_job = models.CharField(
        max_length=200,
        blank=True,
        help_text="Associated job or project name e.g. Villa Renovation - Jumeirah.",
    )
    payment_terms = models.CharField(
        max_length=150,
        help_text="Payment terms e.g. Net 30, Cash on Delivery.",
    )
    shipping_delivery_terms = models.CharField(
        max_length=150,
        help_text="Shipping / delivery terms e.g. FOB, CIF, DDP.",
    )
    po_issued_date = models.DateField(
        help_text="Date the PO was issued.",
    )

    # Internal notes
    internal_remarks = models.TextField(
        blank=True,
        help_text="Internal remarks or additional info for this PO.",
    )

    # Status
    status = models.CharField(
        max_length=50,
        default="Draft",
        help_text="Current status e.g. Draft, Confirmed, Released, Closed.",
    )
    is_confirmed = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)

    # Computed totals (stored for performance)
    net_amount = models.DecimalField(
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
    grand_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
    )

    VAT_RATE = Decimal("0.05")

    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="purchase_orders",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_purchase_orders",
    )
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_purchase_orders",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.po_number:
            self.po_number = f"PO-{self.pk:06d}"
            super().save(update_fields=["po_number"])

    def __str__(self) -> str:
        po_number = self.po_number or f"PO-{self.pk or 'NEW'}"
        return f"{po_number} ({self.status})"


class PurchaseOrderLineItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="po_line_items",
    )
    product_code = models.CharField(max_length=100, null=True, blank=True, default="")
    purchase_requisition = models.ForeignKey(
        PurchaseRequisition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="po_line_items",
        help_text="The purchase requisition associated with this PO line.",
    )
    description = models.CharField(max_length=255, null=True, blank=True, default="")
    unit = models.CharField(max_length=50, null=True, blank=True, default="")
    requested_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Requested quantity.",
    )
    required_by_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date by which this item is required.",
    )
    delivery_location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        default="",
        help_text="Delivery location for this line item.",
    )
    last_purchase_rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Last purchase rate for this item.",
    )

    # Editable pricing
    negotiated_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Negotiated unit price agreed with the vendor.",
    )
    line_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        editable=False,
    )

    class Meta:
        verbose_name = "Purchase Order Line Item"
        verbose_name_plural = "Purchase Order Line Items"

    def save(self, *args, **kwargs):
        requested_qty = self.requested_qty or Decimal("0.00")
        negotiated_price = self.negotiated_price or Decimal("0.00")
        self.line_total = requested_qty * negotiated_price
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.purchase_order_id} - {self.product_code}"
