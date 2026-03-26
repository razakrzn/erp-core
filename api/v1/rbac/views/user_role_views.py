from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.rbac.models import UserRole
from core.permissions.rbac_permission import RBACPermission
from core.utils.responses import APIResponse

from ..serializers import (
    UserRoleDetailsSerializer,
    UserRoleSerializer,
    UserRoleWriteSerializer,
)


class UserRoleListCreateAPIView(APIView):
    """List user-role assignments or create one."""
    permission_classes = [IsAuthenticated, RBACPermission]
    serializer_class = UserRoleWriteSerializer
    permission_prefix = "core.users"

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = UserRole.objects.select_related("user", "role").order_by("user", "role")
        user_id = request.query_params.get("user_id")
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        role_id = request.query_params.get("role_id")
        if role_id is not None:
            queryset = queryset.filter(role_id=role_id)
        serializer = UserRoleSerializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = UserRoleWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        return APIResponse.success(
            data=UserRoleSerializer(instance).data,
            message="User role assigned successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class UserRoleDetailAPIView(APIView):
    """Retrieve or delete a UserRole by id."""
    permission_classes = [IsAuthenticated, RBACPermission]
    serializer_class = UserRoleDetailsSerializer
    permission_prefix = "core.users"

    def get(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        ur = UserRole.objects.filter(pk=pk).select_related("user", "role").first()
        if ur is None:
            return APIResponse.error(
                message="User role not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return APIResponse.success(
            data=UserRoleDetailsSerializer(ur).data,
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def delete(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        ur = UserRole.objects.filter(pk=pk).first()
        if ur is None:
            return APIResponse.error(
                message="User role not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        ur.delete()
        return APIResponse.success(
            data=None,
            message="User role removed successfully.",
            status_code=status.HTTP_200_OK,
        )
