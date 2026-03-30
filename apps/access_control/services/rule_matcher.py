from __future__ import annotations

from typing import Optional

from apps.access_control.models import APIAccessRule
from django.db import models


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
        # Normalize route: remove regex markers often found in match.route
        route = route.replace("^", "").replace("$", "")
    except Resolver404:
        return None

    # Normalize the route to match how it's stored in the database.
    # We check for both the raw route and the route with a leading slash.
    return (
        APIAccessRule.objects.filter(
            method=method,
            is_active=True,
        )
        .filter(models.Q(path=route) | models.Q(path=f"/{route}"))
        .first()
    )
