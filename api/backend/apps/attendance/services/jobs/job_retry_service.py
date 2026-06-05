"""Service for retrying failed attendance jobs."""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

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


class JobRetryService:
    """Retry orchestration for FAILED attendance jobs."""

    @staticmethod
    @transaction.atomic
    def retry_failed_job(*, company_id, job_id, payload: dict, request_user) -> AttendanceJob:
        job = AttendanceJob.objects.select_for_update().filter(
            id=job_id,
            company_id=company_id,
            deleted_at__isnull=True,
            is_active=True,
        ).first()
        if job is None:
            raise NotFound("Attendance job not found.")
        if job.status != AttendanceJobStatus.FAILED:
            raise ValidationError({"status": "Only FAILED jobs can be retried."})
        if job.job_type != AttendanceJobType.DAILY_COMPUTE:
            raise ValidationError({"job_type": "Retry is currently supported only for DAILY_COMPUTE jobs."})

        actor_employee = get_request_employee(request_user)
        role_codes = validate_trigger_role(actor_employee=actor_employee, request_user=request_user)
        triggered_by = (
            get_employee_or_error(company_id=company_id, employee_id=payload["triggered_by"])
            if payload.get("triggered_by")
            else actor_employee
        )
        action_source = get_action_source_for_employee(actor_employee, role_codes=role_codes)

        old_data = {
            "status": job.status,
            "attempt_count": job.attempt_count,
            "error_log": job.error_log,
        }
        retry_event = {
            "retried_at": timezone.now().isoformat(),
            "retried_by": (
                {
                    "id": str(triggered_by.id),
                    "name": triggered_by.full_name,
                    "employee_code": triggered_by.employee_code,
                }
                if triggered_by
                else {"role": "SYSTEM"}
            ),
            "retry_reason": payload.get("retry_reason") or "",
            "previous_status": job.status,
        }
        retry_history = list((job.meta_data or {}).get("retry_history", []))
        retry_history.append(retry_event)

        job.attempt_count += 1
        job.status = AttendanceJobStatus.QUEUED
        job.started_at = None
        job.completed_at = None
        job.error_log = None
        job.updated_by = actor_employee or triggered_by
        job.meta_data = {
            **(job.meta_data or {}),
            "retry_history": retry_history,
            "last_retry": retry_event,
            "action_source": action_source,
        }

        task_id = DailyComputeService.trigger_daily_compute(job.id)
        job.meta_data["celery_task_id"] = task_id
        job.save(
            update_fields=[
                "attempt_count",
                "status",
                "started_at",
                "completed_at",
                "error_log",
                "updated_by",
                "meta_data",
                "updated_at",
            ]
        )

        append_job_audit_log(
            company_id=job.company_id,
            job_id=job.id,
            action="UPDATE",
            changed_by_id=getattr(actor_employee, "id", None) or getattr(triggered_by, "id", None),
            action_source=action_source,
            old_data=old_data,
            new_data={
                "status": job.status,
                "attempt_count": job.attempt_count,
                "last_retry": retry_event,
            },
        )

        logger.info(
            "Attendance job retried",
            extra={"job_id": str(job.id), "company_id": str(job.company_id)},
        )
        return job
