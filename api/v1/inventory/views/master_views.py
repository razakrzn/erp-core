from django.db.models import Q
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from core.utils.schema_docs_shims import OpenApiParameter, extend_schema, extend_schema_view

from apps.inventory.models import Brand, Category, Finish, Grade, Material, Product, Size, Thickness
from core.utils.responses import APIResponse

from ..serializers import (
    BrandSerializer,
    CategorySerializer,
    DropdownOptionSerializer,
    DropdownOptionWithValueSerializer,
    FinishSerializer,
    GradeSerializer,
    MaterialSerializer,
    SizeSerializer,
    ThicknessSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="List master values"),
    retrieve=extend_schema(summary="Get master value details"),
    create=extend_schema(summary="Create master value"),
    update=extend_schema(summary="Update master value"),
    partial_update=extend_schema(summary="Partial update master value"),
    destroy=extend_schema(summary="Delete master value"),
    dropdown=extend_schema(
        summary="List master values for dropdowns",
        parameters=[
            OpenApiParameter("q", str, OpenApiParameter.QUERY, description="Search by name or code"),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY, description="Maximum number of results"),
            OpenApiParameter("include_inactive", bool, OpenApiParameter.QUERY, description="Set to 'true' to include inactive values"),
            OpenApiParameter("product_name", str, OpenApiParameter.QUERY, description="Filter by associated product name"),
            OpenApiParameter("grade", str, OpenApiParameter.QUERY, description="Filter by associated product grade"),
            OpenApiParameter("thickness", str, OpenApiParameter.QUERY, description="Filter by associated product thickness"),
            OpenApiParameter("size", str, OpenApiParameter.QUERY, description="Filter by associated product size"),
        ],
    ),
)
class BaseInventoryMasterViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-created_at']
    dropdown_serializer_class = DropdownOptionSerializer
    dropdown_queryset_fields = ('id', 'name')
    dropdown_search_fields = ('name', 'code')
    # Set to the reverse relation name from this model to Product (e.g. 'product', 'product_set')
    # to enable dropdown filtering by product_name, grade, thickness, size.
    dropdown_product_relation = None

    @staticmethod
    def _to_bool(value):
        if value is None:
            return False
        return value.lower() in {'1', 'true', 'yes', 'on'}

    def _get_product_filter_kwargs(self):
        """Build Product filter kwargs from query params for dropdown filtering."""
        params = self.request.query_params
        product_name = (params.get('product_name') or '').strip()
        grade = (params.get('grade') or '').strip()
        thickness = (params.get('thickness') or '').strip()
        size = (params.get('size') or '').strip()
        kwargs = {}
        if product_name:
            kwargs['name__iexact'] = product_name
        if grade:
            kwargs['grade__name__iexact'] = grade
        if thickness:
            kwargs['thickness__name__icontains'] = thickness
        if size:
            kwargs['size__name__icontains'] = size
        return kwargs

    def get_dropdown_queryset(self):
        queryset = self.get_queryset().order_by('name')

        include_inactive = self._to_bool(self.request.query_params.get('include_inactive'))
        if not include_inactive:
            queryset = queryset.filter(is_active=True)

        search_text = (self.request.query_params.get('q') or '').strip()
        if search_text:
            query = Q()
            for field in self.dropdown_search_fields:
                query |= Q(**{f'{field}__icontains': search_text})
            queryset = queryset.filter(query)

        # Apply product-based filters (product_name, grade, thickness, size) when supported
        relation = getattr(self, 'dropdown_product_relation', None)
        if relation:
            filter_kwargs = self._get_product_filter_kwargs()
            if filter_kwargs:
                prefix_kwargs = {f'{relation}__{k}': v for k, v in filter_kwargs.items()}
                queryset = queryset.filter(**prefix_kwargs).distinct()

        return queryset.only(*self.dropdown_queryset_fields)

    @action(detail=False, methods=['get'], url_path='dropdown')
    def dropdown(self, request, *args, **kwargs):
        queryset = self.get_dropdown_queryset()
        limit_param = request.query_params.get('limit')

        if limit_param:
            try:
                limit = max(1, int(limit_param))
                queryset = queryset[:limit]
            except ValueError:
                return APIResponse.error(
                    message='Invalid limit parameter. Please provide a positive integer.',
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.dropdown_serializer_class(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message=f'{self.queryset.model._meta.verbose_name_plural.title()} dropdown retrieved successfully.',
            status_code=status.HTTP_200_OK,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message=f'{self.queryset.model._meta.verbose_name_plural.title()} retrieved successfully.',
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message=f'{self.queryset.model._meta.verbose_name.title()} retrieved successfully.',
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message=f'{self.queryset.model._meta.verbose_name.title()} created successfully.',
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(
            data=serializer.data,
            message=f'{self.queryset.model._meta.verbose_name.title()} updated successfully.',
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message=f'{self.queryset.model._meta.verbose_name.title()} deleted successfully.',
            status_code=status.HTTP_200_OK,
        )


class CategoryViewSet(BaseInventoryMasterViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name', 'code', 'slug', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']


class BrandViewSet(BaseInventoryMasterViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    search_fields = ['name', 'code', 'slug']
    ordering_fields = ['name', 'created_at', 'updated_at']


class MaterialViewSet(BaseInventoryMasterViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    search_fields = ['name', 'code', 'slug', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']


class SizeViewSet(BaseInventoryMasterViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    dropdown_serializer_class = DropdownOptionWithValueSerializer
    dropdown_queryset_fields = ('id', 'name', 'value', 'code')
    dropdown_search_fields = ('name', 'value', 'code')
    search_fields = ['name', 'value', 'code', 'slug']
    ordering_fields = ['name', 'created_at', 'updated_at']
    dropdown_product_relation = 'product_set'


class ThicknessViewSet(BaseInventoryMasterViewSet):
    queryset = Thickness.objects.all()
    serializer_class = ThicknessSerializer
    dropdown_serializer_class = DropdownOptionWithValueSerializer
    dropdown_queryset_fields = ('id', 'name', 'value', 'code')
    dropdown_search_fields = ('name', 'value', 'code')
    search_fields = ['name', 'code', 'slug']
    ordering_fields = ['name', 'created_at', 'updated_at']
    dropdown_product_relation = 'product_set'


class GradeViewSet(BaseInventoryMasterViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    search_fields = ['name', 'code', 'slug']
    ordering_fields = ['name', 'created_at', 'updated_at']
    dropdown_product_relation = 'product'


class FinishViewSet(BaseInventoryMasterViewSet):
    queryset = Finish.objects.all()
    serializer_class = FinishSerializer
    search_fields = ['name', 'code', 'slug']
    ordering_fields = ['name', 'created_at', 'updated_at']
    dropdown_product_relation = 'product_set'
