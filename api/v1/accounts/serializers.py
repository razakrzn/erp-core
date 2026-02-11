from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model used by the v1 API.
    """

    class Meta:
        model = User
        # Adjust the fields list to match what you want exposed via the API
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name"
        ]
        read_only_fields = [
            "id",
            "date_joined",
            "created_at",
        ]