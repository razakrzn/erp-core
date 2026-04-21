from __future__ import annotations

from collections.abc import Iterable

from apps.company.models import CompanyModule


def get_company_module_access_overrides(
    company_id: int,
    feature_ids: Iterable[int] | None = None,
) -> dict[int, bool]:
    """
    Return explicit module access overrides keyed by module id for a company.

    Modules are implicitly enabled when their parent feature is enabled, so only
    explicit overrides are persisted.
    """

    queryset = CompanyModule.objects.filter(company_id=company_id)
    if feature_ids is not None:
        queryset = queryset.filter(module__feature_id__in=list(feature_ids))
    return dict(queryset.values_list("module_id", "is_enabled"))


def get_company_disabled_module_ids(
    company_id: int,
    feature_ids: Iterable[int] | None = None,
) -> set[int]:
    """
    Return module ids explicitly disabled for a company.
    """

    queryset = CompanyModule.objects.filter(
        company_id=company_id,
        is_enabled=False,
    )
    if feature_ids is not None:
        queryset = queryset.filter(module__feature_id__in=list(feature_ids))
    return set(queryset.values_list("module_id", flat=True))
