import sys
import os
import django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from decimal import Decimal
from datetime import date
from django.db import transaction as db_transaction
from django_tenants.utils import schema_context
from apps.employees.models import (
    Employee,
    EmployeeType,
    Grade,
    Branch,
    HolidayCalendar,
)

from apps.leave.models import (
    LeaveType,
    LeavePolicy,
    LeavePolicyRule,
    EmployeeLeavePolicy,
    LeaveBalance,
    LeaveRequest,
    HolidayBranchMap,
)


# ----------------------------
# Leave Types
# ----------------------------
@db_transaction.atomic
def seed_leave_types(schema_name, EMPLOYEE_TYPE_ID):

    print("\nSeeding Leave Types...\n")

    with schema_context(schema_name):

        employee_type = EmployeeType.objects.get(id=EMPLOYEE_TYPE_ID)

        pl_leave = LeaveType.objects.create(
            code="PL",
            name="Privilege Leave",
            employee_type=employee_type,
            description="Privilege Leave",
            max_days_per_year=Decimal("18.00"),
            max_consecutive_days=15,
            carry_forward_enabled=True,
            max_carry_forward_days=Decimal("30.00"),
            encashable=True,
            requires_attachment=False,
            min_notice_days=1,
            applicable_gender="all",
            is_paid=True,
            allow_half_day=False,
            allow_hourly=False,
            leave_year_type="calendar",
            color_code="#2563EB",
            is_active=True,
        )

        cl_leave = LeaveType.objects.create(
            code="CL",
            name="Casual Leave",
            employee_type=employee_type,
            description="Casual Leave",
            max_days_per_year=Decimal("12.00"),
            max_consecutive_days=3,
            carry_forward_enabled=False,
            encashable=False,
            requires_attachment=False,
            min_notice_days=0,
            applicable_gender="all",
            is_paid=True,
            allow_half_day=True,
            allow_hourly=False,
            leave_year_type="calendar",
            color_code="#16A34A",
            is_active=True,
        )

        sl_leave = LeaveType.objects.create(
            code="SL",
            name="Sick Leave",
            employee_type=employee_type,
            description="Sick Leave",
            max_days_per_year=Decimal("12.00"),
            max_consecutive_days=10,
            carry_forward_enabled=False,
            encashable=False,
            requires_attachment=True,
            attachment_threshold_days=2,
            min_notice_days=0,
            applicable_gender="all",
            is_paid=True,
            allow_half_day=True,
            allow_hourly=False,
            leave_year_type="calendar",
            color_code="#DC2626",
            is_active=True,
        )

        ml_leave = LeaveType.objects.create(
            code="ML",
            name="Maternity Leave",
            employee_type=employee_type,
            description="Maternity Leave",
            max_days_per_year=Decimal("182.00"),
            max_consecutive_days=182,
            carry_forward_enabled=False,
            encashable=False,
            requires_attachment=True,
            attachment_threshold_days=1,
            min_notice_days=0,
            applicable_gender="female",
            is_paid=True,
            allow_half_day=False,
            allow_hourly=False,
            leave_year_type="calendar",
            color_code="#9333EA",
            is_active=True,
        )

        coff_leave = LeaveType.objects.create(
            code="COFF",
            name="Compensatory Off",
            employee_type=employee_type,
            description="Compensatory Off",
            max_days_per_year=Decimal("30.00"),
            max_consecutive_days=5,
            carry_forward_enabled=False,
            encashable=False,
            requires_attachment=False,
            min_notice_days=0,
            applicable_gender="all",
            is_paid=True,
            allow_half_day=True,
            allow_hourly=False,
            leave_year_type="calendar",
            color_code="#F59E0B",
            is_active=True,
        )

        print("\nLEAVE TYPES SEEDED SUCCESSFULLY!\n")

        print(f"PL_LEAVE_TYPE_ID = '{pl_leave.id}'")
        print(f"CL_LEAVE_TYPE_ID = '{cl_leave.id}'")
        print(f"SL_LEAVE_TYPE_ID = '{sl_leave.id}'")
        print(f"ML_LEAVE_TYPE_ID = '{ml_leave.id}'")
        print(f"COFF_LEAVE_TYPE_ID = '{coff_leave.id}'")

        return pl_leave.id, cl_leave.id, sl_leave.id, ml_leave.id, coff_leave.id


# ----------------------------
# Policy Data
# ----------------------------
@db_transaction.atomic
def seed_leave_policy_data(schema_name, EMPLOYEE_TYPE_ID, GRADE_ID,
                            PL_LEAVE_TYPE_ID, CL_LEAVE_TYPE_ID,
                            SL_LEAVE_TYPE_ID, ML_LEAVE_TYPE_ID):

    print("\nSeeding Leave Policy Data...\n")

    with schema_context(schema_name):

        employee_type = EmployeeType.objects.get(id=EMPLOYEE_TYPE_ID)
        grade = Grade.objects.get(id=GRADE_ID)

        pl_leave = LeaveType.objects.get(id=PL_LEAVE_TYPE_ID)
        cl_leave = LeaveType.objects.get(id=CL_LEAVE_TYPE_ID)
        sl_leave = LeaveType.objects.get(id=SL_LEAVE_TYPE_ID)
        ml_leave = LeaveType.objects.get(id=ML_LEAVE_TYPE_ID)

        consultant_policy = LeavePolicy.objects.create(
            name="Consultant Leave Policy FY2026",
            description="Default consultant leave policy for ESS testing",
            effective_from=date(2026, 1, 1),
            effective_to=None,
            is_active=True,
        )

        pl_policy_rule = LeavePolicyRule.objects.create(
            policy=consultant_policy,
            leave_type=pl_leave,
            probation_restricted=False,
            notice_period_restricted=True,
            grade=grade,
            employee_type=employee_type,
            sandwich_policy_enabled=True,
            min_service_days=0,
            max_leaves_per_month=Decimal("2.00"),
            accrual_enabled=True,
            accrual_frequency="monthly",
            accrual_days=Decimal("1.50"),
            accrual_proration=True,
            accrual_proration_basis="calendar_days",
            rounding_rule="FLOOR",
            allow_negative_balance=False,
            short_leave_monthly_cap=0,
        )

        cl_policy_rule = LeavePolicyRule.objects.create(
            policy=consultant_policy,
            leave_type=cl_leave,
            probation_restricted=False,
            notice_period_restricted=False,
            grade=grade,
            employee_type=employee_type,
            sandwich_policy_enabled=False,
            min_service_days=0,
            max_leaves_per_month=Decimal("2.00"),
            accrual_enabled=True,
            accrual_frequency="monthly",
            accrual_days=Decimal("1.00"),
            accrual_proration=True,
            accrual_proration_basis="calendar_days",
            rounding_rule="FLOOR",
            allow_negative_balance=False,
            short_leave_monthly_cap=0,
        )

        sl_policy_rule = LeavePolicyRule.objects.create(
            policy=consultant_policy,
            leave_type=sl_leave,
            probation_restricted=False,
            notice_period_restricted=False,
            grade=grade,
            employee_type=employee_type,
            sandwich_policy_enabled=False,
            min_service_days=0,
            max_leaves_per_month=Decimal("3.00"),
            accrual_enabled=True,
            accrual_frequency="monthly",
            accrual_days=Decimal("1.00"),
            accrual_proration=True,
            accrual_proration_basis="calendar_days",
            rounding_rule="FLOOR",
            allow_negative_balance=False,
            short_leave_monthly_cap=0,
        )

        ml_policy_rule = LeavePolicyRule.objects.create(
            policy=consultant_policy,
            leave_type=ml_leave,
            probation_restricted=False,
            notice_period_restricted=False,
            grade=grade,
            employee_type=employee_type,
            sandwich_policy_enabled=False,
            min_service_days=180,
            accrual_enabled=False,
            allow_negative_balance=False,
            short_leave_monthly_cap=0,
        )

        print("\nPOLICY SEEDING COMPLETED SUCCESSFULLY!\n")

        return (
            consultant_policy.id,
            pl_policy_rule.id,
            cl_policy_rule.id,
            sl_policy_rule.id,
            ml_policy_rule.id,
        )


# ----------------------------
# Requests
# ----------------------------
@db_transaction.atomic
def seed_leave_requests(schema_name, EMPLOYEE_ID,
                        CONSULTANT_POLICY_ID,
                        PL_LEAVE_TYPE_ID, CL_LEAVE_TYPE_ID, SL_LEAVE_TYPE_ID,
                        PL_POLICY_RULE_ID, CL_POLICY_RULE_ID, SL_POLICY_RULE_ID):

    print("\nSeeding Leave Requests...\n")

    with schema_context(schema_name):

        employee = Employee.objects.get(id=EMPLOYEE_ID)

        consultant_policy = LeavePolicy.objects.get(id=CONSULTANT_POLICY_ID)

        pl_leave = LeaveType.objects.get(id=PL_LEAVE_TYPE_ID)
        cl_leave = LeaveType.objects.get(id=CL_LEAVE_TYPE_ID)
        sl_leave = LeaveType.objects.get(id=SL_LEAVE_TYPE_ID)

        pl_policy_rule = LeavePolicyRule.objects.get(id=PL_POLICY_RULE_ID)
        cl_policy_rule = LeavePolicyRule.objects.get(id=CL_POLICY_RULE_ID)
        sl_policy_rule = LeavePolicyRule.objects.get(id=SL_POLICY_RULE_ID)

        approved_pl_request = LeaveRequest.objects.create(
            employee=employee,
            applied_by=employee,
            policy=consultant_policy,
            policy_rule=pl_policy_rule,
            leave_type=pl_leave,
            from_date=date(2026, 1, 10),
            to_date=date(2026, 1, 12),
            duration_type="full_day",
            total_days=Decimal("3.00"),
            reason="Family vacation",
            notify_team=True,
            status="approved",
            application_source="web",
            mode_of_work="office",
            processed_by_payroll=False,
            idempotency_key="approved-pl-2026",
        )

        pending_cl_request = LeaveRequest.objects.create(
            employee=employee,
            applied_by=employee,
            policy=consultant_policy,
            policy_rule=cl_policy_rule,
            leave_type=cl_leave,
            from_date=date(2026, 2, 14),
            to_date=date(2026, 2, 14),
            duration_type="half_day",
            half_day_session="first_half",
            total_days=Decimal("0.50"),
            reason="Personal work",
            notify_team=True,
            status="pending",
            application_source="web",
            mode_of_work="office",
            processed_by_payroll=False,
            idempotency_key="pending-cl-2026",
        )

        cancelled_sl_request = LeaveRequest.objects.create(
            employee=employee,
            applied_by=employee,
            policy=consultant_policy,
            policy_rule=sl_policy_rule,
            leave_type=sl_leave,
            from_date=date(2026, 3, 1),
            to_date=date(2026, 3, 2),
            duration_type="full_day",
            total_days=Decimal("2.00"),
            reason="Medical rest",
            notify_team=True,
            status="cancelled",
            cancellation_reason="Recovered early",
            application_source="web",
            mode_of_work="office",
            processed_by_payroll=False,
            idempotency_key="cancelled-sl-2026",
        )

        print("\nLEAVE REQUESTS SEEDED SUCCESSFULLY!\n")

        print(f"APPROVED_PL_REQUEST_ID = '{approved_pl_request.id}'")
        print(f"PENDING_CL_REQUEST_ID = '{pending_cl_request.id}'")
        print(f"CANCELLED_SL_REQUEST_ID = '{cancelled_sl_request.id}'")

        return approved_pl_request.id, pending_cl_request.id, cancelled_sl_request.id


# ----------------------------
# MAIN EXECUTION (safe order)
# ----------------------------
if __name__ == "__main__":
    #RUN COMMAND
    # python -m apps.leave.seed

    schema_name = "acme"
    #Fill this data from pgAdmin after seeding employee data
    EMPLOYEE_ID = "b1ce2bdd-a88e-4876-8f32-fc64d7b127b4"        #this
    GRADE_ID = "263f6e19-6881-4676-b9bf-b862e2d81dd4"          #this
    EMPLOYEE_TYPE_ID = "1"  

    PL_LEAVE_TYPE_ID, CL_LEAVE_TYPE_ID, SL_LEAVE_TYPE_ID, ML_LEAVE_TYPE_ID, COFF_LEAVE_TYPE_ID = seed_leave_types(
        schema_name, EMPLOYEE_TYPE_ID
    )

    (
        CONSULTANT_POLICY_ID,
        PL_POLICY_RULE_ID,
        CL_POLICY_RULE_ID,
        SL_POLICY_RULE_ID,
        ML_POLICY_RULE_ID,
    ) = seed_leave_policy_data(
        schema_name,
        EMPLOYEE_TYPE_ID,
        GRADE_ID,
        PL_LEAVE_TYPE_ID,
        CL_LEAVE_TYPE_ID,
        SL_LEAVE_TYPE_ID,
        ML_LEAVE_TYPE_ID,
    )

    seed_leave_requests(
        schema_name,
        EMPLOYEE_ID,
        CONSULTANT_POLICY_ID,
        PL_LEAVE_TYPE_ID,
        CL_LEAVE_TYPE_ID,
        SL_LEAVE_TYPE_ID,
        PL_POLICY_RULE_ID,
        CL_POLICY_RULE_ID,
        SL_POLICY_RULE_ID,
    )