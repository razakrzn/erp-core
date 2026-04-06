from django.db import migrations, models


def populate_purchase_request_numbers(apps, schema_editor):
    PurchaseRequisition = apps.get_model("inventory", "PurchaseRequisition")
    for requisition in PurchaseRequisition.objects.filter(purchase_request_number__isnull=True):
        requisition.purchase_request_number = f"PR-{requisition.pk:06d}"
        requisition.save(update_fields=["purchase_request_number"])


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0012_purchaserequisition_and_lineitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchaserequisition",
            name="purchase_request_number",
            field=models.CharField(
                blank=True,
                editable=False,
                help_text="Auto-generated unique purchase requisition number.",
                max_length=30,
                null=True,
                unique=True,
            ),
        ),
        migrations.RunPython(populate_purchase_request_numbers, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name="purchaserequisition",
            name="purchase_request_number",
            field=models.CharField(
                blank=True,
                editable=False,
                help_text="Auto-generated unique purchase requisition number.",
                max_length=30,
                unique=True,
            ),
        ),
    ]
