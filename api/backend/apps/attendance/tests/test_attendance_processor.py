"""
Edge-case tests for session-based attendance processing.

Covers:
- punch_bucketer session/anomaly building
- process_employee_date end-to-end (sessions, exceptions, comp-off, lock guard)
"""

from datetime import date, datetime, time, timedelta

import pytz
from django_tenants.test.cases import TenantTestCase

from apps.attendance.models import (
    AttendanceCycle,
    AttendanceException,
    AttendancePolicy,
    AttendanceStatus,
    DailyAttendance,
    DailyAttendanceSession,
    ExceptionType,
    PunchLog,
    ShiftDefinition,
)
from apps.attendance.models.configuration import EmployeeAttendanceConfig, EmployeeShiftRoster
from apps.attendance.models.enums import FinalizationStatus, PunchSource, PunchType
from apps.attendance.models.masters.office_location import AttendanceOfficeLocation
from apps.attendance.services.attendance_processor import process_employee_date
from apps.attendance.utils.punch_bucketer import bucket_punches
from apps.attendance.utils.shift_window import build_shift_window
from apps.employees.models import Company, Employee, Gender
from apps.leave.models.request_modules.comp_off import (
    CompOffRequest,
    CompOffStatusChoices,
    EarnedAgainstTypeChoices,
)


# ---------------------------------------------------------------------------
# Test constants
# ---------------------------------------------------------------------------

TIMEZONE = "Asia/Kolkata"
COMPANY_CODE = "ATT_PROC_CO"
COMPANY_NAME = "Attendance Processor Test Co"
EMPLOYEE_CODE = "ATTEMP001"

# Fixed dates keep tests deterministic (Wednesday / Thursday / Friday 2026)
DATE_WORKING = date(2026, 5, 28)
DATE_WEEK_OFF = date(2026, 5, 29)
DATE_LOCKED = date(2026, 5, 30)
DATE_REPROCESS = date(2026, 6, 1)

SHIFT_START = time(9, 0)
SHIFT_END = time(18, 0)
SHIFT_TOTAL_MINS = 540
SHIFT_FULL_DAY_MINS = 480
SHIFT_HALF_DAY_MINS = 240
SHIFT_OT_AFTER_MINS = 60


def punch_datetime(attendance_date: date, hour: int, minute: int = 0) -> datetime:
    """Build a timezone-aware punch timestamp in IST."""
    tz = pytz.timezone(TIMEZONE)
    return tz.localize(datetime.combine(attendance_date, time(hour, minute)))


class AttendanceProcessorEdgeCaseTestCase(TenantTestCase):
    """Session-based attendance processor and bucketer edge cases."""

    @classmethod
    def setup_tenant(cls, tenant):
        tenant.company_name = "Attendance Processor Tenant"
        tenant.slug = "attproc"
        tenant.schema_name = "attproc"

    @classmethod
    def setup_domain(cls, domain):
        domain.domain = "attproc.localhost"

    # @classmethod
    # def setUpTestData(cls):
    #     print(">>> setUpTestData called")
    #     cls.company = Company.objects.create(name=COMPANY_NAME, code=COMPANY_CODE)
    #     cls.gender = Gender.objects.create(code="M", label="Male")

    #     cls.employee = Employee.objects.create(
    #         first_name="Session",
    #         last_name="Tester",
    #         employee_code=EMPLOYEE_CODE,
    #         company=cls.company,
    #         gender=cls.gender,
    #         date_of_joining=date(2020, 1, 1),
    #         date_of_birth=date(1990, 1, 1),
    #         is_active=True,
    #     )

    #     cls.policy = AttendancePolicy.objects.create(
    #         company=cls.company,
    #         name="Processor Test Policy",
    #         is_current=True,
    #         late_login_cycle_limit=3,
    #         late_login_grace_mins=0,
    #         late_login_max_grace_mins=15,
    #         early_exit_max_grace_mins=15,
    #         short_leave_max_mins=120,
    #         monthly_grace_instance_limit=2,
    #         half_day_min_mins=SHIFT_HALF_DAY_MINS,
    #         full_day_min_mins=SHIFT_FULL_DAY_MINS,
    #         ot_enabled=True,
    #         ot_min_mins=SHIFT_OT_AFTER_MINS,
    #         lop_deduction_unit="1.00",
    #     )

    #     cls.shift = ShiftDefinition.objects.create(
    #         company=cls.company,
    #         name="General 9-6",
    #         code="GEN_9_6",
    #         shift_type="FIXED",
    #         start_time=SHIFT_START,
    #         end_time=SHIFT_END,
    #         total_mins=SHIFT_TOTAL_MINS,
    #         grace_mins=0,
    #         half_day_mins=SHIFT_HALF_DAY_MINS,
    #         full_day_mins=SHIFT_FULL_DAY_MINS,
    #         ot_after_mins=SHIFT_OT_AFTER_MINS,
    #         early_punch_buffer_mins=60,
    #         late_punch_buffer_mins=120,
    #     )

    #     cls.cycle = AttendanceCycle.objects.create(
    #         company=cls.company,
    #         name="Calendar Month",
    #         cycle_start_day=1,
    #         is_default=True,
    #     )

    #     cls.location = AttendanceOfficeLocation.objects.create(
    #         company=cls.company,
    #         name="HQ",
    #         code="HQ",
    #         timezone=TIMEZONE,
    #     )

    #     cls.config = EmployeeAttendanceConfig.objects.create(
    #         company=cls.company,
    #         employee=cls.employee,
    #         policy=cls.policy,
    #         shift=cls.shift,
    #         cycle=cls.cycle,
    #         location=cls.location,
    #         effective_from=date(2020, 1, 1),
    #     )

    #     status_defs = [
    #         ("PRESENT", "Present", True),
    #         ("ABSENT", "Absent", False),
    #         ("HALF_DAY", "Half Day", True),
    #         ("IN_PROGRESS", "In Progress", False),
    #         ("WEEK_OFF", "Week Off", True),
    #         ("HOLIDAY", "Holiday", True),
    #     ]
    #     for code, name, is_paid in status_defs:
    #         AttendanceStatus.objects.create(
    #             code=code,
    #             name=name,
    #             is_paid=is_paid,
    #             is_present_equivalent=code == "PRESENT",
    #         )

    #     for code, label in (
    #         ("MISSING_IN", "Missing Check In"),
    #         ("MISSING_OUT", "Missing Check Out"),
    #     ):
    #         ExceptionType.objects.create(code=code, label=label, auto_flag=True)

    def setUp(self):
        print(">>> setUp called")
        print(hasattr(self, "employee"))

        print(">>> setUpTestData called")
        self.company = Company.objects.create(name=COMPANY_NAME, code=COMPANY_CODE)
        self.gender = Gender.objects.create(code="M", label="Male")

        self.employee = Employee.objects.create(
            first_name="Session",
            last_name="Tester",
            employee_code=EMPLOYEE_CODE,
            company=self.company,
            gender=self.gender,
            date_of_joining=date(2020, 1, 1),
            date_of_birth=date(1990, 1, 1),
            is_active=True,
        )

        self.policy = AttendancePolicy.objects.create(
            company=self.company,
            name="Processor Test Policy",
            is_current=True,
            late_login_cycle_limit=3,
            late_login_grace_mins=0,
            late_login_max_grace_mins=15,
            early_exit_max_grace_mins=15,
            short_leave_max_mins=120,
            monthly_grace_instance_limit=2,
            half_day_min_mins=SHIFT_HALF_DAY_MINS,
            full_day_min_mins=SHIFT_FULL_DAY_MINS,
            ot_enabled=True,
            ot_min_mins=SHIFT_OT_AFTER_MINS,
            lop_deduction_unit="1.00",
        )

        self.shift = ShiftDefinition.objects.create(
            company=self.company,
            name="General 9-6",
            code="GEN_9_6",
            shift_type="FIXED",
            start_time=SHIFT_START,
            end_time=SHIFT_END,
            total_mins=SHIFT_TOTAL_MINS,
            grace_mins=0,
            half_day_mins=SHIFT_HALF_DAY_MINS,
            full_day_mins=SHIFT_FULL_DAY_MINS,
            ot_after_mins=SHIFT_OT_AFTER_MINS,
            early_punch_buffer_mins=60,
            late_punch_buffer_mins=120,
        )

        self.cycle = AttendanceCycle.objects.create(
            company=self.company,
            name="Calendar Month",
            cycle_start_day=1,
            is_default=True,
        )

        self.location = AttendanceOfficeLocation.objects.create(
            company=self.company,
            name="HQ",
            code="HQ",
            timezone=TIMEZONE,
        )

        self.config = EmployeeAttendanceConfig.objects.create(
            company=self.company,
            employee=self.employee,
            policy=self.policy,
            shift=self.shift,
            cycle=self.cycle,
            location=self.location,
            effective_from=date(2020, 1, 1),
        )

        status_defs = [
            ("PRESENT", "Present", True),
            ("ABSENT", "Absent", False),
            ("HALF_DAY", "Half Day", True),
            ("IN_PROGRESS", "In Progress", False),
            ("WEEK_OFF", "Week Off", True),
            ("HOLIDAY", "Holiday", True),
        ]
        for code, name, is_paid in status_defs:
            AttendanceStatus.objects.create(
                code=code,
                name=name,
                is_paid=is_paid,
                is_present_equivalent=code == "PRESENT",
            )

        for code, label in (
            ("MISSING_IN", "Missing Check In"),
            ("MISSING_OUT", "Missing Check Out"),
        ):
            ExceptionType.objects.create(code=code, label=label, auto_flag=True)


        PunchLog.objects.filter(employee=self.employee).delete()
        DailyAttendanceSession.objects.filter(
            attendance__employee=self.employee,
        ).delete()
        AttendanceException.objects.filter(employee=self.employee).delete()
        CompOffRequest.objects.filter(employee=self.employee).delete()
        EmployeeShiftRoster.objects.filter(employee=self.employee).delete()
        DailyAttendance.objects.filter(employee=self.employee).delete()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _create_punch(self, attendance_date, hour, minute, punch_type):
        return PunchLog.objects.create(
            company=self.company,
            employee=self.employee,
            punch_time=punch_datetime(attendance_date, hour, minute),
            punch_type=punch_type,
            punch_source=PunchSource.BIOMETRIC,
        )

    def _bucket(self, attendance_date):
        window = build_shift_window(self.shift, attendance_date, TIMEZONE)

        print("WINDOW START:", window.window_start)
        print("WINDOW END:", window.window_end)

        punch_count = PunchLog.objects.filter(employee=self.employee).count()
        print("PUNCH COUNT:", punch_count)
        print("ALL PUNCH TYPES:", list(PunchLog.objects.filter(employee=self.employee).values_list("punch_type", flat=True)))
        print("EMPLOYEE ID:", self.employee.id)

        print(
            list(
                PunchLog.objects.filter(employee=self.employee)
                .values("punch_time", "punch_type")
            )
        )

        # Debug: ensure bucketer filter inputs match stored punch timestamps
        window_start = window.window_start
        window_end = window.window_end

        punch_qs = PunchLog.objects.filter(employee=self.employee).order_by("punch_time")
        print("PUNCH TIMES (raw):")
        for p in punch_qs:
            print("  ", p.punch_time, "type=", getattr(p, "punch_type", None))

        # Show which punches match the window bounds as-is
        matching = list(
            punch_qs.filter(punch_time__gte=window_start, punch_time__lte=window_end).values(
                "punch_time", "punch_type"
            )
        )
        print("PUNCHES MATCHING WINDOW (as-is):", matching)

        summary = bucket_punches(
            self.employee.id,
            window.window_start,
            window.window_end,
        )

        print("BUCKET SUMMARY:")
        print("  has_any_punch=", summary.has_any_punch)
        print("  valid_punches_len=", len(summary.valid_punches))
        print("  sessions_len=", len(summary.sessions))
        print("  first_in=", summary.first_in, "last_out=", summary.last_out)
        print("  is_currently_in=", summary.is_currently_in)
        print("  anomalies=", summary.anomalies)

        return summary

    def _process(self, attendance_date, force=False):
        return process_employee_date(self.employee.id, attendance_date, force=force)

    def _attendance(self, attendance_date):
        return DailyAttendance.objects.get(
            employee=self.employee,
            attendance_date=attendance_date,
        )

    def _sessions(self, attendance_date):
        attendance = self._attendance(attendance_date)
        return list(
            DailyAttendanceSession.objects.filter(
                attendance=attendance,
                deleted_at__isnull=True,
            ).order_by("session_no")
        )

    def _unresolved_exception_codes(self, attendance_date):
        attendance = self._attendance(attendance_date)
        return set(
            AttendanceException.objects.filter(
                attendance=attendance,
                is_resolved=False,
            ).values_list("exception_type__code", flat=True)
        )

    # ------------------------------------------------------------------
    # Punch bucketer edge cases
    # ------------------------------------------------------------------

    def test_bucketer_single_session(self):
        self._create_punch(DATE_WORKING, 9, 0, PunchType.IN)
        self._create_punch(DATE_WORKING, 18, 0, PunchType.OUT)

        summary = self._bucket(DATE_WORKING)

        self.assertEqual(len(summary.sessions), 1)
        self.assertEqual(summary.session_work_mins, 540)
        self.assertEqual(summary.short_leave_mins, 0)
        self.assertFalse(summary.is_currently_in)
        self.assertEqual(summary.anomalies, [])

    def test_bucketer_multiple_sessions_with_break(self):
        self._create_punch(DATE_WORKING, 9, 0, PunchType.IN)
        self._create_punch(DATE_WORKING, 12, 0, PunchType.OUT)
        self._create_punch(DATE_WORKING, 13, 0, PunchType.IN)
        self._create_punch(DATE_WORKING, 18, 0, PunchType.OUT)

        summary = self._bucket(DATE_WORKING)

        self.assertEqual(len(summary.sessions), 2)
        self.assertEqual(summary.session_work_mins, 480)
        self.assertEqual(summary.short_leave_mins, 60)
        self.assertEqual(summary.sessions[0].work_mins, 180)
        self.assertEqual(summary.sessions[1].work_mins, 300)
        self.assertEqual(summary.sessions[1].break_mins, 60)

    def test_bucketer_in_only_open_session(self):
        self._create_punch(DATE_WORKING, 9, 0, PunchType.IN)

        summary = self._bucket(DATE_WORKING)

        self.assertTrue(summary.is_currently_in)
        self.assertEqual(summary.session_work_mins, 0)
        codes = {item["code"] for item in summary.anomalies}
        self.assertIn("MISSING_OUT", codes)

    def test_bucketer_out_only_missing_in(self):
        self._create_punch(DATE_WORKING, 10, 0, PunchType.OUT)

        summary = self._bucket(DATE_WORKING)

        self.assertIsNone(summary.first_in)
        self.assertIsNotNone(summary.last_out)
        self.assertEqual(summary.sessions, [])
        codes = {item["code"] for item in summary.anomalies}
        self.assertIn("MISSING_IN", codes)

    def test_bucketer_duplicate_in_then_out(self):
        self._create_punch(DATE_WORKING, 9, 0, PunchType.IN)
        self._create_punch(DATE_WORKING, 9, 30, PunchType.IN)
        self._create_punch(DATE_WORKING, 18, 0, PunchType.OUT)

        summary = self._bucket(DATE_WORKING)

        self.assertEqual(len(summary.sessions), 1)
        self.assertEqual(summary.session_work_mins, 540)
        codes = {item["code"] for item in summary.anomalies}
        self.assertIn("DUPLICATE_IN", codes)

    def test_bucketer_in_out_out_extra_out(self):
        self._create_punch(DATE_WORKING, 9, 0, PunchType.IN)
        self._create_punch(DATE_WORKING, 18, 0, PunchType.OUT)
        self._create_punch(DATE_WORKING, 18, 5, PunchType.OUT)

        summary = self._bucket(DATE_WORKING)

        self.assertEqual(len(summary.sessions), 1)
        self.assertEqual(summary.session_work_mins, 540)
        codes = {item["code"] for item in summary.anomalies}
        self.assertIn("MISSING_IN", codes)

    def test_bucketer_deduplicates_same_type_within_threshold(self):
        self._create_punch(DATE_WORKING, 9, 0, PunchType.IN)
        self._create_punch(DATE_WORKING, 9, 1, PunchType.IN)
        self._create_punch(DATE_WORKING, 18, 0, PunchType.OUT)

        summary = self._bucket(DATE_WORKING)

        self.assertEqual(len(summary.valid_punches), 2)
        print("VALID PUNCHES COUNT:", len(summary.valid_punches))
        self.assertEqual(len(summary.sessions), 1)

    def test_bucketer_no_punches(self):
        summary = self._bucket(DATE_WORKING)

        self.assertFalse(summary.has_any_punch)
        self.assertEqual(summary.sessions, [])
        self.assertEqual(summary.anomalies, [])

    # ------------------------------------------------------------------
    # Processor end-to-end edge cases
    # ------------------------------------------------------------------

    def test_processor_no_punches_marks_absent(self):
        result = self._process(DATE_WORKING)

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, "ABSENT")
        attendance = self._attendance(DATE_WORKING)
        self.assertEqual(attendance.actual_work_mins, 0)
        self.assertEqual(self._sessions(DATE_WORKING), [])

    def test_processor_single_session_present(self):
        self._create_punch(DATE_WORKING, 9, 0, PunchType.IN)
        self._create_punch(DATE_WORKING, 18, 0, PunchType.OUT)

        result = self._process(DATE_WORKING)

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, "PRESENT")
        self.assertEqual(result.actual_work_mins, 540)

        attendance = self._attendance(DATE_WORKING)
        self.assertEqual(attendance.actual_work_mins, 540)
        self.assertEqual(attendance.short_leave_mins, 0)
        self.assertEqual(attendance.rounded_pay_mins, 540)

        sessions = self._sessions(DATE_WORKING)
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].work_mins, 540)

    def test_processor_multiple_sessions(self):
        self._create_punch(DATE_WORKING, 9, 0, PunchType.IN)
        self._create_punch(DATE_WORKING, 12, 0, PunchType.OUT)
        self._create_punch(DATE_WORKING, 13, 0, PunchType.IN)
        self._create_punch(DATE_WORKING, 18, 0, PunchType.OUT)

        result = self._process(DATE_WORKING)

        self.assertTrue(result.success)
        self.assertEqual(result.actual_work_mins, 480)

        attendance = self._attendance(DATE_WORKING)
        self.assertEqual(attendance.short_leave_mins, 60)
        self.assertEqual(len(self._sessions(DATE_WORKING)), 2)

    def test_processor_in_only_in_progress_and_missing_out_exception(self):
        self._create_punch(DATE_WORKING, 9, 0, PunchType.IN)

        result = self._process(DATE_WORKING)

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, "IN_PROGRESS")

        attendance = self._attendance(DATE_WORKING)
        self.assertTrue(attendance.is_currently_in)
        self.assertIsNone(attendance.last_out)

        sessions = self._sessions(DATE_WORKING)
        self.assertEqual(len(sessions), 1)
        self.assertIsNone(sessions[0].out_time)

        self.assertEqual(self._unresolved_exception_codes(DATE_WORKING), {"MISSING_OUT"})

    def test_processor_out_only_creates_missing_in_without_crash(self):
        self._create_punch(DATE_WORKING, 10, 0, PunchType.OUT)

        result = self._process(DATE_WORKING)

        self.assertTrue(result.success)
        self.assertEqual(self._unresolved_exception_codes(DATE_WORKING), {"MISSING_IN"})
        self.assertEqual(self._sessions(DATE_WORKING), [])

    def test_processor_reprocess_resolves_missing_out(self):
        self._create_punch(DATE_REPROCESS, 9, 0, PunchType.IN)
        self._process(DATE_REPROCESS)
        self.assertEqual(self._unresolved_exception_codes(DATE_REPROCESS), {"MISSING_OUT"})

        self._create_punch(DATE_REPROCESS, 18, 0, PunchType.OUT)
        result = self._process(DATE_REPROCESS)

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, "PRESENT")
        self.assertEqual(self._unresolved_exception_codes(DATE_REPROCESS), set())

    def test_processor_sessions_rebuilt_on_reprocess(self):
        self._create_punch(DATE_REPROCESS, 9, 0, PunchType.IN)
        self._create_punch(DATE_REPROCESS, 12, 0, PunchType.OUT)
        self._process(DATE_REPROCESS)

        first_session_ids = {str(s.id) for s in self._sessions(DATE_REPROCESS)}
        self.assertEqual(len(first_session_ids), 1)

        self._create_punch(DATE_REPROCESS, 13, 0, PunchType.IN)
        self._create_punch(DATE_REPROCESS, 18, 0, PunchType.OUT)
        self._process(DATE_REPROCESS)

        active_sessions = self._sessions(DATE_REPROCESS)
        self.assertEqual(len(active_sessions), 2)
        self.assertTrue(all(str(s.id) not in first_session_ids for s in active_sessions))

        soft_deleted = DailyAttendanceSession.objects.filter(
            attendance__employee=self.employee,
            attendance__attendance_date=DATE_REPROCESS,
            deleted_at__isnull=False,
        ).count()
        self.assertEqual(soft_deleted, 1)

    def test_processor_ot_uses_shift_fallback(self):
        # 9:00 → 19:00 = 600 mins; full_day=480 → excess=120 >= ot_after=60
        self._create_punch(DATE_WORKING, 9, 0, PunchType.IN)
        self._create_punch(DATE_WORKING, 19, 0, PunchType.OUT)

        result = self._process(DATE_WORKING)

        self.assertTrue(result.success)
        self.assertEqual(result.ot_mins, 120)
        self.assertEqual(self._attendance(DATE_WORKING).ot_mins, 120)

    def test_processor_locked_row_skipped_without_force(self):
        DailyAttendance.objects.create(
            company=self.company,
            employee=self.employee,
            attendance_date=DATE_LOCKED,
            shift=self.shift,
            policy=self.policy,
            status=AttendanceStatus.objects.get(code="PRESENT"),
            actual_work_mins=999,
            finalization_status=FinalizationStatus.LOCKED,
        )
        self._create_punch(DATE_LOCKED, 9, 0, PunchType.IN)
        self._create_punch(DATE_LOCKED, 18, 0, PunchType.OUT)

        result = self._process(DATE_LOCKED, force=False)

        self.assertTrue(result.success)
        self.assertTrue(result.skipped)
        self.assertEqual(self._attendance(DATE_LOCKED).actual_work_mins, 999)

    def test_processor_locked_row_reprocessed_with_force(self):
        DailyAttendance.objects.create(
            company=self.company,
            employee=self.employee,
            attendance_date=DATE_LOCKED,
            shift=self.shift,
            policy=self.policy,
            status=AttendanceStatus.objects.get(code="PRESENT"),
            actual_work_mins=999,
            finalization_status=FinalizationStatus.LOCKED,
        )
        self._create_punch(DATE_LOCKED, 9, 0, PunchType.IN)
        self._create_punch(DATE_LOCKED, 18, 0, PunchType.OUT)

        result = self._process(DATE_LOCKED, force=True)

        self.assertTrue(result.success)
        self.assertFalse(result.skipped)
        self.assertEqual(result.actual_work_mins, 540)
        self.assertEqual(self._attendance(DATE_LOCKED).actual_work_mins, 540)

    def test_processor_week_off_with_punches_keeps_status_and_creates_comp_off(self):
        EmployeeShiftRoster.objects.create(
            company=self.company,
            employee=self.employee,
            shift=self.shift,
            cycle=self.cycle,
            roster_date=DATE_WEEK_OFF,
            is_week_off=True,
        )
        self._create_punch(DATE_WEEK_OFF, 9, 0, PunchType.IN)
        self._create_punch(DATE_WEEK_OFF, 18, 0, PunchType.OUT)

        result = self._process(DATE_WEEK_OFF)

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, "WEEK_OFF")
        self.assertEqual(result.actual_work_mins, 540)

        attendance = self._attendance(DATE_WEEK_OFF)
        self.assertEqual(attendance.status.code, "WEEK_OFF")
        self.assertEqual(attendance.actual_work_mins, 540)
        self.assertEqual(len(self._sessions(DATE_WEEK_OFF)), 1)

        comp_off = CompOffRequest.objects.get(
            employee=self.employee,
            worked_date=DATE_WEEK_OFF,
        )
        self.assertEqual(comp_off.status, CompOffStatusChoices.PENDING)
        self.assertEqual(
            comp_off.earned_against_date_type,
            EarnedAgainstTypeChoices.WEEKEND,
        )

    def test_processor_week_off_without_punches_has_no_comp_off(self):
        EmployeeShiftRoster.objects.create(
            company=self.company,
            employee=self.employee,
            shift=self.shift,
            cycle=self.cycle,
            roster_date=DATE_WEEK_OFF,
            is_week_off=True,
        )

        result = self._process(DATE_WEEK_OFF)

        self.assertTrue(result.success)
        self.assertEqual(result.status_code, "WEEK_OFF")
        self.assertFalse(
            CompOffRequest.objects.filter(
                employee=self.employee,
                worked_date=DATE_WEEK_OFF,
            ).exists()
        )

    def test_processor_policy_snapshot_preserved_on_write(self):
        self._create_punch(DATE_WORKING, 9, 0, PunchType.IN)
        self._create_punch(DATE_WORKING, 18, 0, PunchType.OUT)

        self._process(DATE_WORKING)

        attendance = self._attendance(DATE_WORKING)
        self.assertEqual(attendance.policy_id, self.policy.id)

        self.policy.is_current = False
        self.policy.save(update_fields=["is_current"])

        attendance.refresh_from_db()
        self.assertEqual(attendance.policy_id, self.policy.id)
