from decimal import Decimal

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("inventory", "0016_remove_pr_totals_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="PurchaseOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("po_number", models.CharField(blank=True, editable=False, help_text="Auto-generated unique purchase order number.", max_length=30, unique=True)),
                ("order_date", models.DateField()),
                ("expected_delivery_date", models.DateField(blank=True, null=True)),
                ("status", models.CharField(default="Draft", help_text="Current status e.g. Draft, Issued, Partially Received, Received, Cancelled.", max_length=50)),
                ("notes", models.TextField(blank=True)),
                ("total_amount", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=14)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchase_orders", to=settings.AUTH_USER_MODEL)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_purchase_orders", to=settings.AUTH_USER_MODEL)),
                ("vendor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="purchase_orders", to="inventory.vendor")),
            ],
            options={
                "verbose_name": "Purchase Order",
                "verbose_name_plural": "Purchase Orders",
                "ordering": ["-created_at"],
            },
        ),
    ]
