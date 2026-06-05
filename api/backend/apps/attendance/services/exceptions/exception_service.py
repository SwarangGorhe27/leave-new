"""Service layer for attendance exception and anomaly APIs."""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.attendance.models import HRAttendanceAuditLog
from apps.attendance.models.enums import AuditActionSource, AuditActionType, ExceptionSeverity
from apps.attendance.selectors.exceptions.exception_selectors import (
    get_active_exception_types,
    get_exception_detail,
    get_exception_list_queryset,
    get_linked_punch_ids,
    get_summary_breakdown,
    get_summary_queryset,
)
from apps.attendance.validators.exception_validators import validate_exception_is_resolvable
from apps.employees.models.employee import Employee

logger = logging.getLogger(__name__)


class AttendanceExceptionService:
    """Business logic for attendance exceptions."""

    @staticmethod
    def list_exceptions(company_id, filters: dict) -> dict:
        queryset = get_exception_list_queryset(company_id, filters)
        return {
            "data": list(queryset),
            "total": queryset.count(),
            "unresolved_count": queryset.filter(is_resolved=False).count(),
        }

    @staticmethod
    def get_exception_detail(company_id, exception_id) -> dict:
        exception_obj = get_exception_detail(company_id, exception_id)
        if exception_obj is None:
            raise ValidationError({"id": "Attendance exception not found."})

        return {
            "id": exception_obj.id,
            "employee_id": exception_obj.employee_id,
            "employee_name": exception_obj.employee.full_name if exception_obj.employee else "",
            "attendance_id": exception_obj.attendance_id,
            "attendance_date": (
                exception_obj.attendance.attendance_date if exception_obj.attendance else None
            ),
            "exception_type_id": exception_obj.exception_type_id,
            "exception_type_code": exception_obj.exception_type.code,
            "exception_type_label": exception_obj.exception_type.label,
            "severity": exception_obj.severity,
            "detected_at": exception_obj.detected_at,
            "is_resolved": exception_obj.is_resolved,
            "resolved_by": exception_obj.resolved_by_id,
            "resolver_name": (
                exception_obj.resolved_by.full_name if exception_obj.resolved_by else None
            ),
            "resolved_at": exception_obj.resolved_at,
            "resolution_note": exception_obj.resolution_note,
            "linked_punch_ids": get_linked_punch_ids(exception_obj),
        }

    @staticmethod
    def list_exception_types(company_id, *, is_active=True) -> dict:
        queryset = get_active_exception_types(is_active=is_active)
        return {"data": list(queryset)}

    @staticmethod
    def get_summary(company_id, filters: dict) -> dict:
        queryset = get_summary_queryset(company_id, filters)
        by_type = [
            {
                "code": item["exception_type__code"],
                "label": item["exception_type__label"],
                "count": item["count"],
                "unresolved": item["unresolved"],
            }
            for item in get_summary_breakdown(company_id, filters)
        ]
        return {
            "by_type": by_type,
            "total": queryset.count(),
            "critical_unresolved": queryset.filter(
                is_resolved=False,
                severity=ExceptionSeverity.CRITICAL,
            ).count(),
        }

    @staticmethod
    def _get_resolver(company_id, resolved_by_id=None, actor_employee_id=None):
        target_id = resolved_by_id or actor_employee_id
        if not target_id:
            return None

        resolver = Employee.objects.filter(id=target_id, company_id=company_id).first()
        if resolver is None:
            raise ValidationError({"resolved_by": "Resolver employee not found for this company."})
        return resolver

    @staticmethod
    def _create_audit_log(*, exception_obj, old_data, changed_by_id):
        try:
            HRAttendanceAuditLog.objects.create(
                company_id=exception_obj.company_id,
                table_name="att_exception",
                record_id=str(exception_obj.id),
                action=AuditActionType.UPDATE,
                old_data=old_data,
                new_data={
                    "is_resolved": exception_obj.is_resolved,
                    "resolved_by": str(exception_obj.resolved_by_id) if exception_obj.resolved_by_id else None,
                    "resolved_at": (
                        exception_obj.resolved_at.isoformat()
                        if exception_obj.resolved_at
                        else None
                    ),
                    "resolution_note": exception_obj.resolution_note,
                },
                changed_by_id=changed_by_id,
                action_source=AuditActionSource.HR_ADMIN,
            )
        except Exception:
            logger.warning(
                "Failed to create audit log for attendance exception %s",
                exception_obj.id,
                exc_info=True,
            )

    @staticmethod
    @transaction.atomic
    def resolve_exception(
        company_id,
        exception_id,
        *,
        resolution_note: str,
        resolved_by_id=None,
        actor_employee_id=None,
    ) -> dict:
        exception_obj = get_exception_detail(company_id, exception_id, for_update=True)
        validate_exception_is_resolvable(exception_obj)

        resolver = AttendanceExceptionService._get_resolver(
            company_id,
            resolved_by_id=resolved_by_id,
            actor_employee_id=actor_employee_id,
        )

        resolved_at = timezone.now()
        old_data = {
            "is_resolved": exception_obj.is_resolved,
            "resolved_by": str(exception_obj.resolved_by_id) if exception_obj.resolved_by_id else None,
            "resolved_at": (
                exception_obj.resolved_at.isoformat() if exception_obj.resolved_at else None
            ),
            "resolution_note": exception_obj.resolution_note,
        }

        exception_obj.is_resolved = True
        exception_obj.resolution_note = resolution_note
        exception_obj.resolved_by = resolver
        exception_obj.resolved_at = resolved_at
        exception_obj.meta_data = exception_obj.meta_data or {}
        exception_obj.meta_data.update({"resolved_at": resolved_at.isoformat()})
        exception_obj.save(
            update_fields=[
                "is_resolved",
                "resolution_note",
                "resolved_by",
                "resolved_at",
                "meta_data",
                "updated_at",
            ]
        )

        AttendanceExceptionService._create_audit_log(
            exception_obj=exception_obj,
            old_data=old_data,
            changed_by_id=resolver.id if resolver else actor_employee_id,
        )

        logger.info(
            "Attendance exception %s resolved for company %s",
            exception_obj.id,
            company_id,
        )

        return {
            "id": exception_obj.id,
            "is_resolved": exception_obj.is_resolved,
            "resolved_by": exception_obj.resolved_by_id,
            "resolved_at": exception_obj.resolved_at,
        }

    @staticmethod
    @transaction.atomic
    def bulk_resolve(
        company_id,
        exception_ids,
        *,
        resolution_note: str,
        resolved_by_id=None,
        actor_employee_id=None,
    ) -> dict:
        resolver = AttendanceExceptionService._get_resolver(
            company_id,
            resolved_by_id=resolved_by_id,
            actor_employee_id=actor_employee_id,
        )

        resolved_count = 0
        failed_ids = []

        for exception_id in exception_ids:
            try:
                with transaction.atomic():
                    exception_obj = get_exception_detail(
                        company_id,
                        exception_id,
                        for_update=True,
                    )
                    validate_exception_is_resolvable(exception_obj)

                    old_data = {
                        "is_resolved": exception_obj.is_resolved,
                        "resolved_by": (
                            str(exception_obj.resolved_by_id)
                            if exception_obj.resolved_by_id
                            else None
                        ),
                        "resolved_at": (
                            exception_obj.resolved_at.isoformat()
                            if exception_obj.resolved_at
                            else None
                        ),
                        "resolution_note": exception_obj.resolution_note,
                    }

                    resolved_at = timezone.now()
                    exception_obj.is_resolved = True
                    exception_obj.resolution_note = resolution_note
                    exception_obj.resolved_by = resolver
                    exception_obj.resolved_at = resolved_at
                    exception_obj.meta_data = exception_obj.meta_data or {}
                    exception_obj.meta_data.update({"resolved_at": resolved_at.isoformat()})
                    exception_obj.save(
                        update_fields=[
                            "is_resolved",
                            "resolution_note",
                            "resolved_by",
                            "resolved_at",
                            "meta_data",
                            "updated_at",
                        ]
                    )

                    AttendanceExceptionService._create_audit_log(
                        exception_obj=exception_obj,
                        old_data=old_data,
                        changed_by_id=resolver.id if resolver else actor_employee_id,
                    )
                    resolved_count += 1
            except ValidationError:
                failed_ids.append(str(exception_id))
            except Exception:
                logger.exception(
                    "Bulk resolution failed for attendance exception %s",
                    exception_id,
                )
                failed_ids.append(str(exception_id))

        logger.info(
            "Bulk resolved attendance exceptions for company %s: resolved=%s failed=%s",
            company_id,
            resolved_count,
            len(failed_ids),
        )

        return {
            "resolved_count": resolved_count,
            "failed_ids": failed_ids,
            "message": f"Resolved {resolved_count} attendance exception(s).",
        }
