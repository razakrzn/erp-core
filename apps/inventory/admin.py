from django.contrib import admin

from .models import (
    Brand,
    Category,
    Finish,
    Grade,
    Material,
    Product,
    PurchaseOrder,
    PurchaseOrderLineItem,
    PurchaseRequisition,
    PurchaseRequisitionLineItem,
    Size,
    Thickness,
    Unit,
    Vendor,
    VendorContact,
)


class VendorContactInline(admin.TabularInline):
    model = VendorContact
    extra = 1


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = (
        "trade_name",
        "license_no",
        "trn_number",
        "phone",
        "email",
        "status",
    )
    list_filter = ("status", "vendor_type", "city_emirate")
    search_fields = (
        "trade_name",
        "license_no",
        "trn_number",
        "email",
        "phone",
    )
    inlines = [VendorContactInline]


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
    search_fields = ("name", "sku", "product_code", "hsn_sac_code", "preferred_supplier__trade_name")


class PurchaseRequisitionLineItemInline(admin.TabularInline):
    model = PurchaseRequisitionLineItem
    extra = 0
    readonly_fields = ("net_required_qty",)


@admin.register(PurchaseRequisition)
class PurchaseRequisitionAdmin(admin.ModelAdmin):
    list_display = (
        "purchase_request_number",
        "requisition_date",
        "requisition_type",
        "stock_reason_category",
        "project_site",
        "job_order_ref",
        "required_by_date",
        "delivery_location",
        "priority",
        "status",
        "created_by",
        "created_at",
    )
    list_filter = (
        "status",
        "requisition_type",
        "priority",
        "delivery_location",
        "required_by_date",
        "created_at",
    )
    search_fields = (
        "purchase_request_number",
        "id",
        "stock_reason_category",
        "project_site",
        "job_order_ref",
        "delivery_location",
        "created_by__username",
    )
    readonly_fields = (
        "purchase_request_number",
        "created_at",
        "updated_at",
    )
    inlines = (PurchaseRequisitionLineItemInline,)


@admin.register(PurchaseRequisitionLineItem)
class PurchaseRequisitionLineItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "purchase_requisition",
        "product_name",
        "product_code",
        "requested_qty",
        "net_required_qty",
    )
    list_filter = ("purchase_requisition__status",)
    search_fields = ("purchase_requisition__id", "product_name", "product_code")
    readonly_fields = ("net_required_qty",)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        "po_number",
        "purchase_requisition",
        "vendor",
        "po_issued_date",
        "status",
        "net_amount",
        "vat_amount",
        "grand_total",
        "created_by",
        "created_at",
    )
    list_filter = ("status", "po_issued_date", "created_at", "is_confirmed", "is_closed")
    search_fields = ("po_number", "vendor__trade_name", "created_by__username")
    readonly_fields = ("po_number", "created_at", "updated_at")


@admin.register(PurchaseOrderLineItem)
class PurchaseOrderLineItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "purchase_order",
        "product",
        "qty",
        "negotiated_price",
        "line_total",
        "required_by",
    )
    list_filter = ("required_by", "purchase_order__status")
    search_fields = (
        "purchase_order__po_number",
        "product__name",
        "product__sku",
        "delivery_location",
        "unit",
    )
    readonly_fields = ("line_total",)
