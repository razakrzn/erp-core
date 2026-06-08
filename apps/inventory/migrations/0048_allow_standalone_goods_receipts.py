from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0047_goodsreceipt_approval_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="goodsreceipt",
            name="purchase_order",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="goods_receipts",
                to="inventory.purchaseorder",
            ),
        ),
        migrations.AlterField(
            model_name="goodsreceiptitem",
            name="purchase_order_line_item",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="goods_receipt_items",
                to="inventory.purchaseorderlineitem",
            ),
        ),
    ]
