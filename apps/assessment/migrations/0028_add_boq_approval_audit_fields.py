from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0027_alter_quotetermsconditions_options"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="boq",
            name="approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="approved_boqs",
                to=settings.AUTH_USER_MODEL,
                verbose_name="approved by",
            ),
        ),
        migrations.AddField(
            model_name="boq",
            name="rejected_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="rejected_boqs",
                to=settings.AUTH_USER_MODEL,
                verbose_name="rejected by",
            ),
        ),
    ]
