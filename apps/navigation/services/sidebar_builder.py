from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from apps.company.models import Company, CompanyFeature
from apps.navigation.models import Feature, Module
from apps.rbac.services.permission_engine import user_has_permission


def build_sidebar(user: Any, company: Optional[Company] = None) -> List[Dict[str, Any]]:
    """
    Build a sidebar configuration for the given user and company.

    Only features enabled for the company and modules for which the user has
    at least one permission are included in the result.

    When company is None and user is a superuser, all features are listed
    without company-based filtering.
    """
    is_superuser = getattr(user, "is_superuser", False)

    if company is None:
        if not is_superuser:
            return []
        # Superuser without company: list all features (no company filtering)
        features = (
            Feature.objects.all()
            .prefetch_related("modules__permissions")
            .order_by("order", "feature_name")
        )
    else:
        enabled_feature_ids: Sequence[int] = list(
            CompanyFeature.objects.filter(
                company=company,
                is_enabled=True,
            ).values_list("feature_id", flat=True)
        )

        if not enabled_feature_ids:
            return []

        features = (
            Feature.objects.filter(id__in=enabled_feature_ids)
            .prefetch_related("modules__permissions")
            .order_by("order", "feature_name")
        )

    sidebar: List[Dict[str, Any]] = []

    for feature in features:
        # Superuser feature is visible only to superusers.
        if feature.feature_code.lower() == "superuser" and not is_superuser:
            continue
        modules: Sequence[Module] = feature.modules.all().order_by("order", "module_name")
        module_list: List[Dict[str, Any]] = []

        for module in modules:
            # User has access to the module if they have any of its permissions.
            has_access = any(
                user_has_permission(user, perm.permission_code)
                for perm in module.permissions.all()
            )

            if has_access:
                module_list.append(
                    {
                        "module_name": module.module_name,
                        "module_code": module.module_code,
                        "route": module.route,
                        "icon": module.icon,
                    }
                )

        if module_list:
            sidebar.append(
                {
                    "feature_name": feature.feature_name,
                    "feature_code": feature.feature_code,
                    "icon": feature.icon,
                    "modules": module_list,
                }
            )

    return sidebar
