"""
Auth serializers for login and token refresh.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """
    Validates username and password for login.
    """

    username = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password,
        )
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs
