from __future__ import annotations

import calendar
import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.attendance.models import (
    AttendanceCompanyConfig,
    AttendanceCycle,
    AttendanceDevice,
    AttendanceHolidayDay,
    AttendancePolicy,
    AttendanceStatus,
    DailyAttendance,
    EmployeeAttendanceConfig,
    EmployeeShiftRoster,
    MonthlyAttendanceSummary,
    PunchLog,
    SwipeLogExportJob,
    SwipeLogImportJob,
    ShiftDefinition,
    ShiftMaster,
    ShiftType,
    WeeklyOff,
)
from apps.attendance.models.enums import (
    DeviceSourceType,
    DeviceStatus,
    DeviceSyncStatus,
    FinalizationStatus,
    PunchSource,
    PunchType,
    ShiftFamily,
    WorkMode,
)
from apps.attendance.models.masters.office_location import AttendanceOfficeLocation
from apps.attendance.models.requests import AttendanceRequest
from apps.attendance.models.requests import OvertimeRequest, RegularizationRequest
from apps.attendance.models.roster_lock import RosterLockConfig, RosterLockState, RosterLockStatus
from apps.attendance.models.roster_publish_log import EmpShiftRosterPublishLog, RosterPublishStatus
from apps.attendance.models.shift_swap import EmpShiftSwapRequest, ShiftSwapStatus
from apps.attendance.models.trackers import LateLoginCycleTracker
from apps.attendance.models.unmapped_punch import UnmappedPunchLog
from apps.employees.models import City, Company, Country, Employee, OfficeLocation, State
from apps.employees.models.masters.recruitment import RejectionReason
from apps.leave.models.masters.reason import Reason, ReasonModuleChoices
from apps.attendance.models.masters.policy_masters import RegularizationReason


@dataclass
class ReportRow:
    table: str
    column: str
    previous_null_count: int
    updated_record_count: int
    remaining_null_count: int


class Command(BaseCommand):
    help = "Seed dummy attendance data and backfill required null fields"

    def add_arguments(self, parser):
        parser.add_argument("--schema", type=str, default="public")
        parser.add_argument("--company-id", type=str, default=None)
        parser.add_argument("--employees", type=int, default=20)
        parser.add_argument("--days", type=int, default=30)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        with schema_context(options["schema"]):
            company = self._resolve_company(options["company_id"])
            if not company:
                self.stdout.write(self.style.ERROR("No company found"))
                return

            rows = self._seed_and_backfill(
                company=company,
                employees_count=options["employees"],
                days=options["days"],
                dry_run=options["dry_run"],
            )
            self._print_report(rows)
            if not options["dry_run"]:
                validation_errors = self._validate_admin_attendance_seed(company, options["employees"])
                if validation_errors:
                    for message in validation_errors:
                        self.stdout.write(self.style.ERROR(message))
                    raise CommandError("Admin attendance seed validation failed")
                self.stdout.write(self.style.SUCCESS("Admin attendance seed validation passed"))

    def _resolve_company(self, company_id: str | None):
        if company_id:
            return Company.objects.filter(id=company_id).first()
        return Company.objects.filter(is_active=True).first()

    def _print_report(self, rows: Iterable[ReportRow]):
        self.stdout.write(self.style.SUCCESS("Attendance demo-data and null-fix report"))
        for row in rows:
            self.stdout.write(
                f"{row.table}.{row.column} | before={row.previous_null_count} "
                f"updated={row.updated_record_count} remaining={row.remaining_null_count}"
            )

    @transaction.atomic
    def _seed_and_backfill(self, company: Company, employees_count: int, days: int, dry_run: bool):
        report: list[ReportRow] = []

        policy = self._seed_policy(company, report, dry_run)
        cycle = self._seed_cycle(company, report, dry_run)
        shift_master, shift_definition = self._seed_shifts(company, report, dry_run)
        self._seed_company_config(company, policy, cycle, shift_definition, report, dry_run)
        self._seed_statuses(report, dry_run)
        self._seed_reason_masters(company, report, dry_run)
        office_location = self._seed_office_location(company, report, dry_run)
        device_location = self._resolve_device_office_location(report, dry_run)
        self._seed_weekly_off(company, report, dry_run)
        self._seed_holidays(company, report, dry_run)
        employees = self._get_employees(company, employees_count)
        self._seed_employee_config(company, employees, policy, cycle, shift_definition, office_location, report, dry_run)
        self._seed_roster(company, employees, cycle, shift_definition, days, report, dry_run)
        self._seed_devices(company, device_location, report, dry_run)
        self._seed_punches(company, employees, shift_master, days, report, dry_run)
        self._seed_daily_attendance(company, employees, policy, shift_definition, days, report, dry_run)
        self._seed_summary(company, employees, days, report, dry_run)
        self._seed_roster_lock(company, employees, report, dry_run)
        self._seed_unmapped_punches(company, report, dry_run)
        self._seed_attendance_requests(company, employees, shift_definition, report, dry_run)
        self._seed_operational_trackers(company, employees, policy, shift_definition, report, dry_run)
        self._seed_export_import_jobs(company, employees, report, dry_run)
        self._backfill_missing(company, report, dry_run)
        return report

    def _seed_policy(self, company, report, dry_run):
        before = AttendancePolicy.objects.filter(company=company).count()
        policy = AttendancePolicy.objects.filter(company=company, is_current=True).first()
        if not policy and not dry_run:
            policy, _ = AttendancePolicy.objects.update_or_create(
                company=company,
                name="Standard Attendance Policy",
                version=1,
                defaults={
                    "is_current": True,
                    "late_login_cycle_limit": 3,
                    "late_login_grace_mins": 15,
                    "late_login_max_grace_mins": 60,
                    "early_exit_max_grace_mins": 90,
                    "short_leave_max_mins": 120,
                    "monthly_grace_instance_limit": 2,
                    "half_day_min_work_mins": 300,
                    "half_day_min_mins": 300,
                    "half_day_max_mins": 479,
                    "full_day_min_mins": 480,
                    "ot_enabled": True,
                    "ot_min_mins": 480,
                    "max_regularizations_month": 2,
                    "meta_data": {"seeded": True},
                    "is_active": True,
                },
            )
        after = AttendancePolicy.objects.filter(company=company).count()
        report.append(ReportRow("mst_attendance_policy", "row", before, after - before, after - before))
        return policy

    def _seed_cycle(self, company, report, dry_run):
        before = AttendanceCycle.objects.filter(company=company).count()
        cycle = AttendanceCycle.objects.filter(company=company, is_default=True).first()
        if not cycle and not dry_run:
            cycle = AttendanceCycle.objects.create(
                company=company,
                name="Monthly Cycle",
                cycle_start_day=1,
                is_default=True,
            )
        after = AttendanceCycle.objects.filter(company=company).count()
        report.append(ReportRow("mst_attendance_cycle", "row", before, after - before, after - before))
        return cycle

    def _seed_shifts(self, company, report, dry_run):
        before = ShiftMaster.objects.filter(company=company).count()
        def_before = ShiftDefinition.objects.filter(company=company).count()
        configs = [
            ("SD_DAY_0930_1830", "Day Shift", ShiftFamily.FIXED, "09:30", "18:30", False),
            ("SD_UK1_1200_2100", "UK 1 Shift", ShiftFamily.FIXED, "12:00", "21:00", False),
            ("SD_UK2_1500_0000", "UK 2 Shift", ShiftFamily.NIGHT, "15:00", "00:00", True),
            ("SD_US1_1600_0100", "US 1 Shift", ShiftFamily.NIGHT, "16:00", "01:00", True),
            ("SD_US2_1800_0330", "US 2 Shift", ShiftFamily.NIGHT, "18:00", "03:30", True),
        ]
        if not ShiftType.objects.filter(code="FIXED").exists() and not dry_run:
            ShiftType.objects.get_or_create(code="FIXED", defaults={"label": "Fixed Shift"})
            ShiftType.objects.get_or_create(code="NIGHT", defaults={"label": "Night Shift"})
            ShiftType.objects.get_or_create(code="FLEXIBLE", defaults={"label": "Flexible Shift"})

        if not ShiftMaster.objects.filter(company=company).exists() and not dry_run:
            for code, name, family, start, end, cross in configs:
                shift_type = ShiftType.objects.filter(code="FIXED" if family == ShiftFamily.FIXED else "NIGHT").first()
                if not shift_type:
                    shift_type = ShiftType.objects.filter(code="FLEXIBLE").first()
                ShiftMaster.objects.get_or_create(
                    company=company,
                    code=code,
                    defaults={
                        "name": name,
                        "shift_type": shift_type,
                        "start_time": datetime.strptime(start, "%H:%M").time(),
                        "end_time": datetime.strptime(end, "%H:%M").time(),
                        "total_mins": self._minutes_between(start, end),
                        "grace_mins": 15,
                        "half_day_mins": 300,
                        "full_day_mins": 480,
                        "cross_midnight": cross,
                        "ot_after_mins": self._minutes_between(start, end),
                    },
                )
        if not ShiftDefinition.objects.filter(company=company).exists() and not dry_run:
            for code, name, family, start, end, cross in configs:
                ShiftDefinition.objects.get_or_create(
                    company=company,
                    code=code,
                    defaults={
                        "name": name,
                        "shift_type": family,
                        "start_time": datetime.strptime(start, "%H:%M").time(),
                        "end_time": datetime.strptime(end, "%H:%M").time(),
                        "cross_midnight": cross,
                        "total_mins": self._minutes_between(start, end),
                        "grace_mins": 15,
                        "half_day_mins": 300,
                        "full_day_mins": 480,
                        "ot_after_mins": self._minutes_between(start, end),
                    },
                )
        after = ShiftMaster.objects.filter(company=company).count()
        def_after = ShiftDefinition.objects.filter(company=company).count()
        report.append(ReportRow("mst_shift_master", "row", before, after - before, 0))
        report.append(ReportRow("mst_shift_definition", "row", def_before, def_after - def_before, 0))
        return ShiftMaster.objects.filter(company=company, is_active=True).first(), ShiftDefinition.objects.filter(company=company, is_active=True).first()

    def _minutes_between(self, start: str, end: str) -> int:
        start_dt = datetime.strptime(start, "%H:%M")
        end_dt = datetime.strptime(end, "%H:%M")
        minutes = int((end_dt - start_dt).total_seconds() // 60)
        if minutes <= 0:
            minutes += 24 * 60
        return minutes

    def _seed_office_location(self, company, report, dry_run):
        before = AttendanceOfficeLocation.objects.filter(company=company).count()
        if before == 0 and not dry_run:
            AttendanceOfficeLocation.objects.get_or_create(
                company=company,
                code="HQ-MAIN",
                defaults={
                    "name": "Head Office",
                    "timezone": "Asia/Kolkata",
                    "address_line1": "Head Office",
                    "geofence_radius_m": 500,
                },
            )
        after = AttendanceOfficeLocation.objects.filter(company=company).count()
        report.append(ReportRow("mst_attendance_office_location", "row", before, after - before, 0))
        return AttendanceOfficeLocation.objects.filter(company=company).first()

    def _resolve_device_office_location(self, report, dry_run):
        """AttendanceDevice.location FK points to employees.OfficeLocation, not AttendanceOfficeLocation."""
        before = OfficeLocation.objects.filter(is_active=True).count()
        location = OfficeLocation.objects.filter(is_active=True).first()
        if location or dry_run:
            report.append(ReportRow("mst_office_location", "device_location", before, 0, 0 if location else 1))
            return location

        country = Country.objects.filter(is_active=True).first() or Country.objects.first()
        state = (
            State.objects.filter(country=country, is_active=True).first()
            if country
            else State.objects.filter(is_active=True).first()
        ) or State.objects.first()
        city = (
            City.objects.filter(state=state, is_active=True).first()
            if state
            else City.objects.filter(is_active=True).first()
        ) or City.objects.first()

        if country and state and city:
            location, _ = OfficeLocation.objects.get_or_create(
                code="HQ-MAIN-ATT",
                defaults={
                    "label": "Head Office",
                    "country": country,
                    "state": state,
                    "city": city,
                    "timezone": "Asia/Kolkata",
                    "is_headquarter": True,
                    "is_active": True,
                },
            )
        after = OfficeLocation.objects.filter(is_active=True).count()
        report.append(ReportRow("mst_office_location", "device_location", before, after - before, 0 if location else 1))
        return location

    def _seed_company_config(self, company, policy, cycle, shift, report, dry_run):
        before = AttendanceCompanyConfig.objects.filter(company=company).count()
        updated = 0
        if not dry_run:
            cfg, created = AttendanceCompanyConfig.objects.get_or_create(
                company=company,
                defaults={
                    "timezone": "Asia/Kolkata",
                    "fiscal_year_start": 4,
                    "week_start_day": 1,
                    "default_policy": policy,
                    "default_cycle": cycle,
                    "default_shift": shift,
                    "geofence_required": False,
                    "meta_data": {"seeded": True},
                },
            )
            if created:
                updated = 1
            else:
                changed = []
                if cfg.default_policy_id is None and policy:
                    cfg.default_policy = policy
                    changed.append("default_policy")
                if cfg.default_cycle_id is None and cycle:
                    cfg.default_cycle = cycle
                    changed.append("default_cycle")
                if cfg.default_shift_id is None and shift:
                    cfg.default_shift = shift
                    changed.append("default_shift")
                if changed:
                    cfg.save(update_fields=changed)
                    updated = 1
        after = AttendanceCompanyConfig.objects.filter(company=company).count()
        report.append(ReportRow("mst_attendance_company_config", "row", before, updated, 0 if after else 1))

    def _seed_statuses(self, report, dry_run):
        needed = [
            ("PRESENT", "Present", True, True, 1),
            ("ABSENT", "Absent", False, False, 2),
            ("HALF_DAY", "Half Day", True, True, 3),
            ("LEAVE", "Leave", True, False, 4),
            ("LOP", "Loss of Pay", False, False, 5),
            ("HOLIDAY", "Holiday", True, False, 6),
            ("WEEK_OFF", "Week Off", True, False, 7),
            ("IN_PROGRESS", "In Progress", True, True, 8),
        ]
        before = AttendanceStatus.objects.count()
        if not dry_run:
            for code, name, paid, present_eq, order in needed:
                AttendanceStatus.objects.get_or_create(
                    code=code,
                    defaults={
                        "name": name,
                        "is_paid": paid,
                        "is_present_equivalent": present_eq,
                        "sort_order": order,
                        "is_active": True,
                    },
                )
        after = AttendanceStatus.objects.count()
        report.append(ReportRow("mst_attendance_status", "row", before, after - before, 0))

    def _seed_reason_masters(self, company, report, dry_run):
        reg_before = Reason.objects.filter(module=ReasonModuleChoices.REGULARIZATION).count()
        rej_before = RejectionReason.objects.filter(company_id=company.id).count()
        reg_reason_before = RegularizationReason.objects.filter(company_id=company.id).count()

        if not dry_run:
            for code, label in [
                ("MISSED_PUNCH", "Missed Punch"),
                ("DEVICE_FAILURE", "Device Failure"),
                ("TRAFFIC_DELAY", "Traffic Delay"),
                ("SHIFT_MISMATCH", "Shift Mismatch"),
            ]:
                Reason.objects.get_or_create(
                    module=ReasonModuleChoices.REGULARIZATION,
                    code=code,
                    defaults={"label": label, "meta_data": {"seeded": True}},
                )

            for code, name, stage in [
                ("NOT_A_FIT", "Not a Fit", "manager_screening"),
                ("ROLE_RESTRUCTURE", "Role Restructuring", "final_round"),
                ("BUDGET_CONSTRAINT", "Budget Constraint", "offer_stage"),
            ]:
                RejectionReason.objects.get_or_create(
                    company_id=company.id,
                    code=code,
                    defaults={"name": name, "rejection_stage": stage},
                )

            for code, name in [
                ("MISSED_PUNCH", "Missed Punch"),
                ("TRAFFIC_DELAY", "Traffic Delay"),
                ("DEVICE_ISSUE", "Device Issue"),
                ("APPROVAL_PENDING", "Approval Pending"),
            ]:
                RegularizationReason.objects.get_or_create(
                    company_id=company.id,
                    code=code,
                    defaults={"name": name},
                )

        reg_after = Reason.objects.filter(module=ReasonModuleChoices.REGULARIZATION).count()
        rej_after = RejectionReason.objects.filter(company_id=company.id).count()
        reg_reason_after = RegularizationReason.objects.filter(company_id=company.id).count()
        report.append(ReportRow("mst_reason", "regularization", reg_before, reg_after - reg_before, 0))
        report.append(ReportRow("mst_rejection_reason", "row", rej_before, rej_after - rej_before, 0))
        report.append(ReportRow("mst_regularization_reason", "row", reg_reason_before, reg_reason_after - reg_reason_before, 0))

    def _seed_weekly_off(self, company, report, dry_run):
        before = WeeklyOff.objects.filter(company=company).count()
        if not dry_run:
            for wk in (5, 6):
                WeeklyOff.objects.get_or_create(
                    company=company,
                    week_day=wk,
                    defaults={"effective_from": date.today(), "reason": "Weekend", "is_active": True},
                )
        after = WeeklyOff.objects.filter(company=company).count()
        report.append(ReportRow("mst_weekly_off", "row", before, after - before, 0))

    def _seed_holidays(self, company, report, dry_run):
        before = AttendanceHolidayDay.objects.filter(company=company).count()

        HolidayTypeModel = AttendanceHolidayDay._meta.get_field("holiday_type").remote_field.model

        htype = HolidayTypeModel.objects.filter(code="NATIONAL").first()
        if not htype and not dry_run:
            # Ensure we never insert AttendanceHolidayDay with holiday_type=NULL.
            # If NATIONAL is missing in this tenant schema, create it.
            try:
                htype = HolidayTypeModel.objects.create(
                    code="NATIONAL",
                    label="National Holidays",
                    defaults={},
                )
            except TypeError:
                # Some holiday type models may not have `label` or may use different required fields.
                # Fall back to creating with minimal fields.
                htype = HolidayTypeModel.objects.create(code="NATIONAL")
            except Exception:
                htype = None

        if not htype:
            # Final fallback: pick any existing holiday type to satisfy the FK constraint.
            htype = HolidayTypeModel.objects.first()

        dates = [
            ("Republic Day", date(date.today().year, 1, 26)),
            ("Independence Day", date(date.today().year, 8, 15)),
            ("Gandhi Jayanti", date(date.today().year, 10, 2)),
        ]

        if not dry_run:
            if not htype:
                # Still nothing available; skip to avoid NOT NULL constraint failure.
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping holiday seeding for schema due to missing holiday_type (code=NATIONAL) and no fallback HolidayType rows available."
                    )
                )
            else:
                for name, hol_date in dates:
                    AttendanceHolidayDay.objects.get_or_create(
                        company=company,
                        holiday_date=hol_date,
                        defaults={
                            "calendar_year": hol_date.year,
                            "name": name,
                            "holiday_type": htype,
                            "is_paid": True,
                            "is_restricted": False,
                        },
                    )

        after = AttendanceHolidayDay.objects.filter(company=company).count()
        report.append(ReportRow("mst_attendance_holiday_calendar", "row", before, after - before, 0))


    def _get_employees(self, company, employees_count):
        qs = Employee.objects.filter(company=company, status=Employee.StatusChoices.ACTIVE)[:employees_count]
        return list(qs)

    def _seed_employee_config(self, company, employees, policy, cycle, shift, office_location, report, dry_run):
        before = EmployeeAttendanceConfig.objects.filter(company=company).count()
        if policy and cycle and shift and not dry_run:
            for emp in employees:
                EmployeeAttendanceConfig.objects.get_or_create(
                    company=company,
                    employee=emp,
                    defaults={
                        "policy": policy,
                        "cycle": cycle,
                        "shift": shift,
                        "location": office_location,
                        "effective_from": date.today(),
                        "is_active": True,
                    },
                )
        after = EmployeeAttendanceConfig.objects.filter(company=company).count()
        report.append(ReportRow("emp_attendance_config", "row", before, after - before, 0))

    def _seed_roster(self, company, employees, cycle, shift, days, report, dry_run):
        before = EmployeeShiftRoster.objects.filter(company=company).count()
        if cycle and shift and not dry_run:
            start = date.today().replace(day=1)
            for emp in employees:
                for offset in range(days):
                    d = start + timedelta(days=offset)
                    EmployeeShiftRoster.objects.get_or_create(
                        company=company,
                        employee=emp,
                        roster_date=d,
                        defaults={"shift": shift, "cycle": cycle, "is_week_off": d.weekday() in (5, 6)},
                    )
        after = EmployeeShiftRoster.objects.filter(company=company).count()
        report.append(ReportRow("emp_shift_roster", "row", before, after - before, 0))

    def _seed_punches(self, company, employees, shift, days, report, dry_run):
        before = PunchLog.objects.filter(company=company).count()
        if shift and not dry_run:
            base = date.today() - timedelta(days=days)
            fallback_employee = employees[0] if employees else None
            for emp in employees:
                for i in range(days):
                    punch_date = base + timedelta(days=i)
                    if punch_date.weekday() in (5, 6):
                        continue
                    in_dt = timezone.make_aware(
                        datetime.combine(punch_date, shift.start_time) + timedelta(minutes=random.randint(-10, 15))
                    )
                    out_dt = timezone.make_aware(
                        datetime.combine(punch_date, shift.end_time) + timedelta(minutes=random.randint(-10, 30))
                    )
                    for punch_time, ptype in ((in_dt, PunchType.IN), (out_dt, PunchType.OUT)):
                        PunchLog.objects.get_or_create(
                            company=company,
                            employee=emp,
                            punch_time=punch_time,
                            defaults={
                                "punch_type": ptype,
                                "punch_source": PunchSource.BIOMETRIC,
                                "source": "ESSL",
                                "created_by": fallback_employee,
                            },
                        )
        after = PunchLog.objects.filter(company=company).count()
        report.append(ReportRow("att_punch_log", "row", before, after - before, 0))

    def _seed_daily_attendance(self, company, employees, policy, shift, days, report, dry_run):
        before = DailyAttendance.objects.filter(company=company).count()
        present = AttendanceStatus.objects.filter(code="PRESENT").first()
        absent = AttendanceStatus.objects.filter(code="ABSENT").first()
        half_day = AttendanceStatus.objects.filter(code="HALF_DAY").first()
        leave = AttendanceStatus.objects.filter(code="LEAVE").first()
        week_off = AttendanceStatus.objects.filter(code="WEEK_OFF").first()
        if policy and shift and present and not dry_run:
            base = date.today() - timedelta(days=days)
            for emp in employees:
                for i in range(days):
                    d = base + timedelta(days=i)
                    if d.weekday() in (5, 6):
                        status_obj = week_off or present
                    else:
                        roll = i % 11
                        if roll == 0 and absent:
                            status_obj = absent
                        elif roll == 3 and half_day:
                            status_obj = half_day
                        elif roll == 7 and leave:
                            status_obj = leave
                        else:
                            status_obj = present
                    DailyAttendance.objects.get_or_create(
                        company=company,
                        employee=emp,
                        attendance_date=d,
                        defaults={
                            "shift": shift,
                            "policy": policy,
                            "status": status_obj,
                            "work_mode": WorkMode.OFFICE,
                            "actual_work_mins": 480,
                            "late_in_mins": 0,
                            "early_exit_mins": 0,
                            "short_leave_mins": 0,
                            "ot_mins": 0,
                            "lop_days": 0,
                            "is_late": False,
                            "is_early_exit": False,
                            "is_grace": False,
                            "finalization_status": FinalizationStatus.DRAFT,
                        },
                    )
        after = DailyAttendance.objects.filter(company=company).count()
        report.append(ReportRow("emp_daily_attendance", "row", before, after - before, 0))

    def _seed_summary(self, company, employees, days, report, dry_run):
        before = MonthlyAttendanceSummary.objects.filter(company=company).count()
        if not dry_run:
            today = date.today()
            start = today.replace(day=1)
            end = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
            for emp in employees:
                MonthlyAttendanceSummary.objects.get_or_create(
                    company=company,
                    employee=emp,
                    year=today.year,
                    month=today.month,
                    cycle_start_date=start,
                    cycle_end_date=end,
                    defaults={
                        "present_days": 20,
                        "absent_days": 2,
                        "half_days": 1,
                        "leave_days": 1,
                        "paid_days": 20,
                        "total_work_mins": 20 * 480,
                        "ot_mins": 0,
                    },
                )
        after = MonthlyAttendanceSummary.objects.filter(company=company).count()
        report.append(ReportRow("emp_monthly_attendance_summary", "row", before, after - before, 0))

    def _seed_devices(self, company, device_location, report, dry_run):
        before = AttendanceDevice.objects.filter(company=company).count()
        if not dry_run and before == 0:
            AttendanceDevice.objects.create(
                company=company,
                device_code="31",
                device_name="Main Gate Biometric",
                location=device_location,
                source_type=DeviceSourceType.BIOMAX,
                model="BioMax-X300",
                serial_number="BIO-31",
                is_trusted=True,
                status=DeviceStatus.ONLINE,
                sync_status=DeviceSyncStatus.NEVER_SYNCED,
                uptime_percentage=100.00,
            )
        after = AttendanceDevice.objects.filter(company=company).count()
        report.append(ReportRow("mst_attendance_device", "row", before, after - before, 0))

    def _seed_roster_lock(self, company, employees, report, dry_run):
        cfg_before = RosterLockConfig.objects.filter(company=company).count()
        state_before = RosterLockState.objects.filter(company=company).count()
        fallback_employee = employees[0] if employees else None
        if not dry_run:
            RosterLockConfig.objects.get_or_create(
                company=company,
                lock_date=25,
                defaults={"auto_lock_enabled": True, "grace_days": 3},
            )
            RosterLockState.objects.get_or_create(
                company=company,
                lock_year=date.today().year,
                lock_month=date.today().month,
                defaults={
                    "status": RosterLockStatus.UNLOCKED,
                    "is_locked": False,
                    "lock_reason": "Seeded for attendance testing",
                    "locked_by": fallback_employee,
                    "unlocked_by": fallback_employee,
                },
            )
        cfg_after = RosterLockConfig.objects.filter(company=company).count()
        state_after = RosterLockState.objects.filter(company=company).count()
        report.append(ReportRow("att_roster_lock_config", "row", cfg_before, cfg_after - cfg_before, 0))
        report.append(ReportRow("att_roster_lock_state", "row", state_before, state_after - state_before, 0))

    def _seed_unmapped_punches(self, company, report, dry_run):
        before = UnmappedPunchLog.objects.filter(company=company).count()
        if not dry_run:
            seeds = [
                (900001, "E99901", "DeviceLogs_1_2026", "IN", 31, "Employee code not mapped during ingest"),
                (900002, "E99902", "DeviceLogs_1_2026", "OUT", 31, "Employee master missing at sync time"),
            ]
            for log_id, user_id, source_table, punch_type, device_id, reason in seeds:
                UnmappedPunchLog.objects.get_or_create(
                    essl_log_id=log_id,
                    essl_source_table=source_table,
                    defaults={
                        "company": company,
                        "essl_user_id": user_id,
                        "punch_time": timezone.now() - timedelta(days=log_id % 5 + 1),
                        "punch_type": punch_type,
                        "device_id": device_id,
                        "reason": reason,
                        "raw_payload": {"seeded": True, "source": "attendance_seed_and_backfill"},
                        "resolved": False,
                    },
                )
        after = UnmappedPunchLog.objects.filter(company=company).count()
        report.append(ReportRow("att_unmapped_punch_log", "row", before, after - before, 0))

    def _seed_attendance_requests(self, company, employees, shift, report, dry_run):
        before = AttendanceRequest.objects.count()
        fallback_employee = employees[0] if employees else None
        if fallback_employee and shift and not dry_run:
            attendance_lookup = {
                row.attendance_date: row
                for row in DailyAttendance.objects.filter(company=company, employee=fallback_employee)
            }
            seed_rows = [
                {
                    "request_type": "regularization",
                    "date": date.today() - timedelta(days=2),
                    "reason": "Missed punch due to device issue",
                    "punch_in": shift.start_time,
                    "punch_out": shift.end_time,
                    "working_hours": "08:00",
                    "manager_status": "approved",
                    "final_status": "fully_approved",
                },
                {
                    "request_type": "late_login",
                    "date": date.today() - timedelta(days=3),
                    "reason": "Traffic delay on route to office",
                    "punch_in": shift.start_time,
                    "working_hours": "08:30",
                    "manager_status": "pending",
                    "final_status": "pending",
                },
                {
                    "request_type": "half_day",
                    "date": date.today() - timedelta(days=4),
                    "reason": "Personal work, requesting half-day regularization",
                    "punch_out": shift.end_time,
                    "working_hours": "04:00",
                    "manager_status": "approved",
                    "final_status": "pending_admin_approval",
                },
            ]
            for row in seed_rows:
                request, created = AttendanceRequest.objects.get_or_create(
                    employee=fallback_employee,
                    request_type=row["request_type"],
                    date=row["date"],
                    reason=row["reason"],
                    defaults={
                        "shift_time": f"{shift.start_time.strftime('%H:%M')} - {shift.end_time.strftime('%H:%M')}",
                        "punch_in": row.get("punch_in"),
                        "punch_out": row.get("punch_out"),
                        "working_hours": row["working_hours"],
                        "manager_status": row["manager_status"],
                        "final_status": row["final_status"],
                    },
                )
                if created:
                    ApprovalWorkflow = AttendanceRequest._meta.apps.get_model("attendance", "ApprovalWorkflow")
                    ApprovalWorkflow.objects.get_or_create(
                        request=request,
                        stage="manager",
                        status="pending",
                        defaults={"approver": fallback_employee, "comment": "Seeded approval workflow"},
                    )
                attendance = attendance_lookup.get(row["date"])
                if attendance and row["request_type"] == "regularization":
                    RegularizationRequest.objects.get_or_create(
                        company=company,
                        employee=fallback_employee,
                        attendance=attendance,
                        regularization_date=row["date"],
                        reg_type="MISSING_PUNCH",
                        defaults={
                            "requested_in": timezone.make_aware(datetime.combine(row["date"], shift.start_time)),
                            "requested_out": timezone.make_aware(datetime.combine(row["date"], shift.end_time)),
                            "requested_status": "PRESENT",
                            "permission_mins": 0,
                            "justification": row["reason"],
                            "status": "APPROVED",
                            "request_number": f"REG-{row['date'].strftime('%Y%m%d')}",
                        },
                    )
                if attendance and row["request_type"] == "late_login":
                    RegularizationRequest.objects.get_or_create(
                        company=company,
                        employee=fallback_employee,
                        attendance=attendance,
                        regularization_date=row["date"],
                        reg_type="PERMISSION",
                        defaults={
                            "mode": "LATE_LOGIN",
                            "requested_in": timezone.make_aware(datetime.combine(row["date"], shift.start_time)),
                            "requested_status": "PRESENT",
                            "permission_mins": 30,
                            "justification": row["reason"],
                            "status": "PENDING",
                            "request_number": f"LAT-{row['date'].strftime('%Y%m%d')}",
                        },
                    )
                if attendance and row["request_type"] == "half_day":
                    OvertimeRequest.objects.get_or_create(
                        company=company,
                        employee=fallback_employee,
                        attendance=attendance,
                        ot_date=row["date"],
                        claimed_ot_mins=0,
                        defaults={
                            "approved_ot_mins": 0,
                            "reason": row["reason"],
                            "status": "PENDING",
                            "request_number": f"HALF-{row['date'].strftime('%Y%m%d')}",
                        },
                    )
        after = AttendanceRequest.objects.count()
        report.append(ReportRow("attendance_requests", "row", before, after - before, 0))

    def _seed_operational_trackers(self, company, employees, policy, shift_definition, report, dry_run):
        tracker_before = LateLoginCycleTracker.objects.filter(company=company).count()
        roster_log_before = EmpShiftRosterPublishLog.objects.filter(company=company).count()
        swap_before = EmpShiftSwapRequest.objects.filter(company=company).count()

        fallback_employee = employees[0] if employees else None
        alt_employee = employees[1] if len(employees) > 1 else fallback_employee

        if not dry_run and fallback_employee and policy:
            cycle_month = date.today().replace(day=1)
            LateLoginCycleTracker.objects.get_or_create(
                company=company,
                employee=fallback_employee,
                policy=policy,
                cycle_month=cycle_month,
                defaults={
                    "cycle_number": 1,
                    "late_count": 2,
                    "is_cycle_closed": False,
                    "half_day_triggered_date": cycle_month + timedelta(days=7),
                    "meta_data": {"seeded": True},
                },
            )

            EmpShiftRosterPublishLog.objects.get_or_create(
                company=company,
                publish_year=cycle_month.year,
                publish_month=cycle_month.month,
                defaults={
                    "status": RosterPublishStatus.PUBLISHED,
                    "published_count": len(employees),
                    "unpublished_count": 0,
                    "department_ids": [],
                    "is_locked": True,
                    "published_at": timezone.now() - timedelta(days=1),
                    "published_by": fallback_employee,
                    "note": "Seeded roster publish event for attendance testing",
                },
            )

            if alt_employee and shift_definition and fallback_employee != alt_employee:
                EmpShiftSwapRequest.objects.get_or_create(
                    company=company,
                    requester=fallback_employee,
                    target=alt_employee,
                    swap_date=date.today() + timedelta(days=3),
                    defaults={
                        "requester_shift": shift_definition,
                        "target_shift": shift_definition,
                        "status": ShiftSwapStatus.PENDING_APPROVAL,
                        "reason": "Seeded swap request for attendance testing",
                        "meta_data": {"seeded": True},
                    },
                )

        tracker_after = LateLoginCycleTracker.objects.filter(company=company).count()
        roster_log_after = EmpShiftRosterPublishLog.objects.filter(company=company).count()
        swap_after = EmpShiftSwapRequest.objects.filter(company=company).count()
        report.append(ReportRow("emp_late_login_cycle_tracker", "row", tracker_before, tracker_after - tracker_before, 0))
        report.append(ReportRow("emp_shift_roster_publish_log", "row", roster_log_before, roster_log_after - roster_log_before, 0))
        report.append(ReportRow("emp_shift_swap_request", "row", swap_before, swap_after - swap_before, 0))

    def _seed_export_import_jobs(self, company, employees, report, dry_run):
        exp_before = SwipeLogExportJob.objects.filter(company=company).count()
        imp_before = SwipeLogImportJob.objects.filter(company=company).count()

        fallback_employee = employees[0] if employees else None
        if not dry_run and fallback_employee:
            export_jobs = [
                {
                    "status": "COMPLETED",
                    "export_format": "CSV",
                    "total_records": 150,
                    "processed_records": 150,
                    "file_size": 25000,
                    "file_path": "/exports/export_2026_01_001.csv",
                    "file_url": "http://acme.localhost:8000/files/export_2026_01_001.csv",
                    "from_date": date.today().replace(day=1),
                    "to_date": date.today(),
                    "started_at": timezone.now() - timedelta(days=5, hours=1),
                    "completed_at": timezone.now() - timedelta(days=5),
                },
                {
                    "status": "PROCESSING",
                    "export_format": "XLSX",
                    "total_records": 200,
                    "processed_records": 90,
                    "file_size": None,
                    "file_path": None,
                    "file_url": None,
                    "from_date": date.today().replace(day=1),
                    "to_date": date.today(),
                    "started_at": timezone.now() - timedelta(hours=1),
                    "completed_at": None,
                    "celery_task_id": str(random.randint(100000, 999999)),
                },
                {
                    "status": "FAILED",
                    "export_format": "PDF",
                    "total_records": 100,
                    "processed_records": 50,
                    "file_size": None,
                    "file_path": None,
                    "file_url": None,
                    "from_date": date.today().replace(day=1),
                    "to_date": date.today(),
                    "error_message": "Database connection timeout during export",
                    "started_at": timezone.now() - timedelta(days=2, hours=1),
                    "completed_at": timezone.now() - timedelta(days=2),
                },
            ]
            for job in export_jobs:
                SwipeLogExportJob.objects.get_or_create(
                    company=company,
                    requested_by=fallback_employee,
                    status=job["status"],
                    export_format=job["export_format"],
                    total_records=job["total_records"],
                    processed_records=job["processed_records"],
                    defaults={
                        "file_size": job.get("file_size"),
                        "file_path": job.get("file_path"),
                        "file_url": job.get("file_url"),
                        "from_date": job.get("from_date"),
                        "to_date": job.get("to_date"),
                        "error_message": job.get("error_message"),
                        "celery_task_id": job.get("celery_task_id"),
                        "started_at": job.get("started_at"),
                        "completed_at": job.get("completed_at"),
                        "include_employee_details": True,
                        "include_device_details": True,
                    },
                )

            import_jobs = [
                {
                    "status": "COMPLETED",
                    "total_rows": 100,
                    "accepted": 98,
                    "rejected": 2,
                    "duplicate_detected": 0,
                    "file_path": "/imports/punch_log_2026_05.csv",
                    "started_at": timezone.now() - timedelta(days=7, hours=1),
                    "completed_at": timezone.now() - timedelta(days=7),
                },
                {
                    "status": "PROCESSING",
                    "total_rows": 150,
                    "accepted": 75,
                    "rejected": 5,
                    "duplicate_detected": 2,
                    "file_path": "/imports/punch_log_2026_06_batch1.csv",
                    "started_at": timezone.now() - timedelta(hours=2),
                    "completed_at": None,
                },
                {
                    "status": "FAILED",
                    "total_rows": 80,
                    "accepted": 40,
                    "rejected": 40,
                    "duplicate_detected": 10,
                    "file_path": "/imports/punch_log_2026_03_corrupted.csv",
                    "errors": [
                        "Row 15: Invalid punch_time format",
                        "Row 22: Employee ID not found",
                        "Row 45: Duplicate punch within 5 minutes",
                    ],
                    "started_at": timezone.now() - timedelta(days=2, hours=1),
                    "completed_at": timezone.now() - timedelta(days=2),
                },
            ]
            for job in import_jobs:
                SwipeLogImportJob.objects.get_or_create(
                    company=company,
                    created_by=fallback_employee,
                    status=job["status"],
                    total_rows=job["total_rows"],
                    accepted=job["accepted"],
                    rejected=job["rejected"],
                    duplicate_detected=job["duplicate_detected"],
                    defaults={
                        "file_path": job.get("file_path"),
                        "errors": job.get("errors", []),
                        "started_at": job.get("started_at"),
                        "completed_at": job.get("completed_at"),
                    },
                )

        exp_after = SwipeLogExportJob.objects.filter(company=company).count()
        imp_after = SwipeLogImportJob.objects.filter(company=company).count()
        report.append(ReportRow("att_swipe_log_export_job", "row", exp_before, exp_after - exp_before, 0))
        report.append(ReportRow("att_swipe_log_import_job", "row", imp_before, imp_after - imp_before, 0))

    def _backfill_missing(self, company, report, dry_run):
        fallback_employee = Employee.objects.filter(company=company, status=Employee.StatusChoices.ACTIVE).first()
        fallback_device = AttendanceDevice.objects.filter(company=company, is_active=True).first()
        if not dry_run:
            if fallback_employee:
                for row in PunchLog.objects.filter(company=company, created_by__isnull=True).iterator():
                    row.created_by = fallback_employee
                    row.save(update_fields=["created_by"])
            if fallback_device:
                for row in PunchLog.objects.filter(company=company, device__isnull=True).iterator():
                    row.device = fallback_device
                    row.save(update_fields=["device"])
        report.append(ReportRow("att_punch_log", "created_by/device", PunchLog.objects.filter(company=company, created_by__isnull=True).count() + PunchLog.objects.filter(company=company, device__isnull=True).count(), 0, PunchLog.objects.filter(company=company, created_by__isnull=True).count() + PunchLog.objects.filter(company=company, device__isnull=True).count()))

    def _validate_admin_attendance_seed(self, company: Company, employees_requested: int) -> list[str]:
        """Post-seed checks for admin attendance dashboards and APIs."""
        errors: list[str] = []
        active_employees = Employee.objects.filter(
            company=company, status=Employee.StatusChoices.ACTIVE
        ).count()

        required_masters = [
            ("Attendance policy", AttendancePolicy.objects.filter(company=company, is_current=True).exists()),
            ("Attendance cycle", AttendanceCycle.objects.filter(company=company, is_default=True).exists()),
            ("Shift definition", ShiftDefinition.objects.filter(company=company, is_active=True).exists()),
            ("Attendance statuses", AttendanceStatus.objects.filter(code="PRESENT", is_active=True).exists()),
        ]
        for label, ok in required_masters:
            if not ok:
                errors.append(f"Missing required master: {label}")

        if active_employees == 0:
            errors.append("No active employees found for company; admin matrix/roster views will be empty")
        elif employees_requested > 0 and EmployeeShiftRoster.objects.filter(company=company).count() == 0:
            errors.append("No shift roster rows seeded for active employees")

        min_counts = [
            ("emp_shift_roster", EmployeeShiftRoster.objects.filter(company=company).count(), 1),
            ("att_punch_log", PunchLog.objects.filter(company=company).count(), 1),
            ("emp_daily_attendance", DailyAttendance.objects.filter(company=company).count(), 1),
            ("mst_attendance_device", AttendanceDevice.objects.filter(company=company).count(), 1),
            ("att_swipe_log_export_job", SwipeLogExportJob.objects.filter(company=company).count(), 1),
        ]
        for table, count, minimum in min_counts:
            if active_employees > 0 and count < minimum:
                errors.append(f"{table}: expected at least {minimum} row(s), found {count}")

        cfg = AttendanceCompanyConfig.objects.filter(company=company).first()
        if not cfg:
            errors.append("mst_attendance_company_config: company attendance config row is missing")
        else:
            if not cfg.default_policy_id:
                errors.append("mst_attendance_company_config: default_policy is not set")
            if not cfg.default_cycle_id:
                errors.append("mst_attendance_company_config: default_cycle is not set")
            if not cfg.default_shift_id:
                errors.append("mst_attendance_company_config: default_shift is not set")

        return errors
