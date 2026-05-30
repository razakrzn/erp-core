from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from apps.inventory.models import PurchaseOrder, PurchaseOrderLineItem
from core.utils.responses import build_actions


class PurchaseOrderLineItemSerializer(serializers.ModelSerializer):
    purchase_request_number = serializers.CharField(
        source="purchase_requisition.purchase_request_number",
        read_only=True,
    )

    class Meta:
        model = PurchaseOrderLineItem
        fields = [
            "id",
            "purchase_order",
            "product_code",
            "purchase_requisition",
            "purchase_request_number",
            "description",
            "unit",
            "requested_qty",
            "required_by_date",
            "delivery_location",
            "last_purchase_rate",
            "negotiated_price",
            "line_total",
        ]
        read_only_fields = ["line_total", "purchase_order"]
        extra_kwargs = {
            "purchase_requisition": {"required": False, "write_only": True},
        }


class PurchaseOrderSerializer(serializers.ModelSerializer):
    line_items = PurchaseOrderLineItemSerializer(source="po_line_items", many=True, required=False)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    actions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "po_number",
            "vendor",
            "associated_job",
            "payment_terms",
            "shipping_delivery_terms",
            "po_issued_date",
            "internal_remarks",
            "status",
            "is_approved",
            "is_rejected",
            "reject_note",
            "net_amount",
            "vat_amount",
            "grand_total",
            "created_by",
            "created_by_name",
            "updated_by",
            "confirmed_by",
            "created_at",
            "updated_at",
            "line_items",
            "actions",
        ]
        read_only_fields = [
            "po_number",
            "net_amount",
            "vat_amount",
            "grand_total",
            "created_by",
            "created_by_name",
            "updated_by",
            "confirmed_by",
            "created_at",
            "updated_at",
        ]

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return None
        return obj.created_by.get_full_name() or obj.created_by.get_username()

    def get_actions(self, obj):
        request = self.context.get("request")
        view = self.context.get("view")

        if not request or not view or getattr(view, "action", None) != "retrieve":
            return None

        computed_actions = build_actions(request.user, getattr(view, "permission_prefix", ""))
        return {
            "canApprove": bool(computed_actions.get("canApprove", False)),
            "canReject": bool(computed_actions.get("canReject", False)),
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("actions") is None:
            data.pop("actions", None)
        return data

    @staticmethod
    def _recalculate_totals(instance):
        net_amount = sum((line.line_total for line in instance.po_line_items.all()), Decimal("0.00"))
        instance.net_amount = net_amount
        instance.vat_amount = net_amount * PurchaseOrder.VAT_RATE
        instance.grand_total = instance.net_amount + instance.vat_amount
        instance.save(update_fields=["net_amount", "vat_amount", "grand_total", "updated_at"])

    def create(self, validated_data):
        line_items_data = validated_data.pop("po_line_items", [])
        with transaction.atomic():
            purchase_order = PurchaseOrder.objects.create(**validated_data)
            for item_data in line_items_data:
                PurchaseOrderLineItem.objects.create(purchase_order=purchase_order, **item_data)
            self._recalculate_totals(purchase_order)
        return purchase_order

    def update(self, instance, validated_data):
        line_items_data = validated_data.pop("po_line_items", None)
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if line_items_data is not None:
                instance.po_line_items.all().delete()
                for item_data in line_items_data:
                    PurchaseOrderLineItem.objects.create(purchase_order=instance, **item_data)
            self._recalculate_totals(instance)
        return instance


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    vendor = serializers.SerializerMethodField(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "po_number",
            "vendor",
            "po_issued_date",
            "status",
            "net_amount",
            "grand_total",
            "created_by_name",
        ]

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return None
        return obj.created_by.get_full_name() or obj.created_by.get_username()

    def get_vendor(self, obj):
        if not obj.vendor:
            return ""
        return obj.vendor.trade_name or ""
