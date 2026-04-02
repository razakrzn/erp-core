from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0008_remove_lookup_descriptions"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="ALTER TABLE inventory_product DROP COLUMN IF EXISTS description;",
                    reverse_sql=migrations.RunSQL.noop,
                )
            ],
            state_operations=[],
        ),
    ]
