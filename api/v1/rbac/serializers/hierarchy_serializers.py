from rest_framework import serializers
from apps.rbac.models import RoleHierarchy


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
