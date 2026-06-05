"""Service for Employee Shift History Operations."""

from datetime import date, datetime
from uuid import UUID
from typing import Dict, List, Any, Optional
from django.db.models import Q
from django.db import transaction
from apps.attendance.models import (
    EmployeeShiftRoster,
    EmployeeAttendanceConfig,
    AuditActionType,
    HRAttendanceAuditLog,
)
from apps.employees.models import Employee


class EmployeeShiftHistoryService:
    """Service for shift history operations."""

    @staticmethod
    def get_shift_history(
        employee_id: UUID,
        from_date: date,
        to_date: date,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get shift history for employee in date range."""
        rosters = EmployeeShiftRoster.objects.filter(
            employee_id=employee_id,
            roster_date__gte=from_date,
            roster_date__lte=to_date,
            deleted_at__isnull=True,
        ).select_related("shift").order_by("-roster_date")[:limit]

        shifts = [
            {
                "date": str(r.roster_date),
                "shift_code": r.shift.code,
                "shift_name": r.shift.name,
                "is_week_off": r.is_week_off,
                "is_holiday": False,
            }
            for r in rosters
        ]

        return {
            "employee_id": str(employee_id),
            "from_date": str(from_date),
            "to_date": str(to_date),
            "shifts": shifts,
            "total": len(shifts),
        }

    @staticmethod
    def get_current_shift(
        employee_id: UUID,
        as_of_date: Optional[date] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get current/today shift for employee."""
        if as_of_date is None:
            as_of_date = date.today()

        try:
            roster = EmployeeShiftRoster.objects.select_related("shift").get(
                employee_id=employee_id,
                roster_date=as_of_date,
                deleted_at__isnull=True,
            )
            return {
                "employee_id": str(employee_id),
                "date": str(roster.roster_date),
                "shift_code": roster.shift.code,
                "shift_name": roster.shift.name,
                "shift_start": roster.shift.start_time,
                "shift_end": roster.shift.end_time,
                "is_week_off": roster.is_week_off,
            }
        except EmployeeShiftRoster.DoesNotExist:
            return None

    @staticmethod
    def get_shift_config(employee_id: UUID) -> Optional[Dict[str, Any]]:
        """Get attendance configuration for employee."""
        try:
            config = EmployeeAttendanceConfig.objects.get(
                employee_id=employee_id,
                deleted_at__isnull=True,
                effective_to__isnull=True,  # Active config
            )
            return {
                "id": str(config.id),
                "employee_id": str(employee_id),
                "config_type": config.config_type,
                "effective_from": str(config.effective_from),
                "is_active": True,
                "updated_at": str(config.updated_at),
            }
        except EmployeeAttendanceConfig.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def update_shift_config(
        employee_id: UUID,
        config_type: str,
        effective_from: date,
        company_id: UUID,
        updated_by_id: UUID,
    ) -> Dict[str, Any]:
        """Update shift configuration for employee."""
        # Soft close previous config
        EmployeeAttendanceConfig.objects.filter(
            employee_id=employee_id,
            deleted_at__isnull=True,
            effective_to__isnull=True,
        ).update(effective_to=date.today())

        # Create new config
        config = EmployeeAttendanceConfig.objects.create(
            employee_id=employee_id,
            company_id=company_id,
            config_type=config_type,
            effective_from=effective_from,
            created_by_id=updated_by_id,
            updated_by_id=updated_by_id,
        )

        # Audit log
        HRAttendanceAuditLog.objects.create(
            company_id=company_id,
            entity_type="EmployeeAttendanceConfig",
            entity_id=str(config.id),
            action=AuditActionType.CREATE,
            changed_by_id=updated_by_id,
            new_data={
                "employee_id": str(employee_id),
                "config_type": config_type,
                "effective_from": str(effective_from),
            },
        )

        return {
            "id": str(config.id),
            "employee_id": str(employee_id),
            "config_type": config_type,
            "effective_from": str(effective_from),
            "created_at": str(config.created_at),
        }

    @staticmethod
    def get_bulk_history(
        employee_ids: List[UUID],
        from_date: date,
        to_date: date,
    ) -> Dict[str, Any]:
        """Get shift history for multiple employees."""
        rosters = EmployeeShiftRoster.objects.filter(
            employee_id__in=employee_ids,
            roster_date__gte=from_date,
            roster_date__lte=to_date,
            deleted_at__isnull=True,
        ).select_related("employee", "shift")

        # Group by employee
        history_by_emp = {}
        for roster in rosters:
            emp_id = str(roster.employee_id)
            if emp_id not in history_by_emp:
                history_by_emp[emp_id] = []
            history_by_emp[emp_id].append(
                {
                    "date": str(roster.roster_date),
                    "shift": roster.shift.code,
                }
            )

        return {
            "from_date": str(from_date),
            "to_date": str(to_date),
            "employees": len(history_by_emp),
            "history": history_by_emp,
        }
