from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCompanyAdminOrReadOnly(BasePermission):
    """
    Example permission for Company endpoints.

    - Allows all users to perform safe (read-only) requests.
    - Requires authenticated staff user for write operations.

    Adapt this to your RBAC model later (e.g. using apps.rbac).
    """

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        return bool(user and user.is_authenticated and user.is_staff)
