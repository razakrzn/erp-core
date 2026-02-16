from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model used by the v1 API.
    Password is write-only and hashed on create/update.
    """

    password = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
        min_length=6,
        help_text="Required on create. Min 6 characters. Optional on update.",
    )
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "company",
            "first_name",
            "last_name",
            "role_name",
        ]
        read_only_fields = [
            "id",
            "date_joined",
            "created_at",
        ]

    def get_role_name(self, obj):
        user_role = obj.user_roles.select_related("role").first()
        if user_role:
            return user_role.role.role_name
        if obj.is_superuser:
            return "Superuser"
        return None

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError({"password": "This field is required when creating a user."})
        user = User.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance