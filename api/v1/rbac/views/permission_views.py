from apps.rbac.models import RolePermission

from ..serializers import RolePermissionSerializer, RolePermissionWriteSerializer
from .shared import BaseRBACViewSet


class RolePermissionViewSet(BaseRBACViewSet):
    queryset = RolePermission.objects.select_related("role", "permission").order_by("role", "permission")
    serializer_class = RolePermissionSerializer
    permission_prefix = ["core.roles", "hr.roles"]

    def get_queryset(self):
        queryset = super().get_queryset()

        role_id = self.request.query_params.get("role_id")
        if role_id is not None:
            queryset = queryset.filter(role_id=role_id)

        permission_id = self.request.query_params.get("permission_id")
        if permission_id is not None:
            queryset = queryset.filter(permission_id=permission_id)

        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return RolePermissionWriteSerializer
        return RolePermissionSerializer
