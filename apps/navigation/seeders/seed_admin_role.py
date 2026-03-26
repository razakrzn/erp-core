"""
Seed an "Admin" role for a company with all permissions from that company's enabled features.

Usage:
    # For a specific company (by id):
    from apps.navigation.seeders.seed_admin_role import run
    run(company_id=1)

    # From shell:
    python manage.py shell -c "from apps.navigation.seeders.seed_admin_role import run; run(company_id=1)"
"""

from __future__ import annotations

from django.db import transaction

from apps.company.models import Company, CompanyFeature
from apps.navigation.models import Permission
from apps.rbac.models import Role, RolePermission
from apps.rbac.services import role_service


ADMIN_ROLE_CODE = "admin"
ADMIN_ROLE_NAME = "Admin"


def _get_permission_codes_for_company(company_id: int) -> list[str]:
    """
    Return all permission codes from modules of features enabled for the company,
    excluding the special \"core\" feature.
    """
    enabled_feature_ids = CompanyFeature.objects.filter(
        company_id=company_id,
        is_enabled=True,
    ).exclude(
        feature__feature_code__iexact="core",
    ).values_list("feature_id", flat=True)

    return list(
        Permission.objects.filter(
            module__feature_id__in=enabled_feature_ids,
        ).values_list("permission_code", flat=True)
    )


@transaction.atomic
def run(company_id: int) -> Role:
    """
    Create or update the Admin role for the given company with all permissions
    from that company's enabled features.

    - If the Admin role does not exist, it is created with all permissions.
    - If it already exists, its permissions are replaced with all permissions
      from the company's enabled features (idempotent).

    Args:
        company_id: Company primary key.

    Returns:
        The Role instance (Admin for that company).

    Raises:
        Company.DoesNotExist: If company_id is invalid.
    """
    Company.objects.get(pk=company_id)

    permission_codes = _get_permission_codes_for_company(company_id)
    role = Role.objects.filter(
        company_id=company_id,
        role_code=ADMIN_ROLE_CODE,
    ).first()

    if role is None:
        role = role_service.create_role(
            company_id=company_id,
            role_name=ADMIN_ROLE_NAME,
            permission_codes=permission_codes,
            role_code=ADMIN_ROLE_CODE,
        )
    else:
        role_service.update_role(
            role_id=role.id,
            permission_codes=permission_codes,
        )
        role.refresh_from_db()

    return role
