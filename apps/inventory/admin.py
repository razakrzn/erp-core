from django.contrib import admin

from .models import (
    Adjustment,
    Category,
    Product,
    PurchaseReceipt,
    Stock,
    StockMovement,
    StockTransfer,
    Warehouse,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "product_type", "is_active")
    search_fields = ("name", "sku")
    list_filter = ("is_active", "product_type", "category")


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "location")
    search_fields = ("name", "code", "location")


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "quantity", "reserved_quantity")
    search_fields = ("product__name", "product__sku", "warehouse__name", "warehouse__code")
    list_filter = ("warehouse",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "movement_type", "quantity", "moved_at")
    search_fields = ("product__name", "product__sku", "reference")
    list_filter = ("movement_type", "warehouse", "moved_at")


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ("product", "from_warehouse", "to_warehouse", "quantity", "transferred_at")
    search_fields = ("product__name", "product__sku", "reference")
    list_filter = ("from_warehouse", "to_warehouse", "transferred_at")


@admin.register(PurchaseReceipt)
class PurchaseReceiptAdmin(admin.ModelAdmin):
    list_display = ("reference", "warehouse", "received_at")
    search_fields = ("reference", "warehouse__name", "warehouse__code")
    list_filter = ("warehouse", "received_at")


@admin.register(Adjustment)
class AdjustmentAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "quantity_delta", "reason", "adjusted_at")
    search_fields = ("product__name", "product__sku", "reason")
    list_filter = ("warehouse", "adjusted_at")
