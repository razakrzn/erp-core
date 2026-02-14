from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.permissions import BasePermission

from apps.access_control.services.api_access_service import get_required_permission


if TYPE_CHECKING:  # pragma: no cover - type-checking only
    from rest_framework.request import Request


class IsSuperuser(BasePermission):
    """Allow access only to superusers."""

    def has_permission(self, request: "Request", view: Any) -> bool:
        return bool(getattr(request.user, "is_superuser", False))


from apps.rbac.services.permission_engine import user_has_permission


class RBACPermission(BasePermission):
    """
    Global RBAC permission class for the API.

    For each request, this class:
    1. Resolves the required permission code via the API access service.
    2. If no rule is defined, allows the request.
    3. Otherwise, asks the RBAC permission engine whether the user has it.
    """

    def has_permission(self, request: "Request", view: Any) -> bool:
        permission_code = get_required_permission(request)

        # If no specific permission is configured for this endpoint, allow access.
        if not permission_code:
            return True

        # Delegate to the RBAC engine (which handles caching & role logic).
        return bool(user_has_permission(request.user, permission_code))
