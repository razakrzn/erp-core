from __future__ import annotations

from typing import Iterable, List, Sequence

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from apps.company.models import Company
from apps.navigation.models import Permission
from apps.rbac.models import Role, RolePermission, UserRole

User = get_user_model()


def _generate_role_code(role_name: str) -> str:
    """
    Generate a simple code from the role name (e.g. 'Admin User' -> 'ADMIN_USER').
    """
    return "_".join(part for part in role_name.upper().split() if part)


@transaction.atomic
def create_role(
    company_id: int,
    role_name: str,
    permission_codes: Iterable[str] | None = None,
    role_code: str | None = None,
) -> Role:
    """
    Create a new role for a company and optionally attach permissions.
    """
    company = Company.objects.get(id=company_id)

    if role_code is None:
        role_code = _generate_role_code(role_name)

    if Role.objects.filter(company=company, role_code=role_code).exists():
        raise ValidationError("Role with this code already exists for the company.")

    role = Role.objects.create(
        role_name=role_name,
        role_code=role_code,
        company=company,
    )

    if permission_codes:
        permissions = list(Permission.objects.filter(permission_code__in=list(permission_codes)))
        role_permissions: List[RolePermission] = [RolePermission(role=role, permission=perm) for perm in permissions]
        RolePermission.objects.bulk_create(role_permissions, ignore_conflicts=True)

    return role


@transaction.atomic
def update_role(
    role_id: int,
    role_name: str | None = None,
    permission_codes: Iterable[str] | None = None,
) -> Role:
    """
    Update an existing role's name and/or its permissions.
    """
    role = Role.objects.get(id=role_id)

    if role_name:
        role.role_name = role_name
        role.save(update_fields=["role_name"])

    if permission_codes is not None:
        # Reset the role's permissions to match the provided codes.
        RolePermission.objects.filter(role=role).delete()
        permissions = list(Permission.objects.filter(permission_code__in=list(permission_codes)))
        role_permissions: List[RolePermission] = [RolePermission(role=role, permission=perm) for perm in permissions]
        RolePermission.objects.bulk_create(role_permissions, ignore_conflicts=True)

    return role


def assign_user_to_role(user_id: int, role_id: int) -> bool:
    """
    Assign a user to a role. No-op if the assignment already exists.
    """
    user = User.objects.get(id=user_id)
    role = Role.objects.get(id=role_id)

    UserRole.objects.get_or_create(user=user, role=role)
    return True


def remove_user_role(user_id: int, role_id: int) -> bool:
    """
    Remove a role assignment from a user.
    """
    UserRole.objects.filter(
        user_id=user_id,
        role_id=role_id,
    ).delete()

    return True


def get_role_permissions(role_id: int) -> Sequence[dict]:
    """
    Return the permissions attached to a role as a list of dicts.
    """
    role = Role.objects.get(id=role_id)

    return Permission.objects.filter(
        role_permissions__role=role,
    ).values(
        "permission_code",
        "permission_name",
    )


def get_company_roles(company_id: int) -> Sequence[dict]:
    """
    List roles for a given company with minimal fields.
    """
    return Role.objects.filter(company_id=company_id).values(
        "id",
        "role_name",
        "role_code",
    )
