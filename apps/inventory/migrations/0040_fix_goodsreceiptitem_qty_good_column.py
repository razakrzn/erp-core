from django.db import migrations


def rename_requested_qty_to_qty_good(apps, schema_editor):
    table_name = "inventory_goodsreceiptitem"
    connection = schema_editor.connection

    with connection.cursor() as cursor:
        table_names = connection.introspection.table_names(cursor)
        if table_name not in table_names:
            return

        description = connection.introspection.get_table_description(cursor, table_name)
        column_names = {col.name for col in description}

        # Existing DBs may still have the old column name from an earlier applied migration.
        if "requested_qty" in column_names and "qty_good" not in column_names:
            cursor.execute(
                """
                ALTER TABLE inventory_goodsreceiptitem
                CHANGE COLUMN requested_qty qty_good NUMERIC(12,2) NOT NULL DEFAULT 0.00
                """
            )


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0039_purchaseorder_approval_flags"),
    ]

    operations = [
        migrations.RunPython(
            rename_requested_qty_to_qty_good,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
