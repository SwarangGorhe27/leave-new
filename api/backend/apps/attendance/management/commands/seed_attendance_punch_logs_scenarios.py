from __future__ import annotations

"""Seed PunchLog rows + (optional) DailyAttendance for specific scenarios.

This command is tenant-aware (django-tenants) and ONLY touches PunchLog
(and optionally DailyAttendance) for the requested employees/date range.

What it does (per your requirements):
1) Reads employee records from apps.employees.Employee.
2) For exactly one employee (the "tonight shift" employee):
   - updates/ensures EmployeeShiftRoster for tonight's roster_date to the
     Night shift.
3) For the remaining two employees:
   - ensures EmployeeShiftRoster for tonight's roster_date uses the
     Flexible (10:00-18:00) shift.
4) Inserts PunchLog entries for:
   - today (tenant-local) + previous N days (N = --days-back)
   - for the Night shift employee, it also seeds the normal cross-midnight
     OUT punch (22:00 on roster_date, OUT on roster_date+1 at 06:00).
5) It additionally supports several attendance scenario types via
   deterministic punch-time offsets:
   - LEAVE (half-day leave)
   - SHORT_LEAVE
   - LATE_LOGIN
   - EARLY_GOING

Notes:
- The command is idempotent for PunchLog based on (essl_log_id,
  essl_source_table). For seeded punches we intentionally set a deterministic
  pair so re-running won't duplicate.
- It does NOT modify any other module logic.

Usage example:
python manage.py seed_attendance_punch_logs_scenarios \
  --schema acme \
  --company-id <COMPANY_UUID> \
  --days-back 2 \
  --seed 123 \
  --punch-only

"""


import argparse
import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from django.core.management.base import BaseCommand
from typing import Dict, List, Optional, Tuple
from django.db import transaction
from django_tenants.utils import schema_context
from django.utils import timezone


from apps.attendance.models import (
    AttendanceStatus,
    DailyAttendance,
    DailyAttendanceSession,
    EmployeeAttendanceConfig,
    EmployeeShiftRoster,
    PunchLog,
    ShiftDefinition,
)
from apps.attendance.models.enums import FinalizationStatus, PunchSource, PunchType, WorkMode
from apps.employees.models import Company, Employee


# =====================
# Constants (examples)
# =====================

# Use these IDs from your DB snapshot.
DEFAULT_COMPANY_ID = "3e3d1590-4251-41f1-be99-0d4d16b09ec7"
DEFAULT_TENANT_SCHEMA = "acme"

# Employees from your DB snapshot.
EMPLOYEE_NIGHT_SHIFT_EMPLOYEE_CODE = "PTSPL0001"  # Rajesh Kumar (shift gets updated to night)
EMPLOYEE_FLEX_EMPLOYEE_CODE_A = "PTSPL0002"  # Priya Singh
EMPLOYEE_FLEX_EMPLOYEE_CODE_B = "PTSPL0003"  # Amit Patel

# ShiftDefinition IDs from your DB snapshot.
SHIFT_ID_FLEXIBLE = "0598b73d-3af1-4f6c-b92f-cc0c0255e44d"  # FLEX_1000_1800
SHIFT_ID_NIGHT = "ac51c2dc-a11f-4189-9503-dd189f0a0c24"  # NIGHT_2200_0600

# Deterministic punch metadata
SEEDED_SOURCE = "ESSL"
SEEDED_EH_SOURCE_TABLE = "SEED_ATT_SCENARIOS"


@dataclass(frozen=True)
class EmployeeScenarioConfig:
    employee: Employee
    roster_shift_id_today: str


class Command(BaseCommand):
    help = "Seed tenant-aware PunchLog rows (and optionally DailyAttendance) for scenarios (leave/short-late/early)."

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("--schema", type=str, default=DEFAULT_TENANT_SCHEMA)
        parser.add_argument("--company-id", type=str, default=None)
        parser.add_argument("--days-back", type=int, default=2)
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument(
            "--punch-only",
            action="store_true",
            help="If set, only PunchLog rows are seeded; DailyAttendance is untouched.",
        )
        parser.add_argument(
            "--employee-code-night",
            type=str,
            default=EMPLOYEE_NIGHT_SHIFT_EMPLOYEE_CODE,
        )
        parser.add_argument(
            "--employee-code-flex-a",
            type=str,
            default=EMPLOYEE_FLEX_EMPLOYEE_CODE_A,
        )
        parser.add_argument(
            "--employee-code-flex-b",
            type=str,
            default=EMPLOYEE_FLEX_EMPLOYEE_CODE_B,
        )
        parser.add_argument(
            "--shift-id-flexible",
            type=str,
            default=SHIFT_ID_FLEXIBLE,
        )
        parser.add_argument(
            "--shift-id-night",
            type=str,
            default=SHIFT_ID_NIGHT,
        )
        parser.add_argument(
            "--include-scenarios",
            action="store_true",
            help="If set, applies LATE/SHORT_LEAVE/HALF_DAY_LEAVE/EARLY_GOING punch offsets.",
        )

    def handle(self, *args, **options):
        schema = options["schema"]
        company_id = options["company_id"] or DEFAULT_COMPANY_ID
        days_back = int(options["days_back"])
        seed = int(options["seed"])
        punch_only = bool(options["punch_only"])
        include_scenarios = bool(options["include_scenarios"])

        random.seed(seed)

        with schema_context(schema):
            company = self._resolve_company(company_id)
            if not company:
                raise RuntimeError(f"Company not found: {company_id}")

            night_emp = self._get_employee_by_code(company, options["employee_code_night"])
            flex_emp_a = self._get_employee_by_code(company, options["employee_code_flex_a"])
            flex_emp_b = self._get_employee_by_code(company, options["employee_code_flex_b"])

            flex_shift = self._get_shift_definition(company, options["shift_id_flexible"])
            night_shift = self._get_shift_definition(company, options["shift_id_night"])

            today_local = self._tenant_today()
            roster_date_today = today_local

            scenarios = self._scenario_dates(days_back)

            with transaction.atomic():
                # 1) Ensure roster shifts for tonight's roster_date.
                self._upsert_roster_for_emp(night_emp, night_shift, roster_date_today)
                self._upsert_roster_for_emp(flex_emp_a, flex_shift, roster_date_today)
                self._upsert_roster_for_emp(flex_emp_b, flex_shift, roster_date_today)

                # 2) Seed PunchLog for today + previous days.
                punch_rows = self._build_punch_rows(
                    company=company,
                    employees=[night_emp, flex_emp_a, flex_emp_b],
                    roster_date_today=roster_date_today,
                    days_back=days_back,
                    scenarios=scenarios,
                    include_scenarios=include_scenarios,
                    night_shift=night_shift,
                    flex_shift=flex_shift,
                    seed=seed,
                )

                created = self._bulk_upsert_punchlogs(punch_rows)

                # daily = []
                # if not punch_only:
                #     daily = self._seed_daily_attendance_for_range(
                #         company=company,
                #         employees=[night_emp, flex_emp_a, flex_emp_b],
                #         roster_date_today=roster_date_today,
                #         days_back=days_back,
                #         scenarios=scenarios,
                #         include_scenarios=include_scenarios,
                #         night_shift=night_shift,
                #         flex_shift=flex_shift,
                #     )

            # 3) Write summary txt.
            # summary_txt_path = self._write_summary_txt(
            #     schema=schema,
            #     company_id=company_id,
            #     roster_date_today=roster_date_today,
            #     days_back=days_back,
            #     employees=[night_emp, flex_emp_a, flex_emp_b],
            #     night_shift_id=night_shift.id,
            #     flex_shift_id=flex_shift.id,
            #     scenarios=scenarios,
            #     include_scenarios=include_scenarios,
            #     punch_created=created,
            #     daily_created=daily,
            # )

            # self.stdout.write(self.style.SUCCESS(f"Seed completed. Summary: {summary_txt_path}"))

    def _resolve_company(self, company_id: str) -> Optional[Company]:
        return Company.objects.filter(id=company_id).first()

    def _get_employee_by_code(self, company: Company, code: str) -> Employee:
        emp = Employee.objects.filter(company=company, employee_code=code).first()
        if not emp:
            raise RuntimeError(f"Employee not found for company={company.id}, code={code}")
        return emp

    def _get_shift_definition(self, company: Company, shift_id: str) -> ShiftDefinition:
        return ShiftDefinition.objects.filter(company=company, id=shift_id).first()  # type: ignore[return-value]

    def _tenant_today(self) -> date:
        # Uses Django timezone utilities; tenant timezone should be configured at DB level.
        return timezone.localdate()

    def _scenario_dates(self, days_back: int) -> Dict[str, List[date]]:
        """Assign scenario types to specific offsets from roster_date_today.

        We deterministically map scenario types to last 4 days (or fewer).
        """
        today = self._tenant_today()
        offsets = list(range(days_back + 1))  # 0..days_back

        def d(off: int) -> date:
            return today - timedelta(days=off)

        # Map:
        # - half-day leave: off=days_back (earliest seeded)
        # - short leave: off=days_back-1
        # - late login: off=1 (yesterday) if available else earliest
        # - early going: off=0 (today)
        scenarios: Dict[str, List[date]] = {}
        if days_back >= 0:
            scenarios["EARLY_GOING"] = [d(0)]
        if days_back >= 1:
            scenarios["LATE_LOGIN"] = [d(1)]
        if days_back >= 2:
            scenarios["SHORT_LEAVE"] = [d(2 if days_back >= 2 else 1)]
        if days_back >= 3:
            scenarios["HALF_DAY_LEAVE"] = [d(3)]
        else:
            # still seed half-day leave using earliest seeded date when days_back<3
            scenarios["HALF_DAY_LEAVE"] = [d(days_back)]

        return scenarios

    def _upsert_roster_for_emp(self, emp: Employee, shift: ShiftDefinition, roster_date: date) -> None:
        EmployeeShiftRoster.objects.update_or_create(
            company=emp.company,
            employee=emp,
            roster_date=roster_date,
            defaults={
                "shift": shift,
                # Keep cycle as-is if present; else leave empty? cycle is required in model.
                # We only adjust shift, but model requires cycle. We'll attempt to reuse
                # employee's active cycle from EmployeeAttendanceConfig.
                "cycle": self._get_emp_cycle(emp),
                "is_week_off": False,
                "override_reason": "seed_attendance_punch_logs_scenarios",
            },
        )

    def _get_emp_cycle(self, emp: Employee):
        cfg = EmployeeAttendanceConfig.objects.filter(company=emp.company, employee=emp, is_active=True).first()
        if not cfg:
            # fallback: any cycle from company's attendance cycle masters
            # To avoid importing more models, we derive from cfg; if missing, raise.
            raise RuntimeError(f"EmployeeAttendanceConfig missing for employee={emp.id}")
        return cfg.cycle

    def _build_punch_rows(
        self,
        company: Company,
        employees: List[Employee],
        roster_date_today: date,
        days_back: int,
        scenarios: Dict[str, List[date]],
        include_scenarios: bool,
        night_shift: ShiftDefinition,
        flex_shift: ShiftDefinition,
        seed: int,
    ) -> List[PunchLog]:
        rows: List[PunchLog] = []

        # Offsets for scenarios (minutes)
        LATE_MIN = 25
        SHORT_LEAVE_MIN = 60
        EARLY_EXIT_MIN = 45
        HALF_DAY_LEAVE_MIN = 240  # half-day work reduction logic (used only for daily)

        # Use deterministic variations
        base_rand = random.Random(seed)

        date_range = [roster_date_today - timedelta(days=i) for i in range(days_back + 1)]

        for emp in employees:
            roster_shift = self._resolve_shift_for_emp_today(emp, night_shift, flex_shift)

            for d in date_range:
                # Build IN/OUT for given shift
                # Determine scenario punch adjustments
                late_login = include_scenarios and d in scenarios.get("LATE_LOGIN", [])
                early_going = include_scenarios and d in scenarios.get("EARLY_GOING", [])
                short_leave = include_scenarios and d in scenarios.get("SHORT_LEAVE", [])
                half_day_leave = include_scenarios and d in scenarios.get("HALF_DAY_LEAVE", [])

                # Choose shift start/end
                if roster_shift.id == night_shift.id:
                    in_dt = datetime.combine(d, night_shift.start_time)
                    out_dt = datetime.combine(d, night_shift.end_time)
                    # cross-midnight: end_time is next day
                    if night_shift.cross_midnight or (night_shift.end_time <= night_shift.start_time):
                        out_dt = out_dt + timedelta(days=1)

                else:
                    in_dt = datetime.combine(d, flex_shift.start_time)
                    out_dt = datetime.combine(d, flex_shift.end_time)

                # Apply scenario offsets
                # Late login: push IN later
                if late_login:
                    in_dt = in_dt + timedelta(minutes=LATE_MIN)

                # Early going: pull OUT earlier
                if early_going:
                    out_dt = out_dt - timedelta(minutes=EARLY_EXIT_MIN)

                # Short leave: pull OUT earlier (but not as much)
                if short_leave:
                    out_dt = out_dt - timedelta(minutes=SHORT_LEAVE_MIN)

                # Half-day leave: push OUT earlier significantly (approx)
                if half_day_leave:
                    out_dt = out_dt - timedelta(minutes=HALF_DAY_LEAVE_MIN)

                # Add tiny deterministic jitter so punches look realistic.
                jitter_in = base_rand.randint(-5, 10)
                jitter_out = base_rand.randint(-10, 15)
                in_dt = in_dt + timedelta(minutes=jitter_in)
                out_dt = out_dt + timedelta(minutes=jitter_out)

                # Punch types
                in_type = PunchType.IN
                out_type = PunchType.OUT

                # Deterministic essl dedup IDs (avoid duplicates on rerun)
                # Must be unique per employee+date+type.
                essl_base = self._stable_essl_log_id(emp, d)

                # IN
                rows.append(
                    PunchLog(
                        company=company,
                        employee=emp,
                        punch_time=in_dt,
                        received_at=in_dt,
                        punch_type=in_type,
                        punch_source=PunchSource.BIOMETRIC,
                        source=SEEDED_SOURCE,
                        essl_log_id=essl_base,
                        essl_source_table=SEEDED_EH_SOURCE_TABLE,
                        is_trusted=True,
                        created_by=None,
                        raw_payload={"seed": True, "scenario": "IN"},
                        meta_data={"scenario_in": True, "date": str(d)},
                    )
                )
                # OUT
                rows.append(
                    PunchLog(
                        company=company,
                        employee=emp,
                        punch_time=out_dt,
                        received_at=out_dt,
                        punch_type=out_type,
                        punch_source=PunchSource.BIOMETRIC,
                        source=SEEDED_SOURCE,
                        essl_log_id=essl_base + 1,
                        essl_source_table=SEEDED_EH_SOURCE_TABLE,
                        is_trusted=True,
                        created_by=None,
                        raw_payload={"seed": True, "scenario": "OUT"},
                        meta_data={"scenario_out": True, "date": str(d)},
                    )
                )

        return rows

    def _resolve_shift_for_emp_today(self, emp: Employee, night_shift: ShiftDefinition, flex_shift: ShiftDefinition) -> ShiftDefinition:
        if emp.employee_code == EMPLOYEE_NIGHT_SHIFT_EMPLOYEE_CODE:
            return night_shift
        # default others to flexible
        return flex_shift

    def _stable_essl_log_id(self, emp: Employee, d: date) -> int:
        # Make a stable positive integer from uuid + date.
        # Not cryptographically strong; only needs deterministic uniqueness.
        base = abs(hash((str(emp.id), str(d))))
        return base % 9000000000

    def _bulk_upsert_punchlogs(self, punch_rows: List[PunchLog]) -> int:
        if not punch_rows:
            return 0

        # Upsert by unique constraint (essl_log_id, essl_source_table).
        # Django doesn't have native upsert for this easily without DB support;
        # we do a two-step: find existing, then bulk_create only missing.
        keys: List[Tuple[int, str]] = [(int(r.essl_log_id), str(r.essl_source_table)) for r in punch_rows]
        existing = set(
            PunchLog.objects.filter(
                essl_source_table=SEEDED_EH_SOURCE_TABLE,
                essl_log_id__in=[k[0] for k in keys],
            ).values_list("essl_log_id", "essl_source_table")
        )

        to_create: List[PunchLog] = []
        for r in punch_rows:
            k = (int(r.essl_log_id), str(r.essl_source_table))
            if k not in existing:
                to_create.append(r)

        if to_create:
            PunchLog.objects.bulk_create(to_create, batch_size=500)

        return len(to_create)

    # def _seed_daily_attendance_for_range(
    #     self,
    #     company: Company,
    #     employees: List[Employee],
    #     roster_date_today: date,
    #     days_back: int,
    #     scenarios: Dict[str, List[date]],
    #     include_scenarios: bool,
    #     night_shift: ShiftDefinition,
    #     flex_shift: ShiftDefinition,
    # ) -> List[DailyAttendance]:
    #     present = AttendanceStatus.objects.filter(code="PRESENT").first()
    #     if not present:
    #         # If statuses are missing, keep silent.
    #         return []

    #     work_mode = WorkMode.OFFICE
    #     daily_created: List[DailyAttendance] = []

    #     date_range = [roster_date_today - timedelta(days=i) for i in range(days_back + 1)]

    #     for emp in employees:
    #         shift = night_shift if emp.employee_code == EMPLOYEE_NIGHT_SHIFT_EMPLOYEE_CODE else flex_shift
