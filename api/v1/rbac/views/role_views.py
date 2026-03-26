from __future__ import annotations

from typing import Any

from django.db import IntegrityError
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.rbac.models import Role
from core.permissions.rbac_permission import RBACPermission
from core.utils.responses import APIResponse

from ..serializers import (
    RoleDetailSerializer,
    RoleSerializer,
    RoleWriteSerializer,
)
from .shared import _get_company_id


class RoleListCreateAPIView(APIView):
    """List roles or create a role."""
    permission_classes = [IsAuthenticated, RBACPermission]
    serializer_class = RoleWriteSerializer
    permission_prefix = "core.roles"

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = Role.objects.order_by("company", "role_name")
        company_id = _get_company_id(request, kwargs)
        if company_id is not None:
            queryset = queryset.filter(company_id=company_id)

        requested_company_id = request.query_params.get("company_id")
        if requested_company_id is not None:
            queryset = queryset.filter(company_id=requested_company_id)
            
        serializer = RoleSerializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        company_id = _get_company_id(request, kwargs)

        if request.user.is_superuser:
            override_company_id = request.data.get("company_id")
            if override_company_id is not None:
                try:
                    company_id = int(override_company_id)
                except (ValueError, TypeError):
                    return APIResponse.error(
                        message="Invalid company_id.",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

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
    """Retrieve, update, or delete a Role by id."""
    permission_classes = [IsAuthenticated, RBACPermission]
    serializer_class = RoleWriteSerializer
    permission_prefix = "core.roles"

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
