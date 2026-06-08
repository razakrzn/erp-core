from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0036_alter_product_sku"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="purchaseorder",
            name="purchase_requisition",
        ),
    ]
