from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0004_remove_lookup_code_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name="price"),
        ),
        migrations.DeleteModel(
            name="Price",
        ),
    ]
