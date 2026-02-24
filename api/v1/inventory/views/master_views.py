from rest_framework import filters, status, viewsets

from apps.inventory.models import Brand, Category, Finish, Grade, Material, Size, Thickness
from core.utils.responses import APIResponse

from ..serializers import (
    BrandSerializer,
    CategorySerializer,
    FinishSerializer,
    GradeSerializer,
    MaterialSerializer,
    SizeSerializer,
    ThicknessSerializer,
)


class BaseInventoryMasterViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
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
    search_fields = ['name', 'value', 'code', 'slug']
    ordering_fields = ['name', 'created_at', 'updated_at']


class ThicknessViewSet(BaseInventoryMasterViewSet):
    queryset = Thickness.objects.all()
    serializer_class = ThicknessSerializer
    search_fields = ['name', 'code', 'slug']
    ordering_fields = ['name', 'created_at', 'updated_at']


class GradeViewSet(BaseInventoryMasterViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    search_fields = ['name', 'code', 'slug']
    ordering_fields = ['name', 'created_at', 'updated_at']


class FinishViewSet(BaseInventoryMasterViewSet):
    queryset = Finish.objects.all()
    serializer_class = FinishSerializer
    search_fields = ['name', 'code', 'slug']
    ordering_fields = ['name', 'created_at', 'updated_at']

