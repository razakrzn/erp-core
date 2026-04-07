from django.db import transaction
from rest_framework import serializers

from apps.inventory.models import PurchaseRequisition, PurchaseRequisitionLineItem


class PurchaseRequisitionLineItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField(read_only=True)
    product_code = serializers.SerializerMethodField(read_only=True)
    standard_cost = serializers.SerializerMethodField(read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)
    unit_name = serializers.SerializerMethodField(read_only=True)
    

    class Meta:
        model = PurchaseRequisitionLineItem
        fields = [
            "id",
            "purchase_requisition",
            "product",
            "product_name",
            "product_code",
            "standard_cost",
            "category_name",
            "unit_name",
            "stock_on_hand",
            "pending_pr_qty",
            "pending_po_qty",
            "requested_qty",
            "net_required_qty",
        ]
        read_only_fields = ["net_required_qty"]
        extra_kwargs = {
            "purchase_requisition": {"required": False},
        }

    def get_product_name(self, obj):
        return obj.product.name if obj.product else None

    def get_product_code(self, obj):
        return obj.product.product_code if obj.product else None

    def get_standard_cost(self, obj):
        return obj.product.standard_cost if obj.product else None

    def get_category_name(self, obj):
        if not obj.product or not obj.product.category:
            return None
        return obj.product.category.name

    def get_unit_name(self, obj):
        if not obj.product or not obj.product.unit:
            return None
        return obj.product.unit.name


class PurchaseRequisitionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField(read_only=True)
    approved_by_name = serializers.SerializerMethodField(read_only=True)
    rejected_by_name = serializers.SerializerMethodField(read_only=True)
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
            "is_approved",
            "is_rejected",
            "created_by",
            "created_by_name",
            "approved_by",
            "approved_by_name",
            "rejected_by",
            "rejected_by_name",
            "created_at",
            "updated_at",
            "line_items",
        ]
        read_only_fields = [
            "purchase_request_number",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return None
        return obj.created_by.get_full_name() or obj.created_by.get_username()

    def get_approved_by_name(self, obj):
        if not obj.approved_by:
            return None
        return obj.approved_by.get_full_name() or obj.approved_by.get_username()

    def get_rejected_by_name(self, obj):
        if not obj.rejected_by:
            return None
        return obj.rejected_by.get_full_name() or obj.rejected_by.get_username()

    def create(self, validated_data):
        line_items_data = validated_data.pop("line_items", [])

        with transaction.atomic():
            requisition = PurchaseRequisition.objects.create(**validated_data)
            for item_data in line_items_data:
                PurchaseRequisitionLineItem.objects.create(purchase_requisition=requisition, **item_data)

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
                    PurchaseRequisitionLineItem.objects.create(purchase_requisition=instance, **item_data)

        return instance


class PurchaseRequisitionListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchaseRequisition
        fields = [
            "id",
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
