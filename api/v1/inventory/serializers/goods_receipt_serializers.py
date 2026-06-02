from decimal import Decimal

from django.db.models import DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce
from django.db import transaction
from rest_framework import serializers

from apps.inventory.models import GoodsReceipt, GoodsReceiptItem, PurchaseOrder, PurchaseOrderLineItem, ReceivedGoodsPhoto


class GoodsReceiptItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceiptItem
        fields = [
            "id",
            "purchase_order_line_item",
            "product",
            "product_code",
            "product_name",
            "unit",
            "po_qty",
            "already_received",
            "qty_good",
            "qty_rejected",
            "rejection_reason",
            "defect_photo",
        ]
        read_only_fields = ["product", "product_code", "product_name", "unit", "po_qty", "already_received"]


class ReceivedGoodsPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceivedGoodsPhoto
        fields = ["id", "photo", "uploaded_at"]
        read_only_fields = ["uploaded_at"]


class GoodsReceiptSerializer(serializers.ModelSerializer):
    purchase_order_id = serializers.PrimaryKeyRelatedField(
        source="purchase_order",
        queryset=PurchaseOrder.objects.all(),
        write_only=True,
    )
    purchase_order = serializers.SerializerMethodField(read_only=True)
    material_intakes = GoodsReceiptItemSerializer(many=True, required=False)
    received_goods_photos = ReceivedGoodsPhotoSerializer(many=True, read_only=True)
    received_goods_photo_files = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = GoodsReceipt
        fields = [
            "id",
            "grn_number",
            "purchase_order",
            "purchase_order_id",
            "purchase_order_no",
            "po_date",
            "grn_recording_date",
            "vendor_name",
            "vendor_trn",
            "vendor_address",
            "vendor_invoice_no",
            "vendor_invoice_date",
            "delivery_challan_no",
            "delivery_challan_date",
            "vendor_delivery_challan",
            "vendor_invoice",
            "overall_quality_status",
            "quality_notes",
            "material_intakes",
            "received_goods_photos",
            "received_goods_photo_files",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "grn_number",
            "purchase_order_no",
            "po_date",
            "vendor_name",
            "vendor_trn",
            "vendor_address",
            "received_goods_photos",
            "created_at",
            "updated_at",
        ]

    def get_purchase_order(self, obj):
        if not obj.purchase_order:
            return None
        return {
            "id": obj.purchase_order.id,
            "po_number": obj.purchase_order.po_number or "",
        }

    def validate_material_intakes(self, value):
        if not value:
            raise serializers.ValidationError("At least one material intake is required.")
        return value

    def validate(self, attrs):
        purchase_order = attrs.get("purchase_order")
        line_items = attrs.get("material_intakes", None)
        if purchase_order is None and self.instance is not None:
            purchase_order = self.instance.purchase_order

        if not purchase_order:
            raise serializers.ValidationError({"purchase_order_id": "This field is required."})

        if line_items is None:
            return attrs

        po_line_item_ids = {
            item["purchase_order_line_item"].id
            for item in line_items
            if item.get("purchase_order_line_item") is not None
        }
        existing_po_line_item_ids = set(
            PurchaseOrderLineItem.objects.filter(purchase_order=purchase_order, id__in=po_line_item_ids).values_list(
                "id", flat=True
            )
        )
        missing = po_line_item_ids - existing_po_line_item_ids
        if missing:
            raise serializers.ValidationError(
                {"material_intakes": f"Invalid PO line item(s) for selected purchase order: {sorted(missing)}"}
            )
        return attrs

    def create(self, validated_data):
        line_items_data = validated_data.pop("material_intakes", [])
        received_goods_photo_files = validated_data.pop("received_goods_photo_files", [])

        with transaction.atomic():
            goods_receipt = GoodsReceipt.objects.create(**validated_data)
            for line_data in line_items_data:
                GoodsReceiptItem.objects.create(goods_receipt=goods_receipt, **line_data)
            for photo_file in received_goods_photo_files:
                ReceivedGoodsPhoto.objects.create(goods_receipt=goods_receipt, photo=photo_file)

        return goods_receipt

    def update(self, instance, validated_data):
        line_items_data = validated_data.pop("material_intakes", None)
        received_goods_photo_files = validated_data.pop("received_goods_photo_files", None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if line_items_data is not None:
                instance.material_intakes.all().delete()
                for line_data in line_items_data:
                    GoodsReceiptItem.objects.create(goods_receipt=instance, **line_data)

            if received_goods_photo_files is not None:
                instance.received_goods_photos.all().delete()
                for photo_file in received_goods_photo_files:
                    ReceivedGoodsPhoto.objects.create(goods_receipt=instance, photo=photo_file)

        return instance


class GoodsReceiptListSerializer(serializers.ModelSerializer):
    products = serializers.IntegerField(read_only=True, source="products_count")
    received_qty = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GoodsReceipt
        fields = [
            "id",
            "grn_number",
            "purchase_order_no",
            "grn_recording_date",
            "vendor_name",
            "products",
            "received_qty",
        ]

    def get_received_qty(self, obj):
        value = getattr(obj, "total_already_received", None)
        if value is None:
            value = sum((item.already_received for item in obj.material_intakes.all()), Decimal("0.00"))
        return f"{(value or Decimal('0.00')):.2f}"


class ApprovedPurchaseOrderLineItemForGRNSerializer(serializers.ModelSerializer):
    purchase_request_number = serializers.CharField(
        source="purchase_requisition.purchase_request_number",
        read_only=True,
    )
    already_received = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PurchaseOrderLineItem
        fields = [
            "id",
            "purchase_order",
            "product",
            "product_code",
            "purchase_request_number",
            "description",
            "unit",
            "requested_qty",
            "required_by_date",
            "delivery_location",
            "last_purchase_rate",
            "negotiated_price",
            "line_total",
            "already_received",
        ]

    def get_already_received(self, obj):
        total = (
            GoodsReceiptItem.objects.filter(purchase_order_line_item=obj)
            .aggregate(
                total=Coalesce(
                    Sum(
                        F("qty_good"),
                        output_field=DecimalField(max_digits=14, decimal_places=2),
                    ),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=14, decimal_places=2),
                )
            )
            .get("total")
        )
        return f"{(total or Decimal('0.00')):.2f}"


class ApprovedPurchaseOrderForGRNSerializer(serializers.ModelSerializer):
    vendor = serializers.SerializerMethodField(read_only=True)
    line_items = ApprovedPurchaseOrderLineItemForGRNSerializer(source="po_line_items", many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "po_number",
            "po_issued_date",
            "vendor",
            "line_items",
        ]

    def get_vendor(self, obj):
        if not obj.vendor:
            return None
        return {
            "id": obj.vendor.id,
            "trade_name": obj.vendor.trade_name or "",
            "trn_number": obj.vendor.trn_number or "",
            "store_office_no": obj.vendor.store_office_no or "",
            "building_name": obj.vendor.building_name or "",
            "street_area": obj.vendor.street_area or "",
            "city_emirate": obj.vendor.city_emirate or "",
        }
