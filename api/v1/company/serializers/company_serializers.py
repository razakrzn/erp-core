from rest_framework import serializers

from apps.company.models import Company


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for the Company model used by the v1 API.
    """

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "code",
            "address",
            "phone",
            "email",
            "website",
            "licence_number",
            "logo",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
