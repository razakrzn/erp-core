from rest_framework import serializers

from apps.company.models import Company, CompanyUser

from ..accounts.serializers import UserSerializer


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
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CompanyUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CompanyUser model used by the v1 API.

    Exposes the related user and company via their primary keys while also
    providing nested, read-only detail representations.
    """

    user_detail = UserSerializer(source="user", read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)
    company_code = serializers.CharField(source="company.code", read_only=True)

    class Meta:
        model = CompanyUser
        fields = [
            "id",
            "company",
            "user",
            "is_owner",
            "created_at",
            "user_detail",
            "company_name",
            "company_code",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "user_detail",
            "company_name",
            "company_code",
        ]

