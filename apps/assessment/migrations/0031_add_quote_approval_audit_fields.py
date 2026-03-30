from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0030_add_quote_reject_note"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="quote",
            name="approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="approved_quotes",
                to=settings.AUTH_USER_MODEL,
                verbose_name="approved by",
            ),
        ),
        migrations.AddField(
            model_name="quote",
            name="rejected_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="rejected_quotes",
                to=settings.AUTH_USER_MODEL,
                verbose_name="rejected by",
            ),
        ),
    ]
