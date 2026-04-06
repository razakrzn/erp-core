from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from apps.inventory.models import Product, PurchaseRequisition, PurchaseRequisitionLineItem


class PurchaseRequisitionLineItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchaseRequisitionLineItem
        fields = [
            "id",
            "purchase_requisition",
            "product",
            "product_name",
            "stock_on_hand",
            "pending_pr_qty",
            "pending_po_qty",
            "requested_qty",
            "net_required_qty",
            "line_total",
        ]
        read_only_fields = ["net_required_qty", "line_total"]
        extra_kwargs = {
            "purchase_requisition": {"required": False},
        }

    def get_product_name(self, obj):
        return obj.product.name if obj.product else None


class PurchaseRequisitionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField(read_only=True)
    line_items = PurchaseRequisitionLineItemSerializer(many=True, required=False)

    class Meta:
        model = PurchaseRequisition
        fields = [
            "id",
            "purchase_request_number",
            "stock_reason_category",
            "required_by_date",
            "priority",
            "delivery_location",
            "reason_description",
            "notes_to_purchase_team",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "estimated_subtotal",
            "vat_amount",
            "total_value",
            "line_items",
        ]
        read_only_fields = [
            "purchase_request_number",
            "created_by",
            "created_at",
            "updated_at",
            "estimated_subtotal",
            "vat_amount",
            "total_value",
        ]

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return None
        return obj.created_by.get_full_name() or obj.created_by.get_username()

    def _calculate_totals(self, requisition):
        line_items = requisition.line_items.all()
        subtotal = sum((item.line_total for item in line_items), Decimal("0.00"))
        vat_amount = (subtotal * requisition.VAT_RATE).quantize(Decimal("0.01"))
        total_value = (subtotal + vat_amount).quantize(Decimal("0.01"))
        requisition.estimated_subtotal = subtotal
        requisition.vat_amount = vat_amount
        requisition.total_value = total_value
        requisition.save(update_fields=["estimated_subtotal", "vat_amount", "total_value", "updated_at"])

    @staticmethod
    def _line_total_from_payload(item_data):
        requested_qty = item_data.get("requested_qty") or Decimal("0.00")
        product_id = item_data.get("product")
        if not product_id:
            return Decimal("0.00")

        product = Product.objects.filter(pk=product_id).only("price").first()
        if not product:
            return Decimal("0.00")
        return (requested_qty * (product.price or Decimal("0.00"))).quantize(Decimal("0.01"))

    def create(self, validated_data):
        line_items_data = validated_data.pop("line_items", [])

        with transaction.atomic():
            requisition = PurchaseRequisition.objects.create(**validated_data)
            for item_data in line_items_data:
                item_data["line_total"] = self._line_total_from_payload(item_data)
                PurchaseRequisitionLineItem.objects.create(purchase_requisition=requisition, **item_data)
            self._calculate_totals(requisition)

        return requisition

    def update(self, instance, validated_data):
        line_items_data = validated_data.pop("line_items", None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if line_items_data is not None:
                instance.line_items.all().delete()
                for item_data in line_items_data:
                    item_data["line_total"] = self._line_total_from_payload(item_data)
                    PurchaseRequisitionLineItem.objects.create(purchase_requisition=instance, **item_data)

            self._calculate_totals(instance)

        return instance


class PurchaseRequisitionListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchaseRequisition
        fields = [
            "purchase_request_number",
            "priority",
            "created_by_name",
            "status",
            "required_by_date",
        ]

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return None
        return obj.created_by.get_full_name() or obj.created_by.get_username()
