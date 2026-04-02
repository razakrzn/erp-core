from django.db import migrations


def migrate_list_permissions_to_view(apps, schema_editor):
    Permission = apps.get_model("navigation", "Permission")
    RolePermission = apps.get_model("rbac", "RolePermission")
    APIAccessRule = apps.get_model("access_control", "APIAccessRule")

    old_to_new_codes: dict[str, str] = {}

    list_permissions = Permission.objects.filter(permission_code__iendswith=".list").order_by("id")

    for permission in list_permissions:
        old_code = permission.permission_code
        new_code = f"{old_code[:-5]}.view"
        old_to_new_codes[old_code] = new_code

        target_permission = Permission.objects.filter(permission_code=new_code).first()

        if target_permission and target_permission.pk != permission.pk:
            conflicting_role_ids = set(
                RolePermission.objects.filter(permission_id=target_permission.pk).values_list("role_id", flat=True)
            )
            if conflicting_role_ids:
                RolePermission.objects.filter(permission_id=permission.pk, role_id__in=conflicting_role_ids).delete()

            RolePermission.objects.filter(permission_id=permission.pk).update(permission_id=target_permission.pk)
            permission.delete()
            continue

        permission.permission_code = new_code
        if (permission.permission_name or "").lower().startswith("list "):
            permission.permission_name = f"View {permission.permission_name[5:]}"
        permission.save(update_fields=["permission_code", "permission_name"])

    for old_code, new_code in old_to_new_codes.items():
        APIAccessRule.objects.filter(permission_code=old_code).update(permission_code=new_code)


class Migration(migrations.Migration):
    dependencies = [
        ("access_control", "0001_initial"),
        ("navigation", "0001_initial"),
        ("rbac", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_list_permissions_to_view, migrations.RunPython.noop),
    ]
