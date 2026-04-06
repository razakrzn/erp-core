from django.contrib import admin

from .models import (
    Brand,
    Category,
    Finish,
    Grade,
    Material,
    Product,
    PurchaseRequisition,
    PurchaseRequisitionLineItem,
    Size,
    Thickness,
    Unit,
    Vendor,
)


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
    list_display = (
        "name",
        "sku",
        "product_code",
        "status",
        "price",
        "standard_cost",
        "opening_stock",
        "preferred_supplier",
        "category",
        "brand",
        "material",
        "unit",
    )
    list_filter = ("status", "category", "brand", "material", "grade", "finish", "unit", "preferred_supplier")
    search_fields = ("name", "sku", "product_code", "hsn_sac_code", "preferred_supplier__legal_trade_name")


class PurchaseRequisitionLineItemInline(admin.TabularInline):
    model = PurchaseRequisitionLineItem
    extra = 0
    autocomplete_fields = ("product",)
    readonly_fields = ("net_required_qty", "line_total")


@admin.register(PurchaseRequisition)
class PurchaseRequisitionAdmin(admin.ModelAdmin):
    list_display = (
        "purchase_request_number",
        "stock_reason_category",
        "required_by_date",
        "priority",
        "status",
        "created_by",
        "total_value",
        "created_at",
    )
    list_filter = ("status", "priority", "required_by_date", "created_at")
    search_fields = (
        "purchase_request_number",
        "id",
        "stock_reason_category",
        "delivery_location",
        "created_by__username",
    )
    readonly_fields = (
        "purchase_request_number",
        "estimated_subtotal",
        "vat_amount",
        "total_value",
        "created_at",
        "updated_at",
    )
    inlines = (PurchaseRequisitionLineItemInline,)


@admin.register(PurchaseRequisitionLineItem)
class PurchaseRequisitionLineItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "purchase_requisition",
        "product",
        "requested_qty",
        "net_required_qty",
        "line_total",
    )
    list_filter = ("purchase_requisition__status",)
    search_fields = ("purchase_requisition__id", "product__name", "product__sku")
    readonly_fields = ("net_required_qty", "line_total")
