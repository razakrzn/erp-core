from __future__ import annotations

from typing import Optional

from apps.access_control.models import APIAccessRule


def match_api_rule(method: str, path: str) -> Optional[APIAccessRule]:
    """
    Return the active `APIAccessRule` matching the given HTTP method and path.

    This performs an exact match on both fields; if no rule is found, `None`
    is returned.
    """
    return APIAccessRule.objects.filter(
        method=method,
        path=path,
        is_active=True,
    ).first()
