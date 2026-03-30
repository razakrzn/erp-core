from __future__ import annotations

from typing import Any, Dict, List, Optional
from django.core.cache import cache
from django.db.models import Prefetch

from apps.company.models import Company, CompanyFeature
from apps.navigation.models import Feature, Module
from apps.rbac.services.permission_engine import get_user_permission_codes


def build_sidebar(user: Any, company: Optional[Company] = None) -> List[Dict[str, Any]]:
    """
    Build a sidebar configuration for the given user and company.
    Optimized with prefetching and caching.
    """
    is_superuser = getattr(user, "is_superuser", False)
    company_id = company.id if company else "no_company"
    cache_key = f"sidebar_{user.id}_{company_id}"

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

        if not enabled_feature_ids:
            return []

        features_qs = Feature.objects.filter(id__in=enabled_feature_ids)

    # 2. Fetch all features, modules, and permissions in minimal queries.
    features = features_qs.prefetch_related(module_prefetch).order_by("order", "feature_name")

    # 3. Efficiently fetch user's permissions once.
    user_permissions: set[str] = get_user_permission_codes(user)
    sidebar: List[Dict[str, Any]] = []

    # 4. Process in memory
    for feature in features:
        # Superuser feature check
        if feature.feature_code.lower() == "superuser" and not is_superuser:
            continue

        module_list: List[Dict[str, Any]] = []
        # Calling .all() here uses the prefetch cache, preserving order from Prefetch queryset
        for module in feature.modules.all():
            # Check permissions
            module_perms = {p.permission_code for p in module.permissions.all()}
            if is_superuser or (module_perms & user_permissions):
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
