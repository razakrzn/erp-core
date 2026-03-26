from rest_framework import serializers
from apps.rbac.models import RolePermission


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer for RolePermission (role-permission link)."""

    role_name = serializers.ReadOnlyField(source="role.role_name")
    permission_name = serializers.ReadOnlyField(source="permission.permission_name")
    permission_code = serializers.ReadOnlyField(source="permission.permission_code")

    class Meta:
        model = RolePermission
        fields = ["id", "role", "role_name", "permission", "permission_name", "permission_code"]


class RolePermissionWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating RolePermission."""

    class Meta:
        model = RolePermission
        fields = ["role", "permission"]
