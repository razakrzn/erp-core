from __future__ import annotations

from rest_framework.request import Request


def _get_company_id(request: Request, kwargs: dict) -> int | None:
    """Company from current user's company only (request.user.company_id)."""
    if not getattr(request, "user", None) or not getattr(request.user, "is_authenticated", False):
        return None
    if request.user.is_superuser:
        return None

    if not hasattr(request.user, "company_id"):
        return None
    return request.user.company_id
