from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.company.models import Company, CompanyFeature, CompanyModule
from apps.navigation.models import Feature, Module
from core.permissions.rbac_permission import IsSuperuser, RBACPermission
from core.utils.responses import APIResponse

from ..serializers import (
    CompanyModuleAccessSerializer,
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


class BaseCompanyModuleAccessAPIView(APIView):
    permission_classes = [IsAuthenticated, RBACPermission]
    serializer_class = CompanyModuleAccessSerializer
    permission_prefix = "core.modules"
    target_enabled_state: bool = True
    success_message = "Module access updated successfully."
    response_key = "module_access"

    def _get_company(self, company_id: int) -> Company | None:
        return Company.objects.filter(pk=company_id).first()

    def _get_feature(self, feature_id: int) -> Feature | None:
        return Feature.objects.filter(pk=feature_id).first()

    def _get_module(self, module_id: int) -> Module | None:
        return Module.objects.select_related("feature").filter(pk=module_id).first()

    def post(self, request: Request, company_id: int, *args: Any, **kwargs: Any) -> Response:
        """
        Manage module access for a company inside an enabled feature.

        Request body:
        {
          "feature_id": 3,
          "module_id": 12
        }

        Success response:
        {
          "success": true,
          "message": "Module enabled successfully for this company.",
          "data": {
            "module_access": {
              "company_id": 7,
              "feature_id": 3,
              "module_id": 12,
              "enabled": true
            }
          }
        }

        Error scenarios:
        - 400 when `feature_id` or `module_id` is missing/invalid.
        - 400 when the module does not belong to the given feature.
        - 400 when the feature is not enabled for the company.
        - 404 when the company, feature, or module does not exist.
        - 403 when the authenticated user lacks `core.modules.create`.
        """

        company = self._get_company(company_id)
        if company is None:
            return APIResponse.error(
                message="Company not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        feature_id = serializer.validated_data["feature_id"]
        module_id = serializer.validated_data["module_id"]

        feature = self._get_feature(feature_id)
        if feature is None:
            return APIResponse.error(
                message=f"Feature not found with ID: {feature_id}.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        module = self._get_module(module_id)
        if module is None:
            return APIResponse.error(
                message=f"Module not found with ID: {module_id}.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if module.feature_id != feature.id:
            return APIResponse.error(
                message="The selected module does not belong to the specified feature.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        company_feature_enabled = CompanyFeature.objects.filter(
            company=company,
            feature=feature,
            is_enabled=True,
        ).exists()
        if not company_feature_enabled:
            return APIResponse.error(
                message="This feature is not enabled for the specified company.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        CompanyModule.objects.update_or_create(
            company=company,
            module=module,
            defaults={"is_enabled": self.target_enabled_state},
        )

        return APIResponse.success(
            data={
                self.response_key: {
                    "company_id": company.id,
                    "feature_id": feature.id,
                    "module_id": module.id,
                    "enabled": self.target_enabled_state,
                }
            },
            message=self.success_message,
            status_code=status.HTTP_200_OK,
        )


class EnableCompanyModuleAPIView(BaseCompanyModuleAccessAPIView):
    """
    Enable a module for a company inside an already-enabled feature.

    Endpoint:
    `POST /api/v1/navigation/company/{company_id}/enable-module/`

    Request example:
    {
      "feature_id": 3,
      "module_id": 12
    }

    Response example:
    {
      "success": true,
      "message": "Module enabled successfully for this company.",
      "data": {
        "module_access": {
          "company_id": 7,
          "feature_id": 3,
          "module_id": 12,
          "enabled": true
        }
      },
      "status_code": 200
    }
    """

    target_enabled_state = True
    success_message = "Module enabled successfully for this company."


class DisableCompanyModuleAPIView(BaseCompanyModuleAccessAPIView):
    """
    Disable a module for a company inside an already-enabled feature.

    Endpoint:
    `POST /api/v1/navigation/company/{company_id}/disable-module/`

    Request example:
    {
      "feature_id": 3,
      "module_id": 12
    }

    Response example:
    {
      "success": true,
      "message": "Module disabled successfully for this company.",
      "data": {
        "module_access": {
          "company_id": 7,
          "feature_id": 3,
          "module_id": 12,
          "enabled": false
        }
      },
      "status_code": 200
    }
    """

    target_enabled_state = False
    success_message = "Module disabled successfully for this company."
