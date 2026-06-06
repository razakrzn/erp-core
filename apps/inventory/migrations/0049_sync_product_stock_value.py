from decimal import Decimal

from django.db import migrations, models


def sync_product_stock_value(apps, schema_editor):
    Product = apps.get_model("inventory", "Product")

    for product in Product.objects.all().iterator():
        standard_cost = product.standard_cost or Decimal("0.00")
        stock_on_hand = product.stock_on_hand or Decimal("0.00")
        product.stock_value_aed = standard_cost * stock_on_hand
        product.save(update_fields=["stock_value_aed"])


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0048_allow_standalone_goods_receipts"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="stock_value_aed",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=0,
                editable=False,
                max_digits=14,
                null=True,
                verbose_name="stock value (AED)",
            ),
        ),
        migrations.RunPython(sync_product_stock_value, reverse_code=migrations.RunPython.noop),
    ]
