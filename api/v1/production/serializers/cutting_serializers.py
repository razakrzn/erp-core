import json

from rest_framework import serializers

from apps.production.models import CuttingOptimizationJob
from apps.production.services import validate_cad_file_name


class CuttingOptimizationJobListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view: fewer fields, error_message only when present."""

    class Meta:
        model = CuttingOptimizationJob
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "cad_file",
            "status",
            "error_message",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get("error_message"):
            data.pop("error_message", None)
        return data


class CuttingOptimizationJobSerializer(serializers.ModelSerializer):
    cad_reupload_required = serializers.SerializerMethodField()

    class Meta:
        model = CuttingOptimizationJob
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "cad_file",
            "cad_reupload_required",
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
        is_valid, error_message = validate_cad_file_name(value.name or "")
        if not is_valid and error_message:
            raise serializers.ValidationError(error_message)
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

    def validate(self, attrs):
        if self.instance is None and not attrs.get("cad_file"):
            raise serializers.ValidationError({"cad_file": "This field is required."})
        return attrs

    def get_cad_reupload_required(self, obj: CuttingOptimizationJob) -> bool:
        if not obj.cad_file:
            return True
        is_valid, _ = validate_cad_file_name(obj.cad_file.name or "")
        return not is_valid
