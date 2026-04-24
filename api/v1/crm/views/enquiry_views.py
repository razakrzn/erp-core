from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.conf import settings
from django.db.models.functions import Lower
import socket

from apps.crm.models import Enquiry

from ..serializers import EnquiryDetailSerializer, EnquiryListSerializer
from .shared import BaseCRMViewSet


class EnquiryViewSet(BaseCRMViewSet):
    queryset = Enquiry.objects.select_related("existing_client")
    serializer_class = EnquiryDetailSerializer
    search_fields = [
        "enquiry_code",
        "project_name",
        "company_name",
        "trn",
        "phone_number",
        "new_client_name",
        "existing_client__customer_name",
    ]
    ordering_fields = ["enquiry_code", "project_name", "trn", "created_at", "updated_at"]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    permission_prefix = "sales.enquiry"

    def filter_queryset(self, queryset):
        ordering = self.request.query_params.get("ordering", "")
        if "project_name" in ordering:
            queryset = queryset.annotate(project_name_lower=Lower("project_name"))

        queryset = super().filter_queryset(queryset)

        # After OrderingFilter has applied sorting, if it was project_name, 
        # replace it with project_name_lower in the queryset's order_by clause.
        if "project_name" in ordering:
            new_order = []
            for field in queryset.query.order_by:
                if field == "project_name":
                    new_order.append("project_name_lower")
                elif field == "-project_name":
                    new_order.append("-project_name_lower")
                else:
                    new_order.append(field)
            queryset = queryset.order_by(*new_order)

        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        status_value = (self.request.query_params.get("status") or "").strip()
        if status_value:
            queryset = queryset.filter(status__iexact=status_value)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return EnquiryListSerializer
        return EnquiryDetailSerializer

    def _validate_attachment_payload(self, request):
        """
        Ensure attachment writes include an actual uploaded file stream.
        Prevents saving only a filename/path string, which produces broken media URLs.
        Also prevents accidental clears when clients send empty attachment values.
        """
        if "attachment" not in request.data:
            return

        has_uploaded_file = "attachment" in request.FILES
        raw_value = request.data.get("attachment")
        is_empty_value = raw_value in (None, "", "null")

        if not has_uploaded_file and not is_empty_value:
            raise ValidationError(
                {
                    "attachment": (
                        "Invalid attachment payload. Send attachment as multipart/form-data "
                        "with a real file stream."
                    )
                }
            )

        if not has_uploaded_file and is_empty_value:
            raise ValidationError(
                {
                    "attachment": (
                        "Empty attachment value is not allowed. "
                        "To keep existing file, omit the attachment key."
                    )
                }
            )

    def create(self, request, *args, **kwargs):
        self._validate_attachment_payload(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._validate_attachment_payload(request)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="attachment-debug")
    def attachment_debug(self, request, pk=None):
        """
        Diagnose attachment resolution for a single enquiry.
        Helps identify whether failures are due to DB value, file storage, or URL routing.
        """
        enquiry = self.get_object()
        attachment = enquiry.attachment

        if not attachment:
            return Response(
                {
                    "has_attachment": False,
                    "message": "No attachment is set on this enquiry.",
                }
            )

        # Build absolute URL exactly as serializers do when request context is present.
        relative_url = attachment.url
        absolute_url = request.build_absolute_uri(relative_url)

        exists = attachment.storage.exists(attachment.name)
        try:
            physical_path = attachment.path
        except Exception:
            physical_path = None
        try:
            file_size = attachment.size if exists else None
        except Exception:
            file_size = None

        return Response(
            {
                "has_attachment": True,
                "attachment_name": attachment.name,
                "relative_url": relative_url,
                "absolute_url": absolute_url,
                "storage_exists": exists,
                "file_size": file_size,
                "physical_path": physical_path,
                "media_root": str(settings.MEDIA_ROOT),
                "server_hostname": socket.gethostname(),
            }
        )
