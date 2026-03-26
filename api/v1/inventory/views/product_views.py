from django_filters import rest_framework as django_filters
from django.db.models import Q
from rest_framework import filters, status
from rest_framework.decorators import action

from apps.inventory.models import Product
from core.utils.responses import APIResponse

from ..serializers import ProductDropdownSerializer, ProductListSerializer, ProductSerializer
from .shared import BaseInventoryViewSet


class ProductFilter(django_filters.FilterSet):
    slug = django_filters.CharFilter(field_name='slug', lookup_expr='iexact')
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
            'slug',
            'category_id',
            'brand_id',
            'material_id',
            'size_id',
            'thickness_id',
            'grade_id',
            'finish_id',
            'is_active',
        ]


class ProductViewSet(BaseInventoryViewSet):
    queryset = Product.objects.select_related(
        'category', 'brand', 'material', 'size', 'thickness', 'grade', 'finish'
    )
    serializer_class = ProductSerializer
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'slug', 'sku']
    ordering_fields = ['name', 'slug', 'price', 'created_at', 'updated_at']
    ordering = ['-created_at']
    permission_prefix = "procurement.materials"

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    @staticmethod
    def _to_bool(value):
        if value is None:
            return False
        return value.lower() in {'1', 'true', 'yes', 'on'}

    @action(detail=False, methods=['get'], url_path='dropdown')
    def dropdown(self, request, *args, **kwargs):
        queryset = Product.objects.only('id', 'name', 'slug', 'is_active').order_by('name')

        include_inactive = self._to_bool(request.query_params.get('include_inactive'))
        if not include_inactive:
            queryset = queryset.filter(is_active=True)

        search_text = (request.query_params.get('q') or '').strip()
        if search_text:
            queryset = queryset.filter(
                Q(name__icontains=search_text) | Q(slug__icontains=search_text) | Q(sku__icontains=search_text)
            )

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

        serializer = ProductDropdownSerializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Products dropdown retrieved successfully.',
            status_code=status.HTTP_200_OK,
        )
