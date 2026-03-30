import logging

from django.db import transaction
from rest_framework import filters, status
from rest_framework.decorators import action
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

logger = logging.getLogger(__name__)


class BoqViewSet(BaseAssessmentViewSet):
    queryset = Boq.objects.select_related("enquiry")
    serializer_class = BoqDetailSerializer
    search_fields = ["boq_number", "enquiry__project_name"]
    ordering_fields = ["boq_number", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "estimation.boq"

    def get_serializer_class(self):
        if self.action == "list":
            return BoqListSerializer
        return BoqDetailSerializer

    @staticmethod
    def _parse_boolean_action_value(raw_value, field_name="value"):
        if isinstance(raw_value, bool):
            return raw_value
        if raw_value is None:
            raise ValidationError({field_name: "This field is required and must be true or false."})
        normalized = str(raw_value).strip().lower()
        if normalized in {"true", "1", "yes"}:
            return True
        if normalized in {"false", "0", "no"}:
            return False
        raise ValidationError({field_name: "Invalid boolean value. Use true or false."})

    def perform_update(self, serializer):
        """
        Keep approval audit fields in sync even when BOQ is updated via generic
        PUT/PATCH endpoints (not only custom approve/reject actions).
        """
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        validated = serializer.validated_data
        instance = serializer.instance
        save_kwargs = {}
        user_id = getattr(user, "id", None)

        logger.debug(
            "[BOQ perform_update] boq_id=%s user_id=%s validated_keys=%s incoming_is_approved=%s incoming_is_rejected=%s "
            "current_is_approved=%s current_is_rejected=%s current_approved_by_id=%s current_rejected_by_id=%s",
            instance.id,
            user_id,
            list(validated.keys()),
            validated.get("is_approved", "<missing>"),
            validated.get("is_rejected", "<missing>"),
            getattr(instance, "is_approved", None),
            getattr(instance, "is_rejected", None),
            getattr(instance, "approved_by_id", None),
            getattr(instance, "rejected_by_id", None),
        )

        if self._model_has_field("updated_by") and user:
            save_kwargs["updated_by"] = user

        # Business rule: any manual BOQ edit (PUT/PATCH) should revoke approval.
        save_kwargs["is_approved"] = False
        save_kwargs["approved_by"] = None
        save_kwargs["is_rejected"] = False
        save_kwargs["rejected_by"] = None
        save_kwargs["reject_note"] = ""

        if "is_approved" in validated:
            if validated.get("is_approved"):
                save_kwargs["approved_by"] = user
                save_kwargs["rejected_by"] = None
            else:
                save_kwargs["approved_by"] = None

        if "is_rejected" in validated:
            if validated.get("is_rejected"):
                reject_note = (validated.get("reject_note", getattr(instance, "reject_note", "")) or "").strip()
                if not reject_note:
                    raise ValidationError({"reject_note": "This field is required when rejecting BOQ."})
                save_kwargs["rejected_by"] = user
                save_kwargs["approved_by"] = None
                save_kwargs["reject_note"] = reject_note
            else:
                save_kwargs["rejected_by"] = None
                save_kwargs["reject_note"] = ""

        # If one flag is omitted, preserve existing semantics.
        if "is_approved" not in validated and "is_rejected" in validated and validated.get("is_rejected"):
            if getattr(instance, "is_approved", False):
                save_kwargs["approved_by"] = None
        if "is_rejected" not in validated and "is_approved" in validated and validated.get("is_approved"):
            if getattr(instance, "is_rejected", False):
                save_kwargs["rejected_by"] = None
                save_kwargs["reject_note"] = ""
        if "is_approved" in validated and validated.get("is_approved"):
            save_kwargs["reject_note"] = ""

        # Enforce revoke-approval rule even if payload sends is_approved=true.
        save_kwargs["is_approved"] = False
        save_kwargs["approved_by"] = None
        save_kwargs["is_rejected"] = False
        save_kwargs["rejected_by"] = None
        save_kwargs["reject_note"] = ""

        logger.debug(
            "[BOQ perform_update] boq_id=%s user_id=%s computed_save_kwargs=%s",
            instance.id,
            user_id,
            {
                key: (value.id if hasattr(value, "id") else value)
                for key, value in save_kwargs.items()
            },
        )
        serializer.save(**save_kwargs)
        serializer.instance.refresh_from_db()
        logger.debug(
            "[BOQ perform_update] boq_id=%s persisted is_approved=%s is_rejected=%s approved_by_id=%s rejected_by_id=%s updated_by_id=%s",
            serializer.instance.id,
            serializer.instance.is_approved,
            serializer.instance.is_rejected,
            serializer.instance.approved_by_id,
            serializer.instance.rejected_by_id,
            serializer.instance.updated_by_id,
        )

    @action(detail=True, methods=["patch"], url_path="approve")
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        value = self._parse_boolean_action_value(request.data.get("value", None), "value")
        logger.debug(
            "[BOQ approve] boq_id=%s user_id=%s raw_value=%s before is_approved=%s is_rejected=%s approved_by_id=%s rejected_by_id=%s",
            instance.id,
            getattr(request.user, "id", None),
            value,
            instance.is_approved,
            instance.is_rejected,
            instance.approved_by_id,
            instance.rejected_by_id,
        )
        instance.is_approved = value
        if value:
            instance.is_rejected = False
            instance.approved_by = request.user if request.user and request.user.is_authenticated else None
            instance.rejected_by = None
            instance.reject_note = ""
        else:
            instance.approved_by = None
        instance.updated_by = request.user if request.user and request.user.is_authenticated else instance.updated_by
        instance.save()
        instance.refresh_from_db()
        logger.debug(
            "[BOQ approve] boq_id=%s after is_approved=%s is_rejected=%s approved_by_id=%s rejected_by_id=%s updated_by_id=%s",
            instance.id,
            instance.is_approved,
            instance.is_rejected,
            instance.approved_by_id,
            instance.rejected_by_id,
            instance.updated_by_id,
        )

        message = "Bill of Quantity Approved" if value else "Bill of Quantity Approval Cancelled"
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"], url_path="reject")
    def reject(self, request, *args, **kwargs):
        instance = self.get_object()
        value = self._parse_boolean_action_value(request.data.get("value", None), "value")
        reject_note = (request.data.get("reject_note", "") or "").strip()
        if value and not reject_note:
            raise ValidationError({"reject_note": "This field is required when rejecting BOQ."})
        logger.debug(
            "[BOQ reject] boq_id=%s user_id=%s raw_value=%s before is_approved=%s is_rejected=%s approved_by_id=%s rejected_by_id=%s",
            instance.id,
            getattr(request.user, "id", None),
            value,
            instance.is_approved,
            instance.is_rejected,
            instance.approved_by_id,
            instance.rejected_by_id,
        )
        instance.is_rejected = value
        if value:
            instance.is_approved = False
            instance.rejected_by = request.user if request.user and request.user.is_authenticated else None
            instance.approved_by = None
            instance.reject_note = reject_note
        else:
            instance.rejected_by = None
            instance.reject_note = ""
        instance.updated_by = request.user if request.user and request.user.is_authenticated else instance.updated_by
        instance.save()
        instance.refresh_from_db()
        logger.debug(
            "[BOQ reject] boq_id=%s after is_approved=%s is_rejected=%s approved_by_id=%s rejected_by_id=%s updated_by_id=%s",
            instance.id,
            instance.is_approved,
            instance.is_rejected,
            instance.approved_by_id,
            instance.rejected_by_id,
            instance.updated_by_id,
        )

        message = "Bill of Quantity Rejected" if value else "Bill of Quantity Rejection Cancelled"
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_200_OK,
        )


class BoqItemViewSet(BaseAssessmentViewSet):
    queryset = BoqItem.objects.select_related("boq")
    serializer_class = BoqItemDetailSerializer
    search_fields = ["item_code", "name", "boq__boq_number"]
    ordering_fields = ["item_code", "name", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "estimation.boq"

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
