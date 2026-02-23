from django.contrib import admin

from .models import Brand, Category, Finish, Grade, Material, Product, Size, Thickness


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "updated_at")
    search_fields = ("name", "code", "slug")
    list_filter = ("is_active",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "updated_at")
    search_fields = ("name", "code", "slug")
    list_filter = ("is_active",)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "updated_at")
    search_fields = ("name", "code", "slug")
    list_filter = ("is_active",)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "code", "is_active", "updated_at")
    search_fields = ("name", "value", "code", "slug")
    list_filter = ("is_active",)


@admin.register(Thickness)
class ThicknessAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "code", "is_active", "updated_at")
    search_fields = ("name", "code", "slug")
    list_filter = ("is_active",)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "updated_at")
    search_fields = ("name", "code", "slug")
    list_filter = ("is_active",)


@admin.register(Finish)
class FinishAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "updated_at")
    search_fields = ("name", "code", "slug")
    list_filter = ("is_active",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "price",
        "category",
        "brand",
        "material",
        "size",
        "thickness",
        "grade",
        "finish",
        "is_active",
        "updated_at",
    )
    search_fields = ("name", "sku")
    list_filter = (
        "is_active",
        "category",
        "brand",
        "material",
        "size",
        "thickness",
        "grade",
        "finish",
    )
