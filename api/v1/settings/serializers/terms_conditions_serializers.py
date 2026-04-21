from rest_framework import serializers

from apps.settings.models import TermsConditions


class TermsConditionsBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsConditions
        fields = "__all__"


class TermsConditionsListSerializer(TermsConditionsBaseSerializer):
    class Meta:
        model = TermsConditions
        fields = [
            "id",
            "title",
            "category",
            "is_default",
        ]


class TermsConditionsDetailSerializer(TermsConditionsBaseSerializer):
    class Meta:
        model = TermsConditions
        fields = [
            "id",
            "title",
            "category",
            "content",
            "is_default",
        ]
