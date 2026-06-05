import os
import sys
from uuid import UUID
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
    Team,
    Department,
    Company,
    Designation,
    EmployeeType,
    ReportingManager,
    EmployeeEmploymentDetails,
    EmployeeReportingRelationship,
)
    

def seed_team_hierarchy():
    print("=" * 80)
    print("SEEDING TEAM HIERARCHY")
    print("=" * 80)

    # ------------------------------------------------------------------
    # REPLACE THESE UUIDS
    # ------------------------------------------------------------------

    COMPANY_ID = UUID("467f28f1-746e-4f6a-8a9b-e4491e419f84")

    DEPARTMENT_ID = UUID("7545d206-850a-4d68-a72d-7011a8ebee7b")

    MANAGER_DESIGNATION_ID = UUID(
        "1c576021-113a-4497-a34c-15ab107a2a8e"
    )

    EMPLOYEE_DESIGNATION_ID = UUID(
        "a5ca417a-f7c6-4e34-8e00-f18c4da16c4f"
    )

    EMPLOYEE_TYPE_ID = "1"

    MANAGER_EMPLOYEE_ID = UUID(
        "7d2fd57a-c1ef-48c4-9750-107694d05234"
    )

    EMPLOYEE_IDS = [
        UUID("dd5a3a8a-8546-4b13-bf56-e88e8e66ac8a"),
        UUID("8bd6223e-27c1-40dc-8603-e3d2c0716c86"),
        UUID("8bd6223e-27c1-40dc-8603-e3d2c0716c86"),
        UUID("c39fd35f-6273-4c5c-aa06-7ef5ca6a3683"),
    ]

    # ------------------------------------------------------------------
    # FETCH REFERENCES
    # ------------------------------------------------------------------

    company = Company.objects.get(id=COMPANY_ID)
    department = Department.objects.get(id=DEPARTMENT_ID)

    manager_designation = Designation.objects.get(
        id=MANAGER_DESIGNATION_ID
    )

    employee_designation = Designation.objects.get(
        id=EMPLOYEE_DESIGNATION_ID
    )

    employee_type = EmployeeType.objects.get(
        id=EMPLOYEE_TYPE_ID
    )

    manager = Employee.objects.get(
        id=MANAGER_EMPLOYEE_ID
    )

    employees = Employee.objects.filter(
        id__in=EMPLOYEE_IDS
    )

    print(f"✓ Company       : {company}")
    print(f"✓ Department    : {department}")
    print(f"✓ Manager       : {manager}")
    print(f"✓ Team Members  : {employees.count()}")

    # ------------------------------------------------------------------
    # CREATE TEAM
    # ------------------------------------------------------------------

    team, created = Team.objects.get_or_create(
        company=company,
        code="DEV001",
        defaults={
            "name": "Development Team",
            "department": department,
            "team_manager": manager,
        },
    )

    if created:
        print(f"✓ Team Created: {team.name}")
    else:
        print(f"✓ Team Exists: {team.name}")

    # ------------------------------------------------------------------
    # REPORTING MANAGER
    # ------------------------------------------------------------------

    reporting_manager, created = (
        ReportingManager.objects.get_or_create(
            company_id=company.id,
            employee=manager,
            defaults={
                "designation": manager_designation,
                "department": department,
                "is_primary": True,
                "sort_order": 1,
            },
        )
    )

    if created:
        print("✓ Reporting Manager Created")
    else:
        print("✓ Reporting Manager Exists")

    # ------------------------------------------------------------------
    # EMPLOYMENT DETAILS FOR MANAGER
    # ------------------------------------------------------------------

    EmployeeEmploymentDetails.objects.get_or_create(
        employee=manager,
        defaults={
            "employee_type": employee_type,
            "department": department,
            "designation": manager_designation,
            "team": team,
        },
    )

    print("✓ Manager Employment Details")

    # ------------------------------------------------------------------
    # EMPLOYMENT DETAILS FOR TEAM MEMBERS
    # ------------------------------------------------------------------

    for emp in employees:

        EmployeeEmploymentDetails.objects.get_or_create(
            employee=emp,
            defaults={
                "employee_type": employee_type,
                "department": department,
                "designation": employee_designation,
                "team": team,
            },
        )

        EmployeeReportingRelationship.objects.get_or_create(
            employee=emp,
            reports_to_employee=manager,
            relationship_type=(
                EmployeeReportingRelationship.RelationshipType.PRIMARY
            ),
            defaults={
                "effective_from": date.today(),
                "department": department,
                "company": company,
                "is_active": True,
            },
        )

        print(
            f"✓ {emp} reports to {manager}"
        )

    print()
    print("=" * 80)
    print("TEAM HIERARCHY SEEDED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    with schema_context("acme"):
        seed_team_hierarchy()