from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0035_add_quoteitem_sku"),
    ]

    operations = [
        migrations.CreateModel(
            name="Accessory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("accessory_id", models.CharField(max_length=100, verbose_name="accessory id")),
                ("accessory_name", models.CharField(max_length=200, verbose_name="accessory name")),
                (
                    "accessory_price",
                    models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name="accessory price"),
                ),
                (
                    "accessory_qty",
                    models.DecimalField(decimal_places=3, default=0, max_digits=14, verbose_name="accessory qty"),
                ),
                (
                    "quote_item",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="accessory_lines",
                        to="assessment.quoteitem",
                        verbose_name="quote item",
                    ),
                ),
            ],
            options={
                "verbose_name": "accessory",
                "verbose_name_plural": "accessories",
                "ordering": ["-id"],
            },
        ),
    ]

