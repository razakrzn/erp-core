from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser

from apps.production.models import CuttingOptimizationJob
from apps.production.services import validate_cad_file_name
from apps.production.tasks import process_cutting_optimization_job_sync
from core.utils.responses import APIResponse

from ..serializers import CuttingOptimizationJobListSerializer, CuttingOptimizationJobSerializer
from .shared import BaseProductionViewSet


class CuttingOptimizationJobViewSet(BaseProductionViewSet):
    queryset = CuttingOptimizationJob.objects.all()
    serializer_class = CuttingOptimizationJobSerializer
    parser_classes = [MultiPartParser, FormParser]
    search_fields = ["name", "slug", "status"]
    ordering_fields = ["created_at", "updated_at", "name", "status"]
    ordering = ["-created_at"]
    permission_prefix = "production.cutting_optimization"

    def _job_has_reprocessable_cad(self, job: CuttingOptimizationJob) -> bool:
        if not job.cad_file:
            return False
        is_valid, _ = validate_cad_file_name(job.cad_file.name or "")
        if not is_valid:
            return False
        try:
            return job.cad_file.storage.exists(job.cad_file.name)
        except Exception:
            return False

    def _dispatch_optimization(self, job):
        try:
            from apps.production.tasks import process_cutting_optimization_job

            process_cutting_optimization_job.delay(job.id)
        except Exception:
            # Fallback to sync processing when Celery/broker is unavailable.
            try:
                process_cutting_optimization_job_sync(job)
            except Exception as exc:
                job.status = "failed"
                job.error_message = str(exc)
                job.save(update_fields=["status", "error_message", "updated_at"])
                raise
            return

        job.status = "pending"
        job.error_message = ""
        job.save(update_fields=["status", "error_message", "updated_at"])

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CuttingOptimizationJobListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CuttingOptimizationJobListSerializer(queryset, many=True)
        return APIResponse.success(
            data={"items": serializer.data, "pagination": None},
            message="Data retrieved successfully",
            status_code=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return APIResponse.success(
            data=serializer.data,
            message="Cutting optimization job retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.save(status="pending")
        self._dispatch_optimization(job)

        # Refresh to return latest state if sync fallback ran.
        job.refresh_from_db()
        response_serializer = self.get_serializer(job)
        return APIResponse.success(
            data=response_serializer.data,
            message="Cutting optimization started successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="retry")
    def retry(self, request, *args, **kwargs):
        job = self.get_object()

        reuploaded_cad = request.FILES.get("cad_file")
        if reuploaded_cad:
            is_valid, error_message = validate_cad_file_name(reuploaded_cad.name or "")
            if not is_valid:
                message = error_message or "Unsupported CAD file."
                return APIResponse.error(
                    errors={"cad_file": [message]},
                    message="Validation error",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        if reuploaded_cad is None and not self._job_has_reprocessable_cad(job):
            return APIResponse.error(
                errors={"cad_file": ["Original CAD source is unavailable. Please reupload a .dxf file and retry."]},
                message="CAD reupload required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        update_fields = ["status", "error_message", "updated_at"]
        if reuploaded_cad:
            old_name = job.cad_file.name if job.cad_file else ""
            job.cad_file = reuploaded_cad
            if old_name and old_name != job.cad_file.name:
                job.cad_file.storage.delete(old_name)
            update_fields.append("cad_file")

        job.status = "pending"
        job.error_message = ""
        job.save(update_fields=update_fields)
        self._dispatch_optimization(job)
        job.refresh_from_db()
        serializer = self.get_serializer(job)
        return APIResponse.success(
            data=serializer.data,
            message="Cutting optimization retry triggered successfully.",
            status_code=status.HTTP_200_OK,
        )
