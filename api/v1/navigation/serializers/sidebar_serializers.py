from rest_framework import serializers


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
