from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticated
from core.permissions.rbac_permission import RBACPermission

from core.utils.responses import APIResponse


class BaseProductionViewSet(viewsets.ModelViewSet):
    """Generic base class for production-related ViewSets with common behavior."""

    permission_classes = [IsAuthenticated, RBACPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering = ["-created_at"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.queryset.model._meta.verbose_name_plural.title()} retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.queryset.model._meta.verbose_name.title()} retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.queryset.model._meta.verbose_name.title()} created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.queryset.model._meta.verbose_name.title()} updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(self.get_object())
        return APIResponse.success(
            data=None,
            message=f"{self.queryset.model._meta.verbose_name.title()} deleted successfully.",
            status_code=status.HTTP_200_OK,
        )
