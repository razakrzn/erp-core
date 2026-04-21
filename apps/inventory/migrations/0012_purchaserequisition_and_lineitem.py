from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0011_sync_inventory_state"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PurchaseRequisition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "stock_reason_category",
                    models.CharField(
                        help_text="Category describing the reason for this stock requisition.",
                        max_length=150,
                    ),
                ),
                ("required_by_date", models.DateField()),
                (
                    "priority",
                    models.CharField(
                        default="Medium",
                        help_text="Priority level e.g. Low, Medium, High, Urgent.",
                        max_length=50,
                    ),
                ),
                (
                    "delivery_location",
                    models.CharField(
                        blank=True,
                        help_text="Destination delivery location.",
                        max_length=200,
                    ),
                ),
                (
                    "reason_description",
                    models.TextField(
                        blank=True,
                        help_text="Provide justification for this purchase requisition.",
                    ),
                ),
                (
                    "notes_to_purchase_team",
                    models.TextField(
                        blank=True,
                        help_text="Specific instructions for the procurement department.",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        default="Draft",
                        help_text="Current status e.g. Draft, Submitted for Approval, Approved, Rejected.",
                        max_length=50,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "estimated_subtotal",
                    models.DecimalField(decimal_places=2, default=Decimal("0.00"), editable=False, max_digits=14),
                ),
                (
                    "vat_amount",
                    models.DecimalField(decimal_places=2, default=Decimal("0.00"), editable=False, max_digits=14),
                ),
                (
                    "total_value",
                    models.DecimalField(decimal_places=2, default=Decimal("0.00"), editable=False, max_digits=14),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="purchase_requisitions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Purchase Requisition",
                "verbose_name_plural": "Purchase Requisitions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PurchaseRequisitionLineItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "stock_on_hand",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        help_text="Current stock level at time of PR creation.",
                        max_digits=12,
                    ),
                ),
                (
                    "pending_pr_qty",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        help_text="Quantity in other pending purchase requisitions.",
                        max_digits=12,
                    ),
                ),
                (
                    "pending_po_qty",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        help_text="Quantity in pending purchase orders.",
                        max_digits=12,
                    ),
                ),
                (
                    "requested_qty",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Quantity requested by the requester.",
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "net_required_qty",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        editable=False,
                        help_text="Net quantity needed after accounting for stock and pending orders.",
                        max_digits=12,
                    ),
                ),
                (
                    "line_total",
                    models.DecimalField(decimal_places=2, default=Decimal("0.00"), editable=False, max_digits=14),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="requisition_line_items",
                        to="inventory.product",
                    ),
                ),
                (
                    "purchase_requisition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="line_items",
                        to="inventory.purchaserequisition",
                    ),
                ),
            ],
            options={
                "verbose_name": "Purchase Requisition Line Item",
                "verbose_name_plural": "Purchase Requisition Line Items",
            },
        ),
    ]
