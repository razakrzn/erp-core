from django.contrib import admin

from .models import Brand, Category, Finish, Grade, Material, Product, Size, Thickness, Unit, Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = (
        "legal_trade_name",
        "trade_license_number",
        "tax_registration_number",
        "phone_number",
        "email_address",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "legal_trade_name",
        "trade_license_number",
        "tax_registration_number",
        "email_address",
        "phone_number",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Thickness)
class ThicknessAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Finish)
class FinishAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "price", "category", "brand", "material", "unit")
    list_filter = ("category", "brand", "material", "grade", "finish", "unit")
    search_fields = ("name", "sku")
