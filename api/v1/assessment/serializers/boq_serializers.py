from rest_framework import serializers

from apps.assessment.models import Boq, BoqItem


class BoqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boq
        fields = [
            "id",
            "enquiry",
            "boq_number",
            "is_approved",
            "is_rejected",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["boq_number", "created_at", "updated_at", "created_by", "updated_by"]


class BoqItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoqItem
        fields = [
            "id",
            "boq",
            "item_code",
            "name",
            "description",
            "quantity",
            "unit",
            "is_template",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["item_code", "created_at", "updated_at"]
