# Generated manually for add_user_company

from django.db import migrations, models
import django.db.models.deletion


def set_company_for_existing_users(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Company = apps.get_model("company", "Company")
    company = Company.objects.first()
    if company is None:
        # Create a default company so existing users can be assigned
        company = Company.objects.create(name="Default Company", code="DEFAULT")
    User.objects.filter(company__isnull=True).update(company=company)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("company", "0004_remove_companyuser"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="users",
                to="company.company",
            ),
        ),
        migrations.RunPython(set_company_for_existing_users, noop),
        migrations.AlterField(
            model_name="user",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="users",
                to="company.company",
            ),
        ),
    ]
