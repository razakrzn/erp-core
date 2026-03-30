from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from apps.access_control.services.api_access_service import get_required_permission
from apps.rbac.services.permission_engine import user_has_permission


if TYPE_CHECKING:  # pragma: no cover - type-checking only
    from rest_framework.request import Request


class IsSuperuser(BasePermission):
    """Allow access only to superusers."""

    def has_permission(self, request: "Request", view: Any) -> bool:
        return bool(getattr(request.user, "is_superuser", False))


class RBACPermission(BasePermission):
    """
    Global RBAC permission class for the API.

    For each request, this class:
    1. Resolves the required permission code via the API access service.
    2. If no rule is defined, allows the request.
    3. Otherwise, asks the RBAC permission engine whether the user has it.
    """

    @staticmethod
    def _normalize_prefixes(prefix: Any) -> list[str]:
        if not prefix:
            return []
        if isinstance(prefix, str):
            return [prefix]
        if isinstance(prefix, (list, tuple, set)):
            return [p for p in prefix if isinstance(p, str) and p]
        return []

    @staticmethod
    def _resolve_action_suffix(request: "Request", view: Any) -> str:
        # Map DRF actions/HTTP methods to permission suffixes.
        action = getattr(view, "action", None)
        method = request.method.upper()

        if action == "create" or (not action and method == "POST"):
            return "create"
        if action in ["update", "partial_update"] or (not action and method in ["PUT", "PATCH"]):
            return "edit"
        if action == "destroy" or (not action and method == "DELETE"):
            return "delete"
        return "view"

    def has_permission(self, request: "Request", view: Any) -> bool:
        permission_code = get_required_permission(request)
        candidate_codes: list[str] = []
        prefixes = self._normalize_prefixes(getattr(view, "permission_prefix", None))
        suffix = self._resolve_action_suffix(request, view)

        # Always consider view-derived prefixes (single or multiple), so views can
        # intentionally support aliases such as ["core.roles", "hr.roles"].
        if prefixes:
            candidate_codes.extend([f"{prefix}.{suffix}" for prefix in prefixes])

        # If an explicit API rule exists, include it as an additional candidate.
        if permission_code:
            candidate_codes.insert(0, permission_code)

        # De-duplicate while preserving order.
        candidate_codes = list(dict.fromkeys(candidate_codes))

        # If no specific permission is configured for this endpoint, deny access (Secure by Default).
        if not candidate_codes:
            # Superusers always have access even to unconfigured endpoints.
            if getattr(request.user, "is_superuser", False):
                return True
            # For everyone else, deny access if not explicitly configured.
            return False

        # Delegate to the RBAC engine (which handles caching & role logic).
        if not any(user_has_permission(request.user, code) for code in candidate_codes):
            raise PermissionDenied(detail="You don't have permission to perform this action")

        return True
