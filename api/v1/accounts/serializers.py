from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.rbac.models import Role, UserRole

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model used by the v1 API.
    Password is write-only and hashed on create/update.
    Optional role_id on create assigns the user to that role (same company enforced).
    """

    password = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
        min_length=6,
        help_text="Required on create. Min 6 characters. Optional on update.",
    )
    company_details = serializers.SerializerMethodField()
    role_details = serializers.SerializerMethodField()
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
        help_text="Optional role id to assign on user creation. Role must belong to the user's company.",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "company_details",
            "role_details",
            "role_id",
            "company",
        ]
        read_only_fields = [
            "id",
            "company_details",
            "role_details",
            "date_joined",
            "created_at",
        ]
        extra_kwargs = {"company": {"write_only": True}}
    
    def get_company_details(self, obj: User) -> dict[str, Any] | None:
        # 'obj' is the User instance
        if obj.company:
            return {
                "id": obj.company.id,
                "company_name": obj.company.name
            }
        return None

    def get_role_details(self, obj: User) -> dict[str, Any] | str | None:
        user_role = obj.user_roles.select_related("role").first()
        if user_role:
            return {
                "id": user_role.role.id,
                "role_name": user_role.role.role_name
            }
        if obj.is_superuser:
            return "Superuser"
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Superusers have no company; omit company_details from response
        if instance.is_superuser:
            data.pop("company_details", None)
        return data

    def create(self, validated_data):
        role = validated_data.pop("role_id", None)
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "This field is required when creating a user."})
        user = User.objects.create_user(password=password, **validated_data)
        if role is not None:
            user_company_id = getattr(user, "company_id", None)
            if user_company_id is not None and role.company_id != user_company_id:
                raise serializers.ValidationError(
                    {"role_id": "Role must belong to the same company as the user."}
                )
            UserRole.objects.get_or_create(user=user, role=role)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
