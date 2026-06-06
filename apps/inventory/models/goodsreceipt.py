from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from .products import Product
from .purchaseorder import PurchaseOrder, PurchaseOrderLineItem


class GoodsReceipt(models.Model):
    grn_number = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        editable=False,
        help_text="Auto-generated unique goods receipt number.",
    )
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="goods_receipts",
    )
    purchase_order_no = models.CharField(max_length=30, blank=True, default="")
    po_date = models.DateField(null=True, blank=True)
    grn_recording_date = models.DateField(default=timezone.localdate)

    vendor_name = models.CharField(max_length=255, blank=True, default="")
    vendor_trn = models.CharField(max_length=15, blank=True, default="")
    vendor_address = models.TextField(blank=True, default="")

    vendor_invoice_no = models.CharField(max_length=100, blank=True, default="")
    vendor_invoice_date = models.DateField(null=True, blank=True)
    delivery_challan_no = models.CharField(max_length=100, blank=True, default="")
    delivery_challan_date = models.DateField(null=True, blank=True)
    vendor_delivery_challan = models.FileField(
        upload_to="inventory/grn/vendor_delivery_challan/",
        null=True,
        blank=True,
    )
    vendor_invoice = models.FileField(
        upload_to="inventory/grn/vendor_invoice/",
        null=True,
        blank=True,
    )

    overall_quality_status = models.CharField(
        max_length=30,
        default="accepted",
    )
    quality_notes = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=50,
        default="Pending",
        help_text="Current status e.g. Pending, Approved, Rejected.",
    )
    is_approved = models.BooleanField(default=False, null=True, blank=True)
    is_rejected = models.BooleanField(default=False, null=True, blank=True)
    reject_note = models.TextField(
        null=True,
        blank=True,
        default="",
        help_text="Reason for rejecting this goods receipt.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Goods Receipt"
        verbose_name_plural = "Goods Receipts"

    def __str__(self) -> str:
        return f"GRN {self.pk or 'NEW'} - {self.purchase_order_no or self.purchase_order_id}"

    def _resolve_status_from_flags(self):
        if self.is_approved:
            return "Approved"
        if self.is_rejected:
            return "Rejected"
        return "Pending"

    @staticmethod
    def _compose_vendor_address(vendor) -> str:
        parts = [
            vendor.store_office_no or "",
            vendor.building_name or "",
            vendor.street_area or "",
            vendor.city_emirate or "",
        ]
        return ", ".join([part.strip() for part in parts if part and part.strip()])

    def populate_from_purchase_order(self):
        if not self.purchase_order_id:
            return

        po = self.purchase_order
        vendor = po.vendor
        self.purchase_order_no = po.po_number or ""
        self.po_date = po.po_issued_date

        if vendor:
            self.vendor_name = vendor.trade_name or ""
            self.vendor_trn = vendor.trn_number or ""
            self.vendor_address = self._compose_vendor_address(vendor)
        else:
            self.vendor_name = ""
            self.vendor_trn = ""
            self.vendor_address = ""

    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        self.populate_from_purchase_order()
        self.status = self._resolve_status_from_flags()
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {"status"}
        super().save(*args, **kwargs)
        if is_new and not self.grn_number:
            self.grn_number = f"GRN-{self.pk:06d}"
            super().save(update_fields=["grn_number"])


class GoodsReceiptItem(models.Model):
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        related_name="material_intakes",
    )
    purchase_order_line_item = models.ForeignKey(
        PurchaseOrderLineItem,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="goods_receipt_items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="goods_receipt_items",
    )

    product_code = models.CharField(max_length=100, blank=True, default="")
    product_name = models.CharField(max_length=255, blank=True, default="")
    unit = models.CharField(max_length=50, blank=True, default="")
    po_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        default=Decimal("0.00"),
    )
    already_received = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        default=Decimal("0.00"),
        editable=False,
    )
    qty_good = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        default=Decimal("0.00"),
    )
    qty_rejected = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        default=Decimal("0.00"),
    )
    rejection_reason = models.TextField(blank=True, default="")
    defect_photo = models.FileField(
        upload_to="inventory/grn/defects/",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Goods Receipt Item"
        verbose_name_plural = "Goods Receipt Items"

    def __str__(self) -> str:
        return f"GRN Item {self.pk or 'NEW'} - {self.product_code or self.product_name}"

    def _calculate_previously_received(self) -> Decimal:
        if not self.purchase_order_line_item_id:
            return Decimal("0.00")

        queryset = GoodsReceiptItem.objects.filter(
            purchase_order_line_item_id=self.purchase_order_line_item_id
        )
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        received_total = queryset.aggregate(
            total=Coalesce(
                Sum(
                    F("qty_good"),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                ),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        )["total"]
        return received_total or Decimal("0.00")

    def populate_from_po_line(self):
        if not self.purchase_order_line_item_id:
            return
        line = self.purchase_order_line_item
        self.product_code = line.product_code or ""
        self.product_name = line.description or ""
        self.unit = line.unit or ""
        self.po_qty = line.requested_qty or Decimal("0.00")
        previously_received = self._calculate_previously_received()
        current_receiving = self.qty_good or Decimal("0.00")
        # Store cumulative received quantity (previous + current accepted qty only).
        self.already_received = previously_received + current_receiving
        self.product = self._resolve_product()

    def populate_standalone_item(self):
        if self.purchase_order_line_item_id:
            return

        self.product = self._resolve_product()
        if self.product_id:
            self.product_code = self.product_code or self.product.product_code or ""
            self.product_name = self.product_name or self.product.name or ""
            if not self.unit and self.product.unit_id:
                self.unit = self.product.unit.name or ""
        self.po_qty = self.po_qty or Decimal("0.00")
        self.already_received = self.qty_good or Decimal("0.00")

    def _resolve_product(self):
        if self.product_id:
            return self.product
        if self.purchase_order_line_item_id and self.purchase_order_line_item.product_id:
            return self.purchase_order_line_item.product
        product_code = self.product_code or ""
        if not product_code:
            return None
        return Product.objects.filter(product_code=product_code).first()

    @staticmethod
    def refresh_product_stock(product_id):
        if not product_id:
            return

        product = Product.objects.filter(pk=product_id).first()
        if not product:
            return

        purchased_stock = product.goods_receipt_items.aggregate(
            total=Coalesce(
                Sum(
                    F("qty_good"),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                ),
                Value(Decimal("0.00")),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        )["total"] or Decimal("0.00")
        product.purchased_stock = purchased_stock
        product.save(update_fields=["purchased_stock", "stock_on_hand", "updated_at"])

    def clean(self):
        super().clean()
        if not self.goods_receipt_id:
            raise ValidationError({"goods_receipt": "Goods Receipt Item must belong to a Goods Receipt."})

        if not self.goods_receipt.purchase_order_id:
            if self.purchase_order_line_item_id:
                raise ValidationError(
                    {
                        "purchase_order_line_item": (
                            "Standalone Goods Receipt Items cannot be linked to a Purchase Order line item."
                        )
                    }
                )
            self.populate_standalone_item()
            if not self.product_id and not self.product_code and not self.product_name:
                raise ValidationError(
                    {
                        "product": (
                            "Standalone Goods Receipt Items require a product, product code, or product name."
                        )
                    }
                )
            return

        if not self.purchase_order_line_item_id:
            raise ValidationError(
                {
                    "purchase_order_line_item": (
                        "Purchase order line item is required for Purchase Order-based Goods Receipts."
                    )
                }
            )

        if self.goods_receipt.purchase_order_id != self.purchase_order_line_item.purchase_order_id:
            raise ValidationError(
                {"purchase_order_line_item": "Selected PO line item does not belong to the Goods Receipt purchase order."}
            )

        self.populate_from_po_line()
        total_receiving_now = self.qty_good or Decimal("0.00")
        previously_received = self._calculate_previously_received()
        pending_qty = (self.po_qty or Decimal("0.00")) - previously_received
        if total_receiving_now > pending_qty:
            raise ValidationError(
                {
                    "qty_good": (
                        f"Current GRN accepted quantity (qty_good = {total_receiving_now}) cannot exceed "
                        f"pending PO quantity ({pending_qty}). "
                        f"PO quantity: {self.po_qty}, previously received: {previously_received}."
                    )
                }
            )

    def save(self, *args, **kwargs):
        previous_product_id = None
        if self.pk:
            previous_product_id = (
                GoodsReceiptItem.objects.filter(pk=self.pk).values_list("product_id", flat=True).first()
            )

        if self.purchase_order_line_item_id:
            self.populate_from_po_line()
        else:
            self.populate_standalone_item()
        self.full_clean()
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {
                "product",
                "product_code",
                "product_name",
                "unit",
                "po_qty",
                "already_received",
            }
        super().save(*args, **kwargs)

        affected_product_ids = {previous_product_id, self.product_id}
        for product_id in affected_product_ids:
            self.refresh_product_stock(product_id)

    def delete(self, *args, **kwargs):
        product_id = self.product_id
        result = super().delete(*args, **kwargs)
        self.refresh_product_stock(product_id)
        return result


class ReceivedGoodsPhoto(models.Model):
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        related_name="received_goods_photos",
    )
    photo = models.ImageField(upload_to="inventory/grn/received_goods/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Received Goods Photo"
        verbose_name_plural = "Received Goods Photos"

    def __str__(self) -> str:
        return f"GRN Photo {self.pk or 'NEW'} - GRN {self.goods_receipt_id}"
