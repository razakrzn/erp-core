from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0028_add_boq_approval_audit_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="boq",
            name="reject_note",
            field=models.TextField(blank=True, default="", verbose_name="reject note"),
        ),
    ]
