from rest_framework import serializers

from apps.navigation.models import Feature, Module
from .permission_serializers import PermissionSerializer


class SeederModuleSerializer(serializers.ModelSerializer):
    """Module payload shaped like the navigation seed structure."""

    code = serializers.CharField(source="module_code")
    name = serializers.CharField(source="module_name")
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["code", "name", "route", "icon", "order", "permissions"]


class SeederFeatureSerializer(serializers.ModelSerializer):
    """Feature payload shaped like the navigation seed structure."""

    modules = SeederModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Feature
        fields = ["feature_code", "feature_name", "icon", "order", "modules"]
