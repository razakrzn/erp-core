from rest_framework import serializers

from apps.navigation.models import Module
from .permission_serializers import PermissionSerializer


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for Module with nested permissions."""

    permissions = PermissionSerializer(many=True, read_only=True)
    feature_name = serializers.SlugRelatedField(
        slug_field="feature_name",
        read_only=True,
        source="feature",
    )

    class Meta:
        model = Module
        fields = [
            "id",
            "feature_name",
            "module_code",
            "module_name",
            "route",
            "icon",
            "order",
            "permissions",
        ]


class ModuleWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Module (no nested permissions)."""

    class Meta:
        model = Module
        fields = ["feature", "module_code", "module_name", "route", "icon", "order"]


class ModuleReadOnlySerializer(serializers.ModelSerializer):
    """Read-only serializer for Module: id, module_code, module_name only."""

    class Meta:
        model = Module
        fields = ["id", "module_code", "module_name"]
        read_only_fields = ["id", "module_code", "module_name"]


class CompanyModuleAccessSerializer(serializers.Serializer):
    """Validate company-level module access payloads."""

    feature_id = serializers.IntegerField(required=True, min_value=1)
    module_id = serializers.IntegerField(required=True, min_value=1)
