from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.navigation.models import Permission
from core.permissions.rbac_permission import RBACPermission
from core.utils.responses import APIResponse

from ..serializers import (
    PermissionSerializer,
    PermissionWriteSerializer,
)


class PermissionListCreateAPIView(APIView):
    """
    List all permissions or create a permission.
    """

    permission_classes = [IsAuthenticated, RBACPermission]
    serializer_class = PermissionWriteSerializer
    permission_prefix = "core.rbac"

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = Permission.objects.order_by("module", "permission_name")
        module_id = request.query_params.get("module_id")
        if module_id is not None:
            queryset = queryset.filter(module_id=module_id)
        serializer = PermissionSerializer(queryset, many=True)
        return APIResponse.success(
            data={"permissions": serializer.data},
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = PermissionWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        read_serializer = PermissionSerializer(instance)
        return APIResponse.success(
            data=read_serializer.data,
            message="Permission created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class PermissionDetailAPIView(APIView):
    """
    Retrieve, update, or delete a Permission by id.
    """

    permission_classes = [IsAuthenticated, RBACPermission]
    serializer_class = PermissionWriteSerializer
    permission_prefix = "core.rbac"

    def _get_permission(self, pk: int) -> Permission | None:
        return Permission.objects.filter(pk=pk).first()

    def get(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        permission = self._get_permission(pk)
        if permission is None:
            return APIResponse.error(
                message="Permission not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = PermissionSerializer(permission)
        return APIResponse.success(
            data=serializer.data,
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def put(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        permission = self._get_permission(pk)
        if permission is None:
            return APIResponse.error(
                message="Permission not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = PermissionWriteSerializer(permission, data=request.data, partial=False)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        read_serializer = PermissionSerializer(instance)
        return APIResponse.success(
            data=read_serializer.data,
            message="Permission updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def patch(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        permission = self._get_permission(pk)
        if permission is None:
            return APIResponse.error(
                message="Permission not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = PermissionWriteSerializer(permission, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        read_serializer = PermissionSerializer(instance)
        return APIResponse.success(
            data=read_serializer.data,
            message="Permission updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def delete(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        permission = self._get_permission(pk)
        if permission is None:
            return APIResponse.error(
                message="Permission not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        permission.delete()
        return APIResponse.success(
            data=None,
            message="Permission deleted successfully.",
            status_code=status.HTTP_200_OK,
        )
