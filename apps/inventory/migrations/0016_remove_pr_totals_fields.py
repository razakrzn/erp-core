from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0015_add_purchase_requisition_approval_flags"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="purchaserequisition",
            name="estimated_subtotal",
        ),
        migrations.RemoveField(
            model_name="purchaserequisition",
            name="vat_amount",
        ),
        migrations.RemoveField(
            model_name="purchaserequisition",
            name="total_value",
        ),
        migrations.RemoveField(
            model_name="purchaserequisitionlineitem",
            name="line_total",
        ),
    ]
