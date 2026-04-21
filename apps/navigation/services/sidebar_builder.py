from __future__ import annotations

from typing import Any, Dict, List, Optional
from django.core.cache import cache
from django.db.models import Prefetch

from apps.company.models import Company, CompanyFeature
from apps.company.services import get_company_disabled_module_ids
from apps.navigation.models import Feature, Module
from apps.rbac.services.permission_engine import get_user_permission_codes


SIDEBAR_CACHE_VERSION = 4

# Legacy typo compatibility for permission namespaces used in existing roles.
PERMISSION_CODE_ALIASES = {
    "settings.termsandcondtions.": "settings.terms_conditions.",
    "settings.terms_conditions.": "settings.termsandcondtions.",
}


def _expand_permission_codes(permission_codes: set[str]) -> set[str]:
    """
    Expand permission codes with known legacy aliases so sidebar visibility
    keeps working while stored role permissions are being normalized.
    """
    expanded_codes = set(permission_codes)

    for permission_code in permission_codes:
        for source_prefix, target_prefix in PERMISSION_CODE_ALIASES.items():
            if permission_code.startswith(source_prefix):
                expanded_codes.add(permission_code.replace(source_prefix, target_prefix, 1))

    return expanded_codes


def build_sidebar(user: Any, company: Optional[Company] = None) -> List[Dict[str, Any]]:
    """
    Build a sidebar configuration for the given user and company.
    Optimized with prefetching and caching.
    """
    is_superuser = getattr(user, "is_superuser", False)
    company_id = company.id if company else "no_company"
    cache_key = f"sidebar_v{SIDEBAR_CACHE_VERSION}_{user.id}_{company_id}"

    # Try to get from cache first
    try:
        cached_sidebar = cache.get(cache_key)
        if cached_sidebar is not None:
            return cached_sidebar
    except Exception:
        # Fallback to DB if Redis is down
        pass

    # 1. Prepare base query with efficient prefetching of modules and permissions.
    # We use Prefetch objects to ensure ordering is preserved without breaking the prefetch cache.
    module_prefetch = Prefetch(
        "modules", queryset=Module.objects.all().order_by("order", "module_name").prefetch_related("permissions")
    )

    user_permissions: set[str] = get_user_permission_codes(user)
    effective_user_permissions = _expand_permission_codes(user_permissions)
    disabled_module_ids: set[int] = set()

    if company is None:
        if not is_superuser:
            return []
        features_qs = Feature.objects.all()
    else:
        enabled_feature_ids = list(
            CompanyFeature.objects.filter(
                company=company,
                is_enabled=True,
            ).values_list("feature_id", flat=True)
        )
        disabled_module_ids = get_company_disabled_module_ids(company.id, enabled_feature_ids)

        if not enabled_feature_ids:
            return []

        features_qs = Feature.objects.filter(id__in=enabled_feature_ids).distinct()

    # 2. Fetch all features, modules, and permissions in minimal queries.
    features = features_qs.prefetch_related(module_prefetch).order_by("order", "feature_name")

    sidebar: List[Dict[str, Any]] = []

    # 4. Process in memory
    for feature in features:
        # Superuser feature check
        feature_code = feature.feature_code.lower()
        if feature_code == "superuser" and not is_superuser:
            continue
        if feature_code == "core" and not is_superuser:
            continue

        module_list: List[Dict[str, Any]] = []
        # Calling .all() here uses the prefetch cache, preserving order from Prefetch queryset
        for module in feature.modules.all():
            if company is not None and module.id in disabled_module_ids:
                continue
            # Check permissions
            module_perms = {p.permission_code for p in module.permissions.all()}
            if is_superuser or (module_perms & effective_user_permissions):
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

    # Cache for 10 minutes (600 seconds)
    try:
        cache.set(cache_key, sidebar, 600)
    except Exception:
        pass
    return sidebar
