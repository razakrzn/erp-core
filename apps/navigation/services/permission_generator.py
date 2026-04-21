"""
Automatic permission generation for modules.

Architecture:
- When a Module is created (Django post_save signal), four default permissions
  are created: {feature_code}.{module_code}.create|view|edit|delete.
- Permissions are created via get_or_create(permission_code=...) so duplicates
  are never created and manually added permissions (other codes) are preserved.
- Feature code and module code come from Module.feature.feature_code and
  Module.module_code; naming is consistent and stable for RBAC.

Implementation:
- generate_default_permissions_for_module(module) is the single function used
  by the signal and can be called programmatically (e.g. backfill or tests).
- Manual creation via API or admin continues to work; this only ensures the
  four standard CRUD permissions exist for each new module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from apps.navigation.models import Permission

if TYPE_CHECKING:
    from apps.navigation.models import Module


# Standard CRUD permission actions: (permission_code_suffix, human-readable label)
DEFAULT_PERMISSION_ACTIONS = [
    ("create", "Create"),
    ("view", "View"),
    ("edit", "Edit"),
    ("delete", "Delete"),
]


def generate_default_permissions_for_module(module: "Module") -> list[Permission]:
    """
    Ensure the four default CRUD permissions exist for the given module.

    Permission codes: {feature_code}.{module_code}.create|view|edit|delete.
    Uses get_or_create so no duplicates are created and manually added
    permissions are left unchanged.

    Args:
        module: A saved Module instance with a related Feature (module.feature).

    Returns:
        List of Permission instances (existing or newly created) for the four actions.
    """
    feature_code = module.feature.feature_code
    module_code = module.module_code
    created_list: list[Permission] = []

    for action_code, action_label in DEFAULT_PERMISSION_ACTIONS:
        permission_code = f"{feature_code}.{module_code}.{action_code}"
        permission_name = f"{action_label} {module.module_name}"
        permission, created = Permission.objects.get_or_create(
            permission_code=permission_code,
            defaults={
                "permission_name": permission_name,
                "module": module,
            },
        )
        created_list.append(permission)

    return created_list
