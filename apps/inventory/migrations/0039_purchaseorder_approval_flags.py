from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0038_goodsreceipt_goodsreceiptitem_goodsreceiptphoto"),
    ]

    operations = [
        migrations.RenameField(
            model_name="purchaseorder",
            old_name="is_confirmed",
            new_name="is_approved",
        ),
        migrations.RenameField(
            model_name="purchaseorder",
            old_name="is_closed",
            new_name="is_rejected",
        ),
        migrations.AlterField(
            model_name="purchaseorder",
            name="is_approved",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name="purchaseorder",
            name="is_rejected",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name="purchaseorder",
            name="reject_note",
            field=models.TextField(blank=True, default="", help_text="Reason for rejecting this purchase order.", null=True),
        ),
    ]
