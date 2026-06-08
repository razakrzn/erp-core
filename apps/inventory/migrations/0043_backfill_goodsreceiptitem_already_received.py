from decimal import Decimal

from django.db import migrations


def backfill_already_received_cumulative(apps, schema_editor):
    GoodsReceiptItem = apps.get_model("inventory", "GoodsReceiptItem")

    line_item_ids = (
        GoodsReceiptItem.objects.values_list("purchase_order_line_item_id", flat=True)
        .distinct()
    )

    for line_item_id in line_item_ids:
        cumulative = Decimal("0.00")
        items = GoodsReceiptItem.objects.filter(
            purchase_order_line_item_id=line_item_id
        ).order_by("id")

        for item in items:
            qty_good = item.qty_good or Decimal("0.00")
            qty_rejected = item.qty_rejected or Decimal("0.00")
            cumulative += qty_good + qty_rejected
            item.already_received = cumulative
            item.save(update_fields=["already_received"])


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0042_goodsreceipt_grn_number"),
    ]

    operations = [
        migrations.RunPython(
            backfill_already_received_cumulative,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

