from rest_framework import serializers

from apps.assessment.models import Template, TemplateFinish


class TemplateDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ["id", "name"]


class TemplateFinishDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateFinish
        fields = ["id", "finish_name"]


class TemplateFinishSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateFinish
        fields = [
            "id",
            "template",
            "finish_name",
            "finish_type",
            "material",
            "design",
            "unit_price",
            "unit",
        ]


class TemplateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            "id",
            "name",
            "category",
            "created_at",
            "updated_at",
        ]


class TemplateDetailSerializer(serializers.ModelSerializer):
    finishes = TemplateFinishSerializer(many=True, read_only=True)

    class Meta:
        model = Template
        fields = [
            "id",
            "name",
            "category",
            "finishes",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["created_at", "updated_at", "created_by", "updated_by"]
