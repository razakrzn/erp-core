from rest_framework import serializers

from apps.inventory.models import Brand, Category, Finish, Grade, Material, Product, Size, Thickness, Unit


class InventoryLookupSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
        ]


class CategorySerializer(InventoryLookupSerializer):
    class Meta(InventoryLookupSerializer.Meta):
        model = Category


class BrandSerializer(InventoryLookupSerializer):
    class Meta(InventoryLookupSerializer.Meta):
        model = Brand


class MaterialSerializer(InventoryLookupSerializer):
    class Meta(InventoryLookupSerializer.Meta):
        model = Material


class SizeSerializer(InventoryLookupSerializer):
    class Meta(InventoryLookupSerializer.Meta):
        model = Size


class ThicknessSerializer(InventoryLookupSerializer):
    class Meta(InventoryLookupSerializer.Meta):
        model = Thickness


class GradeSerializer(InventoryLookupSerializer):
    class Meta(InventoryLookupSerializer.Meta):
        model = Grade


class FinishSerializer(InventoryLookupSerializer):
    class Meta(InventoryLookupSerializer.Meta):
        model = Finish


class UnitSerializer(InventoryLookupSerializer):
    class Meta(InventoryLookupSerializer.Meta):
        model = Unit


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    material_name = serializers.SerializerMethodField()
    size_name = serializers.SerializerMethodField()
    thickness_name = serializers.SerializerMethodField()
    grade_name = serializers.SerializerMethodField()
    finish_name = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()
    preferred_supplier_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "sku",
            "product_code",
            "status",
            "price",
            "standard_cost",
            "reorder_level",
            "preferred_supplier",
            "preferred_supplier_name",
            "lead_time_days",
            "max_stock_level",
            "moq",
            "opening_stock",
            "opening_stock_date",
            "hsn_sac_code",
            "admin_notes",
            "category",
            "category_name",
            "brand",
            "brand_name",
            "material",
            "material_name",
            "size",
            "size_name",
            "thickness",
            "thickness_name",
            "grade",
            "grade_name",
            "finish",
            "finish_name",
            "unit",
            "unit_name",
            "created_at",
            "updated_at",
        ]

    def _get_related_name(self, obj, field_name):
        related_obj = getattr(obj, field_name, None)
        return related_obj.name if related_obj else None

    def get_category_name(self, obj):
        return self._get_related_name(obj, "category")

    def get_brand_name(self, obj):
        return self._get_related_name(obj, "brand")

    def get_material_name(self, obj):
        return self._get_related_name(obj, "material")

    def get_size_name(self, obj):
        return self._get_related_name(obj, "size")

    def get_thickness_name(self, obj):
        return self._get_related_name(obj, "thickness")

    def get_grade_name(self, obj):
        return self._get_related_name(obj, "grade")

    def get_finish_name(self, obj):
        return self._get_related_name(obj, "finish")

    def get_unit_name(self, obj):
        return self._get_related_name(obj, "unit")

    def get_preferred_supplier_name(self, obj):
        related_obj = getattr(obj, "preferred_supplier", None)
        return related_obj.legal_trade_name if related_obj else None


class ProductListSerializer(serializers.ModelSerializer):
    brand_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "product_code",
            "name",
            "brand_name",
            "status",
        ]

    def get_brand_name(self, obj):
        return obj.brand.name if obj.brand else None


class ProductDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
        ]
