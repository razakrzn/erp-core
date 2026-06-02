import json
from decimal import Decimal

from django.db.models import Exists, F, OuterRef, Q
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from apps.inventory.models import (
    Category,
    Product,
    PurchaseOrderLineItem,
    PurchaseRequisition,
    PurchaseRequisitionLineItem,
    Vendor,
)
from core.permissions.rbac_permission import RBACPermission
from core.utils.responses import APIResponse, build_actions

from ..serializers import (
    ApprovedPurchaseRequisitionLineItemSerializer,
    PurchaseRequisitionFilterOptionsSerializer,
    PurchaseRequisitionLineItemDropdownOptionSerializer,
    PurchaseRequisitionLineItemFilterOptionSerializer,
    PurchaseRequisitionLineItemSerializer,
    PurchaseRequisitionListSerializer,
    PurchaseRequisitionSerializer,
)
from .shared import BaseInventoryViewSet


class PurchaseRequisitionViewSet(BaseInventoryViewSet):
    queryset = PurchaseRequisition.objects.select_related("created_by").prefetch_related("line_items")
    serializer_class = PurchaseRequisitionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "purchase_request_number",
        "requisition_type",
        "stock_reason_category",
        "job_order_ref",
        "rework_notes",
        "priority",
        "status",
        "delivery_location",
        "created_by__username",
    ]
    ordering_fields = [
        "id",
        "requisition_date",
        "required_by_date",
        "priority",
        "status",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]
    permission_prefix = "procurement.purchase_requisitions"

    @staticmethod
    def _normalize_payload(request):
        payload = request.data.copy()
        line_items_raw = payload.get("line_items", None)

        if isinstance(line_items_raw, str):
            normalized = line_items_raw.strip()
            if normalized:
                payload["line_items"] = json.loads(normalized)
            else:
                payload["line_items"] = []

        return payload

    @staticmethod
    def _parse_filter_tokens(request, *param_names):
        """Parse comma-separated or repeated query params into numeric ids and labels."""
        tokens = []
        for name in param_names:
            for value in request.query_params.getlist(name):
                if not value:
                    continue
                tokens.extend(item.strip() for item in value.split(",") if item.strip())

        ids = []
        labels = []
        for token in tokens:
            if token.isdigit():
                ids.append(int(token))
            else:
                labels.append(token)
        return ids, labels

    def _filter_by_material_categories(self, queryset):
        category_ids, category_names = self._parse_filter_tokens(self.request, "material_categories")
        if not category_ids and not category_names:
            return queryset

        if category_ids:
            category_names.extend(
                Category.objects.filter(id__in=category_ids).values_list("name", flat=True)
            )

        category_names = list(dict.fromkeys(name for name in category_names if name))
        line_item_filter = Q()
        if category_names:
            line_item_filter |= Q(line_items__product_category__in=category_names)

        product_filter = Q()
        if category_ids:
            product_filter |= Q(category_id__in=category_ids)
        if category_names:
            product_filter |= Q(category__name__in=category_names)
        if product_filter:
            product_ids = Product.objects.filter(product_filter).values_list("id", flat=True)
            line_item_filter |= Q(line_items__product_id__in=product_ids)

        return queryset.filter(line_item_filter) if line_item_filter else queryset

    def _filter_by_vendors(self, queryset):
        vendor_ids, vendor_names = self._parse_filter_tokens(self.request, "vendors", "vendor")
        if not vendor_ids and not vendor_names:
            return queryset

        product_filter = Q()
        if vendor_ids:
            product_filter |= Q(preferred_supplier_id__in=vendor_ids)
        if vendor_names:
            product_filter |= Q(preferred_supplier__trade_name__in=vendor_names)

        product_ids = Product.objects.filter(product_filter).values_list("id", flat=True)
        return queryset.filter(line_items__product_id__in=product_ids)

    def _filter_by_specific_products(self, queryset):
        product_ids, product_names = self._parse_filter_tokens(
            self.request,
            "specific_products",
            "specific_product",
        )
        if not product_ids and not product_names:
            return queryset

        line_item_filter = Q()
        if product_ids:
            line_item_filter |= Q(line_items__product_id__in=product_ids)
        if product_names:
            line_item_filter |= Q(line_items__product_name__in=product_names)
            matched_ids = Product.objects.filter(name__in=product_names).values_list("id", flat=True)
            line_item_filter |= Q(line_items__product_id__in=matched_ids)

        return queryset.filter(line_item_filter)

    @staticmethod
    def _resolve_line_item_product_codes(line_items):
        product_code_by_line_item_id = {}
        product_ids = []

        for line_item in line_items:
            if line_item.product_code:
                product_code_by_line_item_id[line_item.id] = line_item.product_code
            elif line_item.product_id:
                product_ids.append(line_item.product_id)

        if product_ids:
            products = Product.objects.filter(id__in=product_ids).values("id", "product_code")
            product_code_by_id = {row["id"]: row["product_code"] for row in products if row["product_code"]}
            for line_item in line_items:
                if line_item.id in product_code_by_line_item_id:
                    continue
                code = product_code_by_id.get(line_item.product_id)
                if code:
                    product_code_by_line_item_id[line_item.id] = code

        return product_code_by_line_item_id

    @staticmethod
    def _build_last_purchase_lookup(product_codes):
        if not product_codes:
            return {}

        po_lines = (
            PurchaseOrderLineItem.objects.filter(product_code__in=product_codes)
            .select_related("purchase_order", "purchase_order__vendor")
            .order_by("product_code", "-purchase_order__po_issued_date", "-purchase_order__created_at", "-id")
        )

        lookup = {}
        for po_line in po_lines:
            code = po_line.product_code
            if not code or code in lookup:
                continue

            purchase_order = po_line.purchase_order
            rate = po_line.negotiated_price
            if rate is None or rate <= 0:
                rate = po_line.last_purchase_rate or Decimal("0.00")

            is_meaningful = rate > 0 or purchase_order.is_approved or purchase_order.is_rejected
            if not is_meaningful:
                continue

            vendor = purchase_order.vendor
            lookup[code] = {
                "last_purchase_rate": rate,
                "last_purchase_qty": po_line.requested_qty,
                "last_purchase_vendor": vendor.trade_name if vendor else None,
            }

        return lookup

    @classmethod
    def _approved_line_item_serializer_context(cls, line_items):
        product_code_by_line_item_id = cls._resolve_line_item_product_codes(line_items)
        product_codes = list(dict.fromkeys(product_code_by_line_item_id.values()))
        return {
            "product_code_by_line_item_id": product_code_by_line_item_id,
            "last_purchase_by_product_code": cls._build_last_purchase_lookup(product_codes),
        }

    @staticmethod
    def _parse_ordering_param(raw_ordering, allowed_fields, default_ordering):
        ordering = []
        for token in (raw_ordering or "").split(","):
            value = token.strip()
            if not value:
                continue
            normalized = value[1:] if value.startswith("-") else value
            if normalized in allowed_fields:
                ordering.append(value)
        return ordering or default_ordering

    def get_serializer_class(self):
        if self.action == "list":
            return PurchaseRequisitionListSerializer
        return PurchaseRequisitionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        status_value = (self.request.query_params.get("status") or "").strip()
        if status_value:
            queryset = queryset.filter(status__iexact=status_value)

        queryset = self._filter_by_material_categories(queryset)
        queryset = self._filter_by_vendors(queryset)
        queryset = self._filter_by_specific_products(queryset)

        return queryset.distinct()

    @action(detail=False, methods=["get"], url_path="filter-options")
    def filter_options(self, request, *args, **kwargs):
        product_ids = (
            PurchaseRequisitionLineItem.objects.exclude(product_id__isnull=True)
            .values_list("product_id", flat=True)
            .distinct()
        )
        products = Product.objects.filter(id__in=product_ids)

        material_categories = list(
            Category.objects.filter(products__id__in=product_ids)
            .distinct()
            .order_by("name")
            .values("id", label=F("name"))
        )

        vendors = list(
            Vendor.objects.filter(products__id__in=product_ids)
            .exclude(trade_name__isnull=True)
            .exclude(trade_name__exact="")
            .distinct()
            .order_by("trade_name")
            .values("id", label=F("trade_name"))
        )

        specific_products = list(
            products.exclude(name__isnull=True)
            .exclude(name__exact="")
            .order_by("name")
            .values("id", label=F("name"))
            .distinct()
        )

        serializer = PurchaseRequisitionFilterOptionsSerializer(
            data={
                "material_categories": material_categories,
                "vendors": vendors,
                "specific_products": specific_products,
            }
        )
        serializer.is_valid(raise_exception=True)
        return APIResponse.success(
            data=serializer.validated_data,
            message="Purchase requisition filter options retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="approved-line-items")
    def approved_line_items(self, request, *args, **kwargs):
        queryset = PurchaseRequisitionLineItem.objects.select_related("purchase_requisition").filter(
            purchase_requisition__is_approved=True
        )
        existing_po_line_items = PurchaseOrderLineItem.objects.filter(
            purchase_requisition_id=OuterRef("purchase_requisition_id")
        ).filter(
            Q(product_code=OuterRef("product_code"))
            | (
                (Q(product_code__isnull=True) | Q(product_code__exact=""))
                & Q(description=OuterRef("product_name"))
            )
        )
        queryset = queryset.annotate(_has_purchase_order=Exists(existing_po_line_items)).filter(
            _has_purchase_order=False
        )

        category_ids, category_names = self._parse_filter_tokens(request, "product_category", "product_categories")
        if category_ids:
            category_names.extend(
                Category.objects.filter(id__in=category_ids).values_list("name", flat=True)
            )
        category_names = list(dict.fromkeys(name for name in category_names if name))
        if category_names:
            queryset = queryset.filter(product_category__in=category_names)

        _unused_ids, product_names = self._parse_filter_tokens(request, "product_name", "product_names")
        product_names = list(dict.fromkeys(name for name in product_names if name))
        if product_names:
            queryset = queryset.filter(product_name__in=product_names)

        vendor_ids, vendor_names = self._parse_filter_tokens(
            request,
            "preferred_supplier",
            "preferred_suppliers",
            "vendors",
        )
        if vendor_ids or vendor_names:
            product_filter = Q()
            if vendor_ids:
                product_filter |= Q(preferred_supplier_id__in=vendor_ids)
            if vendor_names:
                product_filter |= Q(preferred_supplier__trade_name__in=vendor_names)
            product_ids = Product.objects.filter(product_filter).values_list("id", flat=True)
            queryset = queryset.filter(product_id__in=product_ids)

        pr_ids, pr_numbers = self._parse_filter_tokens(
            request,
            "purchase_request_number",
            "purchase_request_numbers",
        )
        if pr_ids:
            queryset = queryset.filter(purchase_requisition_id__in=pr_ids)
        pr_numbers = list(dict.fromkeys(number for number in pr_numbers if number))
        if pr_numbers:
            queryset = queryset.filter(purchase_requisition__purchase_request_number__in=pr_numbers)

        search_term = (request.query_params.get("search") or "").strip()
        if search_term:
            queryset = queryset.filter(
                Q(product_name__icontains=search_term)
                | Q(product_code__icontains=search_term)
                | Q(product_category__icontains=search_term)
                | Q(purchase_requisition__purchase_request_number__icontains=search_term)
            )

        ordering = self._parse_ordering_param(
            request.query_params.get("ordering"),
            {
                "id",
                "purchase_requisition_id",
                "product_name",
                "product_code",
                "requested_qty",
                "net_required_qty",
            },
            ["id"],
        )
        queryset = queryset.order_by(*ordering)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ApprovedPurchaseRequisitionLineItemSerializer(
                page,
                many=True,
                context=self._approved_line_item_serializer_context(page),
            )
            return self.get_paginated_response(serializer.data)

        line_items = list(queryset)
        serializer = ApprovedPurchaseRequisitionLineItemSerializer(
            line_items,
            many=True,
            context=self._approved_line_item_serializer_context(line_items),
        )
        return APIResponse.success(
            data=serializer.data,
            message="Approved purchase requisition line items retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="line-items/product-categories-dropdown")
    def line_item_product_categories_dropdown(self, request, *args, **kwargs):
        query = (request.query_params.get("search") or request.query_params.get("query") or "").strip()
        queryset = (
            PurchaseRequisitionLineItem.objects.exclude(product_category__isnull=True)
            .exclude(product_category__exact="")
            .values_list("product_category", flat=True)
            .distinct()
            .order_by("product_category")
        )
        if query:
            queryset = queryset.filter(product_category__icontains=query)

        options = [{"value": value, "label": value} for value in queryset]
        serializer = PurchaseRequisitionLineItemDropdownOptionSerializer(data=options, many=True)
        serializer.is_valid(raise_exception=True)
        return APIResponse.success(
            data=serializer.validated_data,
            message="Line item product categories retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="line-items/filter-options")
    def line_item_filter_options(self, request, *args, **kwargs):
        base_path = "/api/v1/inventory/purchase-requisitions/line-items"
        payload = [
            {
                "key": "product_category",
                "label": "Product Category",
                "options_endpoint": f"{base_path}/product-categories-dropdown/",
            },
            {
                "key": "product_name",
                "label": "Product Name",
                "options_endpoint": f"{base_path}/product-names-dropdown/",
            },
            {
                "key": "preferred_supplier",
                "label": "Preferred Supplier",
                "options_endpoint": f"{base_path}/preferred-supplier-dropdown/",
            },
            {
                "key": "purchase_request_number",
                "label": "Purchase Request Number",
                "options_endpoint": f"{base_path}/purchase-request-numbers-dropdown/",
            },
        ]
        serializer = PurchaseRequisitionLineItemFilterOptionSerializer(data=payload, many=True)
        serializer.is_valid(raise_exception=True)
        return APIResponse.success(
            data=serializer.validated_data,
            message="Line item filter options retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="line-items/product-names-dropdown")
    def line_item_product_names_dropdown(self, request, *args, **kwargs):
        query = (request.query_params.get("search") or request.query_params.get("query") or "").strip()
        queryset = (
            PurchaseRequisitionLineItem.objects.exclude(product_name__isnull=True)
            .exclude(product_name__exact="")
            .values_list("product_name", flat=True)
            .distinct()
            .order_by("product_name")
        )
        if query:
            queryset = queryset.filter(product_name__icontains=query)

        options = [{"value": value, "label": value} for value in queryset]
        serializer = PurchaseRequisitionLineItemDropdownOptionSerializer(data=options, many=True)
        serializer.is_valid(raise_exception=True)
        return APIResponse.success(
            data=serializer.validated_data,
            message="Line item product names retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="line-items/preferred-supplier-dropdown")
    def line_item_preferred_supplier_dropdown(self, request, *args, **kwargs):
        query = (request.query_params.get("search") or request.query_params.get("query") or "").strip()
        product_ids = (
            PurchaseRequisitionLineItem.objects.exclude(product_id__isnull=True)
            .values_list("product_id", flat=True)
            .distinct()
        )
        vendors = (
            Vendor.objects.filter(products__id__in=product_ids)
            .exclude(trade_name__isnull=True)
            .exclude(trade_name__exact="")
            .distinct()
            .order_by("trade_name")
        )
        if query:
            vendors = vendors.filter(trade_name__icontains=query)

        options = [{"value": str(vendor.id), "label": vendor.trade_name} for vendor in vendors]
        serializer = PurchaseRequisitionLineItemDropdownOptionSerializer(data=options, many=True)
        serializer.is_valid(raise_exception=True)
        return APIResponse.success(
            data=serializer.validated_data,
            message="Line item preferred suppliers retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="line-items/purchase-request-numbers-dropdown")
    def line_item_purchase_request_numbers_dropdown(self, request, *args, **kwargs):
        query = (request.query_params.get("search") or request.query_params.get("query") or "").strip()
        queryset = (
            PurchaseRequisition.objects.filter(is_approved=True)
            .exclude(purchase_request_number__isnull=True)
            .exclude(purchase_request_number__exact="")
            .values_list("purchase_request_number", flat=True)
            .distinct()
            .order_by("purchase_request_number")
        )
        if query:
            queryset = queryset.filter(purchase_request_number__icontains=query)

        options = [{"value": value, "label": value} for value in queryset]
        serializer = PurchaseRequisitionLineItemDropdownOptionSerializer(data=options, many=True)
        serializer.is_valid(raise_exception=True)
        return APIResponse.success(
            data=serializer.validated_data,
            message="Line item purchase request numbers retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        try:
            payload = self._normalize_payload(request)
        except (TypeError, ValueError, json.JSONDecodeError):
            return APIResponse.error(
                message="Invalid line_items. Send a valid JSON array for line_items.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message="Purchase Requisition created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        computed_actions = build_actions(request.user, self.permission_prefix)
        detail_actions = {
            "canApprove": bool(computed_actions.get("canApprove", False)),
            "canReject": bool(computed_actions.get("canReject", False)),
        }

        if isinstance(data, dict):
            data = {**data, "actions": detail_actions}

        return APIResponse.success(
            data=data,
            message=f"{self.queryset.model._meta.verbose_name.title()} retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

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

    @action(detail=True, methods=["patch"], url_path="approve")
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        value = self._parse_boolean_action_value(request.data.get("value", None), "value")
        user = request.user if request.user and request.user.is_authenticated else None
        was_approved = bool(instance.is_approved)

        instance.is_approved = value
        if value:
            instance.is_rejected = False
            instance.approved_by = user
            instance.rejected_by = None
            instance.reject_note = ""
        else:
            instance.approved_by = None

        instance.updated_by = user if user else instance.updated_by
        instance.save(
            update_fields=[
                "is_approved",
                "is_rejected",
                "approved_by",
                "rejected_by",
                "reject_note",
                "updated_by",
                "updated_at",
            ]
        )
        if value and not was_approved:
            instance.ensure_production_order()

        message = "Purchase Requisition Approved" if value else "Purchase Requisition Approval Cancelled"
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
            raise ValidationError({"reject_note": "This field is required when rejecting Purchase Requisition."})
        user = request.user if request.user and request.user.is_authenticated else None

        instance.is_rejected = value
        if value:
            instance.is_approved = False
            instance.rejected_by = user
            instance.reject_note = reject_note
            instance.approved_by = None
        else:
            instance.rejected_by = None
            instance.reject_note = ""

        instance.updated_by = user if user else instance.updated_by
        instance.save(
            update_fields=[
                "is_approved",
                "is_rejected",
                "approved_by",
                "rejected_by",
                "reject_note",
                "updated_by",
                "updated_at",
            ]
        )

        message = "Purchase Requisition Rejected" if value else "Purchase Requisition Rejection Cancelled"
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="product-names")
    def product_names(self, request, *args, **kwargs):
        product_names = (
            PurchaseRequisitionLineItem.objects.exclude(product_name__isnull=True)
            .exclude(product_name__exact="")
            .order_by("product_name")
            .values_list("product_name", flat=True)
            .distinct()
        )
        return APIResponse.success(
            data=list(product_names),
            message="Product names retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="product-categories")
    def product_categories(self, request, *args, **kwargs):
        product_categories = (
            PurchaseRequisitionLineItem.objects.exclude(product_category__isnull=True)
            .exclude(product_category__exact="")
            .order_by("product_category")
            .values_list("product_category", flat=True)
            .distinct()
        )
        return APIResponse.success(
            data=list(product_categories),
            message="Product categories retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="preferred-vendor-names")
    def preferred_vendor_names(self, request, *args, **kwargs):
        product_ids = (
            PurchaseRequisitionLineItem.objects.exclude(product_id__isnull=True)
            .values_list("product_id", flat=True)
            .distinct()
        )
        preferred_vendor_names = (
            Product.objects.filter(id__in=product_ids)
            .exclude(preferred_supplier__isnull=True)
            .exclude(preferred_supplier__trade_name__isnull=True)
            .exclude(preferred_supplier__trade_name__exact="")
            .order_by("preferred_supplier__trade_name")
            .values_list("preferred_supplier__trade_name", flat=True)
            .distinct()
        )
        return APIResponse.success(
            data=list(preferred_vendor_names),
            message="Preferred vendor names retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class PurchaseRequisitionLineItemViewSet(BaseInventoryViewSet):
    queryset = PurchaseRequisitionLineItem.objects.select_related("purchase_requisition")
    serializer_class = PurchaseRequisitionLineItemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "purchase_requisition__id",
        "product_name",
        "product_code",
        "product_category",
    ]
    ordering_fields = [
        "id",
        "purchase_requisition_id",
        "product_name",
        "product_code",
        "requested_qty",
        "net_required_qty",
    ]
    ordering = ["id"]
    permission_prefix = "procurement.purchase_requisitions"


class PurchaseRequisitionProductNameViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, RBACPermission]
    permission_prefix = "procurement.purchase_requisitions"

    def list(self, request, *args, **kwargs):
        product_names = (
            PurchaseRequisitionLineItem.objects.exclude(product_name__isnull=True)
            .exclude(product_name__exact="")
            .order_by("product_name")
            .values_list("product_name", flat=True)
            .distinct()
        )
        return APIResponse.success(
            data=list(product_names),
            message="Product names retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class PurchaseRequisitionProductCategoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, RBACPermission]
    permission_prefix = "procurement.purchase_requisitions"

    def list(self, request, *args, **kwargs):
        product_categories = (
            PurchaseRequisitionLineItem.objects.exclude(product_category__isnull=True)
            .exclude(product_category__exact="")
            .order_by("product_category")
            .values_list("product_category", flat=True)
            .distinct()
        )
        return APIResponse.success(
            data=list(product_categories),
            message="Product categories retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class PurchaseRequisitionPreferredVendorNameViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, RBACPermission]
    permission_prefix = "procurement.purchase_requisitions"

    def list(self, request, *args, **kwargs):
        product_ids = (
            PurchaseRequisitionLineItem.objects.exclude(product_id__isnull=True)
            .values_list("product_id", flat=True)
            .distinct()
        )
        preferred_vendor_names = (
            Product.objects.filter(id__in=product_ids)
            .exclude(preferred_supplier__isnull=True)
            .exclude(preferred_supplier__trade_name__isnull=True)
            .exclude(preferred_supplier__trade_name__exact="")
            .order_by("preferred_supplier__trade_name")
            .values_list("preferred_supplier__trade_name", flat=True)
            .distinct()
        )
        return APIResponse.success(
            data=list(preferred_vendor_names),
            message="Preferred vendor names retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
