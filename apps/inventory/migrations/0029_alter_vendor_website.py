from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0028_vendor_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vendor",
            name="website",
            field=models.CharField(
                blank=True,
                max_length=500,
                null=True,
                verbose_name="website",
            ),
        ),
    ]
