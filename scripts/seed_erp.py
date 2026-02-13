from apps.navigation.models import Feature, Module

def run():

    hrm = Feature.objects.create(
        feature_code="hrm",
        feature_name="Human Resource Management"
    )

    Module.objects.create(
        module_code="hrm_employees",
        module_name="Employees",
        feature=hrm
    )
