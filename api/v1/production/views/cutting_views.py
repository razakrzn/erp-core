from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser

from apps.production.models import CuttingOptimizationJob
from apps.production.services import run_cutting_optimization
from core.utils.responses import APIResponse

from ..serializers import CuttingOptimizationJobSerializer


class CuttingOptimizationJobViewSet(viewsets.ModelViewSet):
    queryset = CuttingOptimizationJob.objects.all()
    serializer_class = CuttingOptimizationJobSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug", "status"]
    ordering_fields = ["created_at", "updated_at", "name", "status"]
    ordering = ["-created_at"]

    def _dispatch_optimization(self, job):
        try:
            from apps.production.tasks import process_cutting_optimization_job

            process_cutting_optimization_job.delay(job.id)
        except Exception:
            # Fallback to sync processing when Celery/broker is unavailable.
            try:
                result = run_cutting_optimization(job.cad_file.path, job.stock_sheets)
                job.extracted_parts = result.get("parts", [])
                job.optimization_result = result
                job.status = "completed"
                job.error_message = ""
                job.save(
                    update_fields=[
                        "extracted_parts",
                        "optimization_result",
                        "status",
                        "error_message",
                        "updated_at",
                    ]
                )
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
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message="Cutting optimization jobs retrieved successfully.",
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
        job.status = "pending"
        job.error_message = ""
        job.save(update_fields=["status", "error_message", "updated_at"])
        self._dispatch_optimization(job)
        job.refresh_from_db()
        serializer = self.get_serializer(job)
        return APIResponse.success(
            data=serializer.data,
            message="Cutting optimization reprocessing triggered successfully.",
            status_code=status.HTTP_200_OK,
        )
