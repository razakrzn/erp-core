from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0005_move_price_to_product"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="ALTER TABLE inventory_unit DROP COLUMN IF EXISTS symbol;",
                    reverse_sql=migrations.RunSQL.noop,
                )
            ],
            state_operations=[],
        ),
    ]
