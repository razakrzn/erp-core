from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0029_add_boq_reject_note"),
    ]

    operations = [
        migrations.AddField(
            model_name="quote",
            name="reject_note",
            field=models.TextField(blank=True, default="", verbose_name="reject note"),
        ),
    ]
