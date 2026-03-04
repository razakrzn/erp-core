from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from core.permissions.rbac_permission import IsSuperuser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils.responses import APIResponse

from api.v1.navigation.serializers import (
    FeatureReadOnlySerializer,
    FeatureSerializer,
    FeatureWriteSerializer,
    ModuleReadOnlySerializer,
    ModuleSerializer,
    ModuleWriteSerializer,
    PermissionSerializer,
    PermissionWriteSerializer,
    SidebarFeatureSerializer,
)
from apps.company.models import Company, CompanyFeature
from apps.navigation.models import Feature, Module, Permission
from apps.navigation.services.sidebar_builder import build_sidebar
from apps.rbac.services.permission_engine import user_has_permission


class FeatureListAPIView(APIView):
    """
    List features (with modules and permissions) enabled for the current user's company.

    Company is taken from the authenticated user's company (request.user.company_id).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FeatureSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        company_id = getattr(request.user, "company_id", None) if request.user.is_authenticated else None
        if company_id is None:
            return APIResponse.error(
                message="Company context is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        enabled_feature_ids = list(
            CompanyFeature.objects.filter(
                company_id=company_id,
                is_enabled=True,
            ).values_list("feature_id", flat=True)
        )

        if not enabled_feature_ids:
            return APIResponse.success(
                data={"company_id": company_id, "features": []},
                message="No enabled features for this company.",
                status_code=status.HTTP_200_OK,
            )

        features = (
            Feature.objects.filter(id__in=enabled_feature_ids)
            .prefetch_related("modules__permissions")
            .order_by("order", "feature_name")
        )

        user = request.user
        is_superuser = getattr(user, "is_superuser", False)

        if is_superuser:
            # Superuser sees all enabled features and modules, including modules
            # with no permissions (empty permissions array).
            serializer = FeatureSerializer(features, many=True)
            return APIResponse.success(
                data={"company_id": company_id, "features": serializer.data},
                message="Success",
                status_code=status.HTTP_200_OK,
            )

        filtered_features: list[dict[str, Any]] = []
        for feature in features:
            # Superuser feature is visible only to superusers.
            if feature.feature_code.lower() == "superuser":
                continue
            allowed_modules: list[dict[str, Any]] = []
            for module in feature.modules.all().order_by("order", "module_name"):
                allowed_perms = [
                    p
                    for p in module.permissions.all()
                    if user_has_permission(user, p.permission_code)
                ]
                if not allowed_perms:
                    continue
                allowed_modules.append({
                    **ModuleSerializer(module).data,
                    "permissions": PermissionSerializer(allowed_perms, many=True).data,
                })
            if not allowed_modules:
                continue
            filtered_features.append({
                "id": feature.id,
                "feature_code": feature.feature_code,
                "feature_name": feature.feature_name,
                "icon": feature.icon,
                "order": feature.order,
                "modules": allowed_modules,
            })

        return APIResponse.success(
            data={"company_id": company_id, "features": filtered_features},
            message="Success",
            status_code=status.HTTP_200_OK,
        )


class CompanyFeatureListAPIView(APIView):
    """
    List features (with modules and permissions) enabled for a company.

    Company is taken from the URL: GET /company/<company_id>/features/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FeatureSerializer

    def get(self, request: Request, company_id: int, *args: Any, **kwargs: Any) -> Response:
        enabled_feature_ids = list(
            CompanyFeature.objects.filter(
                company_id=company_id,
                is_enabled=True,
            ).values_list("feature_id", flat=True)
        )

        if not enabled_feature_ids:
            return APIResponse.success(
                data={"company_id": company_id, "features": []},
                message="No enabled features for this company.",
                status_code=status.HTTP_200_OK,
            )

        features = (
            Feature.objects.filter(id__in=enabled_feature_ids)
            .prefetch_related("modules__permissions")
            .order_by("order", "feature_name")
        )

        user = request.user
        is_superuser = getattr(user, "is_superuser", False)

        if is_superuser:
            serializer = FeatureSerializer(features, many=True)
            return APIResponse.success(
                data={"company_id": company_id, "features": serializer.data},
                message="Success",
                status_code=status.HTTP_200_OK,
            )

        filtered_features: list[dict[str, Any]] = []
        for feature in features:
            # Superuser feature is visible only to superusers.
            if feature.feature_code.lower() == "superuser":
                continue
            allowed_modules: list[dict[str, Any]] = []
            for module in feature.modules.all().order_by("order", "module_name"):
                allowed_perms = [
                    p
                    for p in module.permissions.all()
                    if user_has_permission(user, p.permission_code)
                ]
                if not allowed_perms:
                    continue
                allowed_modules.append({
                    **ModuleSerializer(module).data,
                    "permissions": PermissionSerializer(allowed_perms, many=True).data,
                })
            if not allowed_modules:
                continue
            filtered_features.append({
                "id": feature.id,
                "feature_code": feature.feature_code,
                "feature_name": feature.feature_name,
                "icon": feature.icon,
                "order": feature.order,
                "modules": allowed_modules,
            })

        return APIResponse.success(
            data={"company_id": company_id, "features": filtered_features},
            message="Success",
            status_code=status.HTTP_200_OK,
        )


class SidebarAPIView(APIView):
    """
    Return the dynamic sidebar for the current user and their company.

    Uses RBAC to include only modules the user has permission to access.
    Superusers without a company get all features in the sidebar (no filtering).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SidebarFeatureSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        company = getattr(request.user, "company", None)
        if company is None and not getattr(request.user, "is_superuser", False):
            return APIResponse.error(
                message="User must be associated with a company.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        sidebar = build_sidebar(request.user, company)
        serializer = SidebarFeatureSerializer(sidebar, many=True)
        return APIResponse.success(
            data={"sidebar": serializer.data},
            message="Success",
            status_code=status.HTTP_200_OK,
        )


class EnableFeatureAPIView(APIView):
    """
    Enable one or more features for a company by feature ID.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FeatureWriteSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        company_id = getattr(request, "company_id", None) or kwargs.get("company_id")
        if company_id is None:
            return APIResponse.error(
                message="Company context is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return APIResponse.error(
                message="Company not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        feature_ids = request.data.get("features") or []
        if not isinstance(feature_ids, list):
            return APIResponse.error(
                message="features must be a list of feature IDs.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        enabled: list[int] = []
        for f_id in feature_ids:
            if not isinstance(f_id, int):
                continue
            feature = Feature.objects.filter(pk=f_id).first()
            if feature is None:
                return APIResponse.error(
                    message=f"Feature not found with ID: {f_id}.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            CompanyFeature.objects.update_or_create(
                company=company,
                feature=feature,
                defaults={"is_enabled": True},
            )
            enabled.append(feature.id)

        return APIResponse.success(
            data={"enabled_features": enabled},
            message="Features enabled successfully.",
            status_code=status.HTTP_200_OK,
        )


class DisableFeatureAPIView(APIView):
    """
    Disable one or more features for a company by feature ID.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FeatureWriteSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        company_id = getattr(request, "company_id", None) or kwargs.get("company_id")
        if company_id is None:
            return APIResponse.error(
                message="Company context is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return APIResponse.error(
                message="Company not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        feature_ids = request.data.get("features") or []
        if not isinstance(feature_ids, list):
            return APIResponse.error(
                message="features must be a list of feature IDs.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        disabled: list[int] = []
        for f_id in feature_ids:
            if not isinstance(f_id, int):
                continue
            feature = Feature.objects.filter(pk=f_id).first()
            if feature is None:
                return APIResponse.error(
                    message=f"Feature not found with ID: {f_id}.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            updated = CompanyFeature.objects.filter(
                company=company,
                feature=feature,
            ).update(is_enabled=False)
            if updated:
                disabled.append(feature.id)

        return APIResponse.success(
            data={"disabled_features": disabled},
            message="Features disabled successfully.",
            status_code=status.HTTP_200_OK,
        )


class FeatureReadOnlyListAPIView(APIView):
    """
    Read-only list of all features: id, feature_code, feature_name only.
    GET only. Authenticated users.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = FeatureReadOnlySerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        features = Feature.objects.order_by("order", "feature_name")
        # Superuser feature is visible only to superusers.
        if not getattr(request.user, "is_superuser", False):
            features = features.exclude(feature_code__iexact="superuser")
        serializer = FeatureReadOnlySerializer(features, many=True)
        return APIResponse.success(
            data={"features": serializer.data},
            message="Success",
            status_code=status.HTTP_200_OK,
        )


class FeatureCreateAPIView(APIView):
    """
    List all features (GET) or create a new Feature (POST). Superuser only.
    """

    permission_classes = [IsAuthenticated, IsSuperuser]
    serializer_class = FeatureWriteSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        features = (
            Feature.objects.all()
            .prefetch_related("modules__permissions")
            .order_by("order", "feature_name")
        )
        serializer = FeatureSerializer(features, many=True)
        return APIResponse.success(
            data={"features": serializer.data},
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = FeatureWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        read_serializer = FeatureSerializer(instance)
        return APIResponse.success(
            data=read_serializer.data,
            message="Feature created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class FeatureDetailAPIView(APIView):
    """
    Retrieve, update (PUT/PATCH), or delete a Feature by id. Superuser only.
    """

    permission_classes = [IsAuthenticated, IsSuperuser]
    serializer_class = FeatureWriteSerializer

    def _get_feature(self, pk: int) -> Feature | None:
        return Feature.objects.filter(pk=pk).prefetch_related("modules__permissions").first()

    def get(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        feature = self._get_feature(pk)
        if feature is None:
            return APIResponse.error(
                message="Feature not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = FeatureSerializer(feature)
        return APIResponse.success(
            data=serializer.data,
            message="Success",
            status_code=status.HTTP_200_OK,
        )

    def put(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        feature = self._get_feature(pk)
        if feature is None:
            return APIResponse.error(
                message="Feature not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = FeatureWriteSerializer(feature, data=request.data, partial=False)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        read_serializer = FeatureSerializer(instance)
        return APIResponse.success(
            data=read_serializer.data,
            message="Feature updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def patch(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        feature = self._get_feature(pk)
        if feature is None:
            return APIResponse.error(
                message="Feature not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = FeatureWriteSerializer(feature, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(
                message="Validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        instance = serializer.save()
        read_serializer = FeatureSerializer(instance)
        return APIResponse.success(
            data=read_serializer.data,
            message="Feature updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def delete(self, request: Request, pk: int, *args: Any, **kwargs: Any) -> Response:
        feature = Feature.objects.filter(pk=pk).first()
        if feature is None:
            return APIResponse.error(
                message="Feature not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        feature.delete()
        return APIResponse.success(
            data=None,
            message="Feature deleted successfully.",
            status_code=status.HTTP_200_OK,
        )


class ModuleReadOnlyListAPIView(APIView):
    """
    Read-only list of all modules: id, module_code, module_name only.
    GET only. Authenticated users.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ModuleReadOnlySerializer

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
    List all modules (GET) or create a module (POST). Superuser only.
    """

    permission_classes = [IsAuthenticated, IsSuperuser]
    serializer_class = ModuleWriteSerializer

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
    Retrieve, update (PUT/PATCH), or delete a Module by id. Superuser only.
    """

    permission_classes = [IsAuthenticated, IsSuperuser]
    serializer_class = ModuleWriteSerializer

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


class PermissionListCreateAPIView(APIView):
    """
    List all permissions (GET) or create a permission (POST).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PermissionWriteSerializer

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
    Retrieve, update (PUT/PATCH), or delete a Permission by id.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PermissionWriteSerializer

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
