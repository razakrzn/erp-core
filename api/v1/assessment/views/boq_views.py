from django.db import transaction
from rest_framework import filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from apps.assessment.models import Boq, BoqItem
from core.utils.responses import APIResponse

from drf_spectacular.utils import extend_schema, extend_schema_view
from ..serializers import (
    BoqDetailSerializer,
    BoqItemCreateRequestSerializer,
    BoqItemDetailSerializer,
    BoqItemListSerializer,
    BoqItemUpdateRequestSerializer,
    BoqListSerializer,
)
from .shared import BaseAssessmentViewSet


class BoqViewSet(BaseAssessmentViewSet):
    queryset = Boq.objects.select_related("enquiry")
    serializer_class = BoqDetailSerializer
    search_fields = ["boq_number", "enquiry__project_name"]
    ordering_fields = ["boq_number", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_serializer_class(self):
        if self.action == "list":
            return BoqListSerializer
        return BoqDetailSerializer

    @action(detail=True, methods=["patch"], url_path="approve")
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        value = request.data.get("value", None)
        if not isinstance(value, bool):
            raise ValidationError({"value": "This field is required and must be a boolean (true/false)."})

        instance.is_approved = value
        if value:
            instance.is_rejected = False
        instance.save()

        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message=f"Boq approval set to {value}.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"], url_path="reject")
    def reject(self, request, *args, **kwargs):
        instance = self.get_object()
        value = request.data.get("value", None)
        if not isinstance(value, bool):
            raise ValidationError({"value": "This field is required and must be a boolean (true/false)."})

        instance.is_rejected = value
        if value:
            instance.is_approved = False
        instance.save()

        serializer = self.get_serializer(instance)
        return APIResponse.success(
            data=serializer.data,
            message=f"Boq rejection set to {value}.",
            status_code=status.HTTP_200_OK,
        )


@extend_schema_view(
    create=extend_schema(
        tags=["Assessment"],
        summary="Batch create BOQ items",
        description="Create multiple BOQ items by providing a parent BOQ ID/Number and a list of items.",
        request=BoqItemCreateRequestSerializer,
    ),
    update=extend_schema(
        tags=["Assessment"],
        summary="Update BOQ item",
        description="Update a single BOQ item. Supports both direct payload format or wrapped {'boq': id, 'items': [...]} format.",
        request=BoqItemUpdateRequestSerializer,
    ),
    partial_update=extend_schema(
        tags=["Assessment"],
        summary="Partial update BOQ item",
        description="Partially update a single BOQ item. Supports both direct payload format or wrapped {'boq': id, 'items': [...]} format.",
        request=BoqItemUpdateRequestSerializer,
    ),
)
class BoqItemViewSet(BaseAssessmentViewSet):
    queryset = BoqItem.objects.select_related("boq")
    serializer_class = BoqItemDetailSerializer
    search_fields = ["item_code", "name", "boq__boq_number"]
    ordering_fields = ["item_code", "name", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_serializer_class(self):
        if self.action == "list":
            return BoqItemListSerializer
        return BoqItemDetailSerializer

    @staticmethod
    def _parse_boolean_query_param(raw_value, field_name):
        if raw_value is None:
            return None
        normalized = str(raw_value).strip().lower()
        if normalized in {"true", "1", "yes"}:
            return True
        if normalized in {"false", "0", "no"}:
            return False
        raise ValidationError({field_name: "Invalid boolean value. Use true or false."})

    @action(detail=False, methods=["get"], url_path="by-boq")
    def by_boq(self, request, *args, **kwargs):
        boq_id = request.query_params.get("boq_id")
        if boq_id in (None, ""):
            raise ValidationError({"boq_id": "This query parameter is required."})

        queryset = self.get_queryset().filter(boq_id=boq_id)
        is_template = self._parse_boolean_query_param(request.query_params.get("is_template"), "is_template")
        if is_template is not None:
            queryset = queryset.filter(is_template=is_template)

        queryset = queryset.order_by("-created_at")
        page = self.paginate_queryset(queryset)
        serializer = BoqItemDetailSerializer(page if page is not None else queryset, many=True)

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return APIResponse.success(
            data=serializer.data,
            message="Boq items retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        payload = request.data

        if not isinstance(payload, dict):
            raise ValidationError({"payload": "Payload must be an object with 'boq' and 'items'."})

        if payload.get("boq") in (None, ""):
            raise ValidationError({"boq": "This field is required."})

        if "items" not in payload or not isinstance(payload.get("items"), list):
            raise ValidationError({"items": "This field is required and must be an array."})

        items_payload = payload.get("items", [])
        if not items_payload:
            raise ValidationError({"items": "At least one item is required."})

        shared_boq = payload.get("boq")
        normalized_items = []
        for item in items_payload:
            row = dict(item)
            row["boq"] = shared_boq
            normalized_items.append(row)
        items_payload = normalized_items

        serializer = self.get_serializer(data=items_payload, many=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Boq items created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def _normalize_single_update_payload(self, payload, partial=False):
        if not isinstance(payload, dict):
            raise ValidationError({"payload": "Payload must be an object."})

        # Support wrapper format: {"boq": <id>, "items": [{...}]}
        if "items" in payload:
            if not isinstance(payload.get("items"), list):
                raise ValidationError({"items": "This field must be an array."})
            items_payload = payload.get("items", [])
            if len(items_payload) != 1:
                raise ValidationError({"items": "PUT/PATCH requires exactly one item in items[] for detail update."})
            row = dict(items_payload[0])
            if "boq" in payload and payload.get("boq") not in (None, ""):
                row["boq"] = payload.get("boq")
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
            message="Boq item updated successfully.",
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
            message="Boq item updated successfully.",
            status_code=status.HTTP_200_OK,
        )
