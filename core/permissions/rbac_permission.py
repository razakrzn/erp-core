from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.exceptions import PermissionDenied
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
        
        # If no explicit rule in database, try to deduce it from the view's permission_prefix
        if not permission_code:
            prefix = getattr(view, "permission_prefix", None)
            if prefix:
                # Map DRF actions/HTTP methods to permission suffixes
                action = getattr(view, "action", None)
                method = request.method.upper()
                
                suffix = "view" # Default
                if action == "create" or (not action and method == "POST"):
                    suffix = "create"
                elif action in ["update", "partial_update"] or (not action and method in ["PUT", "PATCH"]):
                    suffix = "edit"
                elif action == "destroy" or (not action and method == "DELETE"):
                    suffix = "delete"
                elif action in ["list", "retrieve"] or (not action and method == "GET"):
                    suffix = "view"
                
                permission_code = f"{prefix}.{suffix}"

        # If no specific permission is configured for this endpoint, deny access (Secure by Default).
        if not permission_code:
            # Superusers always have access even to unconfigured endpoints.
            if getattr(request.user, "is_superuser", False):
                return True
            # For everyone else, deny access if not explicitly configured.
            return False


        # Delegate to the RBAC engine (which handles caching & role logic).
        if not user_has_permission(request.user, permission_code):
            raise PermissionDenied(
                detail="You don't have permission to perform this action"
            )

        return True



