import json

from rest_framework import serializers

from apps.production.models import CuttingOptimizationJob


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
            "cutlist_pdf_file",
            "cutlist_xlsx_file",
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
            "cutlist_pdf_file",
            "cutlist_xlsx_file",
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
            "cutlist_pdf_file",
            "cutlist_xlsx_file",
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

    def validate(self, attrs):
        if self.instance is None and not attrs.get("cad_file"):
            raise serializers.ValidationError({"cad_file": "This field is required."})
        return attrs

    def get_cad_reupload_required(self, obj: CuttingOptimizationJob) -> bool:
        if not obj.cad_file:
            return True
        lower_name = (obj.cad_file.name or "").lower()
        return not (lower_name.endswith(".dxf") or lower_name.endswith(".dwg"))
