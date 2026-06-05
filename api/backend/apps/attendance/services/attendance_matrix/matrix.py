"""
attendance/services/matrix.py

Business logic layer for the Attendance Matrix sub-module.

All DB queries live here. Views are thin — they call service methods,
pass results to serializers, return responses. No ORM queries in views
or serializers.

Service methods
---------------
AttendanceMatrixService
    .get_summary(company_id, year, month, branch_id)
    .get_live_counts(company_id, branch_id)
    .get_grid(company_id, year, month, filters, page, page_size)
    .get_employee_day(company_id, employee_id, date)
    .get_employee_summary(company_id, employee_id, year, month)
    .get_departments(company_id)
    .get_cycle_bounds(company_id, year, month)
"""

from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from django.db.models import Count, Q

from apps.attendance.models import (
    AttendanceCompanyConfig,
    AttendanceCycle,
    AttendanceHolidayDay,
    AttendanceJob,
    AttendanceStatus,
    DailyAttendance,
    MonthlyAttendanceSummary,
    PunchLog,
    RegularizationRequest,
    ShiftDefinition,
)
from apps.attendance.models.enums import (
    AttendanceJobStatus,
    AttendanceJobType,
    FinalizationStatus,
)
from apps.attendance.utils.date_utils import (
    build_date_headers,
    get_cycle_bounds,
    get_month_display_label,
    resolve_cell_code,
)

from apps.attendance.tasks.matrix_import import (
    process_matrix_import,
)


def _policy_full_day_mins(policy) -> int:
    """Support legacy (full_day_minutes) and v7 (full_day_min_mins) policy columns."""
    if policy is None:
        return 480
    return (
        getattr(policy, "full_day_min_mins", None)
        or getattr(policy, "full_day_minutes", None)
        or 480
    )


class AttendanceMatrixService:
    """
    Stateless service — instantiate per request or call class methods directly.
    All methods are instance methods for easy mocking in tests.
    """

    # -------------------------------------------------------------------------
    # 1. Summary Cards
    # -------------------------------------------------------------------------

    def get_summary(
        self,
        company_id: str,
        year: int,
        month: int,
        branch_id: Optional[str] = None,
    ) -> dict:
        """
        Aggregate data for the six summary cards on the Attendance Matrix page.

        Sources
        -------
        - MonthlyAttendanceSummary  →  avg_hours, punctuality
        - DailyAttendance           →  today's present/absent, deltas
        - AttendanceHolidayDay      →  holiday count, next holiday
        - AttendanceCompanyConfig   →  policy goal (full_day_min_mins)

        Strategy
        --------
        - Monthly aggregates come from emp_monthly_attendance_summary (already
          computed by the rollup job — never recompute from daily rows here).
        - "Today" counts are live reads from emp_daily_attendance.
        - Deltas = today count minus yesterday count (two small COUNT queries).
        """
        today = date.today()
        yesterday = today - timedelta(days=1)

        # ── Company config for week_start_day and policy goal ─────────────────
        config = (
            AttendanceCompanyConfig.objects
            .select_related("default_policy")
            .filter(company_id=company_id)
            .first()
        )
        policy_goal_hours = 8.0  # sensible default
        if config and config.default_policy:
            policy_goal_hours = round(_policy_full_day_mins(config.default_policy) / 60, 1)

        # ── Today's attendance counts ─────────────────────────────────────────
        today_qs = DailyAttendance.objects.filter(
            company_id=company_id,
            attendance_date=today,
            is_active=True,
        )
        if branch_id:
            today_qs = today_qs.filter(
                employee__employment_details__office_location_id=branch_id
            )

        today_status_counts = dict(
            today_qs.values_list("status__code")
                     .annotate(cnt=Count("id"))
        )
        present_today = today_status_counts.get("P", 0) + today_status_counts.get("PRESENT", 0)
        absent_today = today_status_counts.get("A", 0) + today_status_counts.get("ABSENT", 0)
        leave_today = today_status_counts.get("L", 0) + today_status_counts.get("LEAVE", 0)

        # ── Yesterday's counts for deltas ─────────────────────────────────────
        yesterday_qs = DailyAttendance.objects.filter(
            company_id=company_id,
            attendance_date=yesterday,
            is_active=True,
        )
        if branch_id:
            yesterday_qs = yesterday_qs.filter(
                employee__employment_details__office_location_id=branch_id
            )

        yesterday_status_counts = dict(
            yesterday_qs.values_list("status__code")
                         .annotate(cnt=Count("id"))
        )
        present_yesterday = yesterday_status_counts.get("P", 0) + yesterday_status_counts.get("PRESENT", 0)
        absent_yesterday = yesterday_status_counts.get("A", 0) + yesterday_status_counts.get("ABSENT", 0)

        # ── Monthly summary aggregates (avg hours, punctuality) ───────────────
        cycle_start, cycle_end = get_cycle_bounds(company_id, year, month)
        summaries = MonthlyAttendanceSummary.objects.filter(
            company_id=company_id,
            cycle_start_date=cycle_start,
            cycle_end_date=cycle_end,
            is_active=True,
        )
        if branch_id:
            summaries = summaries.filter(
                employee__employment_details__office_location_id=branch_id
            )

        total_work_mins = 0
        total_present_days = 0
        total_late_days = 0
        employee_count = 0

        for s in summaries:
            total_work_mins   += s.total_work_mins
            total_present_days += float(s.present_days)
            total_late_days   += s.late_days
            employee_count    += 1

        # avg hours = total_work_mins across all employees / total present_days / 60
        avg_hours = 0.0
        if total_present_days > 0:
            avg_hours = round(total_work_mins / total_present_days / 60, 1)

        # punctuality = % of present days that were NOT late
        punctuality = 0.0
        if total_present_days > 0:
            on_time_days = total_present_days - total_late_days
            punctuality = round((on_time_days / total_present_days) * 100, 1)

        # ── Previous month punctuality for delta ──────────────────────────────
        prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
        prev_cycle_start, prev_cycle_end = get_cycle_bounds(
            company_id, prev_year, prev_month
        )
        prev_summaries = MonthlyAttendanceSummary.objects.filter(
            company_id=company_id,
            cycle_start_date=prev_cycle_start,
            cycle_end_date=prev_cycle_end,
            is_active=True,
        )
        if branch_id:
            prev_summaries = prev_summaries.filter(
                employee__employment_details__office_location_id=branch_id
            )

        prev_present = 0
        prev_late = 0
        for s in prev_summaries:
            prev_present += float(s.present_days)
            prev_late    += s.late_days

        prev_punctuality = 0.0
        if prev_present > 0:
            prev_punctuality = round(
                ((prev_present - prev_late) / prev_present) * 100, 1
            )
        punctuality_change = round(punctuality - prev_punctuality, 1)

        # ── Holidays ─────────────────────────────────────────────────────────
        holidays_qs = AttendanceHolidayDay.objects.filter(
            company_id=company_id,
            holiday_date__year=year,
            holiday_date__month=month,
            is_active=True,
        )
        if branch_id:
            holidays_qs = holidays_qs.filter(branch_id=branch_id)

        holiday_list = list(
            holidays_qs.order_by("holiday_date")
                       .values("holiday_date", "name")
        )

        # Holidays remaining in month (from today onward)
        remaining_holidays = [
            h for h in holiday_list if h["holiday_date"] >= today
        ]
        next_holiday = remaining_holidays[0] if remaining_holidays else None

        # ── Pending leave count ───────────────────────────────────────────────
        # leave.LeaveRequest referenced by DailyAttendance.leave_request
        # Count LEAVE status rows for this month where finalization != LOCKED
        leave_pending = DailyAttendance.objects.filter(
            company_id=company_id,
            attendance_date__range=(cycle_start, cycle_end),
            status__code="LEAVE",
            finalization_status=FinalizationStatus.DRAFT,
            is_active=True,
        ).count()

        return {
            "total_present": present_today,
            "present_change_today": present_today - present_yesterday,
            "total_absent": absent_today,
            "absent_change_today": absent_today - absent_yesterday,
            "on_leave": leave_today,
            "leave_pending_count": leave_pending,
            "holidays_remaining": len(remaining_holidays),
            "next_holiday_date": (
                next_holiday["holiday_date"].isoformat() if next_holiday else None
            ),
            "next_holiday_name": (
                next_holiday["name"] if next_holiday else None
            ),
            "avg_hours": avg_hours,
            "avg_hours_goal": policy_goal_hours,
            "punctuality_percent": punctuality,
            "punctuality_change": punctuality_change,
        }

    # -------------------------------------------------------------------------
    # 2. Live Monitor
    # -------------------------------------------------------------------------

    def get_live_counts(
        self,
        company_id: str,
        branch_id: Optional[str] = None,
    ) -> dict:
        """
        Lightweight live count of today's attendance.
        Designed for short-interval polling — reads DailyAttendance only,
        no joins to MonthlyAttendanceSummary.
        """
        from django.utils import timezone
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        def count_by_status(target_date: date) -> dict:
            qs = DailyAttendance.objects.filter(
                company_id=company_id,
                attendance_date=target_date,
                is_active=True,
            )
            if branch_id:
                qs = qs.filter(
                    employee__employment_details__office_location_id=branch_id
                )
            return dict(
                qs.values_list("status__code").annotate(cnt=Count("id"))
            )

        today_counts     = count_by_status(today)
        yesterday_counts = count_by_status(yesterday)

        present_today     = today_counts.get("PRESENT", 0)
        absent_today      = today_counts.get("ABSENT", 0)
        leave_today       = today_counts.get("LEAVE", 0)
        present_yesterday = yesterday_counts.get("PRESENT", 0)
        absent_yesterday  = yesterday_counts.get("ABSENT", 0)

        return {
            "as_of": timezone.now().isoformat(),
            "present_count": present_today,
            "absent_count": absent_today,
            "on_leave_count": leave_today,
            "present_delta": present_today - present_yesterday,
            "absent_delta": absent_today - absent_yesterday,
        }

    # -------------------------------------------------------------------------
    # 3. Grid
    # -------------------------------------------------------------------------

    def get_grid(
        self,
        company_id: str,
        year: int,
        month: int,
        department_id: Optional[str] = None,
        branch_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> dict:
        """
        Build the full attendance matrix grid.

        Query strategy
        --------------
        - ONE queryset for all DailyAttendance rows in the cycle date range,
          select_related to avoid N+1 on status / shift / leave_request.
        - Group rows by employee_id in Python — never query per employee.
        - ONE queryset for MonthlyAttendanceSummary for P/A/L columns.
        - Employees list drives pagination; attendance rows are pulled for the
          paginated employee set only.

        Returns
        -------
        Dict with keys: meta (cycle info + date headers), rows (paginated).
        """
        from apps.employees.models import Employee, Department

        cycle_start, cycle_end = get_cycle_bounds(company_id, year, month)

        # ── Company config for week_start_day ─────────────────────────────────
        config = (
            AttendanceCompanyConfig.objects
            .filter(company_id=company_id)
            .values("week_start_day")
            .first()
        )
        week_start_day = config["week_start_day"] if config else 1

        # ── Holiday dates for this cycle ──────────────────────────────────────
        holiday_qs = AttendanceHolidayDay.objects.filter(
            company_id=company_id,
            holiday_date__range=(cycle_start, cycle_end),
            is_active=True,
        )
        if branch_id:
            holiday_qs = holiday_qs.filter(
                Q(branch_id=branch_id) | Q(branch_id__isnull=True)
            )
        holiday_dates = set(
            holiday_qs.values_list("holiday_date", flat=True)
        )

        # ── Date headers ──────────────────────────────────────────────────────
        date_headers = build_date_headers(
            cycle_start, cycle_end, week_start_day, holiday_dates
        )

        # ── Employee queryset (pagination source) ─────────────────────────────
        from apps.attendance.utils.employee_relations import with_employee_org

        emp_qs = with_employee_org(
            Employee.objects.filter(
                company_id=company_id,
                is_active=True,
            )
        )

        if branch_id:
            emp_qs = emp_qs.filter(
                employment_details__office_location_id=branch_id
            )
        if department_id:
            emp_qs = emp_qs.filter(employment_details__department_id=department_id)
        if search:
            emp_qs = emp_qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(employee_code__icontains=search)
                | Q(employment_details__department__name__icontains=search)
            )

        total_records = emp_qs.count()
        offset = (page - 1) * page_size
        employees = list(emp_qs.order_by("employee_code")[offset: offset + page_size])
        employee_ids = [e.id for e in employees]

        # ── DailyAttendance rows for paginated employees ───────────────────────
        daily_rows = (
            DailyAttendance.objects
            .filter(
                company_id=company_id,
                employee_id__in=employee_ids,
                attendance_date__range=(cycle_start, cycle_end),
                is_active=True,
            )
            .select_related(
                "status",
                "shift",
                "leave_request",
                "leave_request__leave_type",  # for leave_type_code
            )
            .order_by("employee_id", "attendance_date")
        )

        # Group daily rows by employee_id → date string → row
        daily_by_emp: dict[str, dict[str, DailyAttendance]] = defaultdict(dict)
        for row in daily_rows:
            daily_by_emp[str(row.employee_id)][row.attendance_date.isoformat()] = row

        # ── Monthly summaries for P/A/L columns ───────────────────────────────
        summaries = MonthlyAttendanceSummary.objects.filter(
            company_id=company_id,
            employee_id__in=employee_ids,
            cycle_start_date=cycle_start,
            cycle_end_date=cycle_end,
            is_active=True,
        )
        summary_by_emp: dict[str, MonthlyAttendanceSummary] = {
            str(s.employee_id): s for s in summaries
        }

        # ── Build rows ────────────────────────────────────────────────────────
        rows = []
        for emp in employees:
            emp_id_str = str(emp.id)
            emp_daily = daily_by_emp.get(emp_id_str, {})
            summary   = summary_by_emp.get(emp_id_str)

            # Build days array — one entry per date header
            days = []
            for header in date_headers:
                d_str = header["date"]
                daily = emp_daily.get(d_str)

                if daily is None:
                    # No record yet (future dates or missing compute)
                    days.append({
                        "date": d_str,
                        "cell_code": None,
                        "status_code": None,
                        "work_mode": None,
                        "leave_type": None,
                        "is_late": False,
                        "actual_work_mins": 0,
                        "is_locked": False,
                    })
                    continue

                # Resolve leave_type_code
                leave_type_code = None
                if (
                    daily.leave_request_id
                    and hasattr(daily.leave_request, "leave_type")
                    and daily.leave_request.leave_type
                ):
                    leave_type_code = daily.leave_request.leave_type.code

                status_code = daily.status.code if daily.status else ""
                cell_code = resolve_cell_code(
                    status_code, daily.work_mode or "OFFICE", leave_type_code
                )

                days.append({
                    "date": d_str,
                    "cell_code": cell_code,
                    "status_code": status_code,
                    "work_mode": daily.work_mode,
                    "leave_type": leave_type_code,
                    "is_late": daily.is_late,
                    "actual_work_mins": daily.actual_work_mins,
                    "is_locked": daily.is_locked,
                })

            # Build summary columns
            summary_data = {
                "present": float(summary.present_days) if summary else 0,
                "absent": float(summary.absent_days) if summary else 0,
                "leave": float(summary.leave_days) if summary else 0,
            }

            # Avatar initials: first letter of first + last name
            first = (emp.first_name or "").strip()
            last  = (emp.last_name or "").strip()
            initials = (
                (first[0] if first else "") + (last[0] if last else "")
            ).upper()

            emp_designation = None
            emp_department = None
            employment = getattr(emp, "employment_details", None)
            if employment is not None:
                if getattr(employment, "designation", None):
                    emp_designation = employment.designation.title
                if getattr(employment, "department", None):
                    emp_department = employment.department.name

            rows.append({
                "employee_id": emp_id_str,
                "employee_code": emp.employee_code,
                "full_name": f"{first} {last}".strip(),
                "department": emp_department,
                "designation": emp_designation,
                "avatar_initials": initials,
                "days": days,
                "summary": summary_data,
            })

        return {
            "meta": {
                "total_records": total_records,
                "page": page,
                "page_size": page_size,
                "cycle_start": cycle_start.isoformat(),
                "cycle_end": cycle_end.isoformat(),
                "display_label": self._month_label(year, month),
                "dates": date_headers,
            },
            "rows": rows,
        }

    # -------------------------------------------------------------------------
    # 4. Employee Day Detail
    # -------------------------------------------------------------------------

    def get_employee_day(
        self,
        company_id: str,
        employee_id: str,
        target_date: date,
    ) -> dict:
        """
        Full detail for a single employee on a single date.

        Pulls:
        - DailyAttendance with shift, status, leave_request → leave_type
        - All PunchLog rows for that date
        - Latest RegularizationRequest for that date (if any)
        """
        # Daily record
        daily = (
            DailyAttendance.objects
            .select_related(
                "status",
                "shift",
                "leave_request",
                "leave_request__leave_type",
            )
            .filter(
                company_id=company_id,
                employee_id=employee_id,
                attendance_date=target_date,
                is_active=True,
            )
            .first()
        )

        if not daily:
            return None

        # Resolve leave info
        leave_data = None
        if daily.leave_request_id and daily.leave_request:
            lr = daily.leave_request
            leave_data = {
                "leave_type_code": lr.leave_type.code if lr.leave_type else None,
                "leave_type_name": lr.leave_type.name if lr.leave_type else None,
                "status": getattr(lr, "status", None),
            }

        # Resolve cell_code
        leave_type_code = leave_data["leave_type_code"] if leave_data else None
        status_code = daily.status.code if daily.status else ""
        cell_code = resolve_cell_code(
            status_code, daily.work_mode or "OFFICE", leave_type_code
        )

        # Punches for the day
        # Date range: midnight to midnight (company timezone ideally)
        # For simplicity, filter on date portion of punch_time
        from django.db.models.functions import TruncDate
        punches_qs = (
            PunchLog.objects
            .filter(
                company_id=company_id,
                employee_id=employee_id,
            )
            .annotate(punch_date=TruncDate("punch_time"))
            .filter(punch_date=target_date)
            .order_by("punch_time")
        )

        # Resolve device names: PunchLog.device_id is an IntegerField (ESSL id)
        # Fetch mst_device for any non-null device_ids
        device_id_set = {p.device_id for p in punches_qs if p.device_id}
        device_name_map: dict[int, str] = {}
        if device_id_set:
            from apps.attendance.models.masters.office_location import (
                AttendanceOfficeLocation,
            )
            # mst_device is not yet imported — import inline to avoid circular
            try:
                from apps.attendance.models.masters.device import Device
                device_name_map = dict(
                    Device.objects.filter(
                        company_id=company_id,
                        device_code__in=[str(d) for d in device_id_set],
                    ).values_list("device_code", "device_name")
                )
            except ImportError:
                pass  # Device model not yet present; graceful degradation

        punches = []
        for p in punches_qs:
            punches.append({
                "punch_time": p.punch_time.isoformat(),
                "punch_type": p.punch_type,
                "punch_source": p.punch_source,
                "device_name": device_name_map.get(p.device_id, "Unknown"),
                "face_verified": p.face_verified,
            })

        # Latest regularization request for this date
        reg = (
            RegularizationRequest.objects
            .filter(
                company_id=company_id,
                employee_id=employee_id,
                regularization_date=target_date,
                is_active=True,
            )
            .order_by("-created_at")
            .first()
        )
        regularization_data = None
        if reg:
            regularization_data = {
                "id": str(reg.id),
                "status": reg.status,
                "reg_type": reg.reg_type,
            }

        return {
            "employee_id": str(employee_id),
            "date": target_date.isoformat(),
            "status_code": status_code,
            "cell_code": cell_code,
            "work_mode": daily.work_mode,
            "shift_name": daily.shift.name if daily.shift else None,
            "shift_start": (
                daily.shift.start_time.strftime("%H:%M") if daily.shift else None
            ),
            "shift_end": (
                daily.shift.end_time.strftime("%H:%M") if daily.shift else None
            ),
            "first_in": daily.first_in.isoformat() if daily.first_in else None,
            "last_out": daily.last_out.isoformat() if daily.last_out else None,
            "actual_work_mins": daily.actual_work_mins,
            "late_in_mins": daily.late_in_mins,
            "early_exit_mins": daily.early_exit_mins,
            "ot_mins": daily.ot_mins,
            "lop_days": float(daily.lop_days),
            "is_late": daily.is_late,
            "is_grace": daily.is_grace,
            "grace_category": daily.grace_category,
            "is_locked": daily.is_locked,
            "finalization_status": daily.finalization_status,
            "punches": punches,
            "leave": leave_data,
            "regularization": regularization_data,
        }

    def update_daily_status(
        self,
        company_id: str,
        employee_id: str,
        target_date: date,
        status_code: str,
        requested_by_id: Optional[str] = None,
    ) -> dict:
        """
        Update the status code for a single employee's daily attendance.

        This is a thin mutation API used by the Attendance Matrix manual update
        workflow. It validates the target row, the requested status master,
        and prevents changes to locked attendance days.
        """
        daily = (
            DailyAttendance.objects
            .select_related("status")
            .filter(
                company_id=company_id,
                employee_id=employee_id,
                attendance_date=target_date,
                is_active=True,
            )
            .first()
        )

        if not daily:
            raise ValueError("Attendance record not found for the requested date.")

        if daily.is_locked:
            raise ValueError("Attendance for this date is locked and cannot be updated.")

        status_obj = (
            AttendanceStatus.objects
            .filter(code=status_code.strip().upper(), is_active=True)
            .first()
        )
        if not status_obj:
            raise ValueError(f"Invalid attendance status code: {status_code}.")

        daily.status = status_obj
        update_fields = ["status"]
        if requested_by_id:
            from apps.employees.models import Employee

            updater = Employee.objects.filter(id=requested_by_id).first()
            if updater:
                daily.updated_by = updater
                update_fields.append("updated_by")
        daily.save(update_fields=update_fields)

        return self.get_employee_day(company_id, employee_id, target_date)

    # -------------------------------------------------------------------------
    # 5. Employee Monthly Summary
    # -------------------------------------------------------------------------

    def get_employee_summary(
        self,
        company_id: str,
        employee_id: str,
        year: int,
        month: int,
    ) -> Optional[dict]:
        """
        Return MonthlyAttendanceSummary for one employee.

        Uses cycle_start/cycle_end as the lookup key — the unique constraint
        is on (employee, cycle_start_date, cycle_end_date), not (employee, year, month).
        """
        cycle_start, cycle_end = get_cycle_bounds(company_id, year, month)

        summary = MonthlyAttendanceSummary.objects.filter(
            company_id=company_id,
            employee_id=employee_id,
            cycle_start_date=cycle_start,
            cycle_end_date=cycle_end,
            is_active=True,
        ).first()

        if not summary:
            return None

        return {
            "employee_id": str(employee_id),
            "year": year,
            "month": month,
            "present_days": float(summary.present_days),
            "absent_days": float(summary.absent_days),
            "half_days": float(summary.half_days),
            "late_days": summary.late_days,
            "leave_days": float(summary.leave_days),
            "lwp_days": float(summary.lwp_days),
            "paid_days": float(summary.paid_days),
            "total_work_mins": summary.total_work_mins,
            "ot_mins": summary.ot_mins,
            "late_login_count": summary.late_login_count,
            "early_exit_count": summary.early_exit_count,
            "grace_instances_used": summary.grace_instances_used,
            "is_locked": summary.is_locked,
        }

    # -------------------------------------------------------------------------
    # 6. Departments
    # -------------------------------------------------------------------------

    def get_departments(self, company_id: str) -> list[dict]:
        """
        Return departments that have at least one active employee in the company.
        Used for the "All Departments" filter dropdown.
        """
        from apps.employees.models import Employee

        dept_counts = (
            Employee.objects
            .filter(company_id=company_id, is_active=True)
            .exclude(employment_details__department_id__isnull=True)
            .values(
                "employment_details__department_id",
                "employment_details__department__name",
            )
            .annotate(employee_count=Count("id"))
            .order_by("employment_details__department__name")
        )

        return [
            {
                "id": str(row["employment_details__department_id"]),
                "name": row["employment_details__department__name"],
                "employee_count": row["employee_count"],
            }
            for row in dept_counts
        ]

    # -------------------------------------------------------------------------
    # 7. Cycle Bounds (thin wrapper)
    # -------------------------------------------------------------------------

    def get_cycle_bounds(
        self, company_id: str, year: int, month: int
    ) -> dict:
        """Return cycle bounds and display label for month navigation."""
        cycle_start, cycle_end = get_cycle_bounds(company_id, year, month)
        return {
            "cycle_start": cycle_start.isoformat(),
            "cycle_end": cycle_end.isoformat(),
            "display_label": self._month_label(year, month),
        }

    # -------------------------------------------------------------------------
    # 8. Export — create AttendanceJob
    # -------------------------------------------------------------------------

    def create_export_job(
        self,
        company_id: str,
        year: int,
        month: int,
        export_format: str,
        requested_by_id: str,
        department_id: Optional[str] = None,
        branch_id: Optional[str] = None,
    ) -> dict:
        """
        Queue an async export job by creating an AttendanceJob row.

        The actual file generation is handled by a Celery task that watches
        for QUEUED jobs of type DAILY_COMPUTE with meta_data.job_subtype=EXPORT.
        Returns job_id immediately — client polls the status endpoint.
        """
        cycle_start, _ = get_cycle_bounds(company_id, year, month)

        job = AttendanceJob.objects.create(
            company_id=company_id,
            job_type=AttendanceJobType.DAILY_COMPUTE,  # use closest type; add EXPORT later
            job_date=cycle_start,
            status=AttendanceJobStatus.QUEUED,
            meta_data={
                "job_subtype": "EXPORT",
                "year": year,
                "month": month,
                "format": export_format,
                "department_id": str(department_id) if department_id else None,
                "branch_id": str(branch_id) if branch_id else None,
                "requested_by": str(requested_by_id),
            },
        )

        return {
            "job_id": str(job.id),
            "status": job.status,
            "message": f"Export job queued. Poll /matrix/export/{job.id}/status for updates.",
        }

    def get_export_job_status(self, job_id: str, company_id: str) -> Optional[dict]:
        """
        Return current status of an export job.
        download_url is only present when status=SUCCESS.
        """
        job = AttendanceJob.objects.filter(
            id=job_id,
            company_id=company_id,
        ).first()

        if not job:
            return None

        result: dict = {
            "job_id": str(job.id),
            "status": job.status,
        }

        if job.status == AttendanceJobStatus.SUCCESS:
            # download_url stored in meta_data by the worker after upload
            result["download_url"] = job.meta_data.get("download_url")
            result["expires_at"]   = job.meta_data.get("download_url_expires_at")

        if job.status == AttendanceJobStatus.FAILED:
            result["error"] = job.error_log

        return result

    # -------------------------------------------------------------------------
    # 9. Import — create AttendanceJob
    # -------------------------------------------------------------------------
    def create_import_job(
        self,
        company_id: str,
        year: int,
        month: int,
        requested_by_id: str,
        rows_received: int,
        validation_errors: list,
        temp_file_path: str,
        records_parsed: int = 0,        # ← NEW: total (employee, date) cells
    ) -> dict:
        """
        Queue an async import job after file validation passes.
        If validation_errors is non-empty, raises ValueError — no job created.
        """
        from apps.attendance.models.exceptions_jobs import AttendanceJob
        from apps.attendance.models.enums import AttendanceJobStatus, AttendanceJobType
        from apps.attendance.utils.date_utils import get_cycle_bounds

        if validation_errors:
            raise ValueError(validation_errors)

        cycle_start, _ = get_cycle_bounds(company_id, year, month)

        job = AttendanceJob.objects.create(
            company_id=company_id,
            job_type=AttendanceJobType.DAILY_COMPUTE,
            job_date=cycle_start,
            status=AttendanceJobStatus.QUEUED,
            meta_data={
                "job_subtype":    "IMPORT",
                "year":           year,
                "month":          month,
                "rows_received":  rows_received,
                "records_parsed": records_parsed,
                "temp_file_path": temp_file_path,
                "requested_by":   str(requested_by_id),
            },
        )
        process_matrix_import.delay(str(job.id))

        return {
            "job_id":            str(job.id),
            "status":            job.status,
            "rows_received":     rows_received,
            "validation_errors": [],
            "message": (
                f"Import job queued. {records_parsed} attendance records "
                f"across {rows_received} employee(s) will be processed."
            ),
        }


    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _month_label(year: int, month: int) -> str:
        return date(year, month, 1).strftime("%B %Y").upper()
