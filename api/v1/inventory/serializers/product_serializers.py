from rest_framework import serializers

from apps.inventory.models import Product


class ProductDropdownSerializer(serializers.Serializer):
    value = serializers.IntegerField(source='id', read_only=True)
    label = serializers.CharField(source='name', read_only=True)


class ProductNameFieldsSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    material_name = serializers.SerializerMethodField()
    size_name = serializers.SerializerMethodField()
    thickness_name = serializers.SerializerMethodField()
    grade_name = serializers.SerializerMethodField()
    finish_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'sku',
            'price',
            'category',
            'category_name',
            'brand',
            'brand_name',
            'material',
            'material_name',
            'size',
            'size_name',
            'thickness',
            'thickness_name',
            'grade',
            'grade_name',
            'finish',
            'finish_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['sku', 'created_at', 'updated_at']

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_brand_name(self, obj):
        return obj.brand.name if obj.brand else None

    def get_material_name(self, obj):
        return obj.material.name if obj.material else None

    def get_size_name(self, obj):
        return obj.size.name if obj.size else None

    def get_thickness_name(self, obj):
        return obj.thickness.name if obj.thickness else None

    def get_grade_name(self, obj):
        return obj.grade.name if obj.grade else None

    def get_finish_name(self, obj):
        return obj.finish.name if obj.finish else None


class ProductSerializer(ProductNameFieldsSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'sku',
            'price',
            'category',
            'category_name',
            'brand',
            'brand_name',
            'material',
            'material_name',
            'size',
            'size_name',
            'thickness',
            'thickness_name',
            'grade',
            'grade_name',
            'finish',
            'finish_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['sku', 'created_at', 'updated_at']


class ProductListSerializer(ProductNameFieldsSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'sku',
            'price',
            'category_name',
            'brand_name',
            'material_name',
            'size_name',
            'thickness_name',
            'grade_name',
            'finish_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
