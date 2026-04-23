from django.db import migrations


def drop_column_if_present(schema_editor, table_name, column_name):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        if table_name not in connection.introspection.table_names(cursor):
            return
        columns = {
            column.name
            for column in connection.introspection.get_table_description(cursor, table_name)
        }
        if column_name in columns:
            schema_editor.execute(
                f"ALTER TABLE {schema_editor.quote_name(table_name)} DROP COLUMN {schema_editor.quote_name(column_name)}"
            )


def remove_unit_symbol_if_present(apps, schema_editor):
    drop_column_if_present(schema_editor, "inventory_unit", "symbol")


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0005_move_price_to_product"),
    ]
    atomic = False

    operations = [
        migrations.RunPython(
            remove_unit_symbol_if_present,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
