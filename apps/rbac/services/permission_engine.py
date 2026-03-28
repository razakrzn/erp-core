from __future__ import annotations

from typing import Any

from apps.rbac.models import RolePermission


def user_has_permission(user: Any, permission_code: str) -> bool:
    """
    Check whether the given user has the specified permission code.

    Superusers (Django is_superuser) are treated as having all permissions.
    Otherwise, this inspects role assignments via the `RolePermission` join model.
    """

    if not getattr(user, "pk", None):
        return False

    if getattr(user, "is_superuser", False):
        return True

    return RolePermission.objects.filter(
        role__assigned_users__user=user,
        permission__permission_code=permission_code,
    ).exists()


def get_user_permission_codes(user: Any) -> set[str]:
    """
    Return a set of all permission codes assigned to the user across all roles.
    """
    if not getattr(user, "pk", None):
        return set()

    if getattr(user, "is_superuser", False):
        # Superusers are handled in callers (is_superuser=True), so returning empty set
        # here is safe and saves a potentially large query.
        return set()

    return set(
        RolePermission.objects.filter(
            role__assigned_users__user=user,
        ).values_list("permission__permission_code", flat=True)
    )



