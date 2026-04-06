from rest_framework import filters

from apps.inventory.models import PurchaseRequisition, PurchaseRequisitionLineItem

from ..serializers import (
    PurchaseRequisitionLineItemSerializer,
    PurchaseRequisitionListSerializer,
    PurchaseRequisitionSerializer,
)
from .shared import BaseInventoryViewSet


class PurchaseRequisitionViewSet(BaseInventoryViewSet):
    queryset = PurchaseRequisition.objects.select_related("created_by").prefetch_related("line_items__product")
    serializer_class = PurchaseRequisitionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "stock_reason_category",
        "priority",
        "status",
        "delivery_location",
        "created_by__username",
    ]
    ordering_fields = [
        "id",
        "required_by_date",
        "priority",
        "status",
        "estimated_subtotal",
        "vat_amount",
        "total_value",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]
    permission_prefix = "procurement.purchase_requisitions"

    def get_serializer_class(self):
        if self.action == "list":
            return PurchaseRequisitionListSerializer
        return PurchaseRequisitionSerializer


class PurchaseRequisitionLineItemViewSet(BaseInventoryViewSet):
    queryset = PurchaseRequisitionLineItem.objects.select_related("purchase_requisition", "product")
    serializer_class = PurchaseRequisitionLineItemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "purchase_requisition__id",
        "product__name",
        "product__sku",
    ]
    ordering_fields = [
        "id",
        "purchase_requisition_id",
        "product_id",
        "requested_qty",
        "net_required_qty",
        "line_total",
    ]
    ordering = ["id"]
    permission_prefix = "procurement.purchase_requisitions"
