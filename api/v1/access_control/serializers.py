from rest_framework import serializers
from apps.access_control.models import APIAccessRule

class APIAccessRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIAccessRule
        fields = [
            "id",
            "name",
            "method",
            "path",
            "permission_code",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
