from __future__ import annotations

from typing import Optional

from apps.access_control.models import APIAccessRule


from django.urls import resolve, Resolver404

def match_api_rule(method: str, path: str) -> Optional[APIAccessRule]:
    """
    Return the active `APIAccessRule` matching the given HTTP method and path.

    This resolves the path to its pattern and looks for a rule matching
    that pattern. If no rule is found, `None` is returned.
    """
    try:
        match = resolve(path)
        route = match.route
    except Resolver404:
        return None

    return APIAccessRule.objects.filter(
        method=method,
        path=route,
        is_active=True,
    ).first()
