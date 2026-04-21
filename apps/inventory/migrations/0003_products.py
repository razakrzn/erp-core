from django.db import migrations, models
import django.db.models.deletion


def cleanup_partial_inventory_product_schema(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    sql = """
    DO $$
    DECLARE
        relation_name text;
    BEGIN
        FOR relation_name IN
            SELECT c.relname
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = current_schema()
              AND c.relkind = 'i'
              AND c.relname LIKE 'inventory\\_product\\_%'
              AND c.relname NOT LIKE '%\\_pkey'
        LOOP
            EXECUTE format('DROP INDEX IF EXISTS %I CASCADE', relation_name);
        END LOOP;
    END $$;
    """
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0002_alter_vendor_address_alter_vendor_email_address_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP TABLE IF EXISTS inv_prices CASCADE;
            DROP TABLE IF EXISTS inv_products CASCADE;
            DROP TABLE IF EXISTS inv_units CASCADE;
            DROP TABLE IF EXISTS inv_finishes CASCADE;
            DROP TABLE IF EXISTS inv_grades CASCADE;
            DROP TABLE IF EXISTS inv_thicknesses CASCADE;
            DROP TABLE IF EXISTS inv_sizes CASCADE;
            DROP TABLE IF EXISTS inv_materials CASCADE;
            DROP TABLE IF EXISTS inv_brands CASCADE;
            DROP TABLE IF EXISTS inv_categories CASCADE;
            DROP TABLE IF EXISTS inventory_price CASCADE;
            DROP TABLE IF EXISTS inventory_product CASCADE;
            DROP TABLE IF EXISTS inventory_unit CASCADE;
            DROP TABLE IF EXISTS inventory_finish CASCADE;
            DROP TABLE IF EXISTS inventory_grade CASCADE;
            DROP TABLE IF EXISTS inventory_thickness CASCADE;
            DROP TABLE IF EXISTS inventory_size CASCADE;
            DROP TABLE IF EXISTS inventory_material CASCADE;
            DROP TABLE IF EXISTS inventory_brand CASCADE;
            DROP TABLE IF EXISTS inventory_category CASCADE;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunPython(
            cleanup_partial_inventory_product_schema,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.CreateModel(
            name="Brand",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True, verbose_name="name")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("is_active", models.BooleanField(default=True, verbose_name="is active")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
            ],
            options={
                "verbose_name": "brand",
                "verbose_name_plural": "brands",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True, verbose_name="name")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("is_active", models.BooleanField(default=True, verbose_name="is active")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
            ],
            options={
                "verbose_name": "category",
                "verbose_name_plural": "categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Finish",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True, verbose_name="name")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("is_active", models.BooleanField(default=True, verbose_name="is active")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
            ],
            options={
                "verbose_name": "finish",
                "verbose_name_plural": "finishes",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Grade",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True, verbose_name="name")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("is_active", models.BooleanField(default=True, verbose_name="is active")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
            ],
            options={
                "verbose_name": "grade",
                "verbose_name_plural": "grades",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Material",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True, verbose_name="name")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("is_active", models.BooleanField(default=True, verbose_name="is active")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
            ],
            options={
                "verbose_name": "material",
                "verbose_name_plural": "materials",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Size",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True, verbose_name="name")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("is_active", models.BooleanField(default=True, verbose_name="is active")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
            ],
            options={
                "verbose_name": "size",
                "verbose_name_plural": "sizes",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Thickness",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True, verbose_name="name")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("is_active", models.BooleanField(default=True, verbose_name="is active")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
            ],
            options={
                "verbose_name": "thickness",
                "verbose_name_plural": "thicknesses",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Unit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True, verbose_name="name")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("is_active", models.BooleanField(default=True, verbose_name="is active")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                ("symbol", models.CharField(blank=True, max_length=20, verbose_name="symbol")),
            ],
            options={
                "verbose_name": "unit",
                "verbose_name_plural": "units",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="name")),
                ("sku", models.CharField(max_length=100, verbose_name="SKU")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("is_active", models.BooleanField(default=True, verbose_name="is active")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                (
                    "brand",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="products",
                        to="inventory.brand",
                        verbose_name="brand",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="products",
                        to="inventory.category",
                        verbose_name="category",
                    ),
                ),
                (
                    "finish",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="products",
                        to="inventory.finish",
                        verbose_name="finish",
                    ),
                ),
                (
                    "grade",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="products",
                        to="inventory.grade",
                        verbose_name="grade",
                    ),
                ),
                (
                    "material",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="products",
                        to="inventory.material",
                        verbose_name="material",
                    ),
                ),
                (
                    "size",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="products",
                        to="inventory.size",
                        verbose_name="size",
                    ),
                ),
                (
                    "thickness",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="products",
                        to="inventory.thickness",
                        verbose_name="thickness",
                    ),
                ),
                (
                    "unit",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="products",
                        to="inventory.unit",
                        verbose_name="unit",
                    ),
                ),
            ],
            options={
                "verbose_name": "product",
                "verbose_name_plural": "products",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Price",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="amount")),
                ("currency", models.CharField(default="AED", max_length=10, verbose_name="currency")),
                ("effective_from", models.DateField(blank=True, null=True, verbose_name="effective from")),
                ("is_active", models.BooleanField(default=True, verbose_name="is active")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prices",
                        to="inventory.product",
                        verbose_name="product",
                    ),
                ),
            ],
            options={
                "verbose_name": "price",
                "verbose_name_plural": "prices",
                "ordering": ["-created_at"],
            },
        ),
    ]
