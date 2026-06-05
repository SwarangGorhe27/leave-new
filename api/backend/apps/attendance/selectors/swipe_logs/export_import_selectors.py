from typing import Optional, List
import uuid
from django.db.models import QuerySet
from apps.attendance.models import SwipeLogExportJob, SwipeLogImportJob, PunchLog

def get_export_job(job_id: uuid.UUID, company_id: uuid.UUID) -> Optional[SwipeLogExportJob]:
    """Retrieve an export job by ID and company."""
    return SwipeLogExportJob.objects.filter(id=job_id, company_id=company_id).first()

def get_import_job(import_id: uuid.UUID, company_id: uuid.UUID) -> Optional[SwipeLogImportJob]:
    """Retrieve an import job by ID and company."""
    return SwipeLogImportJob.objects.filter(id=import_id, company_id=company_id).first()

def get_filtered_swipe_logs(company_id: uuid.UUID, filters: dict) -> QuerySet[PunchLog]:
    """Get filtered swipe logs for export."""
    qs = PunchLog.objects.filter(company_id=company_id)
    
    if "from_date" in filters and filters["from_date"]:
        qs = qs.filter(punch_time__date__gte=filters["from_date"])
    if "to_date" in filters and filters["to_date"]:
        qs = qs.filter(punch_time__date__lte=filters["to_date"])
    if "employee_ids" in filters and filters["employee_ids"]:
        qs = qs.filter(employee_id__in=filters["employee_ids"])
    if "department_ids" in filters and filters["department_ids"]:
        qs = qs.filter(employee__department_id__in=filters["department_ids"])
    if "device_ids" in filters and filters["device_ids"]:
        qs = qs.filter(device_id__in=filters["device_ids"])
    if "punch_type" in filters and filters["punch_type"]:
        qs = qs.filter(punch_type=filters["punch_type"])
        
    return qs.order_by("punch_time")
