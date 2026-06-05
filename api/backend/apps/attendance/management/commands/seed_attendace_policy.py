from django.core.management.base import BaseCommand
from decimal import Decimal
 
from django_tenants.utils import schema_context
from apps.attendance.models.masters.policy_masters import AttendancePolicy
from apps.employees.models import Company
 
 
COMPANY_ID = "3e3d1590-4251-41f1-be99-0d4d16b09ec7"
SCHEMA_NAME = "acme"
 
 
policies = [
    {
        "name": "General Policy",
        "version": 1,
        "is_current": True,
        "is_active": True,
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
        "lop_deduction_unit": Decimal("1.00"),
        "ot_enabled": False,
        "ot_min_mins": None,
        "max_regularizations_month": 2,
        "meta_data": {
            "seeded": True,
            "policy_doc_version": "v7",
            "notes": "Standard policy for permanent full-time employees",
        },
    },
    {
        "name": "Flexible Policy",
        "version": 1,
        "is_current": True,
        "is_active": True,
        "late_login_cycle_limit": 3,
        "late_login_grace_mins": 30,
        "late_login_max_grace_mins": 120,
        "early_exit_max_grace_mins": 120,
        "short_leave_max_mins": 180,
        "monthly_grace_instance_limit": 3,
        "half_day_min_work_mins": 240,
        "half_day_min_mins": 240,
        "half_day_max_mins": 419,
        "full_day_min_mins": 420,
        "lop_deduction_unit": Decimal("1.00"),
        "ot_enabled": False,
        "ot_min_mins": None,
        "max_regularizations_month": 3,
        "meta_data": {
            "seeded": True,
            "policy_doc_version": "v7",
            "notes": "Relaxed policy for remote/hybrid/flexible employees",
        },
    },
    {
        "name": "Operations Policy",
        "version": 1,
        "is_current": True,
        "is_active": True,
        "late_login_cycle_limit": 3,
        "late_login_grace_mins": 10,
        "late_login_max_grace_mins": 30,
        "early_exit_max_grace_mins": 30,
        "short_leave_max_mins": 60,
        "monthly_grace_instance_limit": 1,
        "half_day_min_work_mins": 270,
        "half_day_min_mins": 270,
        "half_day_max_mins": 539,
        "full_day_min_mins": 540,
        "lop_deduction_unit": Decimal("1.00"),
        "ot_enabled": True,
        "ot_min_mins": 540,
        "max_regularizations_month": 2,
        "meta_data": {
            "seeded": True,
            "policy_doc_version": "v7",
            "notes": "For field/operations staff with OT tracking",
        },
    },
    {
        "name": "Probation Policy",
        "version": 1,
        "is_current": True,
        "is_active": True,
        "late_login_cycle_limit": 3,
        "late_login_grace_mins": 5,
        "late_login_max_grace_mins": 30,
        "early_exit_max_grace_mins": 30,
        "short_leave_max_mins": 60,
        "monthly_grace_instance_limit": 0,
        "half_day_min_work_mins": 300,
        "half_day_min_mins": 300,
        "half_day_max_mins": 479,
        "full_day_min_mins": 480,
        "lop_deduction_unit": Decimal("1.00"),
        "ot_enabled": False,
        "ot_min_mins": None,
        "max_regularizations_month": 1,
        "meta_data": {
            "seeded": True,
            "policy_doc_version": "v7",
            "notes": "Stricter policy for employees under probation",
        },
    },
]
 
 
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        created_count = 0
        skipped_count = 0

        with schema_context(SCHEMA_NAME):
            company = Company.objects.get(id=COMPANY_ID)

            for policy_data in policies:
                name = policy_data["name"]
                version = policy_data["version"]

                obj, created = AttendancePolicy.objects.update_or_create(
                    company=company,
                    name=name,
                    version=version,
                    defaults=policy_data,
                )

                if created:
                    self.stdout.write(f"CREATE - {name} v{version}")
                    created_count += 1
                else:
                    self.stdout.write(f"SKIP - {name} v{version}")
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created_count}, Skipped: {skipped_count}"
            )
        )
