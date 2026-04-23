from django.db import migrations


def drop_lookup_code_columns_if_present(apps, schema_editor):
    tables = [
        "inventory_brand",
        "inventory_category",
        "inventory_finish",
        "inventory_grade",
        "inventory_material",
        "inventory_size",
        "inventory_thickness",
        "inventory_unit",
    ]

    connection = schema_editor.connection
    with connection.cursor() as cursor:
        for table in tables:
            columns = {
                column.name for column in connection.introspection.get_table_description(cursor, table)
            }
            if "code" in columns:
                schema_editor.execute(
                    f"ALTER TABLE {schema_editor.quote_name(table)} DROP COLUMN {schema_editor.quote_name('code')}"
                )


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_products"),
    ]
    atomic = False

    operations = [
        migrations.RunPython(
            drop_lookup_code_columns_if_present,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
