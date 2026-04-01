from celery import shared_task

from .models import CuttingOptimizationJob
from .services import run_cutting_optimization

def process_cutting_optimization_job_sync(job: CuttingOptimizationJob) -> None:
    if not job.cad_file:
        raise ValueError("CAD source file is missing. Please reupload and retry.")

    result = run_cutting_optimization(
        file_path=job.cad_file.path,
        stock_sheets=job.stock_sheets,
    )

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
