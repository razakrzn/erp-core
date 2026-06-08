from django.db import migrations, models


def approve_existing_goods_receipts(apps, schema_editor):
    GoodsReceipt = apps.get_model("inventory", "GoodsReceipt")
    GoodsReceipt.objects.all().update(
        status="Approved",
        is_approved=True,
        is_rejected=False,
        reject_note="",
    )


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0046_sync_product_available"),
    ]

    operations = [
        migrations.AddField(
            model_name="goodsreceipt",
            name="status",
            field=models.CharField(
                default="Pending",
                help_text="Current status e.g. Pending, Approved, Rejected.",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="goodsreceipt",
            name="is_approved",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name="goodsreceipt",
            name="is_rejected",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name="goodsreceipt",
            name="reject_note",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Reason for rejecting this goods receipt.",
                null=True,
            ),
        ),
        migrations.RunPython(approve_existing_goods_receipts, reverse_code=migrations.RunPython.noop),
    ]
