from django.db import transaction
from rest_framework import filters
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.assessment.models import Finish, Quote, QuoteItem, Term
from core.utils.responses import APIResponse

from core.utils.schema_docs_shims import extend_schema, extend_schema_view
from ..serializers import (
    FinishSerializer,
    QuoteDetailSerializer,
    QuoteItemCreateRequestSerializer,
    QuoteItemSerializer,
    QuoteItemUpdateRequestSerializer,
    QuoteListSerializer,
    TermSerializer,
)
from .shared import BaseAssessmentViewSet


class QuoteViewSet(BaseAssessmentViewSet):
    queryset = Quote.objects.select_related("boq").prefetch_related("items__finishes", "boq__items")
    serializer_class = QuoteDetailSerializer
    search_fields = ["quote_number", "boq__boq_number", "status"]
    ordering_fields = ["quote_number", "status", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_serializer_class(self):
        if self.action == "list":
            return QuoteListSerializer
        return QuoteDetailSerializer


@extend_schema_view(
    create=extend_schema(
        tags=["Assessment"],
        summary="Batch create Quote items",
        description="Create multiple Quote items by providing a parent Quote ID/Number and a list of items.",
        request=QuoteItemCreateRequestSerializer,
    ),
    update=extend_schema(
        tags=["Assessment"],
        summary="Update Quote item",
        description="Update a single Quote item. Supports both direct payload format or wrapped {'quote': id, 'items': [...]} format.",
        request=QuoteItemUpdateRequestSerializer,
    ),
    partial_update=extend_schema(
        tags=["Assessment"],
        summary="Partial update Quote item",
        description="Partially update a single Quote item. Supports both direct payload format or wrapped {'quote': id, 'items': [...]} format.",
        request=QuoteItemUpdateRequestSerializer,
    ),
)
class QuoteItemViewSet(BaseAssessmentViewSet):
    queryset = QuoteItem.objects.select_related("quote", "boq_item").prefetch_related("finishes")
    serializer_class = QuoteItemSerializer
    search_fields = ["name", "category", "quote__quote_number", "boq_item__item_code"]
    ordering_fields = ["name", "category", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def create(self, request, *args, **kwargs):
        payload = request.data

        if not isinstance(payload, dict):
            raise ValidationError({"payload": "Payload must be an object with 'quote' and 'items'."})

        if payload.get("quote") in (None, ""):
            raise ValidationError({"quote": "This field is required."})

        if "items" not in payload or not isinstance(payload.get("items"), list):
            raise ValidationError({"items": "This field is required and must be an array."})

        items_payload = payload.get("items", [])
        if not items_payload:
            raise ValidationError({"items": "At least one item is required."})

        shared_quote = payload.get("quote")
        normalized_items = []
        for item in items_payload:
            row = dict(item)
            row["quote"] = shared_quote
            normalized_items.append(row)
        items_payload = normalized_items

        serializer = self.get_serializer(data=items_payload, many=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Quote items created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def _normalize_single_update_payload(self, payload, partial=False):
        if not isinstance(payload, dict):
            raise ValidationError({"payload": "Payload must be an object."})

        # Support wrapper format: {"quote": <id>, "items": [{...}]}
        if "items" in payload:
            if not isinstance(payload.get("items"), list):
                raise ValidationError({"items": "This field must be an array."})
            items_payload = payload.get("items", [])
            if len(items_payload) != 1:
                raise ValidationError({"items": "PUT/PATCH requires exactly one item in items[] for detail update."})
            row = dict(items_payload[0])
            if "quote" in payload and payload.get("quote") not in (None, ""):
                row["quote"] = payload.get("quote")
            return row

        # Support direct object format.
        return payload

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        normalized_payload = self._normalize_single_update_payload(request.data, partial=False)
        serializer = self.get_serializer(instance, data=normalized_payload, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Quote item updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        normalized_payload = self._normalize_single_update_payload(request.data, partial=True)
        serializer = self.get_serializer(instance, data=normalized_payload, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Quote item updated successfully.",
            status_code=status.HTTP_200_OK,
        )


class FinishViewSet(BaseAssessmentViewSet):
    queryset = Finish.objects.select_related("quote_item", "quote_item__quote")
    serializer_class = FinishSerializer
    search_fields = ["finish_name", "finish_type", "material", "quote_item__name", "quote_item__quote__quote_number"]
    ordering_fields = ["finish_name", "finish_type", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


class TermViewSet(BaseAssessmentViewSet):
    queryset = Term.objects.select_related("quote")
    serializer_class = TermSerializer
    search_fields = ["title", "category", "quote__quote_number"]
    ordering_fields = ["title", "category", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
