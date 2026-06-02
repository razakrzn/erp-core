from django.db import migrations


def ensure_received_goods_photo_table_name(apps, schema_editor):
    connection = schema_editor.connection
    old_table = "inventory_goodsreceiptphoto"
    new_table = "inventory_receivedgoodsphoto"

    with connection.cursor() as cursor:
        table_names = set(connection.introspection.table_names(cursor))
        if old_table in table_names and new_table not in table_names:
            cursor.execute(f"ALTER TABLE {old_table} RENAME TO {new_table}")


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0040_fix_goodsreceiptitem_qty_good_column"),
    ]

    operations = [
        migrations.RunPython(
            ensure_received_goods_photo_table_name,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

