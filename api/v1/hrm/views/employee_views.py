import json
import re
from pathlib import Path
from uuid import uuid4

from django.core.files.storage import default_storage
from rest_framework import filters, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from apps.hrm.models.employee import Employee
from core.utils.responses import APIResponse

from ..serializers.employee_serializers import (
    EmployeeLightweightSerializer,
    EmployeeListSerializer,
    EmployeeSerializer,
)
from .shared import BaseHRMViewSet


class CompanyScopedEmployeeQuerysetMixin:
    """Shared company-aware employee queryset logic for employee endpoints."""

    def get_company_scoped_employee_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Employee.objects.all()
        if hasattr(user, "company") and user.company:
            return Employee.objects.filter(company=user.company)
        return Employee.objects.none()

    def apply_user_link_filter(self, queryset):
        """
        Filter employees by whether they are linked to an auth user.

        Supported query params:
        - `has_user=true`
        - `has_user=false`
        """
        has_user = self.request.query_params.get("has_user")
        if has_user is None:
            return queryset

        normalized_value = has_user.strip().lower()
        if normalized_value in {"true", "1", "yes"}:
            return queryset.filter(user__isnull=False)
        if normalized_value in {"false", "0", "no"}:
            return queryset.filter(user__isnull=True)
        return queryset


class EmployeeViewSet(CompanyScopedEmployeeQuerysetMixin, BaseHRMViewSet):
    """
    API v1 CRUD viewset for Employee.

    Features:
    - List / retrieve / create / update / delete employees
    - Authenticated access by default
    - Filtered by company
    """

    queryset = Employee.objects.select_related("user", "department", "designation")
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "user__username", "user__first_name", "user__last_name"]
    ordering_fields = ["created_at", "first_name", "last_name"]
    ordering = ["-created_at"]
    permission_prefix = "hr.employees"
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    file_upload_fields = {
        "profile_photo",
        "employee_signature",
        "hr_signature",
        "passport_copy",
        "visa_document",
        "cv_document",
    }
    multi_file_upload_field = "educational_certificates_document"
    previous_employment_certificate_patterns = (
        re.compile(r"^previous_employments\[(\d+)\]\[experience_certificate\]$"),
        re.compile(r"^previous_employments\[(\d+)\]\.experience_certificate$"),
        re.compile(r"^previous_employments\.(\d+)\.experience_certificate$"),
    )
    permit_document_patterns = (
        re.compile(r"^permits\[(\d+)\]\[permits_document\]$"),
        re.compile(r"^permits\[(\d+)\]\.permits_document$"),
        re.compile(r"^permits\.(\d+)\.permits_document$"),
    )

    def _save_educational_certificate_files(self, files):
        saved_paths = []
        for uploaded_file in files:
            safe_name = Path(uploaded_file.name).name
            target_name = f"{uuid4().hex}_{safe_name}"
            target_path = f"employees/documents/educational_certificates/{target_name}"
            stored_path = default_storage.save(target_path, uploaded_file)
            saved_paths.append(stored_path)
        return saved_paths

    def _extract_previous_employment_index(self, key):
        for pattern in self.previous_employment_certificate_patterns:
            match = pattern.match(key)
            if match:
                return int(match.group(1))
        return None

    def _extract_permit_index(self, key):
        for pattern in self.permit_document_patterns:
            match = pattern.match(key)
            if match:
                return int(match.group(1))
        return None

    def _inject_previous_employment_files(self, payload, request):
        indexed_files = []
        for key, file in request.FILES.items():
            index = self._extract_previous_employment_index(key)
            if index is None:
                continue
            indexed_files.append((index, file))

        if not indexed_files:
            return None

        previous_employments = payload.get("previous_employments")
        if previous_employments is None:
            return APIResponse.error(
                errors={"previous_employments": ["Required in data JSON when sending experience_certificate files."]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(previous_employments, list):
            return APIResponse.error(
                errors={"previous_employments": ["Expected a list in data JSON."]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        for index, file in indexed_files:
            if index >= len(previous_employments):
                return APIResponse.error(
                    errors={"previous_employments": [f"Invalid index {index} for experience_certificate file."]},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            if not isinstance(previous_employments[index], dict):
                return APIResponse.error(
                    errors={"previous_employments": [f"Item at index {index} must be an object."]},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            previous_employments[index]["experience_certificate"] = file
        return None

    def _inject_permit_files(self, payload, request):
        indexed_files = []
        for key, file in request.FILES.items():
            index = self._extract_permit_index(key)
            if index is None:
                continue
            indexed_files.append((index, file))

        if not indexed_files:
            return None

        permits = payload.get("permits")
        if permits is None:
            return APIResponse.error(
                errors={"permits": ["Required in data JSON when sending permits_document files."]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(permits, list):
            return APIResponse.error(
                errors={"permits": ["Expected a list in data JSON."]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        for index, file in indexed_files:
            if index >= len(permits):
                return APIResponse.error(
                    errors={"permits": [f"Invalid index {index} for permits_document file."]},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            if not isinstance(permits[index], dict):
                return APIResponse.error(
                    errors={"permits": [f"Item at index {index} must be an object."]},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            permits[index]["permits_document"] = file
        return None

    def _build_employee_payload(self, request):
        content_type = request.content_type or ""
        if "multipart/form-data" not in content_type:
            return request.data, None

        raw_data = request.data.get("data")
        if raw_data in (None, ""):
            parsed_data = {}
        elif isinstance(raw_data, dict):
            parsed_data = raw_data
        else:
            try:
                parsed_data = json.loads(raw_data)
            except (TypeError, ValueError):
                return None, APIResponse.error(
                    errors={"data": ["Invalid JSON format."]},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        if not isinstance(parsed_data, dict):
            return None, APIResponse.error(
                errors={"data": ["JSON object is required."]},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        payload = dict(parsed_data)
        for key, file in request.FILES.items():
            if key == self.multi_file_upload_field:
                continue
            if self._extract_previous_employment_index(key) is not None:
                continue
            if self._extract_permit_index(key) is not None:
                continue
            payload[key] = file
        multi_files = request.FILES.getlist(self.multi_file_upload_field)
        if multi_files:
            payload[self.multi_file_upload_field] = self._save_educational_certificate_files(multi_files)
        error_response = self._inject_previous_employment_files(payload, request)
        if error_response is not None:
            return None, error_response
        error_response = self._inject_permit_files(payload, request)
        if error_response is not None:
            return None, error_response
        return payload, None

    def _validate_file_payload(self, payload, request):
        """
        Ensure file fields are sent as real multipart file streams.
        Prevents saving filename/path strings that do not exist in storage.
        """
        for field in self.file_upload_fields:
            if field not in payload:
                continue

            has_uploaded_file = field in request.FILES
            raw_value = payload.get(field)
            is_empty_value = raw_value in (None, "", "null")

            if not has_uploaded_file and not is_empty_value:
                return APIResponse.error(
                    errors={
                        field: [
                            (
                                f"Invalid {field} payload. Send {field} as multipart/form-data "
                                "with a real file stream."
                            )
                        ]
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if not has_uploaded_file and is_empty_value and request.method not in {"PUT", "PATCH"}:
                return APIResponse.error(
                    errors={
                        field: [
                            (
                                f"Empty {field} value is not allowed. "
                                f"To keep existing {field}, omit the {field} key."
                            )
                        ]
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        if self.multi_file_upload_field in payload:
            uploaded_files = request.FILES.getlist(self.multi_file_upload_field)
            raw_value = payload.get(self.multi_file_upload_field)
            is_empty_value = raw_value in (None, "", "null")

            if not uploaded_files and not is_empty_value and raw_value != []:
                return APIResponse.error(
                    errors={
                        self.multi_file_upload_field: [
                            (
                                f"Invalid {self.multi_file_upload_field} payload. Send it as multipart/form-data "
                                "with one or more real file streams."
                            )
                        ]
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        return None

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeListSerializer
        return EmployeeSerializer

    def get_queryset(self):
        queryset = self.get_company_scoped_employee_queryset().select_related("user", "department", "designation")
        return self.apply_user_link_filter(queryset)

    def create(self, request, *args, **kwargs):
        payload, error_response = self._build_employee_payload(request)
        if error_response is not None:
            return error_response
        error_response = self._validate_file_payload(payload, request)
        if error_response is not None:
            return error_response

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.queryset.model._meta.verbose_name.title()} created successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        payload, error_response = self._build_employee_payload(request)
        if error_response is not None:
            return error_response
        error_response = self._validate_file_payload(payload, request)
        if error_response is not None:
            return error_response

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=payload, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.queryset.model._meta.verbose_name.title()} updated successfully.",
            status_code=status.HTTP_200_OK,
        )


class EmployeeLightweightViewSet(CompanyScopedEmployeeQuerysetMixin, BaseHRMViewSet):
    """
    Lightweight employee API (id + full_name).
    Useful for dropdowns/autocomplete.
    """

    queryset = Employee.objects.select_related("user")
    serializer_class = EmployeeLightweightSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "user__first_name", "user__last_name", "email", "user__username"]
    ordering_fields = ["created_at", "first_name", "last_name"]
    ordering = ["first_name", "last_name", "-created_at"]
    permission_prefix = "hr.employees"

    def get_queryset(self):
        queryset = self.get_company_scoped_employee_queryset().select_related("user")
        return self.apply_user_link_filter(queryset)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return APIResponse.success(
                data={
                    "items": serializer.data,
                    "pagination": {
                        "count": self.paginator.page.paginator.count,
                        "total_pages": self.paginator.page.paginator.num_pages,
                        "current_page": self.paginator.page.number,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link(),
                    },
                },
                message="Employees retrieved successfully.",
                status_code=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Employees retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
