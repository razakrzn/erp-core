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


def remove_lookup_description_columns_if_present(apps, schema_editor):
    for table_name in [
        "inventory_brand",
        "inventory_category",
        "inventory_finish",
        "inventory_grade",
        "inventory_material",
        "inventory_size",
        "inventory_thickness",
        "inventory_unit",
    ]:
        drop_column_if_present(schema_editor, table_name, "description")


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0007_remove_inventory_is_active"),
    ]
    atomic = False

    operations = [
        migrations.RunPython(
            remove_lookup_description_columns_if_present,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
