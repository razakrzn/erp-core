from rest_framework import serializers

from apps.assessment.models import Finish, Quote, QuoteItem, Term


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = [
            "id",
            "quote_number",
            "boq",
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
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]


class QuoteItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteItem
        fields = [
            "id",
            "quote",
            "boq_item",
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
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["amount", "created_at", "updated_at"]


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
