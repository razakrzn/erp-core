"""
RBAC API serializers (roles, role permissions, user roles, role hierarchy).
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.rbac.models import Role, RolePermission, RoleHierarchy, UserRole

User = get_user_model()


# ----- Role -----


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role (read, with nested role_permissions)."""

    class Meta:
        model = Role
        fields = [
            "id",
            "company",
            "role_name",
            "role_code",
            "description",
            "is_active",
            "created_at",
        ]


class RoleWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Role."""

    class Meta:
        model = Role
        fields = ["company", "role_name", "role_code", "description", "is_active"]


class RoleDetailSerializer(serializers.ModelSerializer):
    """Serializer for Role detail with nested role_permission ids."""

    role_permission_ids = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "company",
            "role_name",
            "role_code",
            "description",
            "is_active",
            "created_at",
            "role_permission_ids",
        ]

    def get_role_permission_ids(self, obj: Role) -> list[int]:
        return list(obj.role_permissions.values_list("permission_id", flat=True))


# ----- RolePermission -----


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer for RolePermission (role–permission link)."""

    class Meta:
        model = RolePermission
        fields = ["id", "role", "permission"]


class RolePermissionWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating RolePermission."""

    class Meta:
        model = RolePermission
        fields = ["role", "permission"]


# ----- UserRole -----


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserRole (user–role assignment)."""

    class Meta:
        model = UserRole
        fields = ["id", "user", "role", "assigned_at"]


class UserRoleWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating UserRole."""

    class Meta:
        model = UserRole
        fields = ["user", "role"]


# ----- RoleHierarchy -----


class RoleHierarchySerializer(serializers.ModelSerializer):
    """Serializer for RoleHierarchy (parent–child role)."""

    class Meta:
        model = RoleHierarchy
        fields = ["id", "parent_role", "child_role"]


class RoleHierarchyWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating RoleHierarchy."""

    class Meta:
        model = RoleHierarchy
        fields = ["parent_role", "child_role"]
