from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.navigation.models import Module
from core.permissions.rbac_permission import IsSuperuser, RBACPermission
from core.utils.responses import APIResponse

from ..serializers import (
    ModuleReadOnlySerializer,
    ModuleSerializer,
    ModuleWriteSerializer,
)


class ModuleReadOnlyListAPIView(APIView):
    """
    Read-only list of all modules.
    """

    permission_classes = [IsAuthenticated, RBACPermission]
    serializer_class = ModuleReadOnlySerializer
    permission_prefix = "core.modules"

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        modules = Module.objects.order_by("feature", "order", "module_name")
        serializer = ModuleReadOnlySerializer(modules, many=True)
        return APIResponse.success(
            data={"modules": serializer.data},
            message="Success",
            status_code=status.HTTP_200_OK,
        )


class ModuleListCreateAPIView(APIView):
    """
    List all modules or create a module. Superuser only.
    """

    permission_classes = [IsAuthenticated, IsSuperuser, RBACPermission]
    serializer_class = ModuleWriteSerializer
    permission_prefix = "core.modules"

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = Module.objects.prefetch_related("permissions").order_by("feature", "order", "module_name")
        feature_id = request.query_params.get("feature_id")
        if feature_id is not None:
            queryset = queryset.filter(feature_id=feature_id)
        serializer = ModuleSerializer(queryset, many=True)
        return APIResponse.success(
            data={"modules": serializer.data},
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = ModuleWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        read_serializer = ModuleSerializer(instance)
        return APIResponse.success(
            data=read_serializer.data,
            message="Module created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class ModuleDetailAPIView(APIView):
    """
    Retrieve, update, or delete a Module by id. Superuser only.
    """

    permission_classes = [IsAuthenticated, IsSuperuser]
    serializer_class = ModuleWriteSerializer
    permission_prefix = "core.modules"

    def _get_module(self, pk: int) -> Module | None:
        return Module.objects.filter(pk=pk).prefetch_related("permissions").first()

    def get(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        module = self._get_module(pk)
        if module is None:
            return APIResponse.error(
                message="Module not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = ModuleSerializer(module)
        return APIResponse.success(
            data=serializer.data,
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def put(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        module = self._get_module(pk)
        if module is None:
            return APIResponse.error(
                message="Module not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = ModuleWriteSerializer(module, data=request.data, partial=False)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        read_serializer = ModuleSerializer(instance)
        return APIResponse.success(
            data=read_serializer.data,
            message="Module updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def patch(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        module = self._get_module(pk)
        if module is None:
            return APIResponse.error(
                message="Module not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = ModuleWriteSerializer(module, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        read_serializer = ModuleSerializer(instance)
        return APIResponse.success(
            data=read_serializer.data,
            message="Module updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def delete(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        module = Module.objects.filter(pk=pk).first()
        if module is None:
            return APIResponse.error(
                message="Module not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        module.delete()
        return APIResponse.success(
            data=None,
            message="Module deleted successfully.",
            status_code=status.HTTP_200_OK,
        )
