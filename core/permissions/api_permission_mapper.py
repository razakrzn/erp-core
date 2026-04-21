from __future__ import annotations

from typing import Optional

from rest_framework.request import Request

from apps.access_control.models import APIAccessRule


def get_required_permission(request: Request) -> Optional[str]:
    """
    Resolve the permission code required for the given API request.

    This looks up an `APIAccessRule` using the request's HTTP method and path.
    If no rule matches, `None` is returned, signalling that no explicit
    permission check is required for this endpoint.
    """
    rule = (
        APIAccessRule.objects.filter(
            method=request.method,
            path=request.path_info,  # normalized path without script prefix
        )
        .only("permission_code")
        .first()
    )

    return rule.permission_code if rule else None
