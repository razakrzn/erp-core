from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0038_remove_quoteitem_sku"),
    ]

    operations = [
        migrations.AddField(
            model_name="quote",
            name="attachment",
            field=models.FileField(blank=True, null=True, upload_to="assessment/quotes/", verbose_name="attachment"),
        ),
    ]
