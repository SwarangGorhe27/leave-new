"""
Management Command: setup_attendance_beat
==========================================
Registers nightly attendance processing periodic tasks in django-celery-beat
for every active company in the system.

IMPORTANT: Requires --schema argument since mst_company lives in tenant schema.

Usage:
    python manage.py setup_attendance_beat --schema tenant_acme
    python manage.py setup_attendance_beat --schema tenant_acme --hour 2 --minute 30
    python manage.py setup_attendance_beat --schema tenant_acme --company-id <uuid>
"""

import json
import logging

from django.core.management.base import BaseCommand, CommandError
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django_tenants.utils import get_tenant_model, tenant_context

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Register nightly attendance processing Celery Beat tasks (tenant-aware)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            type=str,
            required=True,
            help="Tenant schema name (e.g. tenant_acme). Required — company table lives in tenant schema.",
        )
        parser.add_argument(
            "--hour",
            type=int,
            default=1,
            help="Hour (0-23) to run the task (default: 1 AM)",
        )
        parser.add_argument(
            "--minute",
            type=int,
            default=0,
            help="Minute (0-59) to run the task (default: 0)",
        )
        parser.add_argument(
            "--company-id",
            type=str,
            default=None,
            help="Register only for this specific company UUID (optional)",
        )

    def handle(self, *args, **options):
        schema_name = options["schema"]
        hour = options["hour"]
        minute = options["minute"]
        company_id = options.get("company_id")

        # ------------------------------------------------------------------
        # Resolve tenant — must exist in public schema
        # ------------------------------------------------------------------
        TenantModel = get_tenant_model()

        try:
            tenant = TenantModel.objects.get(schema_name=schema_name)
        except TenantModel.DoesNotExist:
            raise CommandError(
                f"Tenant with schema '{schema_name}' not found. "
                f"Available schemas: {list(TenantModel.objects.values_list('schema_name', flat=True))}"
            )

        self.stdout.write(f"Using tenant: {schema_name}")

        # ------------------------------------------------------------------
        # CrontabSchedule lives in PUBLIC schema — create outside tenant context
        # ------------------------------------------------------------------
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
            timezone="Asia/Kolkata",
        )

        if created:
            self.stdout.write(f"Created crontab schedule: {hour:02d}:{minute:02d} IST daily")
        else:
            self.stdout.write(f"Reusing existing crontab schedule: {hour:02d}:{minute:02d} IST daily")

        # ------------------------------------------------------------------
        # Company query — must run inside tenant context
        # ------------------------------------------------------------------
        with tenant_context(tenant):
            from apps.employees.models import Company

            qs = Company.objects.filter(is_active=True)
            if company_id:
                qs = qs.filter(id=company_id)

            companies = list(qs)

        if not companies:
            self.stdout.write(self.style.WARNING(
                f"No active companies found in schema '{schema_name}'."
            ))
            return

        self.stdout.write(f"Found {len(companies)} company/companies to register.")

        # ------------------------------------------------------------------
        # PeriodicTask lives in PUBLIC schema — create outside tenant context
        # Pass tenant_schema in kwargs so TenantAwareTask can switch context
        # ------------------------------------------------------------------
        created_count = 0
        updated_count = 0

        for company in companies:
            task_name = f"attendance-nightly-{company.id}"
            kwargs = json.dumps({
                "company_id": str(company.id),
                "process_date": None,
                "tenant_schema": schema_name,  # TenantAwareTask uses this to switch schema
            })

            task, was_created = PeriodicTask.objects.update_or_create(
                name=task_name,
                defaults={
                    "task": "attendance.process_daily_attendance",
                    "crontab": schedule,
                    "kwargs": kwargs,
                    "queue": "attendance",
                    "enabled": True,
                    "description": (
                        f"Nightly attendance processing for "
                        f"{company.name} (schema: {schema_name})"
                    ),
                },
            )

            if was_created:
                created_count += 1
                self.stdout.write(f"  Created : {task_name}")
            else:
                updated_count += 1
                self.stdout.write(f"  Updated : {task_name}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Created: {created_count}, Updated: {updated_count} periodic tasks."
        ))
        self.stdout.write(
            f"\nRun Beat scheduler with:\n"
            f"  celery -A config beat -l info "
            f"--scheduler django_celery_beat.schedulers:DatabaseScheduler\n"
        )



# to register 
# python manage.py setup_attendance_beat
# # or with custom time:
# python manage.py setup_attendance_beat --hour 1 --minute 30
# # or for single company:
# python manage.py setup_attendance_beat --company-id <uuid>
# python manage.py setup_attendance_beat --schema tenant_acme --company-id 1ed58f2e-f83b-4b5d-9172-4f033e88a20c

# To Run Worker   celery -A config worker -l info -Q attendance --pool=solo
# To Run Celery Beat   celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler



# To run the seed data
# python manage.py tenant_command shell --schema=tenant_acme

# exec(
#     open(
#         r"apps\attendance\management\commands\seed_attedance_policy.py",
#         encoding="utf-8"
#     ).read()
# )