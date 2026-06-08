from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


def backfill_purchased_stock(apps, schema_editor):
    Product = apps.get_model("inventory", "Product")
    PurchaseOrderLineItem = apps.get_model("inventory", "PurchaseOrderLineItem")
    PurchaseRequisitionLineItem = apps.get_model("inventory", "PurchaseRequisitionLineItem")
    GoodsReceiptItem = apps.get_model("inventory", "GoodsReceiptItem")

    products_by_code = {
        product.product_code: product.pk
        for product in Product.objects.exclude(product_code__isnull=True).exclude(product_code="")
    }

    requisition_lines = {}
    for line_item in PurchaseRequisitionLineItem.objects.exclude(product_id__isnull=True).iterator():
        key = (line_item.purchase_requisition_id, line_item.product_code or "")
        requisition_lines[key] = line_item.product_id

    for line_item in PurchaseOrderLineItem.objects.all().iterator():
        product_id = requisition_lines.get(
            (line_item.purchase_requisition_id, line_item.product_code or "")
        ) or products_by_code.get(line_item.product_code)
        if product_id:
            line_item.product_id = product_id
            line_item.save(update_fields=["product"])

    for item in GoodsReceiptItem.objects.select_related("purchase_order_line_item").iterator():
        product_id = item.purchase_order_line_item.product_id or products_by_code.get(item.product_code)
        if product_id:
            item.product_id = product_id
            item.save(update_fields=["product"])

    for product in Product.objects.all().iterator():
        purchased_stock = Decimal("0.00")
        for item in GoodsReceiptItem.objects.filter(product_id=product.pk).only("qty_good").iterator():
            purchased_stock += item.qty_good or Decimal("0.00")

        opening_stock = product.opening_stock or 0
        product.purchased_stock = purchased_stock
        product.stock_on_hand = opening_stock + purchased_stock
        product.save(update_fields=["purchased_stock", "stock_on_hand"])


def reset_purchased_stock(apps, schema_editor):
    Product = apps.get_model("inventory", "Product")

    for product in Product.objects.all().iterator():
        product.stock_on_hand = product.opening_stock or 0
        product.purchased_stock = Decimal("0.00")
        product.save(update_fields=["purchased_stock", "stock_on_hand"])


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0044_backfill_goodsreceiptitem_already_received_qty_good_only"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="purchased_stock",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=0,
                editable=False,
                max_digits=12,
                null=True,
                verbose_name="purchased stock",
            ),
        ),
        migrations.AddField(
            model_name="purchaseorderlineitem",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="purchase_order_line_items",
                to="inventory.product",
            ),
        ),
        migrations.AddField(
            model_name="goodsreceiptitem",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="goods_receipt_items",
                to="inventory.product",
            ),
        ),
        migrations.RunPython(backfill_purchased_stock, reverse_code=reset_purchased_stock),
    ]
