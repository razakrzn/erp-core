from django.db import transaction
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from apps.assessment.models import Finish, Quote, QuoteItem, QuoteTermsConditions
from core.utils.responses import APIResponse, build_actions

from ..serializers import (
    FinishSerializer,
    QuotationDetailsSerializer,
    QuoteDetailSerializer,
    QuoteItemSerializer,
    QuoteListSerializer,
    QuoteTermsConditionsSerializer,
)
from .shared import BaseAssessmentViewSet


class QuoteViewSet(BaseAssessmentViewSet):
    queryset = Quote.objects.select_related("boq").prefetch_related("items__finishes", "boq__items")
    serializer_class = QuoteDetailSerializer
    search_fields = ["quote_number", "boq__boq_number", "status"]
    ordering_fields = ["quote_number", "status", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "estimation.quotations"

    def get_serializer_class(self):
        if self.action == "list":
            return QuoteListSerializer
        return QuoteDetailSerializer

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

    @staticmethod
    def _reset_financial_fields(instance):
        instance.discount_amount = 0
        instance.exclusive_total = 0
        instance.vat_percent = 0
        instance.vat_amount = 0
        instance.grand_total = 0

    def perform_update(self, serializer):
        user = self.request.user if self.request.user and self.request.user.is_authenticated else None
        validated = serializer.validated_data
        instance = serializer.instance
        save_kwargs = {}

        if self._model_has_field("updated_by") and user:
            save_kwargs["updated_by"] = user

        # Business rule: any manual Quote edit (PUT/PATCH) should revoke approval.
        save_kwargs["is_approved"] = False
        save_kwargs["approved_by"] = None
        save_kwargs["is_rejected"] = False
        save_kwargs["rejected_by"] = None
        save_kwargs["reject_note"] = ""

        if "is_rejected" in validated:
            if validated.get("is_rejected"):
                reject_note = (validated.get("reject_note", getattr(instance, "reject_note", "")) or "").strip()
                if not reject_note:
                    raise ValidationError({"reject_note": "This field is required when rejecting quotation."})
                save_kwargs["reject_note"] = reject_note
                save_kwargs["rejected_by"] = user
                save_kwargs["approved_by"] = None
            else:
                save_kwargs["reject_note"] = ""
                save_kwargs["rejected_by"] = None

        if "is_approved" in validated and validated.get("is_approved"):
            save_kwargs["reject_note"] = ""
            save_kwargs["approved_by"] = user
            save_kwargs["rejected_by"] = None
        if "is_approved" in validated and not validated.get("is_approved"):
            save_kwargs["approved_by"] = None
        if "is_rejected" not in validated and "is_approved" in validated and validated.get("is_approved"):
            if getattr(instance, "is_rejected", False):
                save_kwargs["reject_note"] = ""

        # Enforce revoke-approval rule even if payload sends is_approved=true.
        save_kwargs["is_approved"] = False
        save_kwargs["approved_by"] = None
        save_kwargs["is_rejected"] = False
        save_kwargs["rejected_by"] = None
        save_kwargs["reject_note"] = ""

        serializer.save(**save_kwargs)

    @action(detail=True, methods=["patch"], url_path="approve")
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        value = self._parse_boolean_action_value(request.data.get("value", None), "value")

        financial_fields = [
            "discount_amount",
            "exclusive_total",
            "vat_percent",
            "vat_amount",
            "grand_total",
        ]
        for field in financial_fields:
            if field in request.data:
                setattr(instance, field, request.data.get(field))

        instance.is_approved = value
        if value:
            instance.is_rejected = False
            instance.reject_note = ""
            instance.approved_by = request.user if request.user and request.user.is_authenticated else None
            instance.rejected_by = None
        else:
            self._reset_financial_fields(instance)
            instance.approved_by = None
        instance.updated_by = request.user if request.user and request.user.is_authenticated else instance.updated_by
        instance.save()

        message = "Quotation Approved" if value else "Quotation Approval Cancelled"
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
            raise ValidationError({"reject_note": "This field is required when rejecting quotation."})
        self._reset_financial_fields(instance)
        instance.is_rejected = value
        if value:
            instance.is_approved = False
            instance.reject_note = reject_note
            instance.rejected_by = request.user if request.user and request.user.is_authenticated else None
            instance.approved_by = None
        else:
            instance.reject_note = ""
            instance.rejected_by = None
        instance.updated_by = request.user if request.user and request.user.is_authenticated else instance.updated_by
        instance.save()

        message = "Quotation Rejected" if value else "Quotation Rejection Cancelled"
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_200_OK,
        )


class QuotationDetailsViewSet(BaseAssessmentViewSet):
    queryset = Quote.objects.select_related("boq", "boq__enquiry").prefetch_related(
        "items__finishes",
        "boq__items",
        "terms_conditions",
    )
    serializer_class = QuotationDetailsSerializer
    http_method_names = ["get"]
    permission_prefix = "estimation.quotations"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        computed_actions = build_actions(request.user, self.permission_prefix)
        detail_actions = {
            "canApprove": bool(computed_actions.get("canApprove", False)),
            "canReject": bool(computed_actions.get("canReject", False)),
        }
        data = serializer.data
        if isinstance(data, dict):
            data = {**data, "actions": detail_actions}
        else:
            data = {"item": data, "actions": detail_actions}
        return APIResponse.success(
            data=data,
            message=f"{self.queryset.model._meta.verbose_name.title()} retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class QuoteItemViewSet(BaseAssessmentViewSet):
    queryset = QuoteItem.objects.select_related("quote", "boq_item").prefetch_related("finishes")
    serializer_class = QuoteItemSerializer
    search_fields = ["name", "category", "quote__quote_number", "boq_item__item_code"]
    ordering_fields = ["name", "category", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "estimation.quotations"

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
    search_fields = [
        "finish_name",
        "finish_type",
        "material",
        "design",
        "quote_item__name",
        "quote_item__quote__quote_number",
    ]
    ordering_fields = ["finish_name", "finish_type", "material", "design"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "estimation.quotations"


class QuoteTermsConditionsViewSet(BaseAssessmentViewSet):
    queryset = QuoteTermsConditions.objects.select_related("quote")
    serializer_class = QuoteTermsConditionsSerializer
    search_fields = ["title", "category", "quote__quote_number"]
    ordering_fields = ["title", "category"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "estimation.quotations"

    def get_queryset(self):
        queryset = super().get_queryset()
        quote_id = self.request.query_params.get("quote_id")
        if quote_id:
            queryset = queryset.filter(quote_id=quote_id)
        return queryset
