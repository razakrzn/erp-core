from decimal import Decimal

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0037_remove_purchaseorder_purchase_requisition"),
    ]

    operations = [
        migrations.CreateModel(
            name="GoodsReceipt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("purchase_order_no", models.CharField(blank=True, default="", max_length=30)),
                ("po_date", models.DateField(blank=True, null=True)),
                ("grn_recording_date", models.DateField(default=django.utils.timezone.localdate)),
                ("vendor_name", models.CharField(blank=True, default="", max_length=255)),
                ("vendor_trn", models.CharField(blank=True, default="", max_length=15)),
                ("vendor_address", models.TextField(blank=True, default="")),
                ("vendor_invoice_no", models.CharField(blank=True, default="", max_length=100)),
                ("vendor_invoice_date", models.DateField(blank=True, null=True)),
                ("delivery_challan_no", models.CharField(blank=True, default="", max_length=100)),
                ("delivery_challan_date", models.DateField(blank=True, null=True)),
                (
                    "vendor_delivery_challan",
                    models.FileField(blank=True, null=True, upload_to="inventory/grn/vendor_delivery_challan/"),
                ),
                ("vendor_invoice", models.FileField(blank=True, null=True, upload_to="inventory/grn/vendor_invoice/")),
                (
                    "overall_quality_status",
                    models.CharField(default="accepted", max_length=30),
                ),
                ("quality_notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "purchase_order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="goods_receipts",
                        to="inventory.purchaseorder",
                    ),
                ),
            ],
            options={
                "verbose_name": "Goods Receipt",
                "verbose_name_plural": "Goods Receipts",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ReceivedGoodsPhoto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("photo", models.ImageField(upload_to="inventory/grn/received_goods/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "goods_receipt",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_goods_photos",
                        to="inventory.goodsreceipt",
                    ),
                ),
            ],
            options={
                "verbose_name": "Goods Receipt Photo",
                "verbose_name_plural": "Goods Receipt Photos",
            },
        ),
        migrations.CreateModel(
            name="GoodsReceiptItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_code", models.CharField(blank=True, default="", max_length=100)),
                ("product_name", models.CharField(blank=True, default="", max_length=255)),
                ("unit", models.CharField(blank=True, default="", max_length=50)),
                (
                    "po_qty",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                (
                    "already_received",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        editable=False,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                (
                    "qty_good",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                (
                    "qty_rejected",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                ("rejection_reason", models.TextField(blank=True, default="")),
                ("defect_photo", models.FileField(blank=True, null=True, upload_to="inventory/grn/defects/")),
                (
                    "goods_receipt",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="material_intakes",
                        to="inventory.goodsreceipt",
                    ),
                ),
                (
                    "purchase_order_line_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="goods_receipt_items",
                        to="inventory.purchaseorderlineitem",
                    ),
                ),
            ],
            options={
                "verbose_name": "Goods Receipt Item",
                "verbose_name_plural": "Goods Receipt Items",
            },
        ),
    ]
