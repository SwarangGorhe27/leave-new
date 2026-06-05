import uuid
from typing import Dict, Any
from django.utils import timezone
from apps.attendance.models import SwipeLogExportJob, ExportStatus
from apps.attendance.selectors.swipe_logs.export_import_selectors import get_filtered_swipe_logs
from apps.attendance.validators.export_import_validators import validate_export_filters
from apps.attendance.tasks.swipe_log_export_task import process_export_job
def queue_export_job(company_id: uuid.UUID, employee_id: uuid.UUID, filters: Dict[str, Any]) -> SwipeLogExportJob:
    """Create and queue a swipe log export job."""
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    
    validate_export_filters(from_date, to_date)
    
    export_format = filters.get("format", "CSV")
    
    # In a real system, we'd estimate total_records here or let the celery task do it.
    qs = get_filtered_swipe_logs(company_id, filters)
    total_records = qs.count()
    
    job = SwipeLogExportJob.objects.create(
        company_id=company_id,
        requested_by_id=employee_id,
        export_format=export_format,
        status=ExportStatus.QUEUED if hasattr(ExportStatus, 'QUEUED') else ExportStatus.PENDING,
        total_records=total_records,
        employee_ids=filters.get("employee_ids", []),
        department_ids=filters.get("department_ids", []),
        from_date=from_date,
        to_date=to_date,
        punch_types=[filters.get("punch_type")] if filters.get("punch_type") else []
    )
    
    # In a production system, we would trigger a celery task here:
    # process_swipe_log_export.delay(job.id)
    # process_export_job.delay(str(job.id))
    
    return job

def schedule_auto_export(company_id: uuid.UUID, employee_id: uuid.UUID, payload: Dict[str, Any]) -> dict:
    """Configure scheduled auto-export."""
    # Here we would create a scheduled task config (e.g. using django-celery-beat or a custom model)
    # For now, we mock the response as requested.
    return {
        "schedule_id": str(uuid.uuid4()),
        "next_run_at": (timezone.now() + timezone.timedelta(days=1)).isoformat()
    }
