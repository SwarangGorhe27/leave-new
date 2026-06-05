#!/usr/bin/env python3
"""
Minimal Leave Module Seeding Script
Creates basic data needed for leave module functionality.
"""

import sys
import os
import django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from decimal import Decimal
from datetime import date, datetime
from django.db import transaction as db_transaction
from django_tenants.utils import schema_context
from django.contrib.auth import get_user_model
User = get_user_model()

# Import models
from apps.employees.models import (
    Employee,
    EmployeeType,
    Grade,
    Branch,
    Company,
    Gender,
    HolidayCalendar,
)

from apps.leave.models import (
    LeaveType,
    LeavePolicy,
    LeavePolicyRule,
    EmployeeLeavePolicy,
    LeaveBalance,
    LeaveRequest,
)

def create_basic_masters(schema_name):
    """Create basic master data needed for leave module."""
    
    print(f"Creating basic master data for schema: {schema_name}")
    
    with schema_context(schema_name):
        # Create Company
        company, _ = Company.objects.get_or_create(
            name="ACME Corporation",
            defaults={
                'code': 'ACME',
                'is_active': True,
            }
        )
        print(f"Company: {company.name}")

        # Create Gender
        gender_male, _ = Gender.objects.get_or_create(
            label="Male",
            defaults={'code': 'M', 'is_active': True}
        )
        gender_female, _ = Gender.objects.get_or_create(
            label="Female", 
            defaults={'code': 'F', 'is_active': True}
        )
        
        # Create Employee Type
        employee_type, _ = EmployeeType.objects.get_or_create(
            label="Full-time Employee",
            defaults={
                'code': 'FTE',
                'is_active': True,
            }
        )
        print(f"Employee Type: {employee_type.label}")

        # Create Grade
        grade, _ = Grade.objects.get_or_create(
            label="Senior Software Engineer",
            defaults={
                'code': 'SSE',
                'company': company,
                'is_active': True,
            }
        )
        print(f"Grade: {grade.label}")

        # Create Branch
        branch, _ = Branch.objects.get_or_create(
            name="Head Office",
            company_id=company.id,
            defaults={
                'code': 'HO',
                'branch_type': 'HEAD_OFFICE',
                'is_active': True,
            }
        )
        print(f"Branch: {branch.name}")

        return company, employee_type, grade, branch, gender_male, gender_female


def create_test_employee(schema_name, company, employee_type, grade, branch, gender):
    """Create a test employee for leave testing."""
    
    print("Creating test employee...")
    
    with schema_context(schema_name):
        # Create Django User first
        user, user_created = User.objects.get_or_create(
            username='john.doe',
            defaults={
                'email': 'john.doe@acme.com',
                'is_active': True,
            }
        )
        if user_created:
            user.set_password('password123')
            user.save()
        
        # Create Employee
        employee, _ = Employee.objects.get_or_create(
            employee_code='EMP001',
            defaults={
                'user': user,
                'company': company,
                'first_name': 'John',
                'last_name': 'Doe',
                'personal_email': 'john.doe@acme.com',
                'official_email': 'john.doe@acme.com',
                'employee_type': employee_type,
                'grade': grade,
                'branch': branch,
                'date_of_joining': date(2025, 1, 1),
                'date_of_birth': date(1990, 1, 1),
                'gender': gender,
                'is_active': True,
            }
        )
        print(f"Employee: {employee.first_name} {employee.last_name} ({employee.employee_code})")
        
        return employee


@db_transaction.atomic
def create_leave_types(schema_name, employee_type):
    """Create basic leave types."""
    
    print("Creating leave types...")
    
    with schema_context(schema_name):
        leave_types = []
        
        # Privilege Leave
        pl_leave, _ = LeaveType.objects.get_or_create(
            code="PL",
            defaults={
                'name': "Privilege Leave",
                'employee_type': employee_type,
                'description': "Privilege Leave for employees",
                'max_days_per_year': Decimal("21.00"),
                'max_consecutive_days': 15,
                'carry_forward_enabled': True,
                'max_carry_forward_days': Decimal("5.00"),
                'encashable': True,
                'requires_attachment': False,
                'min_notice_days': 1,
                'applicable_gender': "all",
                'is_paid': True,
                'allow_half_day': True,
                'allow_hourly': False,
                'leave_year_type': "calendar",
                'color_code': "#2563EB",
                'is_active': True,
            }
        )
        leave_types.append(pl_leave)
        
        # Casual Leave
        cl_leave, _ = LeaveType.objects.get_or_create(
            code="CL",
            defaults={
                'name': "Casual Leave",
                'employee_type': employee_type,
                'description': "Casual Leave for employees",
                'max_days_per_year': Decimal("12.00"),
                'max_consecutive_days': 3,
                'carry_forward_enabled': False,
                'encashable': False,
                'requires_attachment': False,
                'min_notice_days': 0,
                'applicable_gender': "all",
                'is_paid': True,
                'allow_half_day': True,
                'allow_hourly': False,
                'leave_year_type': "calendar",
                'color_code': "#16A34A",
                'is_active': True,
            }
        )
        leave_types.append(cl_leave)
        
        # Sick Leave
        sl_leave, _ = LeaveType.objects.get_or_create(
            code="SL",
            defaults={
                'name': "Sick Leave",
                'employee_type': employee_type,
                'description': "Sick Leave for employees",
                'max_days_per_year': Decimal("12.00"),
                'max_consecutive_days': 10,
                'carry_forward_enabled': False,
                'encashable': False,
                'requires_attachment': True,
                'attachment_threshold_days': 2,
                'min_notice_days': 0,
                'applicable_gender': "all",
                'is_paid': True,
                'allow_half_day': True,
                'allow_hourly': False,
                'leave_year_type': "calendar",
                'color_code': "#DC2626",
                'is_active': True,
            }
        )
        leave_types.append(sl_leave)
        
        print(f"Created {len(leave_types)} leave types")
        return leave_types


@db_transaction.atomic
def create_leave_policy_and_rules(schema_name, employee_type, grade, leave_types):
    """Create leave policy and rules."""
    
    print("Creating leave policy and rules...")
    
    with schema_context(schema_name):
        # Create Leave Policy
        policy, _ = LeavePolicy.objects.get_or_create(
            name="Standard Employee Policy 2026",
            defaults={
                'description': "Standard leave policy for all employees",
                'effective_from': date(2026, 1, 1),
                'effective_to': None,
                'version': 1,
                'is_active': True,
            }
        )
        
        # Create Policy Rules
        rules = []
        for leave_type in leave_types:
            rule, _ = LeavePolicyRule.objects.get_or_create(
                policy=policy,
                leave_type=leave_type,
                defaults={
                    'probation_restricted': False,
                    'notice_period_restricted': False,
                    'grade': grade,
                    'employee_type': employee_type,
                    'sandwich_policy_enabled': False,
                    'min_service_days': 0,
                    'max_leaves_per_month': Decimal("3.00"),
                    'accrual_enabled': True,
                    'accrual_frequency': "monthly",
                    'accrual_days': Decimal("1.75") if leave_type.code == "PL" else Decimal("1.00"),
                    'accrual_proration': True,
                    'accrual_proration_basis': "calendar_days",
                    'rounding_rule': "FLOOR",
                    'allow_negative_balance': False,
                    'short_leave_monthly_cap': 0,
                }
            )
            rules.append(rule)
        
        print(f"Created policy: {policy.name} with {len(rules)} rules")
        return policy, rules


@db_transaction.atomic
def assign_policy_to_employee(schema_name, employee, policy):
    """Assign policy to employee and create leave balances."""
    
    print("Assigning policy to employee...")
    
    with schema_context(schema_name):
        # Assign policy to employee
        assignment, _ = EmployeeLeavePolicy.objects.get_or_create(
            employee=employee,
            policy=policy,
            defaults={
                'effective_from': date(2026, 1, 1),
                'effective_to': None,
            }
        )
        
        # Create leave balances for current year
        current_year = date.today().year
        leave_year_start = date(current_year, 1, 1)
        leave_year_end = date(current_year, 12, 31)
        
        for rule in policy.policy_rules.all():
            balance, _ = LeaveBalance.objects.get_or_create(
                employee=employee,
                leave_type=rule.leave_type,
                year=current_year,
                defaults={
                    'leave_year_start': leave_year_start,
                    'leave_year_end': leave_year_end,
                    'allocated_days': rule.leave_type.max_days_per_year,
                    'accrued_days': Decimal('0.00'),
                    'carried_forward': Decimal('0.00'),
                    'used_days': Decimal('0.00'),
                    'pending_days': Decimal('0.00'),
                    'encashed_days': Decimal('0.00'),
                    'lapsed_days': Decimal('0.00'),
                }
            )
        
        print(f"Assigned policy to {employee.employee_code}")
        return assignment


def create_sample_leave_requests(schema_name, employee, policy, leave_types):
    """Create some sample leave requests for testing."""
    
    print("Creating sample leave requests...")
    
    with schema_context(schema_name):
        requests = []
        
        # Draft request
        draft_request = LeaveRequest.objects.create(
            employee=employee,
            applied_by=employee,
            policy=policy,
            leave_type=leave_types[0],  # PL
            from_date=date(2026, 7, 15),
            to_date=date(2026, 7, 17),
            from_session='first_half',
            to_session='second_half',
            total_days=Decimal('3.00'),
            reason="Vacation with family",
            status='draft',
            application_source='web',
            created_by=employee.id,
            updated_by=employee.id,
        )
        requests.append(draft_request)
        
        # Pending request
        pending_request = LeaveRequest.objects.create(
            employee=employee,
            applied_by=employee,
            policy=policy,
            leave_type=leave_types[1],  # CL
            from_date=date(2026, 6, 10),
            to_date=date(2026, 6, 10),
            from_session='first_half',
            to_session='first_half',
            total_days=Decimal('0.50'),
            reason="Personal work",
            status='pending',
            application_source='web',
            created_by=employee.id,
            updated_by=employee.id,
        )
        requests.append(pending_request)
        
        # Approved request
        approved_request = LeaveRequest.objects.create(
            employee=employee,
            applied_by=employee,
            policy=policy,
            leave_type=leave_types[2],  # SL
            from_date=date(2026, 5, 20),
            to_date=date(2026, 5, 21),
            from_session='first_half',
            to_session='second_half',
            total_days=Decimal('2.00'),
            reason="Medical checkup",
            status='approved',
            application_source='web',
            created_by=employee.id,
            updated_by=employee.id,
        )
        requests.append(approved_request)
        
        print(f"Created {len(requests)} sample leave requests")
        return requests


def main():
    """Main seeding function."""
    
    schema_name = "acme"
    
    print("=" * 60)
    print("LEAVE MODULE - MINIMAL SEEDING SCRIPT")
    print("=" * 60)
    
    try:
        # Create basic master data
        company, employee_type, grade, branch, gender_male, gender_female = create_basic_masters(schema_name)
        
        # Create test employee
        employee = create_test_employee(schema_name, company, employee_type, grade, branch, gender_male)
        
        # Create leave types
        leave_types = create_leave_types(schema_name, employee_type)
        
        # Create leave policy and rules
        policy, rules = create_leave_policy_and_rules(schema_name, employee_type, grade, leave_types)
        
        # Assign policy to employee and create balances
        assignment = assign_policy_to_employee(schema_name, employee, policy)
        
        # Create sample leave requests
        requests = create_sample_leave_requests(schema_name, employee, policy, leave_types)
        
        print("\n" + "=" * 60)
        print("SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Employee ID: {employee.id}")
        print(f"Employee Code: {employee.employee_code}")
        print(f"Policy ID: {policy.id}")
        print(f"Leave Types: {len(leave_types)}")
        print(f"Leave Requests: {len(requests)}")
        print("\nYou can now test the leave module APIs!")
        
    except Exception as e:
        print(f"\nERROR during seeding: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()