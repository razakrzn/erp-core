from rest_framework import serializers

from apps.inventory.models import (
    Brand,
    Category,
    Finish,
    Grade,
    Material,
    Product,
    Size,
    Thickness,
    Unit,
)


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
            "stock_on_hand",
            "reserved",
            "available",
            "stock_value_aed",
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
        read_only_fields = ["stock_on_hand"]

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
        return related_obj.trade_name if related_obj else None

    def create(self, validated_data):
        if ("stock_on_hand" not in validated_data or validated_data.get("stock_on_hand") is None) and (
            validated_data.get("opening_stock") is not None
        ):
            validated_data["stock_on_hand"] = validated_data["opening_stock"]
        return super().create(validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "product_code",
            "name",
            "category_name",
            "brand_name",
            "unit_name",
            "status",
            "stock_on_hand",
            "reserved",
            "available",
            "reorder_level",
            "stock_value_aed",
        ]

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_brand_name(self, obj):
        return obj.brand.name if obj.brand else None

    def get_unit_name(self, obj):
        return obj.unit.name if obj.unit else None


class ProductDropdownSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="id", read_only=True)
    product_name = serializers.CharField(source="name", read_only=True)
    product_price = serializers.DecimalField(source="price", max_digits=12, decimal_places=2, read_only=True)
    product_brand = serializers.CharField(source="brand.name", read_only=True)
    product_size = serializers.CharField(source="size.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "product_price",
            "product_brand",
            "product_size",
        ]
