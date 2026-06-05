"""
Unified Seed file for Leave Module Master Data.

Usage:
    python seed_master_data.py --schema public

This script seeds all master data for the Leave module:
    - Weekend configurations
    - Accrual schedules
    - Holiday calendars
    - Employee leave policy assignments

"""

import sys
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Change to backend directory to ensure proper module imports
os.chdir(BACKEND_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
import argparse

django.setup()

from django.db import transaction as db_transaction
from django_tenants.utils import schema_context
from apps.employees.models import Branch, Employee
from apps.employees.models.masters.hr_setup import HolidayCalendar, Holiday
from apps.leave.models.request_modules.weekends_config import (
    WeekendConfig,
    WeekFrequencyChoices,
)
from apps.leave.models.masters.leave_policy import (
    LeavePolicy,
    LeavePolicyRule,
    EmployeeLeavePolicy,
)
from apps.leave.models.masters.leave_types import LeaveType
from apps.leave.models.masters.accural_schedule import (
    AccrualSchedule,
    AccrualFrequencyChoices,
    RoundingRuleChoices,
)


# =========================================================
# WEEKEND CONFIGURATION
# =========================================================


def seed_weekend_configs(schema_name, branch_id=None):
    """Seed weekend configurations."""

    print("\n" + "=" * 80)
    print("Seeding Weekend Configurations")
    print("=" * 80 + "\n")

    with schema_context(schema_name):
        try:
            # Get branches
            if branch_id:
                branches = Branch.objects.filter(id=branch_id)
                if not branches.exists():
                    print(f"❌ Branch with ID {branch_id} not found!")
                    return
            else:
                branches = Branch.objects.filter(is_active=True)

            if not branches.exists():
                print("❌ No active branches found!")
                return

            # Default weekend configuration: Sunday and Saturday
            weekend_configs = [
                {
                    "day_of_week": 6,
                    "week_frequency": WeekFrequencyChoices.ALL,
                    "description": "Sunday - All weeks",
                },
                {
                    "day_of_week": 5,
                    "week_frequency": WeekFrequencyChoices.ALL,
                    "description": "Saturday - All weeks",
                },
                {
                    "day_of_week": 5,
                    "week_frequency": WeekFrequencyChoices.SECOND,
                    "description": "2nd Saturday (Optional)",
                },
                {
                    "day_of_week": 5,
                    "week_frequency": WeekFrequencyChoices.FOURTH,
                    "description": "4th Saturday (Optional)",
                },
            ]

            created_count = 0
            skipped_count = 0

            for branch in branches:
                print(f"\n📍 Processing Branch: {branch.name} ({branch.id})")
                print("-" * 80)

                for config in weekend_configs:
                    try:
                        existing = WeekendConfig.objects.filter(
                            branch=branch,
                            day_of_week=config["day_of_week"],
                            week_frequency=config["week_frequency"],
                        ).first()

                        if existing:
                            print(
                                f"   ⏭️  Skipped: {config['description']} (already exists)"
                            )
                            skipped_count += 1
                            continue

                        weekend_config = WeekendConfig.objects.create(
                            branch=branch,
                            day_of_week=config["day_of_week"],
                            week_frequency=config["week_frequency"],
                            is_active=True,
                        )

                        print(f"   ✅ Created: {config['description']}")
                        created_count += 1

                    except Exception as e:
                        print(f"   ❌ Error creating {config['description']}: {str(e)}")

            print("\n✅ Weekend Configuration Seeding Completed")
            print(f"   Created: {created_count} | Skipped: {skipped_count}\n")
            return created_count

        except Exception as e:
            print(f"❌ Error during weekend seeding: {str(e)}")
            raise


# =========================================================
# ACCRUAL SCHEDULES
# =========================================================


def get_or_create_leave_type(code, defaults):
    """Get or create leave type."""
    leave_type = LeaveType.objects.filter(code=code).first()

    if not leave_type:
        return LeaveType.objects.create(code=code, **defaults)

    for field, value in defaults.items():
        setattr(leave_type, field, value)
    leave_type.save(update_fields=[*defaults.keys(), "updated_at"])
    return leave_type


def get_or_create_policy():
    """Get or create leave policy."""
    policy = LeavePolicy.objects.filter(name="Accrual Demo Policy FY2026").first()

    if not policy:
        return LeavePolicy.objects.create(
            name="Accrual Demo Policy FY2026",
            description="Seed policy for testing accrual schedule APIs.",
            effective_from=date(2026, 1, 1),
            effective_to=None,
            is_active=True,
            meta_data={"seed_key": "accrual-schedules-demo"},
            meta_tags=["seed", "accrual"],
        )

    policy.description = "Seed policy for testing accrual schedule APIs."
    policy.effective_from = date(2026, 1, 1)
    policy.effective_to = None
    policy.is_active = True
    policy.meta_data = {"seed_key": "accrual-schedules-demo"}
    policy.meta_tags = ["seed", "accrual"]
    policy.save(
        update_fields=[
            "description",
            "effective_from",
            "effective_to",
            "is_active",
            "meta_data",
            "meta_tags",
            "updated_at",
        ]
    )
    return policy


def get_or_create_policy_rule(policy, leave_type, accrual_days):
    """Get or create policy rule."""
    policy_rule = (
        LeavePolicyRule.objects.filter(
            policy=policy,
            leave_type=leave_type,
            grade__isnull=True,
            employee_type__isnull=True,
        )
        .order_by("created_at")
        .first()
    )

    rule_data = {
        "probation_restricted": False,
        "notice_period_restricted": False,
        "sandwich_policy_enabled": False,
        "min_service_days": 0,
        "max_leaves_per_month": accrual_days,
        "accrual_enabled": True,
        "accrual_frequency": AccrualFrequencyChoices.MONTHLY,
        "accrual_days": accrual_days,
        "accrual_proration": True,
        "accrual_proration_basis": "calendar_days",
        "rounding_rule": "FLOOR",
        "allow_negative_balance": False,
        "short_leave_monthly_cap": 0,
        "meta_data": {"seed_key": f"accrual-rule-{leave_type.code.lower()}"},
        "meta_tags": ["seed", "accrual"],
    }

    if not policy_rule:
        return LeavePolicyRule.objects.create(
            policy=policy,
            leave_type=leave_type,
            **rule_data,
        )

    for field, value in rule_data.items():
        setattr(policy_rule, field, value)
    policy_rule.save(update_fields=[*rule_data.keys(), "updated_at"])
    return policy_rule


def get_or_create_schedule(policy_rule, run_day_of_month):
    """Get or create accrual schedule."""
    schedule = (
        AccrualSchedule.objects.filter(
            policy_rule=policy_rule,
            frequency=AccrualFrequencyChoices.MONTHLY,
            run_day_of_month=run_day_of_month,
            run_month__isnull=True,
        )
        .order_by("created_at")
        .first()
    )

    schedule_data = {
        "proration_on_join": True,
        "rounding_rule": RoundingRuleChoices.FLOOR,
        "is_active": True,
        "meta_data": {
            "seed_key": f"monthly-{policy_rule.leave_type.code.lower()}",
            "description": "Runs monthly leave accrual for API testing.",
        },
        "meta_tags": ["seed", "accrual"],
    }

    if not schedule:
        return AccrualSchedule.objects.create(
            policy_rule=policy_rule,
            frequency=AccrualFrequencyChoices.MONTHLY,
            run_day_of_month=run_day_of_month,
            run_month=None,
            **schedule_data,
        )

    for field, value in schedule_data.items():
        setattr(schedule, field, value)
    schedule.run_month = None
    schedule.save(update_fields=[*schedule_data.keys(), "run_month", "updated_at"])
    return schedule


def seed_accrual_schedules(schema_name):
    """Seed accrual schedules."""

    print("\n" + "=" * 80)
    print("Seeding Accrual Schedules")
    print("=" * 80 + "\n")

    with schema_context(schema_name):
        try:
            policy = get_or_create_policy()

            leave_type_configs = [
                (
                    "PL",
                    {
                        "name": "Privilege Leave",
                        "description": "Seed privilege leave for accrual schedule API.",
                        "max_days_per_year": Decimal("18.00"),
                        "max_consecutive_days": 15,
                        "carry_forward_enabled": True,
                        "max_carry_forward_days": Decimal("30.00"),
                        "encashable": True,
                        "requires_attachment": False,
                        "min_notice_days": 1,
                        "applicable_gender": "all",
                        "is_paid": True,
                        "allow_half_day": True,
                        "allow_hourly": False,
                        "leave_year_type": "calendar",
                        "color_code": "#2563EB",
                        "is_active": True,
                        "meta_data": {"seed_key": "accrual-leave-type-pl"},
                        "meta_tags": ["seed", "accrual"],
                    },
                    Decimal("1.50"),
                    1,
                ),
                (
                    "CL",
                    {
                        "name": "Casual Leave",
                        "description": "Seed casual leave for accrual schedule API.",
                        "max_days_per_year": Decimal("12.00"),
                        "max_consecutive_days": 3,
                        "carry_forward_enabled": False,
                        "max_carry_forward_days": None,
                        "encashable": False,
                        "requires_attachment": False,
                        "min_notice_days": 0,
                        "applicable_gender": "all",
                        "is_paid": True,
                        "allow_half_day": True,
                        "allow_hourly": False,
                        "leave_year_type": "calendar",
                        "color_code": "#16A34A",
                        "is_active": True,
                        "meta_data": {"seed_key": "accrual-leave-type-cl"},
                        "meta_tags": ["seed", "accrual"],
                    },
                    Decimal("1.00"),
                    1,
                ),
            ]

            schedules = []
            created_count = 0

            for code, leave_defaults, accrual_days, run_day in leave_type_configs:
                leave_type = get_or_create_leave_type(code, leave_defaults)
                policy_rule = get_or_create_policy_rule(
                    policy,
                    leave_type,
                    accrual_days,
                )
                schedule = get_or_create_schedule(policy_rule, run_day)
                schedules.append(
                    {
                        "id": str(schedule.id),
                        "leave_type_code": code,
                        "frequency": schedule.frequency,
                        "run_day_of_month": schedule.run_day_of_month,
                    }
                )
                created_count += 1
                print(f"✅ Created Accrual Schedule: {code}")

            print("\n✅ Accrual Schedules Seeding Completed")
            print(f"   Created: {created_count}\n")
            return schedules

        except Exception as e:
            print(f"❌ Error during accrual seeding: {str(e)}")
            raise


# =========================================================
# HOLIDAY CALENDARS
# =========================================================


def seed_holidays(schema_name, branch_id=None):
    """Seed holiday calendars."""

    print("\n" + "=" * 80)
    print("Seeding Holiday Calendars")
    print("=" * 80 + "\n")

    with schema_context(schema_name):
        try:
            # Get or create holiday calendar for current year
            current_year = datetime.now().year
            
            holiday_calendar = HolidayCalendar.objects.filter(
                calendar_year=current_year
            ).first()
            
            if not holiday_calendar:
                print(f"❌ No holiday calendar found for year {current_year}!")
                return 0

            holidays_data = [
                {
                    "holiday_date": date(2026, 1, 26),
                    "name": "Republic Day",
                    "type": "NATIONAL",
                },
                {
                    "holiday_date": date(2026, 3, 29),
                    "name": "Holi",
                    "type": "NATIONAL",
                },
                {
                    "holiday_date": date(2026, 4, 2),
                    "name": "Good Friday",
                    "type": "NATIONAL",
                },
                {
                    "holiday_date": date(2026, 4, 14),
                    "name": "Ambedkar Jayanti",
                    "type": "NATIONAL",
                },
                {
                    "holiday_date": date(2026, 5, 1),
                    "name": "Labour Day",
                    "type": "NATIONAL",
                },
                {
                    "holiday_date": date(2026, 8, 15),
                    "name": "Independence Day",
                    "type": "NATIONAL",
                },
                {
                    "holiday_date": date(2026, 9, 16),
                    "name": "Milad-un-Nabi",
                    "type": "NATIONAL",
                },
                {
                    "holiday_date": date(2026, 10, 2),
                    "name": "Gandhi Jayanti",
                    "type": "NATIONAL",
                },
                {
                    "holiday_date": date(2026, 10, 29),
                    "name": "Diwali",
                    "type": "NATIONAL",
                },
                {
                    "holiday_date": date(2026, 12, 25),
                    "name": "Christmas",
                    "type": "NATIONAL",
                },
            ]

            created_count = 0
            skipped_count = 0

            for holiday_data in holidays_data:
                try:
                    existing = Holiday.objects.filter(
                        holiday_calendar_id=holiday_calendar.id,
                        holiday_date=holiday_data["holiday_date"],
                        name=holiday_data["name"],
                    ).first()

                    if existing:
                        print(
                            f"   ⏭️  Skipped: {holiday_data['name']} on {holiday_data['holiday_date']} (already exists)"
                        )
                        skipped_count += 1
                        continue

                    holiday = Holiday.objects.create(
                        holiday_calendar_id=holiday_calendar.id,
                        holiday_date=holiday_data["holiday_date"],
                        name=holiday_data["name"],
                        holiday_type=holiday_data["type"],
                    )

                    print(f"   ✅ Created: {holiday_data['name']} on {holiday_data['holiday_date']}")
                    created_count += 1

                except Exception as e:
                    print(f"   ❌ Error creating {holiday_data['name']}: {str(e)}")

            print("\n✅ Holiday Calendars Seeding Completed")
            print(f"   Created: {created_count} | Skipped: {skipped_count}\n")
            return created_count

        except Exception as e:
            print(f"❌ Error during holiday seeding: {str(e)}")
            raise


# =========================================================
# EMPLOYEE LEAVE POLICY ASSIGNMENTS
# =========================================================


def seed_employee_policies(schema_name, branch_id=None):
    """Seed employee leave policy assignments."""

    print("\n" + "=" * 80)
    print("Seeding Employee Leave Policy Assignments")
    print("=" * 80 + "\n")

    with schema_context(schema_name):
        try:
            # Get or create the accrual policy
            policy = LeavePolicy.objects.filter(
                name="Accrual Demo Policy FY2026"
            ).first()

            if not policy:
                print("❌ Leave policy 'Accrual Demo Policy FY2026' not found!")
                print("   Run accrual schedule seeding first.")
                return 0

            # Get employees to assign policy to
            if branch_id:
                employees = Employee.objects.filter(
                    branch_id=branch_id, is_active=True
                )
            else:
                employees = Employee.objects.filter(is_active=True)

            if not employees.exists():
                print("❌ No active employees found!")
                return 0

            created_count = 0
            skipped_count = 0

            print(f"\n📋 Assigning policy to {employees.count()} employees...")
            print("-" * 80)

            for employee in employees[:10]:  # Limit to first 10 for seeding
                try:
                    existing = EmployeeLeavePolicy.objects.filter(
                        employee=employee,
                        policy=policy,
                    ).first()

                    if existing:
                        emp_name = f"{employee.first_name} {employee.last_name}"
                        print(f"   ⏭️  Skipped: {emp_name} (already assigned)")
                        skipped_count += 1
                        continue

                    employee_policy = EmployeeLeavePolicy.objects.create(
                        employee=employee,
                        policy=policy,
                        effective_from=date(2026, 1, 1),
                        effective_to=None,
                        meta_data={"seed_key": f"emp-policy-{employee.id}"},
                        meta_tags=["seed", "employee-policy"],
                    )

                    emp_name = f"{employee.first_name} {employee.last_name}"
                    print(f"   ✅ Assigned to: {emp_name}")
                    created_count += 1

                except Exception as e:
                    emp_name = f"{employee.first_name} {employee.last_name}"
                    print(f"   ❌ Error assigning policy to {emp_name}: {str(e)}")

            print("\n✅ Employee Policy Assignment Seeding Completed")
            print(f"   Created: {created_count} | Skipped: {skipped_count}\n")
            return created_count

        except Exception as e:
            print(f"❌ Error during employee policy seeding: {str(e)}")
            raise


# =========================================================
# MAIN
# =========================================================


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Seed all master data for HRMS Leave module"
    )
    parser.add_argument(
        "--schema",
        default="acme",
        help="Tenant schema name (default: acme)",
    )
    parser.add_argument(
        "--branch-id",
        help="Optional specific branch ID to seed for",
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("HRMS LEAVE MODULE - MASTER DATA SEEDING")
    print("=" * 80)

    with db_transaction.atomic():
        seed_weekend_configs(schema_name=args.schema, branch_id=args.branch_id)
        seed_accrual_schedules(schema_name=args.schema)
        seed_holidays(schema_name=args.schema, branch_id=args.branch_id)
        seed_employee_policies(schema_name=args.schema, branch_id=args.branch_id)

    print("\n" + "=" * 80)
    print("✅ ALL SEEDING COMPLETED SUCCESSFULLY!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
