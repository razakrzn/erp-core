from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0019_purchaseorder_vendor_fk"),
    ]

    operations = [
        migrations.AlterField(
            model_name="purchaseorder",
            name="vendor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="purchase_orders",
                help_text="Vendor / supplier.",
                to="inventory.vendor",
            ),
        ),
    ]
