from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("production", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cuttingoptimizationjob",
            name="cad_file",
            field=models.FileField(blank=True, null=True, upload_to="production/cad/"),
        ),
        migrations.AddField(
            model_name="cuttingoptimizationjob",
            name="cutlist_pdf_file",
            field=models.FileField(blank=True, null=True, upload_to="production/cutlists/"),
        ),
        migrations.AddField(
            model_name="cuttingoptimizationjob",
            name="cutlist_xlsx_file",
            field=models.FileField(blank=True, null=True, upload_to="production/cutlists/"),
        ),
    ]
