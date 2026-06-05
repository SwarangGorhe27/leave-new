"""Service layer for attendance background job APIs."""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound

from apps.attendance.models import AttendanceJob, AttendanceJobStatus, AttendanceJobType
from apps.attendance.services.jobs.daily_compute_service import DailyComputeService
from apps.attendance.utils.attendance_job_helpers import (
    append_job_audit_log,
    get_action_source_for_employee,
    get_employee_or_error,
    get_request_employee,
    validate_trigger_role,
)

logger = logging.getLogger(__name__)


class AttendanceBackgroundJobService:
    """Business logic for listing, reading, and creating attendance jobs."""

    @staticmethod
    def list_jobs(company_id, filters: dict):
        queryset = AttendanceJob.objects.filter(
            company_id=company_id,
            deleted_at__isnull=True,
            is_active=True,
        ).select_related("created_by")

        if filters.get("job_type"):
            queryset = queryset.filter(job_type=filters["job_type"])
        if filters.get("status"):
            queryset = queryset.filter(status=filters["status"])
        if filters.get("from_date"):
            queryset = queryset.filter(job_date__gte=filters["from_date"])
        if filters.get("to_date"):
            queryset = queryset.filter(job_date__lte=filters["to_date"])

        return queryset.order_by("-created_at", "-job_date")

    @staticmethod
    def get_job_detail(company_id, job_id) -> AttendanceJob:
        job = AttendanceJob.objects.filter(
            id=job_id,
            company_id=company_id,
            deleted_at__isnull=True,
            is_active=True,
        ).select_related("created_by").first()
        if job is None:
            raise NotFound("Attendance job not found.")
        return job

    @staticmethod
    @transaction.atomic
    def create_daily_compute_job(*, payload: dict, request_user) -> AttendanceJob:
        actor_employee = get_request_employee(request_user)
        role_codes = validate_trigger_role(
            actor_employee=actor_employee,
            request_user=request_user,
            job_date=payload["job_date"],
        )
        triggered_by = (
            get_employee_or_error(
                company_id=payload["company_id"],
                employee_id=payload["triggered_by"],
            )
            if payload.get("triggered_by")
            else actor_employee
        )
        action_source = get_action_source_for_employee(actor_employee, role_codes=role_codes)
        queued_at = timezone.now()

        job = AttendanceJob.objects.create(
            company_id=payload["company_id"],
            job_type=AttendanceJobType.DAILY_COMPUTE,
            job_date=payload["job_date"],
            status=AttendanceJobStatus.QUEUED,
            attempt_count=0,
            created_by=triggered_by,
            updated_by=actor_employee or triggered_by,
            meta_data={
                "queued_at": queued_at.isoformat(),
                "triggered_by": (
                    {
                        "id": str(triggered_by.id),
                        "name": triggered_by.full_name,
                        "employee_code": triggered_by.employee_code,
                    }
                    if triggered_by
                    else {"role": "SYSTEM"}
                ),
                "action_source": action_source,
            },
        )

        task_id = DailyComputeService.trigger_daily_compute(job.id)
        job.meta_data = {
            **(job.meta_data or {}),
            "celery_task_id": task_id,
        }
        job.save(update_fields=["meta_data", "updated_at"])

        append_job_audit_log(
            company_id=job.company_id,
            job_id=job.id,
            action="INSERT",
            changed_by_id=getattr(actor_employee, "id", None) or getattr(triggered_by, "id", None),
            action_source=action_source,
            new_data={
                "job_type": job.job_type,
                "job_date": job.job_date.isoformat(),
                "status": job.status,
                "attempt_count": job.attempt_count,
                "queued_at": queued_at.isoformat(),
            },
        )

        logger.info(
            "Attendance daily compute job queued",
            extra={"job_id": str(job.id), "company_id": str(job.company_id)},
        )
        return job
