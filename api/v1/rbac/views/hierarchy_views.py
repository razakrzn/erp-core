from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.rbac.models import RoleHierarchy
from core.permissions.rbac_permission import RBACPermission
from core.utils.responses import APIResponse

from ..serializers import (
    RoleHierarchySerializer,
    RoleHierarchyWriteSerializer,
)


class RoleHierarchyListCreateAPIView(APIView):
    """List role hierarchy links or create one."""
    permission_classes = [IsAuthenticated, RBACPermission]
    serializer_class = RoleHierarchyWriteSerializer
    permission_prefix = "core.roles"

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = RoleHierarchy.objects.select_related("parent_role", "child_role").order_by("parent_role", "child_role")
        parent_id = request.query_params.get("parent_role_id")
        if parent_id is not None:
            queryset = queryset.filter(parent_role_id=parent_id)
        child_id = request.query_params.get("child_role_id")
        if child_id is not None:
            queryset = queryset.filter(child_role_id=child_id)
        serializer = RoleHierarchySerializer(queryset, many=True)
        return APIResponse.success(
            data={"role_hierarchies": serializer.data},
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = RoleHierarchyWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        return APIResponse.success(
            data=RoleHierarchySerializer(instance).data,
            message="Role hierarchy created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class RoleHierarchyDetailAPIView(APIView):
    """Retrieve or delete a RoleHierarchy by id."""
    permission_classes = [IsAuthenticated, RBACPermission]
    serializer_class = RoleHierarchySerializer
    permission_prefix = "core.roles"

    def get(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        rh = RoleHierarchy.objects.filter(pk=pk).select_related("parent_role", "child_role").first()
        if rh is None:
            return APIResponse.error(
                message="Role hierarchy not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return APIResponse.success(
            data=RoleHierarchySerializer(rh).data,
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def delete(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        rh = RoleHierarchy.objects.filter(pk=pk).first()
        if rh is None:
            return APIResponse.error(
                message="Role hierarchy not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        rh.delete()
        return APIResponse.success(
            data=None,
            message="Role hierarchy removed successfully.",
            status_code=status.HTTP_200_OK,
        )
