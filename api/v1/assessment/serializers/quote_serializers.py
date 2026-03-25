from rest_framework import serializers

from apps.assessment.models import Finish, Quote, QuoteItem, Term


class QuoteItemFinishInputSerializer(serializers.Serializer):
    finish_name = serializers.CharField(max_length=200)
    finish_type = serializers.CharField(max_length=150)
    material = serializers.CharField(max_length=200)
    finish_height = serializers.DecimalField(max_digits=14, decimal_places=3, required=False, default=0)
    finish_width = serializers.DecimalField(max_digits=14, decimal_places=3, required=False, default=0)
    quote_item = serializers.IntegerField(required=False)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)


class QuoteListSerializer(serializers.ModelSerializer):
    boq_number = serializers.CharField(source="boq.boq_number", read_only=True)
    project_name = serializers.CharField(source="boq.enquiry.project_name", read_only=True)
    client = serializers.SerializerMethodField()

    class Meta:
        model = Quote
        fields = [
            "id",
            "quote_number",
            "boq_number",
            "project_name",
            "client",
            "status",
            "created_at",
        ]

    def get_client(self, obj):
        if not obj.boq or not obj.boq.enquiry:
            return None
        enquiry = obj.boq.enquiry
        if enquiry.existing_client:
            return enquiry.existing_client.customer_name
        return enquiry.new_client_name or None


class QuoteDetailSerializer(serializers.ModelSerializer):
    boq_id = serializers.PrimaryKeyRelatedField(
        source="boq",
        queryset=Quote._meta.get_field("boq").remote_field.model.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    boq = serializers.SerializerMethodField()
    enquiry = serializers.SerializerMethodField()
    quote_items = serializers.SerializerMethodField()
    class Meta:
        model = Quote
        fields = [
            "id",
            "boq_id",
            "quote_number",
            "boq",
            "enquiry",
            "quote_items",
            "status",
            "total_items",
            "total_amount",
            "is_approved",
            "is_rejected",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = [
            "quote_number",
            "total_items",
            "total_amount",
            "boq",
            "quote_items",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]

    def get_boq(self, obj):
        if not obj.boq:
            return None
        boq_items = obj.boq.items.all().order_by("-created_at")
        return {
            "id": obj.boq.id,
            "boq_number": obj.boq.boq_number,
            "boq_items": [
                {
                    "id": item.id,
                    "item_code": item.item_code,
                    "name": item.name,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "is_template": item.is_template,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                }
                for item in boq_items
            ],
        }
    def get_enquiry(self, obj):
        if not obj.boq.enquiry:
            return None
        return {
            "id": obj.boq.enquiry.id,
            "project_name": obj.boq.enquiry.project_name,
            "status": obj.boq.enquiry.status,
        }

    def to_internal_value(self, data):
        if isinstance(data, dict):
            payload = data.copy()
            if "boq_id" not in payload and "boq" in payload and payload.get("boq") is not None:
                boq_value = payload.get("boq")
                if isinstance(boq_value, dict):
                    payload["boq_id"] = boq_value.get("id")
                else:
                    payload["boq_id"] = boq_value
            return super().to_internal_value(payload)
        return super().to_internal_value(data)

    def get_quote_items(self, obj):
        items = obj.items.all().order_by("-created_at")
        return [
            {
                "id": item.id,
                "boq_item": item.boq_item.id if item.boq_item else None,
                "image": item.image.url if item.image else None,
                "name": item.name,
                "width": item.width,
                "height": item.height,
                "depth": item.depth,
                "accessories": item.accessories,
                "category": item.category,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "amount": item.amount,
                "finish": [
                    {
                        "id": finish.id,
                        "quote_item": finish.quote_item_id,
                        "finish_name": finish.finish_name,
                        "finish_type": finish.finish_type,
                        "material": finish.material,
                        "finish_height": finish.finish_height,
                        "finish_width": finish.finish_width,
                        "created_at": finish.created_at,
                        "updated_at": finish.updated_at,
                    }
                    for finish in sorted(item.finishes.all(), key=lambda finish: finish.created_at, reverse=True)
                ],
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in items
        ]


class QuoteItemSerializer(serializers.ModelSerializer):
    finish = serializers.SerializerMethodField(read_only=True)
    finishes = QuoteItemFinishInputSerializer(many=True, write_only=True, required=False)
    quote_id = serializers.PrimaryKeyRelatedField(
        source="quote",
        queryset=Quote.objects.all(),
        write_only=True,
        required=False,
    )
    boq_item_id = serializers.PrimaryKeyRelatedField(
        source="boq_item",
        queryset=QuoteItem._meta.get_field("boq_item").remote_field.model.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = QuoteItem
        fields = [
            "id",
            "quote",
            "quote_id",
            "boq_item",
            "boq_item_id",
            "image",
            "name",
            "width",
            "height",
            "depth",
            "accessories",
            "category",
            "quantity",
            "unit_price",
            "amount",
            "finishes",
            "finish",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["amount", "created_at", "updated_at"]

    def to_internal_value(self, data):
        if isinstance(data, dict):
            payload = data.copy()
            if "quote_id" not in payload and "quote" in payload and payload.get("quote") is not None:
                quote_value = payload.get("quote")
                if isinstance(quote_value, dict):
                    payload["quote_id"] = quote_value.get("id")
                else:
                    payload["quote_id"] = quote_value
            if "boq_item_id" not in payload and "boq_item" in payload and payload.get("boq_item") is not None:
                boq_item_value = payload.get("boq_item")
                if isinstance(boq_item_value, dict):
                    payload["boq_item_id"] = boq_item_value.get("id")
                else:
                    payload["boq_item_id"] = boq_item_value
            return super().to_internal_value(payload)
        return super().to_internal_value(data)

    def create(self, validated_data):
        finishes_data = validated_data.pop("finishes", [])
        instance = super().create(validated_data)
        self._create_finishes(instance, finishes_data)
        return instance

    def update(self, instance, validated_data):
        finishes_data = validated_data.pop("finishes", None)
        instance = super().update(instance, validated_data)
        if finishes_data is not None:
            instance.finishes.all().delete()
            self._create_finishes(instance, finishes_data)
        return instance

    def _create_finishes(self, quote_item, finishes_data):
        if not finishes_data:
            return
        Finish.objects.bulk_create(
            [
                Finish(
                    quote_item=quote_item,
                    finish_name=finish_data["finish_name"],
                    finish_type=finish_data["finish_type"],
                    material=finish_data["material"],
                    finish_height=finish_data.get("finish_height", 0),
                    finish_width=finish_data.get("finish_width", 0),
                )
                for finish_data in finishes_data
            ]
        )

    def get_finish(self, obj):
        finishes = sorted(obj.finishes.all(), key=lambda finish: finish.created_at, reverse=True)
        return [
            {
                "id": finish.id,
                "quote_item": finish.quote_item_id,
                "finish_name": finish.finish_name,
                "finish_type": finish.finish_type,
                "material": finish.material,
                "finish_height": finish.finish_height,
                "finish_width": finish.finish_width,
                "created_at": finish.created_at,
                "updated_at": finish.updated_at,
            }
            for finish in finishes
        ]


class FinishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finish
        fields = [
            "id",
            "quote_item",
            "finish_name",
            "finish_type",
            "material",
            "finish_height",
            "finish_width",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = [
            "id",
            "quote",
            "title",
            "content",
            "category",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class QuoteItemCreateRequestSerializer(serializers.Serializer):
    quote = serializers.IntegerField(required=True, help_text="The ID or number of the parent Quote.")
    items = QuoteItemSerializer(many=True, required=True)


class QuoteItemUpdateRequestSerializer(serializers.Serializer):
    quote = serializers.IntegerField(required=False, help_text="The ID or number of the parent Quote.")
    items = QuoteItemSerializer(many=True, required=True, min_length=1, max_length=1, help_text="Exactly one item allowed in this array for single object update.")
