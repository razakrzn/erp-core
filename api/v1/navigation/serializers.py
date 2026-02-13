from __future__ import annotations

from rest_framework import serializers

from apps.navigation.models import Feature, Module, Permission


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for navigation Permission (used by RBAC)."""

    class Meta:
        model = Permission
        fields = ["id", "permission_code", "permission_name"]


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for Module with nested permissions."""

    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = [
            "id",
            "module_code",
            "module_name",
            "route",
            "icon",
            "order",
            "permissions",
        ]


class FeatureSerializer(serializers.ModelSerializer):
    """Serializer for Feature with nested modules (and their permissions)."""

    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Feature
        fields = [
            "id",
            "feature_code",
            "feature_name",
            "icon",
            "order",
            "modules",
        ]


class SidebarModuleSerializer(serializers.Serializer):
    """Minimal module payload for sidebar (e.g. from sidebar_builder)."""

    module_code = serializers.CharField()
    module_name = serializers.CharField()
    route = serializers.CharField(allow_null=True)
    icon = serializers.CharField(allow_null=True)


class SidebarFeatureSerializer(serializers.Serializer):
    """Minimal feature payload for sidebar with nested modules."""

    feature_code = serializers.CharField()
    feature_name = serializers.CharField()
    icon = serializers.CharField(allow_null=True)
    modules = SidebarModuleSerializer(many=True)
