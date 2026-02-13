from __future__ import annotations

"""
Lightweight caching helpers for RBAC permission codes.

This module is intentionally dumb: it only knows how to cache and invalidate
sets of permission codes for a given (user, company) pair. The logic for
actually *computing* those permissions lives in `apps.rbac.services.role_service`.
"""

from typing import Iterable, Optional, Set

from django.conf import settings
from django.core.cache import cache


DEFAULT_TTL_SECONDS: int = getattr(
    settings,
    "RBAC_PERMISSION_CACHE_TIMEOUT",
    60 * 10,  # 10 minutes
)

CACHE_PREFIX: str = getattr(
    settings,
    "RBAC_PERMISSION_CACHE_PREFIX",
    "rbac:perms",
)


def _make_cache_key(user_id: int | str, company_id: Optional[int | str]) -> str:
    """
    Build a tenant-aware cache key for a user's permissions.
    """
    tenant_part = company_id if company_id is not None else "none"
    return f"{CACHE_PREFIX}:u:{user_id}:c:{tenant_part}"


def get_cached_permissions(
    user_id: int | str,
    company_id: Optional[int | str] = None,
) -> Optional[Set[str]]:
    """
    Return the cached set of permission codes for a user/company pair, if any.
    """
    key = _make_cache_key(user_id, company_id)
    value = cache.get(key)
    if value is None:
        return None
    return set(value)


def set_cached_permissions(
    user_id: int | str,
    company_id: Optional[int | str],
    permissions: Iterable[str],
    ttl: int = DEFAULT_TTL_SECONDS,
) -> None:
    """
    Cache the given permission codes for a user/company pair.
    """
    key = _make_cache_key(user_id, company_id)
    cache.set(key, list(set(permissions)), ttl)


def invalidate_cached_permissions(
    user_id: int | str,
    company_id: Optional[int | str] = None,
) -> None:
    """
    Invalidate cached permissions for a user/company pair.

    Note: this only clears the exact key; if you use multiple company scopes
    per user, call this once per scope as needed.
    """
    key = _make_cache_key(user_id, company_id)
    cache.delete(key)

