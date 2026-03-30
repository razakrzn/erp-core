from rest_framework import serializers

from apps.inventory.models import Brand, Category, Finish, Grade, Material, Size, Thickness


class DropdownOptionSerializer(serializers.Serializer):
    value = serializers.IntegerField(source="id", read_only=True)
    label = serializers.CharField(source="name", read_only=True)


class DropdownOptionWithValueSerializer(DropdownOptionSerializer):
    label = serializers.SerializerMethodField()

    def get_label(self, obj):
        return f"{obj.name} ({obj.value})"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "code", "slug", "description", "is_active", "created_at", "updated_at"]
        read_only_fields = ["code", "slug", "created_at", "updated_at"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "code", "slug", "is_active", "created_at", "updated_at"]
        read_only_fields = ["code", "slug", "created_at", "updated_at"]


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ["id", "name", "code", "slug", "description", "is_active", "created_at", "updated_at"]
        read_only_fields = ["code", "slug", "created_at", "updated_at"]


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["id", "name", "value", "code", "slug", "is_active", "created_at", "updated_at"]
        read_only_fields = ["code", "slug", "created_at", "updated_at"]


class ThicknessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thickness
        fields = ["id", "name", "value", "code", "slug", "is_active", "created_at", "updated_at"]
        read_only_fields = ["code", "slug", "created_at", "updated_at"]


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ["id", "name", "code", "slug", "is_active", "created_at", "updated_at"]
        read_only_fields = ["code", "slug", "created_at", "updated_at"]


class FinishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finish
        fields = ["id", "name", "code", "slug", "is_active", "created_at", "updated_at"]
        read_only_fields = ["code", "slug", "created_at", "updated_at"]
