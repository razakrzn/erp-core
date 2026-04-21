from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0018_sync_purchase_order_schema"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="purchaseorder",
            name="vendor",
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="vendor",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="purchase_orders",
                to="inventory.vendor",
            ),
        ),
    ]
