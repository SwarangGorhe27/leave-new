"""
================================================================================
SEED FILE: Leave Module Full Seed
================================================================================

Run:
-----
python manage.py shell < leave_module_seed.py

OR

python leave_module_seed.py

================================================================================
"""

import os
import sys
import django
from datetime import date, datetime, timedelta, timezone

# -----------------------------------------------------------------------------
# DJANGO SETUP
# -----------------------------------------------------------------------------

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

from django.db import transaction
from django_tenants.utils import schema_context

from apps.employees.models import (
    Employee,
    EmployeeType,
    Grade,
    Branch,
    HolidayCalendar,
    Holiday,
)

from apps.leave.models import (
    CalendarPeriod,
    LeaveType,
    LeavePolicy,
    LeavePolicyRule,
    EmployeeLeavePolicy,
    AccrualSchedule,
    LeaveEncashmentPolicy,
    Reason,
    ApprovalWorkflowConfig,
    EscalationMatrix,
    LeaveBalance,
    LeaveBalanceLedger,
    LeaveRequest,
    LeaveRequestDay,
    LeaveApproval,
    LeaveStatusHistory,
    LeaveComment,
    LeaveDocument,
    LeaveCancellationRequest,
    LeaveResubmissionHistory,
    EmployeeLeaveRequestCC,
    LeaveDelegation,
    LeaveEncashmentRequest,
    AccrualTransactionLog,
    LeaveSessionChoices,
)

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------

def p(msg):
    print(f"✔ {msg}")


def section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


# -----------------------------------------------------------------------------
# MAIN SEED
# -----------------------------------------------------------------------------

@transaction.atomic
def run_seed():

    with schema_context("acme"):

        # =========================================================================
        # EMPLOYEES
        # =========================================================================

        section("EMPLOYEES")

        hr_manager = Employee.objects.get(employee_code="EMP001")
        manager = Employee.objects.get(employee_code="EMP002")
        employee = Employee.objects.get(employee_code="EMP001")
        employee2 = Employee.objects.get(employee_code="EMP003")

        p(f"HR Manager  : {hr_manager}")
        p(f"Manager     : {manager}")
        p(f"Employee 1  : {employee}")
        p(f"Employee 2  : {employee2}")

        # =========================================================================
        # HOLIDAYS
        # =========================================================================

        section("HOLIDAYS")

        holiday_calendar = HolidayCalendar.objects.get(
            id="0f3e3870-34d6-4e60-846c-0e04a5fc5652"
        )

        republic_day = Holiday.objects.get(
            id="3a6c3c9b-3f56-4cd9-a091-dfcfb46245d7"
        )

        p(f"Holiday Calendar : {holiday_calendar}")
        p(f"Holiday           : {republic_day}")

        # =========================================================================
        # CALENDAR PERIOD
        # =========================================================================

        section("CALENDAR PERIOD")

        calendar_period, _ = CalendarPeriod.objects.get_or_create(
            period_type="fiscal",
            year_start_month=4,
            year_start_day=1,
            defaults={
                "cf_reset_date": date(2026, 4, 1),
                "accrual_start_month": 4,
                "encashment_cycle": "annual",
                "is_active": True,
            },
        )

        p(f"CalendarPeriod : {calendar_period}")

        # =========================================================================
        # LEAVE TYPES
        # =========================================================================

        section("LEAVE TYPES")

        leave_types_data = [
            {
                "code": "CL",
                "name": "Casual Leave",
                "max_days_per_year": 12,
                "max_consecutive_days": 3,
                "carry_forward_enabled": False,
                "encashable": False,
                "requires_attachment": False,
                "min_notice_days": 0,
                "applicable_gender": "all",
                "is_paid": True,
                "allow_half_day": True,
                "allow_hourly": False,
                "backdate_allowed_days": 2,
                "future_apply_cap_days": 30,
                "leave_year_type": "fiscal",
                "color_code": "#4CAF50",
            },
            {
                "code": "SL",
                "name": "Sick Leave",
                "max_days_per_year": 10,
                "max_consecutive_days": None,
                "carry_forward_enabled": False,
                "encashable": False,
                "requires_attachment": True,
                "attachment_threshold_days": 2,
                "min_notice_days": 0,
                "applicable_gender": "all",
                "is_paid": True,
                "allow_half_day": True,
                "allow_hourly": False,
                "backdate_allowed_days": 3,
                "leave_year_type": "fiscal",
                "color_code": "#F44336",
            },
            {
                "code": "PL",
                "name": "Privilege Leave",
                "max_days_per_year": 18,
                "max_consecutive_days": 15,
                "carry_forward_enabled": True,
                "max_carry_forward_days": 10,
                "encashable": True,
                "requires_attachment": False,
                "min_notice_days": 3,
                "applicable_gender": "all",
                "is_paid": True,
                "allow_half_day": True,
                "allow_hourly": False,
                "backdate_allowed_days": 0,
                "future_apply_cap_days": 90,
                "leave_year_type": "fiscal",
                "color_code": "#2196F3",
            },
        ]

        leave_type_objs = {}

        for data in leave_types_data:

            code = data.pop("code")

            obj, _ = LeaveType.objects.get_or_create(
                code=code,
                defaults=data,
            )

            leave_type_objs[code] = obj

            p(f"LeaveType : {obj}")

        lt_cl = leave_type_objs["CL"]
        lt_sl = leave_type_objs["SL"]
        lt_pl = leave_type_objs["PL"]

        # =========================================================================
        # LEAVE POLICY
        # =========================================================================

        section("LEAVE POLICY")

        policy, _ = LeavePolicy.objects.get_or_create(
            name="Corporate Employees Leave Policy 2026",
            defaults={
                "description": "Standard leave policy for FY 2026-27",
                "effective_from": date(2026, 4, 1),
                "effective_to": date(2027, 3, 31),
                "is_active": True,
                "version": 1,
            },
        )

        p(f"LeavePolicy : {policy}")

        # =========================================================================
        # POLICY RULES
        # =========================================================================

        section("LEAVE POLICY RULES")

        policy_rules_data = [
            {
                "leave_type": lt_cl,
                "probation_restricted": True,
                "notice_period_restricted": True,
                "sandwich_policy_enabled": True,
                "min_service_days": 90,
                "max_leaves_per_month": 2,
                "max_leaves_per_quarter": 4,
                "min_gap_between_leaves_days": 7,
                "accrual_enabled": False,
                "allow_negative_balance": False,
            },
            {
                "leave_type": lt_sl,
                "probation_restricted": False,
                "notice_period_restricted": False,
                "sandwich_policy_enabled": False,
                "min_service_days": 0,
                "accrual_enabled": False,
                "allow_negative_balance": False,
            },
            {
                "leave_type": lt_pl,
                "probation_restricted": True,
                "notice_period_restricted": True,
                "sandwich_policy_enabled": True,
                "min_service_days": 180,
                "accrual_enabled": True,
                "accrual_frequency": "monthly",
                "accrual_days": 1.5,
                "allow_negative_balance": False,
            },
        ]

        policy_rule_objs = {}

        for data in policy_rules_data:

            leave_type = data["leave_type"]

            obj, _ = LeavePolicyRule.objects.get_or_create(
                policy=policy,
                leave_type=leave_type,
                grade=None,
                employee_type=None,
                defaults=data,
            )

            policy_rule_objs[leave_type.code] = obj

            p(f"LeavePolicyRule : {obj}")

        rule_cl = policy_rule_objs["CL"]
        rule_sl = policy_rule_objs["SL"]
        rule_pl = policy_rule_objs["PL"]

        # =========================================================================
        # EMPLOYEE LEAVE POLICY
        # =========================================================================

        section("EMPLOYEE LEAVE POLICY")

        for emp in [employee, employee2, manager, hr_manager]:

            obj, _ = EmployeeLeavePolicy.objects.get_or_create(
                employee=emp,
                policy=policy,
                effective_from=date(2026, 4, 1),
                defaults={
                    "effective_to": date(2027, 3, 31)
                },
            )

            p(f"EmployeeLeavePolicy : {obj}")

        # =========================================================================
        # ACCRUAL SCHEDULE
        # =========================================================================

        section("ACCRUAL SCHEDULE")

        accrual_schedule, _ = AccrualSchedule.objects.get_or_create(
            policy_rule=rule_pl,
            defaults={
                "frequency": "monthly",
                "run_day_of_month": 1,
                "proration_on_join": True,
                "rounding_rule": "FLOOR",
                "is_active": True,
            },
        )

        p(f"AccrualSchedule : {accrual_schedule}")

        # =========================================================================
        # LEAVE BALANCES
        # =========================================================================

        section("LEAVE BALANCES")

        balance_configs = [
            (employee, lt_cl, 12, 0, 0, 0),
            (employee, lt_sl, 10, 0, 0, 0),
            (employee, lt_pl, 0, 6, 5, 1),
            (employee2, lt_cl, 12, 0, 0, 0),
            (employee2, lt_sl, 10, 0, 0, 0),
            (employee2, lt_pl, 0, 4.5, 3, 0.5),
        ]

        for emp, lt, allocated, accrued, carried, used in balance_configs:

            obj, _ = LeaveBalance.objects.get_or_create(
                employee=emp,
                leave_type=lt,
                year=2026,
                defaults={
                    "leave_year_start": date(2026, 4, 1),
                    "leave_year_end": date(2027, 3, 31),
                    "allocated_days": allocated,
                    "accrued_days": accrued,
                    "carried_forward": carried,
                    "used_days": used,
                    "pending_days": 0,
                    "encashed_days": 0,
                    "lapsed_days": 0,
                },
            )

            p(f"LeaveBalance : {obj}")

        # =========================================================================
        # LEAVE REQUESTS
        # =========================================================================

        section("LEAVE REQUESTS")

        lr_pending, _ = LeaveRequest.objects.get_or_create(
            employee=employee,
            leave_type=lt_cl,
            from_date=date(2026, 5, 26),
            to_date=date(2026, 5, 28),
            defaults={
                "policy": policy,
                "policy_rule": rule_cl,
                "from_session": LeaveSessionChoices.FIRST_HALF,
                "to_session": LeaveSessionChoices.SECOND_HALF,
                "total_days": 3,
                "reason": "Family function",
                "status": "pending",
                "application_source": "web",
            },
        )

        p(f"Pending LeaveRequest : {lr_pending}")

        lr_approved, _ = LeaveRequest.objects.get_or_create(
            employee=employee,
            leave_type=lt_sl,
            from_date=date(2026, 5, 12),
            to_date=date(2026, 5, 13),
            defaults={
                "policy": policy,
                "policy_rule": rule_sl,
                "from_session": LeaveSessionChoices.FIRST_HALF,
                "to_session": LeaveSessionChoices.SECOND_HALF,
                "total_days": 2,
                "reason": "Medical leave",
                "status": "approved",
                "application_source": "mobile",
            },
        )

        p(f"Approved LeaveRequest : {lr_approved}")

        # =========================================================================
        # LEAVE APPROVALS
        # =========================================================================

        section("LEAVE APPROVALS")

        now = datetime.now(tz=timezone.utc)

        approvals_data = [
            {
                "leave_request": lr_pending,
                "approver": manager,
                "approval_level": 1,
                "status": "pending",
                "sla_deadline": now + timedelta(hours=48),
            },
            {
                "leave_request": lr_approved,
                "approver": manager,
                "approval_level": 1,
                "status": "approved",
                "remarks": "Approved",
                "actioned_at": now - timedelta(days=2),
            },
        ]

        for data in approvals_data:

            obj, _ = LeaveApproval.objects.get_or_create(
                leave_request=data["leave_request"],
                approval_level=data["approval_level"],
                approver=data["approver"],
                defaults=data,
            )

            p(f"LeaveApproval : {obj}")

        # =========================================================================
        # STATUS HISTORY
        # =========================================================================

        section("LEAVE STATUS HISTORY")

        histories = [
            (lr_pending, None, "pending", employee),
            (lr_approved, None, "pending", employee),
            (lr_approved, "pending", "approved", manager),
        ]

        for lr, from_status, to_status, changed_by in histories:

            obj, _ = LeaveStatusHistory.objects.get_or_create(
                leave_request=lr,
                from_status=from_status,
                to_status=to_status,
                changed_by=changed_by,
            )

            p(f"LeaveStatusHistory : {obj}")

        # =========================================================================
        # COMMENTS
        # =========================================================================

        section("LEAVE COMMENTS")

        comments = [
            (lr_pending, employee, "Please approve."),
            (lr_pending, manager, "Complete KT before leave."),
            (lr_approved, manager, "Get well soon."),
        ]

        for lr, commenter, comment in comments:

            obj, _ = LeaveComment.objects.get_or_create(
                leave_request=lr,
                commenter=commenter,
                comment=comment,
            )

            p(f"LeaveComment : {obj}")

        # =========================================================================
        # DOCUMENTS
        # =========================================================================

        section("LEAVE DOCUMENTS")

        LeaveDocument.objects.get_or_create(
            leave_request=lr_approved,
            file_name="prescription.pdf",
            defaults={
                "file_url": "https://cdn.example.com/prescription.pdf",
                "file_type": "application/pdf",
                "file_size_kb": 245,
                "uploaded_by": employee,
            },
        )

        p("LeaveDocument created")

        # =========================================================================
        # ACCRUAL TRANSACTION LOG
        # =========================================================================

        section("ACCRUAL TRANSACTION LOG")

        AccrualTransactionLog.objects.get_or_create(
            employee=employee,
            leave_type=lt_pl,
            accrual_date=date(2026, 5, 1),
            defaults={
                "policy_rule": rule_pl,
                "days_accrued": 1.5,
                "balance_before": 6.5,
                "balance_after": 8.0,
                "run_type": "scheduled",
            },
        )

        p("AccrualTransactionLog created")

        # =========================================================================
        # DONE
        # =========================================================================

        print("\n")
        print("=" * 80)
        print("LEAVE MODULE SEED COMPLETED SUCCESSFULLY")
        print("=" * 80)


# -----------------------------------------------------------------------------
# ENTRY
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    run_seed()