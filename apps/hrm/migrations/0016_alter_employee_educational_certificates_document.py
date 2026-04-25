# Generated manually to support multiple educational certificate uploads

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hrm", "0015_employee_document_fields_and_choice_removals"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employee",
            name="educational_certificates_document",
            field=models.JSONField(blank=True, default=list, verbose_name="educational certificates"),
        ),
    ]
