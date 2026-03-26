from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.rbac.models import RolePermission
from core.permissions.rbac_permission import RBACPermission
from core.utils.responses import APIResponse

from ..serializers import (
    RolePermissionSerializer,
    RolePermissionWriteSerializer,
)


class RolePermissionListCreateAPIView(APIView):
    """List role-permission links or create one."""
    permission_classes = [IsAuthenticated, RBACPermission]
    serializer_class = RolePermissionWriteSerializer
    permission_prefix = "core.roles"

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = RolePermission.objects.select_related("role", "permission").order_by("role", "permission")
        role_id = request.query_params.get("role_id")
        if role_id is not None:
            queryset = queryset.filter(role_id=role_id)
        permission_id = request.query_params.get("permission_id")
        if permission_id is not None:
            queryset = queryset.filter(permission_id=permission_id)
        serializer = RolePermissionSerializer(queryset, many=True)
        return APIResponse.success(
            data={"role_permissions": serializer.data},
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = RolePermissionWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        return APIResponse.success(
            data=RolePermissionSerializer(instance).data,
            message="Role permission added successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class RolePermissionDetailAPIView(APIView):
    """Retrieve or delete a RolePermission by id."""
    permission_classes = [IsAuthenticated, RBACPermission]
    serializer_class = RolePermissionSerializer
    permission_prefix = "core.roles"

    def get(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        rp = RolePermission.objects.filter(pk=pk).select_related("role", "permission").first()
        if rp is None:
            return APIResponse.error(
                message="Role permission not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return APIResponse.success(
            data=RolePermissionSerializer(rp).data,
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def delete(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        rp = RolePermission.objects.filter(pk=pk).first()
        if rp is None:
            return APIResponse.error(
                message="Role permission not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        rp.delete()
        return APIResponse.success(
            data=None,
            message="Role permission removed successfully.",
            status_code=status.HTTP_200_OK,
        )
