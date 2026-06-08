from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db import transaction
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
        default="Pending",
        help_text="Current status: Pending, Approved, Rejected.",
    )
    is_approved = models.BooleanField(default=False, null=True, blank=True)
    is_rejected = models.BooleanField(default=False, null=True, blank=True)
    reject_note = models.TextField(
        null=True,
        blank=True,
        default="",
        help_text="Reason for rejecting this purchase requisition.",
    )
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

    def _resolve_status_from_flags(self):
        if self.is_approved:
            return "Approved"
        if self.is_rejected:
            return "Rejected"
        return "Pending"

    def save(self, *args, **kwargs):
        self.status = self._resolve_status_from_flags()
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {"status"}
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.purchase_request_number:
            self.purchase_request_number = f"PR-{self.pk:06d}"
            super().save(update_fields=["purchase_request_number"])

    def __str__(self) -> str:
        pr_number = self.purchase_request_number or f"PR-{self.pk or 'NEW'}"
        return f"{pr_number} ({self.status})"

    def ensure_pending_purchase_order(self, actor=None):
        """
        Create one pending PO from this approved PR, with line items copied from PR line items.
        Returns (po, created_new).
        """
        existing_po = (
            PurchaseOrder.objects.filter(po_line_items__purchase_requisition=self).order_by("id").first()
        )
        if existing_po:
            return existing_po, False

        created_by = actor or self.approved_by or self.created_by
        if not created_by:
            raise ValueError("Cannot auto-create Purchase Order: no user available for created_by.")

        from .purchaseorder import PurchaseOrder, PurchaseOrderLineItem

        with transaction.atomic():
            po = PurchaseOrder.objects.create(
                vendor=None,
                associated_job=self.job_order_ref or "",
                payment_terms="Pending",
                shipping_delivery_terms="Pending",
                po_issued_date=self.requisition_date or timezone.localdate(),
                internal_remarks=f"Auto-created from approved PR {self.purchase_request_number or self.pk}.",
                status="Pending",
                is_approved=False,
                is_rejected=False,
                reject_note="",
                created_by=created_by,
                updated_by=created_by,
            )

            line_items = self.line_items.all()
            po_line_items = [
                PurchaseOrderLineItem(
                    purchase_order=po,
                    product_id=line_item.product_id,
                    product_code=(line_item.product_code or ""),
                    purchase_requisition=self,
                    description=(line_item.product_name or ""),
                    unit=(line_item.unit or ""),
                    requested_qty=line_item.requested_qty,
                    required_by_date=self.required_by_date,
                    delivery_location=(self.delivery_location or ""),
                    last_purchase_rate=Decimal("0.00"),
                    negotiated_price=Decimal("0.00"),
                )
                for line_item in line_items
            ]
            if po_line_items:
                PurchaseOrderLineItem.objects.bulk_create(po_line_items)

            po.net_amount = sum((item.line_total for item in po.po_line_items.all()), Decimal("0.00"))
            po.vat_amount = po.net_amount * PurchaseOrder.VAT_RATE
            po.grand_total = po.net_amount + po.vat_amount
            po.save(update_fields=["net_amount", "vat_amount", "grand_total", "updated_at"])

        return po, True

    def ensure_production_order(self):
        """
        Create one production order for this PR if it does not exist.
        Returns (production_order, created_new).
        """
        from apps.production.models import ProductionOrder

        order_no = f"PROD-PR-{self.pk:06d}"
        existing = ProductionOrder.objects.filter(order_no=order_no).first()
        if existing:
            return existing, False

        planned_qty = sum((item.requested_qty or Decimal("0.00") for item in self.line_items.all()), Decimal("0.00"))
        production_order = ProductionOrder.objects.create(
            name=f"Production for {self.purchase_request_number or f'PR-{self.pk:06d}'}",
            order_no=order_no,
            status="draft",
            due_date=self.required_by_date,
            planned_quantity=max(int(planned_qty), 0),
            produced_quantity=0,
            description=f"Auto-created from approved Purchase Requisition {self.purchase_request_number or self.pk}.",
            is_active=True,
        )
        return production_order, True


class PurchaseRequisitionLineItem(models.Model):
    purchase_requisition = models.ForeignKey(
        PurchaseRequisition,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="line_items",
    )
    product_id = models.PositiveBigIntegerField(null=True, blank=True)
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
