# Generated manually to split employee permits into a separate Permit model

from django.db import migrations, models


def forward_copy_employee_permits_to_permit(apps, schema_editor):
    Employee = apps.get_model("hrm", "Employee")
    Permit = apps.get_model("hrm", "Permit")

    for employee in Employee.objects.exclude(permits_document="").exclude(permits_document__isnull=True):
        Permit.objects.create(
            employee=employee,
            title="Permit",
            permits_document=employee.permits_document,
        )


def reverse_copy_permit_to_employee_permits(apps, schema_editor):
    Employee = apps.get_model("hrm", "Employee")
    Permit = apps.get_model("hrm", "Permit")

    for employee in Employee.objects.all():
        first_permit = Permit.objects.filter(employee=employee).exclude(permits_document="").first()
        if first_permit:
            employee.permits_document = first_permit.permits_document
            employee.save(update_fields=["permits_document"])


class Migration(migrations.Migration):

    dependencies = [
        ("hrm", "0017_previousemployment_experience_certificate"),
    ]

    operations = [
        migrations.CreateModel(
            name="Permit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="title")),
                (
                    "permits_document",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="employees/documents/permits/",
                        verbose_name="permits",
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="permits",
                        to="hrm.employee",
                        verbose_name="employee",
                    ),
                ),
            ],
            options={
                "verbose_name": "permit",
                "verbose_name_plural": "permits",
            },
        ),
        migrations.RunPython(
            forward_copy_employee_permits_to_permit,
            reverse_copy_permit_to_employee_permits,
        ),
        migrations.RemoveField(
            model_name="employee",
            name="permits_document",
        ),
    ]
