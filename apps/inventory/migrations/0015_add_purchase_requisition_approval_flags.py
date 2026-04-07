from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0014_add_purchase_requisition_audit_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaserequisition",
            name="is_approved",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="purchaserequisition",
            name="is_rejected",
            field=models.BooleanField(default=False),
        ),
    ]
