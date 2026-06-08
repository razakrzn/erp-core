from django.db import migrations, models


def populate_grn_number(apps, schema_editor):
    GoodsReceipt = apps.get_model("inventory", "GoodsReceipt")
    for record in GoodsReceipt.objects.filter(grn_number__isnull=True).only("id", "grn_number"):
        record.grn_number = f"GRN-{record.id:06d}"
        record.save(update_fields=["grn_number"])


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0041_fix_receivedgoodsphoto_table_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="goodsreceipt",
            name="grn_number",
            field=models.CharField(
                blank=True,
                editable=False,
                help_text="Auto-generated unique goods receipt number.",
                max_length=30,
                null=True,
                unique=True,
            ),
        ),
        migrations.RunPython(
            populate_grn_number,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

