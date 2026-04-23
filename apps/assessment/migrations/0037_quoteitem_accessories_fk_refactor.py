from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0036_add_accessory_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accessory",
            name="quote_item",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name="accessories",
                to="assessment.quoteitem",
                verbose_name="quote item",
            ),
        ),
        migrations.RemoveField(
            model_name="quoteitem",
            name="accessories",
        ),
    ]

