from celery import shared_task

from .models import CuttingOptimizationJob
from .services import run_cutting_optimization


@shared_task
def process_cutting_optimization_job(job_id: int):
    job = CuttingOptimizationJob.objects.get(pk=job_id)
    job.status = "processing"
    job.error_message = ""
    job.save(update_fields=["status", "error_message", "updated_at"])

    try:
        result = run_cutting_optimization(
            file_path=job.cad_file.path,
            stock_sheets=job.stock_sheets,
        )
        job.extracted_parts = result.get("parts", [])
        job.optimization_result = result
        job.status = "completed"
        job.save(update_fields=["extracted_parts", "optimization_result", "status", "updated_at"])
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.save(update_fields=["status", "error_message", "updated_at"])
        raise
