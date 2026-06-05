"""
Management command: ess_pending_requests

Lists all PENDING change requests with employee details.
Useful for quick HR CLI review or daily Slack/email digest.

Usage:
    python manage.py ess_pending_requests
    python manage.py ess_pending_requests --module ADDRESS
    python manage.py ess_pending_requests --older-than 3
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "List all pending ESS change requests."

    def add_arguments(self, parser):
        parser.add_argument(
            "--module",
            type=str,
            default=None,
            help="Filter by module (e.g. ADDRESS, PROFILE, BANK).",
        )
        parser.add_argument(
            "--older-than",
            type=int,
            default=None,
            dest="older_than",
            help="Only show requests older than N days.",
        )

    def handle(self, *args, **options):
        from apps.employees.models import EmployeeChangeRequest
        from apps.employees.constants import ChangeRequestStatus

        qs = (
            EmployeeChangeRequest.objects
            .filter(status=ChangeRequestStatus.PENDING)
            .select_related("employee", "employee__department", "employee__designation")
            .order_by("created_at")
        )

        if options["module"]:
            qs = qs.filter(module__iexact=options["module"])

        if options["older_than"]:
            cutoff = timezone.now() - timedelta(days=options["older_than"])
            qs = qs.filter(created_at__lt=cutoff)

        total = qs.count()
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\nPending ESS Change Requests: {total}\n"
        ))

        if total == 0:
            self.stdout.write(self.style.SUCCESS("  ✓ No pending requests."))
            return

        # Group by module
        from collections import defaultdict
        by_module = defaultdict(list)
        for cr in qs:
            by_module[cr.module].append(cr)

        for module, requests in sorted(by_module.items()):
            self.stdout.write(self.style.HTTP_INFO(f"\n  [{module}] — {len(requests)} request(s)"))
            for cr in requests:
                emp       = cr.employee
                dept      = getattr(emp.department, "name", "—") if getattr(emp, "department", None) else "—"
                age_days  = (timezone.now() - cr.created_at).days
                self.stdout.write(
                    f"    ID: {cr.pk}\n"
                    f"    Employee : {emp.full_name} ({emp.employee_code}) — {dept}\n"
                    f"    Action   : {cr.action}  |  Age: {age_days} day(s)\n"
                    f"    Remarks  : {cr.employee_remarks or '—'}\n"
                )

        self.stdout.write(
            f"\nRun: python manage.py shell -c "
            f'"from apps.employees.services.extended import ApprovalService; ..." '
            f"to bulk-approve via code.\n"
        )
