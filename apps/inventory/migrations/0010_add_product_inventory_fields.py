import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0009_remove_product_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="product_code",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                unique=True,
                verbose_name="product code",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="status",
            field=models.CharField(
                blank=True, max_length=20, null=True, verbose_name="status"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="standard_cost",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=0,
                max_digits=12,
                null=True,
                verbose_name="standard cost",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="reorder_level",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="reorder level"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="preferred_supplier",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="products",
                to="inventory.vendor",
                verbose_name="preferred supplier",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="lead_time_days",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="lead time (days)"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="max_stock_level",
            field=models.PositiveIntegerField(
                blank=True, null=True, verbose_name="max stock level"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="moq",
            field=models.PositiveIntegerField(
                blank=True, default=1, null=True, verbose_name="MOQ (min order)"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="opening_stock",
            field=models.PositiveIntegerField(
                blank=True, default=0, null=True, verbose_name="opening stock"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="opening_stock_date",
            field=models.DateField(
                blank=True, null=True, verbose_name="opening stock date"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="hsn_sac_code",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="HSN / SAC code"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="admin_notes",
            field=models.TextField(
                blank=True, null=True, verbose_name="administrative notes"
            ),
        ),
    ]
