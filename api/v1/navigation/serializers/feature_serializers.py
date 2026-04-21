from rest_framework import serializers

from apps.navigation.models import Feature
from .module_serializers import ModuleSerializer


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


class FeatureWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Feature (no nested modules)."""

    class Meta:
        model = Feature
        fields = ["feature_code", "feature_name", "icon", "order"]


class FeatureReadOnlySerializer(serializers.ModelSerializer):
    """Read-only serializer for Feature: id, feature_code, feature_name only."""

    class Meta:
        model = Feature
        fields = ["id", "feature_code", "feature_name"]
        read_only_fields = ["id", "feature_code", "feature_name"]
