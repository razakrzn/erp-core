from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0010_add_product_inventory_fields"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveField(
                    model_name="brand",
                    name="description",
                ),
                migrations.RemoveField(
                    model_name="brand",
                    name="is_active",
                ),
                migrations.RemoveField(
                    model_name="category",
                    name="description",
                ),
                migrations.RemoveField(
                    model_name="category",
                    name="is_active",
                ),
                migrations.RemoveField(
                    model_name="finish",
                    name="description",
                ),
                migrations.RemoveField(
                    model_name="finish",
                    name="is_active",
                ),
                migrations.RemoveField(
                    model_name="grade",
                    name="description",
                ),
                migrations.RemoveField(
                    model_name="grade",
                    name="is_active",
                ),
                migrations.RemoveField(
                    model_name="material",
                    name="description",
                ),
                migrations.RemoveField(
                    model_name="material",
                    name="is_active",
                ),
                migrations.RemoveField(
                    model_name="product",
                    name="description",
                ),
                migrations.RemoveField(
                    model_name="product",
                    name="is_active",
                ),
                migrations.RemoveField(
                    model_name="size",
                    name="description",
                ),
                migrations.RemoveField(
                    model_name="size",
                    name="is_active",
                ),
                migrations.RemoveField(
                    model_name="thickness",
                    name="description",
                ),
                migrations.RemoveField(
                    model_name="thickness",
                    name="is_active",
                ),
                migrations.RemoveField(
                    model_name="unit",
                    name="description",
                ),
                migrations.RemoveField(
                    model_name="unit",
                    name="is_active",
                ),
                migrations.RemoveField(
                    model_name="unit",
                    name="symbol",
                ),
            ],
        ),
    ]
