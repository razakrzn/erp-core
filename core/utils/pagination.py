# utils/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.utils import timezone

class IndustrialPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        """
        Store the view to access permission_prefix in get_paginated_response.
        """
        self.view = view
        return super().paginate_queryset(queryset, request, view)

    def _get_user_permissions(self, user, prefix):
        """
        Helper to fetch and filter permissions for the user based on a prefix.
        """
        from apps.rbac.models import UserRole, RolePermission
        if not user or not user.is_authenticated or not prefix:
            return []

        try:
            # Get IDs of roles assigned to the user
            user_role_ids = UserRole.objects.filter(user=user).values_list('role_id', flat=True)
            if not user_role_ids:
                return []

            # Filter permissions starting with the specified prefix matching {prefix}.*
            # Ensuring it matches crm.customers.view and not crm.customers_other.view
            role_permissions = RolePermission.objects.filter(
                role_id__in=user_role_ids,
                permission__permission_code__startswith=f"{prefix}."
            ).select_related('permission').distinct('permission__permission_code')

            return [
                {
                    "id": rp.permission.id,
                    "permission_name": rp.permission.permission_name,
                    "permission_code": rp.permission.permission_code
                }
                for rp in role_permissions
            ]
        except Exception:
            # Return empty array on failure for API stability
            return []

    def get_paginated_response(self, data):
        user_permissions = []
        actions = {
            "canCreate": False,
            "canEdit": False,
            "canDelete": False,
            "canView": False
        }
        
        user = self.request.user
        
        # Check if the view provides a permission prefix for enrichment
        if hasattr(self, 'view') and self.view:
            prefix = getattr(self.view, 'permission_prefix', None)
            if prefix:
                if user and user.is_authenticated and user.is_superuser:
                    actions = {
                        "canCreate": True,
                        "canEdit": True,
                        "canDelete": True,
                        "canView": True
                    }
                else:
                    user_permissions = self._get_user_permissions(user, prefix)
                    # Transform to actions object for easier frontend consumption
                    for perm in user_permissions:
                        code = perm.get("permission_code", "").lower()
                        if code.endswith(".create") or code.endswith(".add"):
                            actions["canCreate"] = True
                        elif code.endswith(".edit") or code.endswith(".change") or code.endswith(".update"):
                            actions["canEdit"] = True
                        elif code.endswith(".delete"):
                            actions["canDelete"] = True
                        elif code.endswith(".view") or code.endswith(".list"):
                            actions["canView"] = True

        return Response({
            "success": True,
            "message": "Data retrieved successfully",
            "data": {
                "items": data,
                "actions": actions,
                "pagination": {
                    "count": self.page.paginator.count,
                    "total_pages": self.page.paginator.num_pages,
                    "current_page": self.page.number,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                }
            },
            "status_code": 200,
            "timestamp": timezone.now().isoformat(),
        })