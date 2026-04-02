from rest_framework import filters

from apps.inventory.models import Brand, Category, Finish, Grade, Material, Product, Size, Thickness, Unit

from ..serializers import (
    BrandSerializer,
    CategorySerializer,
    FinishSerializer,
    GradeSerializer,
    MaterialSerializer,
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
        "category__name",
        "brand__name",
        "material__name",
        "size__name",
        "thickness__name",
        "grade__name",
        "finish__name",
        "unit__name",
    ]
    ordering_fields = ["id", "name", "sku", "price", "created_at", "updated_at"]
    ordering = ["name"]
    permission_prefix = "procurement.materials"
