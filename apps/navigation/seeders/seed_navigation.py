from apps.navigation.models import Feature, Module, Permission


def run():

    hrm = Feature.objects.create(
        feature_code="hrm",
        feature_name="Human Resource Management",
        icon="user"
    )

    employees = Module.objects.create(
        module_code="employees",
        module_name="Employees",
        feature=hrm,
        route="/hrm/employees",
        icon="user"
    )

    Permission.objects.bulk_create([
        Permission(
            permission_code="hrm.employees.view",
            permission_name="View Employees",
            module=employees
        ),
        Permission(
            permission_code="hrm.employees.create",
            permission_name="Create Employees",
            module=employees
        ),
        Permission(
            permission_code="hrm.employees.edit",
            permission_name="Edit Employees",
            module=employees
        ),
        Permission(
            permission_code="hrm.employees.delete",
            permission_name="Delete Employees",
            module=employees
        )
    ])
