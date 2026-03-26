"""
RBAC API serializers (roles, role permissions, user roles, role hierarchy).
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.navigation.models import Permission
from apps.rbac.models import Role, RolePermission, RoleHierarchy, UserRole

User = get_user_model()


# ----- Role -----


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role (read, with nested role_permissions)."""

    class Meta:
        model = Role
        fields = [
            "id",
            "role_name",
            "role_code",
            "description",
            "is_active",
            "created_at",
        ]


class RoleWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Role (optional permissions on create and PUT/PATCH)."""

    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False,
        write_only=True,
        help_text="Optional list of permission IDs to assign on create or replace on update (PUT/PATCH).",
    )

    class Meta:
        model = Role
        fields = ["role_name", "role_code", "description", "is_active", "permissions"]

    def validate_role_code(self, value: str) -> str:
        company_id = self.context.get("company_id")
        if company_id is None:
            return value
        qs = Role.objects.filter(company_id=company_id, role_code=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A role with this code already exists for your company."
            )
        return value

    def create(self, validated_data: dict) -> Role:
        validated_data["company_id"] = self.context["company_id"]
        permission_list = validated_data.pop("permissions", [])
        instance = super().create(validated_data)
        if permission_list:
            RolePermission.objects.bulk_create(
                [RolePermission(role=instance, permission=p) for p in permission_list],
                ignore_conflicts=True,
            )
        return instance

    def update(self, instance: Role, validated_data: dict) -> Role:
        permission_list = validated_data.pop("permissions", None)
        instance = super().update(instance, validated_data)
        if permission_list is not None:
            RolePermission.objects.filter(role=instance).delete()
            if permission_list:
                RolePermission.objects.bulk_create(
                    [RolePermission(role=instance, permission=p) for p in permission_list],
                    ignore_conflicts=True,
                )
        return instance


class RoleDetailSerializer(serializers.ModelSerializer):
    """Serializer for Role detail with nested role_permission ids."""

    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "role_name",
            "role_code",
            "description",
            "is_active",
            "created_at",
            "permissions",
        ]

    def get_permissions(self, obj: Role) -> list[dict]:
        return [
            {"id": rp.permission_id, "permission_name": rp.permission.permission_name, "permission_code": rp.permission.permission_code}
            for rp in obj.role_permissions.select_related("permission").all()
        ]


# ----- RolePermission -----


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer for RolePermission (role–permission link)."""

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


# ----- UserRole -----


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserRole list/create: user full name and role_name."""

    user_full_name = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = UserRole
        fields = ["id", "user_full_name", "role_name", "assigned_at"]

    def get_user_full_name(self, obj: UserRole) -> str:
        u = obj.user
        parts = [u.first_name or "", u.last_name or ""]
        return " ".join(p for p in parts if p).strip() or u.username or str(u.id)

    def get_role_name(self, obj: UserRole) -> str:
        return obj.role.role_name if obj.role else ""


class UserRoleDetailsSerializer(serializers.ModelSerializer):
    """Serializer for UserRole detail: full user details and role details."""

    user_details = serializers.SerializerMethodField()
    role_details = serializers.SerializerMethodField()

    class Meta:
        model = UserRole
        fields = ["id", "assigned_at", "user_details", "role_details"]

    def get_user_details(self, obj: UserRole) -> dict:
        u = obj.user
        if not u:
            return None
        first = u.first_name or ""
        last = u.last_name or ""
        full_name = " ".join(p for p in [first, last] if p).strip() or u.username or ""
        return {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "full_name": full_name,
        }

    def get_role_details(self, obj: UserRole) -> dict:
        r = obj.role
        if not r:
            return None
        return {
            "id": r.id,
            "role_name": r.role_name,
            "role_code": r.role_code,
            "description": r.description,
            "is_active": r.is_active,
        }


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
