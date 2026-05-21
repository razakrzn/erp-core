from django import forms
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


class PurchaseOrderLineItemInlineForm(forms.ModelForm):
    requisition_line_item = forms.ModelChoiceField(
        queryset=PurchaseRequisitionLineItem.objects.select_related("purchase_requisition").filter(
            purchase_requisition__is_approved=True
        ),
        required=False,
        label="Approved Purchase Requisition Line Item",
    )

    class Meta:
        model = PurchaseOrderLineItem
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["requisition_line_item"].label_from_instance = self._format_requisition_line_item

    @staticmethod
    def _format_requisition_line_item(item):
        pr_number = item.purchase_requisition.purchase_request_number if item.purchase_requisition else "PR-N/A"
        product = item.product_name or item.product_code or f"Line {item.pk}"
        qty = item.requested_qty if item.requested_qty is not None else "-"
        return f"{pr_number} | {product} | Qty: {qty}"

    def save(self, commit=True):
        instance = super().save(commit=False)
        line_item = self.cleaned_data.get("requisition_line_item")
        if line_item:
            requisition = line_item.purchase_requisition
            instance.product_code = line_item.product_code
            instance.description = line_item.product_name
            instance.unit = line_item.unit
            instance.requested_qty = line_item.requested_qty
            if requisition:
                instance.required_by_date = requisition.required_by_date
                instance.delivery_location = requisition.delivery_location
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class VendorContactInline(admin.TabularInline):
    model = VendorContact
    extra = 1


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = (
        "trade_name",
        "category",
        "license_no",
        "trn_number",
        "phone",
        "email",
        "status",
    )
    list_filter = ("status", "category", "vendor_type", "city_emirate")
    search_fields = (
        "trade_name",
        "category",
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
    fields = (
        "product_id",
        "product_code",
        "product_name",
        "product_category",
        "unit",
        "stock_on_hand",
        "pending_pr_qty",
        "pending_po_qty",
        "requested_qty",
        "net_required_qty",
    )
    readonly_fields = ("net_required_qty",)


@admin.register(PurchaseRequisition)
class PurchaseRequisitionAdmin(admin.ModelAdmin):
    list_display = (
        "purchase_request_number",
        "requisition_date",
        "requisition_type",
        "stock_reason_category",
        "job_order_ref",
        "rework_notes",
        "required_by_date",
        "delivery_location",
        "priority",
        "status",
        "created_by",
        "created_at",
    )
    list_filter = (
        "status",
        "is_approved",
        "is_rejected",
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
        "job_order_ref",
        "rework_notes",
        "delivery_location",
        "reason_description",
        "notes_to_purchase_team",
        "created_by__username",
    )
    readonly_fields = (
        "purchase_request_number",
        "status",
        "created_by",
        "updated_by",
        "approved_by",
        "rejected_by",
        "created_at",
        "updated_at",
    )
    inlines = (PurchaseRequisitionLineItemInline,)

    def save_model(self, request, obj, form, change):
        was_approved = False
        if change and obj.pk:
            previous = PurchaseRequisition.objects.filter(pk=obj.pk).only("is_approved").first()
            was_approved = bool(previous and previous.is_approved)

        user = request.user if request.user and request.user.is_authenticated else None
        if obj.is_approved:
            obj.is_rejected = False
            obj.reject_note = ""
            obj.rejected_by = None
            if user:
                obj.approved_by = user
        elif obj.is_rejected:
            obj.is_approved = False
            obj.approved_by = None
            if user:
                obj.rejected_by = user
        else:
            obj.approved_by = None
            obj.rejected_by = None

        super().save_model(request, obj, form, change)

        if obj.is_approved and not was_approved:
            obj.ensure_production_order()


@admin.register(PurchaseRequisitionLineItem)
class PurchaseRequisitionLineItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "purchase_requisition",
        "product_id",
        "product_name",
        "product_code",
        "product_category",
        "unit",
        "requested_qty",
        "net_required_qty",
    )
    list_filter = (
        "product_category",
        "product_name",
        "unit",
        "purchase_requisition__required_by_date",
        "purchase_requisition__priority",
        "purchase_requisition__status",
    )
    search_fields = (
        "purchase_requisition__purchase_request_number",
        "purchase_requisition__id",
        "product_id",
        "product_name",
        "product_code",
        "product_category",
    )
    readonly_fields = ("net_required_qty",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("purchase_requisition").filter(purchase_requisition__is_approved=True)


class PurchaseOrderLineItemInline(admin.TabularInline):
    model = PurchaseOrderLineItem
    form = PurchaseOrderLineItemInlineForm
    extra = 1
    fields = (
        "requisition_line_item",
        "product_code",
        "purchase_requisition",
        "description",
        "unit",
        "requested_qty",
        "required_by_date",
        "delivery_location",
        "last_purchase_rate",
        "negotiated_price",
        "line_total",
    )
    readonly_fields = ("line_total",)


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        "po_number",
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
    inlines = (PurchaseOrderLineItemInline,)


@admin.register(PurchaseOrderLineItem)
class PurchaseOrderLineItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "purchase_order",
        "product_code",
        "purchase_requisition",
        "description",
        "unit",
        "requested_qty",
        "required_by_date",
        "delivery_location",
        "last_purchase_rate",
        "negotiated_price",
        "line_total",
    )
    list_filter = ("required_by_date", "purchase_order__status")
    search_fields = (
        "purchase_order__po_number",
        "product_code",
        "description",
        "purchase_requisition__purchase_request_number",
        "delivery_location",
        "unit",
    )
    readonly_fields = ("line_total",)
