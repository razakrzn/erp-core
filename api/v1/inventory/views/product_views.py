from decimal import Decimal
from calendar import monthrange
from datetime import date

from django.db.models import DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.dateparse import parse_date
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import filters, serializers, status
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
    ProductFilterDropdownOptionSerializer,
    ProductFilterOptionSerializer,
    ProductListSerializer,
    ProductSerializer,
    SizeSerializer,
    ThicknessSerializer,
    UnitSerializer,
)
from .shared import BaseInventoryViewSet


PRODUCT_FILTER_OPTIONS_RESPONSE_SERIALIZER = inline_serializer(
    name="ProductFilterOptionsSuccessResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": ProductFilterOptionSerializer(many=True),
        "status_code": serializers.IntegerField(),
        "timestamp": serializers.DateTimeField(),
    },
)

PRODUCT_CATEGORY_DROPDOWN_RESPONSE_SERIALIZER = inline_serializer(
    name="ProductCategoryDropdownSuccessResponse",
    fields={
        "success": serializers.BooleanField(),
        "message": serializers.CharField(),
        "data": ProductFilterDropdownOptionSerializer(many=True),
        "status_code": serializers.IntegerField(),
        "timestamp": serializers.DateTimeField(),
    },
)

PRODUCT_DATE_RANGE_OPTIONS = [
    {"value": "yearly", "label": "Yearly"},
    {"value": "half_yearly", "label": "Half-Yearly"},
    {"value": "quarterly", "label": "Quarterly"},
    {"value": "monthly", "label": "Monthly"},
    {"value": "custom_range", "label": "Custom Range"},
]
PRODUCT_STOCK_STATUS_OPTIONS = [
    {"value": "all", "label": "All"},
    {"value": "in_stock", "label": "In Stock"},
    {"value": "low_stock", "label": "Low Stock"},
    {"value": "out_of_stock", "label": "Out of Stock"},
]
PRODUCT_SORT_BY_OPTIONS = [
    {"value": "name_asc", "label": "Name (A→Z)"},
    {"value": "name_desc", "label": "Name (Z→A)"},
    {"value": "stock_high_low", "label": "Stock (High→Low)"},
    {"value": "stock_low_high", "label": "Stock (Low→High)"},
    {"value": "stock_value_high_low", "label": "Stock Value (High→Low)"},
]


class BaseInventoryLookupViewSet(BaseInventoryViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "created_at", "updated_at"]
    ordering = ["name"]
    permission_prefix = "procurement.material_settings"


class CategoryViewSet(BaseInventoryLookupViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @extend_schema(
        summary="List active product category dropdown options",
        description=(
            "Returns unique product categories used by active products, sorted alphabetically, "
            "in the standard value/label dropdown format."
        ),
        parameters=[
            OpenApiParameter(
                name="search",
                type=str,
                required=False,
                description="Optional case-insensitive category name search.",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=PRODUCT_CATEGORY_DROPDOWN_RESPONSE_SERIALIZER,
                description="Active product categories retrieved successfully.",
                examples=[
                    OpenApiExample(
                        "Category dropdown response",
                        value={
                            "success": True,
                            "message": "Product categories retrieved successfully.",
                            "data": [
                                {"value": "Accessories", "label": "Accessories"},
                                {"value": "sheet", "label": "sheet"},
                            ],
                            "status_code": 200,
                            "timestamp": "2026-06-03T09:27:26.848301+00:00",
                        },
                    )
                ],
            )
        },
    )
    @action(detail=False, methods=["get"], url_path="categories-dropdown")
    def categories_dropdown(self, request, *args, **kwargs):
        query = (request.query_params.get("search") or request.query_params.get("query") or "").strip()
        queryset = (
            Category.objects.filter(products__status__iexact="active")
            .exclude(name__isnull=True)
            .exclude(name__exact="")
            .values_list("name", flat=True)
            .distinct()
            .order_by("name")
        )
        if query:
            queryset = queryset.filter(name__icontains=query)

        options = [{"value": value, "label": value} for value in queryset]
        serializer = ProductFilterDropdownOptionSerializer(data=options, many=True)
        serializer.is_valid(raise_exception=True)
        return APIResponse.success(
            data=serializer.validated_data,
            message="Product categories retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


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
        "purchased_stock",
        "stock_on_hand",
        "opening_stock_date",
        "created_at",
        "updated_at",
    ]
    ordering = ["name"]
    permission_prefix = "procurement.materials"

    @staticmethod
    def _parse_filter_tokens(request, *param_names):
        tokens = []
        for name in param_names:
            for value in request.query_params.getlist(name):
                if value:
                    tokens.extend(item.strip() for item in value.split(",") if item.strip())
        return tokens

    @staticmethod
    def _period_date_range(period_name):
        today = timezone.localdate()
        normalized = (period_name or "").strip().lower().replace("_", " ").replace("-", " ")

        if normalized == "yearly":
            return date(today.year, 1, 1), date(today.year, 12, 31)
        if normalized in {"half yearly", "halfyearly"}:
            start_month = 1 if today.month <= 6 else 7
            end_month = start_month + 5
            return date(today.year, start_month, 1), date(today.year, end_month, monthrange(today.year, end_month)[1])
        if normalized == "quarterly":
            start_month = ((today.month - 1) // 3) * 3 + 1
            end_month = start_month + 2
            return date(today.year, start_month, 1), date(today.year, end_month, monthrange(today.year, end_month)[1])
        if normalized == "monthly":
            return date(today.year, today.month, 1), date(today.year, today.month, monthrange(today.year, today.month)[1])
        return None

    def _filter_by_date_range(self, queryset):
        date_range = (self.request.query_params.get("date_range") or "").strip()
        normalized = date_range.lower().replace("_", " ").replace("-", " ")
        if normalized in {"custom range", "custom"}:
            start_date = parse_date(
                self.request.query_params.get("start_date")
                or self.request.query_params.get("from_date")
                or ""
            )
            end_date = parse_date(
                self.request.query_params.get("end_date")
                or self.request.query_params.get("to_date")
                or ""
            )
            if start_date:
                queryset = queryset.filter(created_at__date__gte=start_date)
            if end_date:
                queryset = queryset.filter(created_at__date__lte=end_date)
            return queryset

        period = self._period_date_range(date_range)
        if period:
            queryset = queryset.filter(created_at__date__range=period)
        return queryset

    def _filter_by_category(self, queryset):
        tokens = self._parse_filter_tokens(self.request, "category", "categories")
        if not tokens:
            return queryset

        category_ids = [int(token) for token in tokens if token.isdigit()]
        category_names = [token for token in tokens if not token.isdigit()]
        category_filter = Q()
        if category_ids:
            category_filter |= Q(category_id__in=category_ids)
        if category_names:
            category_filter |= Q(category__name__in=category_names)
        return queryset.filter(category_filter)

    def _filter_by_stock_status(self, queryset):
        stock_status = (self.request.query_params.get("stock_status") or "").strip().lower().replace("_", " ")
        if stock_status in {"in stock", "instock"}:
            return queryset.filter(stock_on_hand__gt=F("reorder_level"))
        if stock_status in {"low stock", "lowstock"}:
            return queryset.filter(stock_on_hand__gt=0, stock_on_hand__lte=F("reorder_level"))
        if stock_status in {"out of stock", "outofstock"}:
            return queryset.filter(stock_on_hand__lte=0)
        return queryset

    def _sort_products(self, queryset):
        sort_by = (self.request.query_params.get("sort_by") or "").strip().lower()
        ordering_map = {
            "name (a→z)": "name",
            "name (a-z)": "name",
            "name_asc": "name",
            "name (z→a)": "-name",
            "name (z-a)": "-name",
            "name_desc": "-name",
            "stock (high→low)": "-stock_on_hand",
            "stock (high-low)": "-stock_on_hand",
            "stock_high_low": "-stock_on_hand",
            "stock (low→high)": "stock_on_hand",
            "stock (low-high)": "stock_on_hand",
            "stock_low_high": "stock_on_hand",
            "stock value (high→low)": "-stock_value_aed",
            "stock value (high-low)": "-stock_value_aed",
            "stock_value_high_low": "-stock_value_aed",
        }
        ordering = ordering_map.get(sort_by)
        return queryset.order_by(ordering) if ordering else queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        grn_id = (params.get("grn_id") or params.get("goods_receipt_id") or "").strip()
        if grn_id:
            queryset = queryset.filter(goods_receipt_items__goods_receipt_id=grn_id)

        has_grn_intake = (
            params.get("has_grn_intake")
            or params.get("grn_intake")
            or params.get("purchased")
            or ""
        )
        normalized = str(has_grn_intake).strip().lower()
        if normalized in {"true", "1", "yes"}:
            queryset = queryset.filter(goods_receipt_items__isnull=False)
        elif normalized in {"false", "0", "no"}:
            queryset = queryset.filter(goods_receipt_items__isnull=True)

        queryset = self._filter_by_date_range(queryset)
        queryset = self._filter_by_category(queryset)
        queryset = self._filter_by_stock_status(queryset)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductSerializer

    @staticmethod
    def _build_inventory_summary(queryset):
        decimal_output = DecimalField(max_digits=18, decimal_places=2)
        totals = queryset.aggregate(
            total_stock_value=Coalesce(
                Sum("stock_value_aed", output_field=decimal_output),
                Value(Decimal("0.00")),
                output_field=decimal_output,
            ),
            total_qty_on_hand=Coalesce(
                Sum("stock_on_hand", output_field=decimal_output),
                Value(Decimal("0.00")),
                output_field=decimal_output,
            ),
        )
        return {
            "total_products": {
                "value": queryset.count(),
                "label": "Total Products",
            },
            "total_stock_value": {
                "value": totals["total_stock_value"],
                "currency": "AED",
                "label": "Total Stock Value",
            },
            "low_stock_items": {
                "value": queryset.filter(
                    stock_on_hand__gt=0,
                    stock_on_hand__lte=F("reorder_level"),
                ).count(),
                "label": "Low Stock Items",
            },
            "out_of_stock": {
                "value": queryset.filter(stock_on_hand__lte=0).count(),
                "label": "Out of Stock",
            },
            "total_qty_on_hand": {
                "value": totals["total_qty_on_hand"],
                "label": "Total Qty On Hand",
            },
        }

    @extend_schema(
        summary="List products",
        description="Lists products with inventory summary and supports product inventory filtering and sorting.",
        parameters=[
            OpenApiParameter(
                name="date_range",
                type=str,
                required=False,
                enum=["yearly", "half_yearly", "quarterly", "monthly", "custom_range"],
                description="Filters products by creation date. Use start_date/end_date with Custom Range.",
            ),
            OpenApiParameter(name="start_date", type=date, required=False, description="Custom range start date (YYYY-MM-DD)."),
            OpenApiParameter(name="end_date", type=date, required=False, description="Custom range end date (YYYY-MM-DD)."),
            OpenApiParameter(
                name="category",
                type=str,
                required=False,
                description="Category ID or category label. Supports comma-separated or repeated values.",
            ),
            OpenApiParameter(
                name="stock_status",
                type=str,
                required=False,
                enum=["all", "in_stock", "low_stock", "out_of_stock"],
                description="Filters products by current stock status.",
            ),
            OpenApiParameter(
                name="sort_by",
                type=str,
                required=False,
                enum=["name_asc", "name_desc", "stock_high_low", "stock_low_high", "stock_value_high_low"],
                description="Applies the selected frontend sort option.",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = self._sort_products(queryset)
        inventory_summary = self._build_inventory_summary(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data["data"]["inventory_summary"] = inventory_summary
            return response

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data={
                "items": serializer.data,
                "inventory_summary": inventory_summary,
            },
            message="Products retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="List product filter options",
        description="Returns all frontend filter options supported by the products listing endpoint.",
        responses={
            200: OpenApiResponse(
                response=PRODUCT_FILTER_OPTIONS_RESPONSE_SERIALIZER,
                description="Inventory filter options retrieved successfully.",
                examples=[
                    OpenApiExample(
                        "Inventory filter options response",
                        value={
                            "success": True,
                            "message": "Inventory filter options retrieved successfully.",
                            "data": [
                                {
                                    "key": "date_range",
                                    "label": "Date Filtration",
                                    "options": PRODUCT_DATE_RANGE_OPTIONS,
                                },
                                {
                                    "key": "category",
                                    "label": "Category",
                                    "options_endpoint": "/api/v1/inventory/categories/categories-dropdown/",
                                },
                                {
                                    "key": "stock_status",
                                    "label": "Stock Status",
                                    "options": PRODUCT_STOCK_STATUS_OPTIONS,
                                },
                                {
                                    "key": "sort_by",
                                    "label": "Sort By",
                                    "options": PRODUCT_SORT_BY_OPTIONS,
                                },
                            ],
                            "status_code": 200,
                            "timestamp": "2026-06-03T09:12:45.247065+00:00",
                        },
                    )
                ],
            )
        },
    )
    @action(detail=False, methods=["get"], url_path="filter-options")
    def filter_options(self, request, *args, **kwargs):
        payload = [
            {
                "key": "date_range",
                "label": "Date Filtration",
                "options": PRODUCT_DATE_RANGE_OPTIONS,
            },
            {
                "key": "category",
                "label": "Category",
                "options_endpoint": "/api/v1/inventory/categories/categories-dropdown/",
            },
            {
                "key": "stock_status",
                "label": "Stock Status",
                "options": PRODUCT_STOCK_STATUS_OPTIONS,
            },
            {
                "key": "sort_by",
                "label": "Sort By",
                "options": PRODUCT_SORT_BY_OPTIONS,
            },
        ]
        serializer = ProductFilterOptionSerializer(data=payload, many=True)
        serializer.is_valid(raise_exception=True)
        return APIResponse.success(
            data=serializer.validated_data,
            message="Inventory filter options retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

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
