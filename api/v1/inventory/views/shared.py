from django.db.models import Q
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from core.permissions.rbac_permission import RBACPermission

from core.utils.responses import APIResponse
from ..serializers import DropdownOptionSerializer


class BaseInventoryViewSet(viewsets.ModelViewSet):
    """Generic base class for inventory-related ViewSets with common behavior."""

    permission_classes = [IsAuthenticated, RBACPermission]
    ordering = ["-created_at"]

    def _model_has_field(self, field_name):
        return field_name in {field.name for field in self.get_queryset().model._meta.fields}

    def perform_create(self, serializer):
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        save_kwargs = {}
        if user and self._model_has_field("created_by"):
            save_kwargs["created_by"] = user
        if user and self._model_has_field("updated_by"):
            save_kwargs["updated_by"] = user
        serializer.save(**save_kwargs)

    def perform_update(self, serializer):
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        save_kwargs = {}
        if user and self._model_has_field("updated_by"):
            save_kwargs["updated_by"] = user
        serializer.save(**save_kwargs)

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
        instance = self.get_object()
        serializer = self.get_serializer(instance)
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
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message=f"{self.queryset.model._meta.verbose_name.title()} deleted successfully.",
            status_code=status.HTTP_200_OK,
        )


class BaseInventoryMasterViewSet(BaseInventoryViewSet):
    """Specialized base class for material master ViewSets with dropdown logic."""

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    dropdown_serializer_class = DropdownOptionSerializer
    dropdown_queryset_fields = ("id", "name")
    dropdown_search_fields = ("name", "code")
    # Set to the reverse relation name from this model to Product (e.g. 'product', 'product_set')
    # to enable dropdown filtering by product_name, grade, thickness, size.
    dropdown_product_relation = None

    @staticmethod
    def _to_bool(value):
        if value is None:
            return False
        return value.lower() in {"1", "true", "yes", "on"}

    def _get_product_filter_kwargs(self):
        """Build Product filter kwargs from query params for dropdown filtering."""
        params = self.request.query_params
        product_name = (params.get("product_name") or "").strip()
        grade = (params.get("grade") or "").strip()
        thickness = (params.get("thickness") or "").strip()
        size = (params.get("size") or "").strip()
        kwargs = {}
        if product_name:
            kwargs["name__iexact"] = product_name
        if grade:
            kwargs["grade__name__iexact"] = grade
        if thickness:
            kwargs["thickness__name__icontains"] = thickness
        if size:
            kwargs["size__name__icontains"] = size
        return kwargs

    def get_dropdown_queryset(self):
        queryset = self.get_queryset().order_by("name")

        include_inactive = self._to_bool(self.request.query_params.get("include_inactive"))
        if not include_inactive:
            queryset = queryset.filter(is_active=True)

        search_text = (self.request.query_params.get("q") or "").strip()
        if search_text:
            query = Q()
            for field in self.dropdown_search_fields:
                query |= Q(**{f"{field}__icontains": search_text})
            queryset = queryset.filter(query)

        # Apply product-based filters (product_name, grade, thickness, size) when supported
        relation = getattr(self, "dropdown_product_relation", None)
        if relation:
            filter_kwargs = self._get_product_filter_kwargs()
            if filter_kwargs:
                prefix_kwargs = {f"{relation}__{k}": v for k, v in filter_kwargs.items()}
                queryset = queryset.filter(**prefix_kwargs).distinct()

        return queryset.only(*self.dropdown_queryset_fields)

    @action(detail=False, methods=["get"], url_path="dropdown")
    def dropdown(self, request, *args, **kwargs):
        queryset = self.get_dropdown_queryset()
        limit_param = request.query_params.get("limit")

        if limit_param:
            try:
                limit = max(1, int(limit_param))
                queryset = queryset[:limit]
            except ValueError:
                return APIResponse.error(
                    message="Invalid limit parameter. Please provide a positive integer.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.dropdown_serializer_class(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.queryset.model._meta.verbose_name_plural.title()} dropdown retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
