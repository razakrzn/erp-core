from celery import shared_task
from django.core.files.base import ContentFile

from .models import CuttingOptimizationJob
from .services import build_cutting_job_artifacts, run_cutting_optimization


def _save_file_and_cleanup_previous(field_file, file_name: str, payload: bytes) -> None:
    previous_name = field_file.name
    field_file.save(file_name, ContentFile(payload), save=False)
    if previous_name and previous_name != field_file.name:
        field_file.storage.delete(previous_name)


def process_cutting_optimization_job_sync(job: CuttingOptimizationJob) -> None:
    if not job.cad_file:
        raise ValueError("CAD source file is missing. Please reupload and retry.")

    source_name = job.cad_file.name
    result = run_cutting_optimization(
        file_path=job.cad_file.path,
        stock_sheets=job.stock_sheets,
    )
    artifacts = build_cutting_job_artifacts(
        result,
        source_name=source_name,
        source_file_path=job.cad_file.path,
    )

    _save_file_and_cleanup_previous(
        job.cad_file,
        artifacts["cad_pdf_name"],
        artifacts["cad_pdf_bytes"],
    )
    _save_file_and_cleanup_previous(
        job.cutlist_pdf_file,
        artifacts["cutlist_pdf_name"],
        artifacts["cutlist_pdf_bytes"],
    )
    _save_file_and_cleanup_previous(
        job.cutlist_xlsx_file,
        artifacts["cutlist_xlsx_name"],
        artifacts["cutlist_xlsx_bytes"],
    )

    job.extracted_parts = result.get("parts", [])
    job.optimization_result = result
    job.status = "completed"
    job.error_message = ""
    job.save(
        update_fields=[
            "cad_file",
            "cutlist_pdf_file",
            "cutlist_xlsx_file",
            "extracted_parts",
            "optimization_result",
            "status",
            "error_message",
            "updated_at",
        ]
    )


@shared_task
def process_cutting_optimization_job(job_id: int):
    job = CuttingOptimizationJob.objects.get(pk=job_id)
    job.status = "processing"
    job.error_message = ""
    job.save(update_fields=["status", "error_message", "updated_at"])

    try:
        process_cutting_optimization_job_sync(job)
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.save(update_fields=["status", "error_message", "updated_at"])
        raise
