from rest_framework import serializers

from apps.rbac.models import UserRole


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
