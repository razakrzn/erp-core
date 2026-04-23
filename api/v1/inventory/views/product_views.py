from django.db.models import Q
from rest_framework import filters, status
from rest_framework.decorators import action

from apps.inventory.models import Brand, Category, Finish, Grade, Material, Product, Size, Thickness, Unit

from core.utils.responses import APIResponse

from ..serializers import (
    BrandSerializer,
    CategorySerializer,
    FinishSerializer,
    GradeSerializer,
    MaterialSerializer,
    ProductDropdownSerializer,
    ProductListSerializer,
    ProductSerializer,
    SizeSerializer,
    ThicknessSerializer,
    UnitSerializer,
)
from .shared import BaseInventoryViewSet


class BaseInventoryLookupViewSet(BaseInventoryViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "created_at", "updated_at"]
    ordering = ["name"]
    permission_prefix = "procurement.material_settings"


class CategoryViewSet(BaseInventoryLookupViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(BaseInventoryLookupViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class MaterialViewSet(BaseInventoryLookupViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer


class SizeViewSet(BaseInventoryLookupViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class ThicknessViewSet(BaseInventoryLookupViewSet):
    queryset = Thickness.objects.all()
    serializer_class = ThicknessSerializer


class GradeViewSet(BaseInventoryLookupViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class FinishViewSet(BaseInventoryLookupViewSet):
    queryset = Finish.objects.all()
    serializer_class = FinishSerializer


class UnitViewSet(BaseInventoryLookupViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class ProductViewSet(BaseInventoryViewSet):
    queryset = Product.objects.select_related(
        "preferred_supplier",
        "category",
        "brand",
        "material",
        "size",
        "thickness",
        "grade",
        "finish",
        "unit",
    )
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "name",
        "sku",
        "product_code",
        "status",
        "preferred_supplier__trade_name",
        "hsn_sac_code",
        "category__name",
        "brand__name",
        "material__name",
        "size__name",
        "thickness__name",
        "grade__name",
        "finish__name",
        "unit__name",
    ]
    ordering_fields = [
        "id",
        "name",
        "sku",
        "product_code",
        "status",
        "price",
        "standard_cost",
        "reorder_level",
        "lead_time_days",
        "max_stock_level",
        "moq",
        "opening_stock",
        "opening_stock_date",
        "created_at",
        "updated_at",
    ]
    ordering = ["name"]
    permission_prefix = "procurement.materials"

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductSerializer

    def _build_category_filter(self, category_name):
        normalized = (category_name or "").strip().lower()
        if not normalized:
            return Q()

        # Keep accessories lookup resilient to existing typo variants in master data.
        if normalized == "accessories":
            accessories_variants = [
                "accessories",
                "accessory",
                "accesories",
                "accesory",
                "accesorries",
            ]
            category_q = Q()
            for variant in accessories_variants:
                category_q |= Q(category__name__iexact=variant)
            return category_q

        return Q(category__name__iexact=normalized)

    def _get_dropdown_queryset(self, query="", category_name=None):
        queryset = self.get_queryset().order_by("name")
        if category_name:
            queryset = queryset.filter(self._build_category_filter(category_name))
        if query:
            queryset = queryset.filter(name__icontains=query) | queryset.filter(product_code__icontains=query)
            queryset = queryset.distinct().order_by("name")
        return queryset

    def _parse_dropdown_pagination(self, request):
        page_size_raw = request.query_params.get("page_size", "10")
        page_raw = request.query_params.get("page", "1")
        try:
            page_size = max(1, int(page_size_raw))
        except (TypeError, ValueError):
            page_size = 10
        try:
            page = max(1, int(page_raw))
        except (TypeError, ValueError):
            page = 1
        return page, page_size

    @action(detail=False, methods=["get"], url_path="dropdown")
    def dropdown(self, request, *args, **kwargs):
        query = (request.query_params.get("search") or request.query_params.get("query") or "").strip()
        queryset = self._get_dropdown_queryset(query=query)
        page, page_size = self._parse_dropdown_pagination(request)

        start = (page - 1) * page_size
        end = start + page_size
        serializer = ProductDropdownSerializer(queryset[start:end], many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Products retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="accessories-dropdown")
    def accessories_dropdown(self, request, *args, **kwargs):
        query = (request.query_params.get("search") or request.query_params.get("query") or "").strip()
        queryset = self._get_dropdown_queryset(query=query, category_name="accessories")
        page, page_size = self._parse_dropdown_pagination(request)

        start = (page - 1) * page_size
        end = start + page_size
        serializer = ProductDropdownSerializer(queryset[start:end], many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Products retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="accesories-dropdown")
    def accesories_dropdown(self, request, *args, **kwargs):
        return self.accessories_dropdown(request, *args, **kwargs)
