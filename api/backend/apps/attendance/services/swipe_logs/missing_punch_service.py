"""
Missing Punch Service - Business logic for missing punch exceptions.
"""

import logging
import uuid
import datetime
from django.db import transaction, models
from django.utils import timezone

from apps.attendance.models import (
    AttendanceException,
    PunchLog,
    DailyAttendance,
    ExceptionType,
    AttendanceStatus,
)
from apps.attendance.models.enums import PunchType, PunchSource, ExceptionSeverity
from apps.employees.models.employee import Employee

logger = logging.getLogger(__name__)


class MissingPunchService:
    """
    Service class handling missing punch business logic.
    """

    @staticmethod
    def list_missing_punches(
        company_id: uuid.UUID,
        from_date: datetime.date = None,
        to_date: datetime.date = None,
        department_id: uuid.UUID = None,
        employee_id: uuid.UUID = None,
        is_resolved: bool = None,
    ) -> models.QuerySet:
        """
        List all missing punch exceptions for the company with filters.
        """
        queryset = AttendanceException.objects.filter(
            company_id=company_id,
            exception_type__code__in=["MISSING_IN", "MISSING_OUT"],
        ).select_related(
            "employee",
            "attendance",
            "attendance__shift",
            "exception_type",
        )

        # Filters
        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved)

        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        if department_id:
            queryset = queryset.filter(
                employee__employment_details__department_id=department_id
            )

        if from_date:
            queryset = queryset.filter(
                models.Q(attendance__attendance_date__gte=from_date) |
                models.Q(attendance__isnull=True, detected_at__date__gte=from_date)
            )

        if to_date:
            queryset = queryset.filter(
                models.Q(attendance__attendance_date__lte=to_date) |
                models.Q(attendance__isnull=True, detected_at__date__lte=to_date)
            )

        return queryset.order_by("-detected_at")

    @staticmethod
    def get_missing_punch_summary(
        company_id: uuid.UUID,
        date: datetime.date = None,
        location_id: uuid.UUID = None,
    ) -> dict:
        """
        Compute dashboard missing punch summary counts for the company.
        """
        if date is None:
            date = timezone.now().date()

        # Base exceptions for the date range
        base_qs = AttendanceException.objects.filter(
            company_id=company_id,
            exception_type__code__in=["MISSING_IN", "MISSING_OUT"],
        )

        # Filter by date
        base_qs = base_qs.filter(
            models.Q(attendance__attendance_date=date) |
            models.Q(attendance__isnull=True, detected_at__date=date)
        )

        # Filter by location
        if location_id:
            base_qs = base_qs.filter(
                models.Q(attendance__office_location_id=location_id) |
                models.Q(employee__employment_details__office_location_id=location_id)
            )

        # Calculate counts
        missing_in_count = base_qs.filter(
            is_resolved=False, exception_type__code="MISSING_IN"
        ).count()
        missing_out_count = base_qs.filter(
            is_resolved=False, exception_type__code="MISSING_OUT"
        ).count()
        total_missing = missing_in_count + missing_out_count

        critical_count = base_qs.filter(
            is_resolved=False, severity=ExceptionSeverity.CRITICAL
        ).count()

        # Resolved today (on this date)
        resolved_today = base_qs.filter(
            is_resolved=True,
            updated_at__date=timezone.now().date()
        ).count()

        return {
            "date": date.isoformat(),
            "missing_in_count": missing_in_count,
            "missing_out_count": missing_out_count,
            "total_missing": total_missing,
            "critical_count": critical_count,
            "resolved_today": resolved_today,
        }

    @staticmethod
    @transaction.atomic
    def resolve_missing_punch(
        company_id: uuid.UUID,
        exception_id: uuid.UUID,
        punch_time: datetime.datetime,
        punch_type: str,
        resolution_note: str,
        resolved_by_id: uuid.UUID = None,
    ) -> dict:
        """
        Resolve a missing punch exception by creating a manual PunchLog and marking as resolved.
        """
        # Validate exception exists and belongs to company
        try:
            exception = AttendanceException.objects.select_related(
                "employee", "attendance"
            ).get(id=exception_id, company_id=company_id)
        except AttendanceException.DoesNotExist:
            raise ValueError("Attendance exception not found.")

        if exception.is_resolved:
            raise ValueError("Exception is already resolved.")

        # Ensure resolved_by Employee exists if provided
        resolved_by = None
        if resolved_by_id:
            try:
                resolved_by = Employee.objects.get(id=resolved_by_id)
            except Employee.DoesNotExist:
                pass

        # 1. Create manual PunchLog entry
        punch_log = PunchLog.objects.create(
            company_id=company_id,
            employee=exception.employee,
            punch_time=punch_time,
            punch_type=punch_type,
            punch_source=PunchSource.MANUAL,
            source="MANUAL_RESOLUTION",
            is_trusted=True,
            created_by=resolved_by,
            meta_data={
                "resolved_exception_id": str(exception_id),
                "resolution_note": resolution_note,
                "resolved_by": str(resolved_by_id) if resolved_by_id else None,
            },
        )

        # 2. Mark exception resolved
        exception.is_resolved = True
        exception.resolved_by = resolved_by
        exception.resolution_note = resolution_note
        exception.save()

        # 3. Align DailyAttendance if linked
        if exception.attendance:
            attendance = exception.attendance
            if punch_type == PunchType.IN:
                attendance.first_in = punch_time
            elif punch_type == PunchType.OUT:
                attendance.last_out = punch_time
            attendance.save()

        return {
            "exception_id": str(exception_id),
            "is_resolved": True,
            "resolved_at": timezone.now().isoformat(),
            "created_punch_id": punch_log.id,
        }

    @staticmethod
    @transaction.atomic
    def bulk_resolve(
        company_id: uuid.UUID,
        exception_ids: list,
        resolution_action: str,
        resolution_note: str,
        resolved_by_id: uuid.UUID = None,
    ) -> dict:
        """
        Bulk resolve exceptions via ADD_PUNCH, MARK_LEAVE, or MARK_ABSENT.
        """
        unresolved_exceptions = AttendanceException.objects.filter(
            id__in=exception_ids,
            company_id=company_id,
            is_resolved=False,
        ).select_related("employee", "attendance", "attendance__shift", "exception_type")

        resolved_by = None
        if resolved_by_id:
            try:
                resolved_by = Employee.objects.get(id=resolved_by_id)
            except Employee.DoesNotExist:
                pass

        resolved_count = 0
        failed_ids = []

        # Find status models to update DailyAttendance
        leave_status = None
        absent_status = None
        if resolution_action in ["MARK_LEAVE", "MARK_ABSENT"]:
            try:
                if resolution_action == "MARK_LEAVE":
                    leave_status = AttendanceStatus.objects.filter(
                        company_id=company_id,
                        name__icontains="Leave"
                    ).first()
                else:
                    absent_status = AttendanceStatus.objects.filter(
                        company_id=company_id,
                        name__icontains="Absent"
                    ).first()
            except Exception as e:
                logger.warning(f"Could not retrieve status models: {str(e)}")

        for exception in unresolved_exceptions:
            try:
                if resolution_action == "ADD_PUNCH":
                    # Determine automatically aligned punch time
                    if exception.attendance and exception.attendance.shift:
                        shift = exception.attendance.shift
                        att_date = exception.attendance.attendance_date
                        
                        if exception.exception_type.code == "MISSING_IN":
                            dt = datetime.datetime.combine(att_date, shift.start_time)
                            punch_time = timezone.make_aware(dt)
                            punch_type = PunchType.IN
                        else:
                            dt = datetime.datetime.combine(att_date, shift.end_time)
                            if shift.cross_midnight:
                                dt += datetime.timedelta(days=1)
                            punch_time = timezone.make_aware(dt)
                            punch_type = PunchType.OUT
                    else:
                        punch_time = exception.detected_at
                        punch_type = (
                            PunchType.IN
                            if exception.exception_type.code == "MISSING_IN"
                            else PunchType.OUT
                        )

                    # Create manual swipe
                    punch_log = PunchLog.objects.create(
                        company_id=company_id,
                        employee=exception.employee,
                        punch_time=punch_time,
                        punch_type=punch_type,
                        punch_source=PunchSource.MANUAL,
                        source="BULK_MANUAL_RESOLUTION",
                        is_trusted=True,
                        created_by=resolved_by,
                        meta_data={
                            "resolved_exception_id": str(exception.id),
                            "resolution_note": resolution_note,
                            "bulk_resolved": True,
                        },
                    )

                    # Align DailyAttendance
                    if exception.attendance:
                        attendance = exception.attendance
                        if punch_type == PunchType.IN:
                            attendance.first_in = punch_time
                        elif punch_type == PunchType.OUT:
                            attendance.last_out = punch_time
                        attendance.save()

                elif resolution_action == "MARK_LEAVE" and exception.attendance:
                    if leave_status:
                        exception.attendance.status = leave_status
                        exception.attendance.save()

                elif resolution_action == "MARK_ABSENT" and exception.attendance:
                    if absent_status:
                        exception.attendance.status = absent_status
                        exception.attendance.save()

                # Mark exception as resolved
                exception.is_resolved = True
                exception.resolved_by = resolved_by
                exception.resolution_note = resolution_note
                exception.save()

                resolved_count += 1

            except Exception as e:
                logger.error(f"Bulk resolve failed for exception {exception.id}: {str(e)}")
                failed_ids.append(str(exception.id))

        # Check for requested IDs not found/processed
        found_ids = {str(exc.id) for exc in unresolved_exceptions}
        for req_id in exception_ids:
            if str(req_id) not in found_ids:
                failed_ids.append(str(req_id))

        return {
            "resolved_count": resolved_count,
            "failed_ids": failed_ids,
            "message": f"Successfully resolved {resolved_count} exceptions.",
        }

    @staticmethod
    def get_payroll_report(
        company_id: uuid.UUID,
        cycle_start_date: datetime.date,
        cycle_end_date: datetime.date,
        department_id: uuid.UUID = None,
    ) -> list:
        """
        Generate missing punch exception summary report for payroll period.
        """
        # Query exceptions inside cycle range
        exceptions = AttendanceException.objects.filter(
            company_id=company_id,
            exception_type__code__in=["MISSING_IN", "MISSING_OUT"],
        ).filter(
            models.Q(attendance__attendance_date__gte=cycle_start_date, attendance__attendance_date__lte=cycle_end_date) |
            models.Q(attendance__isnull=True, detected_at__date__gte=cycle_start_date, detected_at__date__lte=cycle_end_date)
        )

        if department_id:
            exceptions = exceptions.filter(
                employee__employment_details__department_id=department_id
            )

        exceptions = exceptions.select_related("employee")

        # Group and compute metrics
        employee_data = {}
        for exception in exceptions:
            emp = exception.employee
            if emp.id not in employee_data:
                employee_data[emp.id] = {
                    "employee_id": str(emp.id),
                    "employee_name": emp.full_name,
                    "missing_in_count": 0,
                    "missing_out_count": 0,
                    "unresolved_count": 0,
                    "resolved_count": 0,
                }

            data = employee_data[emp.id]
            is_unresolved = not exception.is_resolved
            code = exception.exception_type.code

            if is_unresolved:
                data["unresolved_count"] += 1
                if code == "MISSING_IN":
                    data["missing_in_count"] += 1
                elif code == "MISSING_OUT":
                    data["missing_out_count"] += 1
            else:
                data["resolved_count"] += 1

        return list(employee_data.values())
