# Generated manually to match model updates in Employee

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hrm", "0014_remove_employee_job_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="passport_copy",
            field=models.FileField(blank=True, null=True, upload_to="employees/documents/passport/", verbose_name="passport copy"),
        ),
        migrations.AddField(
            model_name="employee",
            name="visa_document",
            field=models.FileField(blank=True, null=True, upload_to="employees/documents/visa/", verbose_name="visa"),
        ),
        migrations.AddField(
            model_name="employee",
            name="cv_document",
            field=models.FileField(blank=True, null=True, upload_to="employees/documents/cv/", verbose_name="CV"),
        ),
        migrations.AddField(
            model_name="employee",
            name="permits_document",
            field=models.FileField(blank=True, null=True, upload_to="employees/documents/permits/", verbose_name="permits"),
        ),
        migrations.AddField(
            model_name="employee",
            name="educational_certificates_document",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="employees/documents/educational_certificates/",
                verbose_name="educational certificates",
            ),
        ),
        migrations.AlterField(
            model_name="employee",
            name="uae_visa_type",
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name="UAE visa type"),
        ),
        migrations.AlterField(
            model_name="employee",
            name="employment_type",
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name="employment type"),
        ),
        migrations.AlterField(
            model_name="employee",
            name="contract_type",
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name="contract type"),
        ),
        migrations.AlterField(
            model_name="employee",
            name="work_location",
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name="work location"),
        ),
    ]
