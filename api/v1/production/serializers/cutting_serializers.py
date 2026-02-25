import json

from rest_framework import serializers

from apps.production.models import CuttingOptimizationJob


class CuttingOptimizationJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuttingOptimizationJob
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "cad_file",
            "status",
            "stock_sheets",
            "extracted_parts",
            "optimization_result",
            "error_message",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "slug",
            "status",
            "extracted_parts",
            "optimization_result",
            "error_message",
            "created_at",
            "updated_at",
        ]

    def validate_cad_file(self, value):
        file_name = (value.name or "").lower()
        if not (file_name.endswith(".dxf") or file_name.endswith(".dwg")):
            raise serializers.ValidationError("Only .dxf or .dwg files are supported.")
        return value

    def validate_stock_sheets(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError("stock_sheets must be valid JSON.") from exc
        if value in (None, ""):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("stock_sheets must be a list.")
        return value
