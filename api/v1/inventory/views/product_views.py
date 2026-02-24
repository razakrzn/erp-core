from django_filters import rest_framework as django_filters
from rest_framework import filters, status, viewsets

from apps.inventory.models import Product
from core.utils.responses import APIResponse

from ..serializers import ProductSerializer


class ProductFilter(django_filters.FilterSet):
    category_id = django_filters.UUIDFilter(field_name='category_id')
    brand_id = django_filters.UUIDFilter(field_name='brand_id')
    material_id = django_filters.UUIDFilter(field_name='material_id')
    size_id = django_filters.UUIDFilter(field_name='size_id')
    thickness_id = django_filters.UUIDFilter(field_name='thickness_id')
    grade_id = django_filters.UUIDFilter(field_name='grade_id')
    finish_id = django_filters.UUIDFilter(field_name='finish_id')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Product
        fields = [
            'category_id',
            'brand_id',
            'material_id',
            'size_id',
            'thickness_id',
            'grade_id',
            'finish_id',
            'is_active',
        ]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        'category', 'brand', 'material', 'size', 'thickness', 'grade', 'finish'
    )
    serializer_class = ProductSerializer
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'sku']
    ordering_fields = ['name', 'price', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Products retrieved successfully.',
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message='Product retrieved successfully.',
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message='Product created successfully.',
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
            message='Product updated successfully.',
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponse.success(
            data=None,
            message='Product deleted successfully.',
            status_code=status.HTTP_200_OK,
        )

