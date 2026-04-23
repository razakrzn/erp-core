from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0034_add_quote_client_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="quoteitem",
            name="sku",
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name="SKU"),
        ),
    ]

