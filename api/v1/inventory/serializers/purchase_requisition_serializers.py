from django.db import transaction
from rest_framework import serializers

from apps.inventory.models import PurchaseRequisition, PurchaseRequisitionLineItem


class PurchaseRequisitionLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequisitionLineItem
        fields = [
            "id",
            "purchase_requisition",
            "product_id",
            "product_name",
            "product_code",
            "product_category",
            "unit",
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
            "requisition_date",
            "requisition_type",
            "stock_reason_category",
            "job_order_ref",
            "rework_notes",
            "required_by_date",
            "priority",
            "delivery_location",
            "reason_description",
            "notes_to_purchase_team",
            "status",
            "is_approved",
            "is_rejected",
            "reject_note",
            "created_by",
            "created_by_name",
            "approved_by",
            "approved_by_name",
            "rejected_by",
            "rejected_by_name",
            "updated_by",
            "created_at",
            "updated_at",
            "line_items",
        ]
        read_only_fields = [
            "purchase_request_number",
            "status",
            "created_by",
            "approved_by",
            "rejected_by",
            "updated_by",
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
        user = self.context.get("request").user if self.context.get("request") else None

        with transaction.atomic():
            requisition = PurchaseRequisition.objects.create(**validated_data)
            for item_data in line_items_data:
                PurchaseRequisitionLineItem.objects.create(purchase_requisition=requisition, **item_data)
            self._sync_approval_fields(requisition, user)
            requisition.save()
            if requisition.is_approved:
                requisition.ensure_production_order()

        return requisition

    def update(self, instance, validated_data):
        line_items_data = validated_data.pop("line_items", None)
        user = self.context.get("request").user if self.context.get("request") else None
        was_approved = bool(instance.is_approved)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            self._sync_approval_fields(instance, user)
            instance.save()

            if line_items_data is not None:
                instance.line_items.all().delete()
                for item_data in line_items_data:
                    PurchaseRequisitionLineItem.objects.create(purchase_requisition=instance, **item_data)
            if instance.is_approved and not was_approved:
                instance.ensure_production_order()

        return instance

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        is_approved = attrs.get("is_approved", getattr(instance, "is_approved", False))
        is_rejected = attrs.get("is_rejected", getattr(instance, "is_rejected", False))
        reject_note = attrs.get("reject_note", getattr(instance, "reject_note", "")) or ""

        if is_approved and is_rejected:
            raise serializers.ValidationError("Purchase requisition cannot be both approved and rejected.")
        if is_rejected and not reject_note.strip():
            raise serializers.ValidationError({"reject_note": "This field is required when rejecting Purchase Requisition."})
        return attrs

    @staticmethod
    def _sync_approval_fields(instance, user):
        auth_user = user if getattr(user, "is_authenticated", False) else None
        if instance.is_approved:
            instance.is_rejected = False
            instance.reject_note = ""
            instance.rejected_by = None
            if auth_user:
                instance.approved_by = auth_user
        elif instance.is_rejected:
            instance.is_approved = False
            instance.approved_by = None
            if auth_user:
                instance.rejected_by = auth_user
        else:
            instance.approved_by = None
            instance.rejected_by = None


class PurchaseRequisitionListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchaseRequisition
        fields = [
            "id",
            "purchase_request_number",
            "requisition_date",
            "requisition_type",
            "priority",
            "created_by_name",
            "status",
            "required_by_date",
        ]

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return None
        return obj.created_by.get_full_name() or obj.created_by.get_username()


class PurchaseRequisitionProductNameListSerializer(serializers.Serializer):
    product_name = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )


class PurchaseRequisitionFilterOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField()


class PurchaseRequisitionFilterOptionsSerializer(serializers.Serializer):
    material_categories = PurchaseRequisitionFilterOptionSerializer(many=True)
    vendors = PurchaseRequisitionFilterOptionSerializer(many=True)
    specific_products = PurchaseRequisitionFilterOptionSerializer(many=True)


class PurchaseRequisitionLineItemDropdownOptionSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class PurchaseRequisitionLineItemFilterOptionSerializer(serializers.Serializer):
    key = serializers.CharField()
    label = serializers.CharField()
    options_endpoint = serializers.CharField()
