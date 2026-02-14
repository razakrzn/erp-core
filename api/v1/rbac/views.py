"""
RBAC API views (roles, role permissions, user roles, role hierarchy).
"""

from __future__ import annotations

from typing import Any

from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils.responses import APIResponse

from api.v1.rbac.serializers import (
    RoleDetailSerializer,
    RoleHierarchySerializer,
    RoleHierarchyWriteSerializer,
    RolePermissionSerializer,
    RolePermissionWriteSerializer,
    RoleSerializer,
    RoleWriteSerializer,
    UserRoleSerializer,
    UserRoleWriteSerializer,
)
from apps.rbac.models import Role, RolePermission, RoleHierarchy, UserRole


def _get_company_id(request: Request, kwargs: dict) -> int | None:
    """Company from current user's company only (request.user.company_id)."""
    if not getattr(request, "user", None) or not getattr(request.user, "is_authenticated", False):
        return None
    if not request.user.is_authenticated or not hasattr(request.user, "company_id"):
        return None
    return request.user.company_id


# ----- Role -----


class RoleListCreateAPIView(APIView):
    """List roles (GET) or create a role (POST)."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = Role.objects.order_by("company", "role_name")
        company_id = _get_company_id(request, kwargs)
        if company_id is not None:
            queryset = queryset.filter(company_id=company_id)
        serializer = RoleSerializer(queryset, many=True)
        return APIResponse.success(
            data={"roles": serializer.data},
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        company_id = _get_company_id(request, kwargs)
        if company_id is None:
            return APIResponse.error(
                message="Company context is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        serializer = RoleWriteSerializer(
            data=request.data,
            context={"company_id": company_id},
        )
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            instance = serializer.save()
        except IntegrityError as e:
            if "uniq_rbac_role_company_code" in str(e):
                return APIResponse.error(
                    message="A role with this code already exists for your company.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            raise
        read_serializer = RoleDetailSerializer(instance)
        return APIResponse.success(
            data=read_serializer.data,
            message="Role created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class RoleDetailAPIView(APIView):
    """Retrieve, update (PUT/PATCH), or delete a Role by id."""

    permission_classes = [IsAuthenticated]

    def _get_role(self, pk: int) -> Role | None:
        return Role.objects.filter(pk=pk).prefetch_related("role_permissions").first()

    def get(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        role = self._get_role(pk)
        if role is None:
            return APIResponse.error(
                message="Role not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = RoleDetailSerializer(role)
        return APIResponse.success(
            data=serializer.data,
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def put(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        role = Role.objects.filter(pk=pk).first()
        if role is None:
            return APIResponse.error(
                message="Role not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = RoleWriteSerializer(role, data=request.data, partial=False)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        return APIResponse.success(
            data=RoleSerializer(instance).data,
            message="Role updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def patch(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        role = Role.objects.filter(pk=pk).first()
        if role is None:
            return APIResponse.error(
                message="Role not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = RoleWriteSerializer(role, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        return APIResponse.success(
            data=RoleSerializer(instance).data,
            message="Role updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def delete(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        role = Role.objects.filter(pk=pk).first()
        if role is None:
            return APIResponse.error(
                message="Role not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        role.delete()
        return APIResponse.success(
            data=None,
            message="Role deleted successfully.",
            status_code=status.HTTP_200_OK,
        )


# ----- RolePermission -----


class RolePermissionListCreateAPIView(APIView):
    """List role-permission links (GET) or create one (POST)."""

    permission_classes = [IsAuthenticated]

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
    """Retrieve or delete a RolePermission by id (no PUT/PATCH for join table)."""

    permission_classes = [IsAuthenticated]

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


# ----- UserRole -----


class UserRoleListCreateAPIView(APIView):
    """List user-role assignments (GET) or create one (POST)."""

    permission_classes = [IsAuthenticated]

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
            data={"user_roles": serializer.data},
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

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        ur = UserRole.objects.filter(pk=pk).select_related("user", "role").first()
        if ur is None:
            return APIResponse.error(
                message="User role not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return APIResponse.success(
            data=UserRoleSerializer(ur).data,
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


# ----- RoleHierarchy -----


class RoleHierarchyListCreateAPIView(APIView):
    """List role hierarchy links (GET) or create one (POST)."""

    permission_classes = [IsAuthenticated]

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

    permission_classes = [IsAuthenticated]

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
