from apps.inventory.models import Brand, Category, Finish, Grade, Material, Size, Thickness
from ..serializers import (
    BrandSerializer,
    CategorySerializer,
    DropdownOptionWithValueSerializer,
    FinishSerializer,
    GradeSerializer,
    MaterialSerializer,
    SizeSerializer,
    ThicknessSerializer,
)
from .shared import BaseInventoryMasterViewSet


class CategoryViewSet(BaseInventoryMasterViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ["name", "code", "slug", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]
    permission_prefix = "procurement.material_settings"


class BrandViewSet(BaseInventoryMasterViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    search_fields = ["name", "code", "slug"]
    ordering_fields = ["name", "created_at", "updated_at"]
    permission_prefix = "procurement.material_settings"


class MaterialViewSet(BaseInventoryMasterViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    search_fields = ["name", "code", "slug", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]
    permission_prefix = "procurement.material_settings"


class SizeViewSet(BaseInventoryMasterViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    dropdown_serializer_class = DropdownOptionWithValueSerializer
    dropdown_queryset_fields = ("id", "name", "value", "code")
    dropdown_search_fields = ("name", "value", "code")
    search_fields = ["name", "value", "code", "slug"]
    ordering_fields = ["name", "created_at", "updated_at"]
    dropdown_product_relation = "product_set"
    permission_prefix = "procurement.material_settings"


class ThicknessViewSet(BaseInventoryMasterViewSet):
    queryset = Thickness.objects.all()
    serializer_class = ThicknessSerializer
    dropdown_serializer_class = DropdownOptionWithValueSerializer
    dropdown_queryset_fields = ("id", "name", "value", "code")
    dropdown_search_fields = ("name", "value", "code")
    search_fields = ["name", "code", "slug"]
    ordering_fields = ["name", "created_at", "updated_at"]
    dropdown_product_relation = "product_set"
    permission_prefix = "procurement.material_settings"


class GradeViewSet(BaseInventoryMasterViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    search_fields = ["name", "code", "slug"]
    ordering_fields = ["name", "created_at", "updated_at"]
    dropdown_product_relation = "product"
    permission_prefix = "procurement.material_settings"


class FinishViewSet(BaseInventoryMasterViewSet):
    queryset = Finish.objects.all()
    serializer_class = FinishSerializer
    search_fields = ["name", "code", "slug"]
    ordering_fields = ["name", "created_at", "updated_at"]
    dropdown_product_relation = "product_set"
    permission_prefix = "procurement.material_settings"
