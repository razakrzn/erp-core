from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("inventory", "0017_purchaseorder"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaseorder",
            name="associated_job",
            field=models.CharField(
                blank=True,
                help_text="Associated job or project name e.g. Villa Renovation - Jumeirah.",
                max_length=200,
            ),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="confirmed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="confirmed_purchase_orders",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="grand_total",
            field=models.DecimalField(decimal_places=2, default=Decimal("0.00"), editable=False, max_digits=14),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="internal_remarks",
            field=models.TextField(blank=True, help_text="Internal remarks or additional info for this PO."),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="is_closed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="is_confirmed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="net_amount",
            field=models.DecimalField(decimal_places=2, default=Decimal("0.00"), editable=False, max_digits=14),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="payment_terms",
            field=models.CharField(help_text="Payment terms e.g. Net 30, Cash on Delivery.", max_length=150, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="po_issued_date",
            field=models.DateField(help_text="Date the PO was issued.", null=True),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="purchase_requisition",
            field=models.ForeignKey(
                blank=True,
                help_text="The Purchase Requisition this PO was raised from.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="purchase_orders",
                to="inventory.purchaserequisition",
            ),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="shipping_delivery_terms",
            field=models.CharField(
                help_text="Shipping / delivery terms e.g. FOB, CIF, DDP.",
                max_length=150,
                default="",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="vat_amount",
            field=models.DecimalField(decimal_places=2, default=Decimal("0.00"), editable=False, max_digits=14),
        ),
        migrations.RemoveField(
            model_name="purchaseorder",
            name="expected_delivery_date",
        ),
        migrations.RemoveField(
            model_name="purchaseorder",
            name="notes",
        ),
        migrations.RemoveField(
            model_name="purchaseorder",
            name="order_date",
        ),
        migrations.RemoveField(
            model_name="purchaseorder",
            name="total_amount",
        ),
        migrations.RemoveField(
            model_name="purchaseorder",
            name="vendor",
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="vendor",
            field=models.CharField(help_text="Vendor / supplier name.", max_length=200, default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="purchaseorder",
            name="status",
            field=models.CharField(
                default="Draft",
                help_text="Current status e.g. Draft, Confirmed, Released, Closed.",
                max_length=50,
            ),
        ),
        migrations.CreateModel(
            name="PurchaseOrderLineItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("unit", models.CharField(help_text="Unit of measure.", max_length=50)),
                (
                    "qty",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Ordered quantity.",
                        max_digits=12,
                        validators=[MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                ("required_by", models.DateField(blank=True, help_text="Date by which this item is required.", null=True)),
                (
                    "delivery_location",
                    models.CharField(blank=True, help_text="Delivery location for this line item.", max_length=200),
                ),
                (
                    "negotiated_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        help_text="Negotiated unit price agreed with the vendor.",
                        max_digits=12,
                        validators=[MinValueValidator(Decimal("0.00"))],
                    ),
                ),
                ("line_total", models.DecimalField(decimal_places=2, default=Decimal("0.00"), editable=False, max_digits=14)),
                (
                    "po_line_items",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="po_line_items",
                        to="inventory.purchaseorder",
                    ),
                ),
                (
                    "pr_line_item",
                    models.ForeignKey(
                        blank=True,
                        help_text="The PR line item this PO line was synced from.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="po_line_items",
                        to="inventory.purchaserequisitionlineitem",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="po_line_items",
                        to="inventory.product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Purchase Order Line Item",
                "verbose_name_plural": "Purchase Order Line Items",
            },
        ),
        migrations.RenameField(
            model_name="purchaseorderlineitem",
            old_name="po_line_items",
            new_name="purchase_order",
        ),
        migrations.AlterField(
            model_name="purchaseorder",
            name="po_issued_date",
            field=models.DateField(help_text="Date the PO was issued."),
        ),
    ]
