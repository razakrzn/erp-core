from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0006_remove_unit_symbol"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    ALTER TABLE inventory_brand DROP COLUMN IF EXISTS is_active;
                    ALTER TABLE inventory_category DROP COLUMN IF EXISTS is_active;
                    ALTER TABLE inventory_finish DROP COLUMN IF EXISTS is_active;
                    ALTER TABLE inventory_grade DROP COLUMN IF EXISTS is_active;
                    ALTER TABLE inventory_material DROP COLUMN IF EXISTS is_active;
                    ALTER TABLE inventory_size DROP COLUMN IF EXISTS is_active;
                    ALTER TABLE inventory_thickness DROP COLUMN IF EXISTS is_active;
                    ALTER TABLE inventory_unit DROP COLUMN IF EXISTS is_active;
                    ALTER TABLE inventory_product DROP COLUMN IF EXISTS is_active;
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                )
            ],
            state_operations=[],
        ),
    ]
