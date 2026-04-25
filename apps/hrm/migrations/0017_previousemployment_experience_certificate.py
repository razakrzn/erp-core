# Generated manually for PreviousEmployment experience certificate upload support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hrm", "0016_alter_employee_educational_certificates_document"),
    ]

    operations = [
        migrations.AddField(
            model_name="previousemployment",
            name="experience_certificate",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="employees/documents/experience_certificates/",
                verbose_name="experience certificate",
            ),
        ),
    ]
