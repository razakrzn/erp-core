from django.db import transaction
from rest_framework import filters
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.assessment.models import Boq, BoqItem
from core.utils.responses import APIResponse

from ..serializers import (
    BoqDetailSerializer,
    BoqItemDetailSerializer,
    BoqItemListSerializer,
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
