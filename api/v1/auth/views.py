"""
Auth API views: login and refresh token.
"""
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from drf_spectacular.utils import extend_schema

from core.utils.responses import APIResponse

from .serializers import LoginSerializer
from api.v1.accounts.serializers import UserSerializer


class LoginView(APIView):
    """
    POST /api/v1/auth/login/
    Body: { "username": "...", "password": "..." }
    Returns: { "data": { "access", "refresh", "user": {...} } }
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        summary="Login",
        description="Authenticate with username and password. Returns JWT access and refresh tokens plus user data.",
        request=LoginSerializer,
        responses={200: None},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh_str = str(refresh)

        user_data = UserSerializer(user).data
        return APIResponse.success(
            data={
                "access": access,
                "refresh": refresh_str,
                "user": user_data,
            },
            message="Login successful.",
            status_code=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):
    """
    POST /api/v1/auth/refresh/
    Body: { "refresh": "<refresh_token>" }
    Returns: { "data": { "access": "<new_access_token>" } }
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        summary="Refresh token",
        description="Exchange a valid refresh token for a new access token.",
        request=TokenRefreshSerializer,
        responses={200: None, 401: None},
    )
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Invalid or expired refresh token.",
                errors=serializer.errors,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        access = serializer.validated_data["access"]
        return APIResponse.success(
            data={"access": str(access)},
            message="Token refreshed successfully.",
            status_code=status.HTTP_200_OK,
        )
