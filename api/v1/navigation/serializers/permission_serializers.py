from rest_framework import serializers
from apps.navigation.models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for navigation Permission (used by RBAC)."""

    module_name = serializers.SlugRelatedField(
        slug_field="module_name",
        read_only=True,
        source="module",
    )

    class Meta:
        model = Permission
        fields = ["id", "module_name", "permission_code", "permission_name"]


class PermissionWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Permission."""

    class Meta:
        model = Permission
        fields = ["module", "permission_code", "permission_name"]
