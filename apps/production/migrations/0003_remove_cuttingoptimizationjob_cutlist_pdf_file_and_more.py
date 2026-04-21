from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("production", "0002_cuttingoptimizationjob_cutlist_files_and_cad_nullable"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cuttingoptimizationjob",
            name="cutlist_pdf_file",
        ),
        migrations.RemoveField(
            model_name="cuttingoptimizationjob",
            name="cutlist_xlsx_file",
        ),
    ]
