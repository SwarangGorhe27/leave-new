"""
Management command: ess_expiry_alerts

Scans for:
  1. Passports expiring within ESS_CONFIG["PASSPORT_EXPIRY_WARNING_DAYS"] days
  2. Certifications expiring within ESS_CONFIG["CERT_EXPIRY_WARNING_DAYS"] days

Outputs a report to stdout. Wire into a daily cron / Celery beat task.

Usage:
    python manage.py ess_expiry_alerts
    python manage.py ess_expiry_alerts --dry-run
    python manage.py ess_expiry_alerts --passport-days 60 --cert-days 30
"""

from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Report passports and certifications expiring soon, and optionally email HR."

    def add_arguments(self, parser):
        parser.add_argument(
            "--passport-days",
            type=int,
            default=None,
            help="Override passport expiry warning window (days). Default: ESS_CONFIG value.",
        )
        parser.add_argument(
            "--cert-days",
            type=int,
            default=None,
            help="Override certification expiry warning window (days). Default: ESS_CONFIG value.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print report without sending emails.",
        )

    def handle(self, *args, **options):
        cfg             = getattr(settings, "ESS_CONFIG", {})
        passport_days   = options["passport_days"] or cfg.get("PASSPORT_EXPIRY_WARNING_DAYS", 90)
        cert_days       = options["cert_days"]     or cfg.get("CERT_EXPIRY_WARNING_DAYS", 60)
        dry_run         = options["dry_run"]
        today           = date.today()

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\nESS Expiry Alerts — {today}  "
            f"[passport={passport_days}d, cert={cert_days}d, dry_run={dry_run}]"
        ))

        # ── Passports ─────────────────────────────────────────────────────────
        self._check_passports(today, passport_days, dry_run)

        # ── Certifications ────────────────────────────────────────────────────
        self._check_certifications(today, cert_days, dry_run)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _check_passports(self, today: date, days: int, dry_run: bool):
        from apps.employees.models.ess_extended import EmployeePassportVisa

        threshold = today + timedelta(days=days)
        expiring  = (
            EmployeePassportVisa.objects
            .filter(
                is_current=True,
                expiry_date__lte=threshold,
                expiry_date__gte=today,
                is_deleted=False,
            )
            .select_related("employee", "employee__user")
            .order_by("expiry_date")
        )

        self.stdout.write(f"\n📘 Passports expiring within {days} days: {expiring.count()}")
        for pv in expiring:
            emp      = pv.employee
            days_left = (pv.expiry_date - today).days
            self.stdout.write(
                f"  [{emp.employee_code}] {emp.full_name} — "
                f"Passport: {pv.passport_number} — Expires: {pv.expiry_date} ({days_left} days)"
            )
            if not dry_run:
                self._notify_employee_expiry(emp, "Passport", pv.passport_number, pv.expiry_date)

    def _check_certifications(self, today: date, days: int, dry_run: bool):
        from apps.employees.models.ess_extended import EmployeeSkillCertification

        threshold = today + timedelta(days=days)
        expiring  = (
            EmployeeSkillCertification.objects
            .filter(
                is_certified=True,
                certification_expiry__lte=threshold,
                certification_expiry__gte=today,
                is_deleted=False,
                is_active=True,
            )
            .select_related("employee", "employee__user")
            .order_by("certification_expiry")
        )

        self.stdout.write(f"\n📗 Certifications expiring within {days} days: {expiring.count()}")
        for sc in expiring:
            emp       = sc.employee
            days_left = (sc.certification_expiry - today).days
            self.stdout.write(
                f"  [{emp.employee_code}] {emp.full_name} — "
                f"{sc.certification_name} ({sc.certification_body}) — "
                f"Expires: {sc.certification_expiry} ({days_left} days)"
            )
            if not dry_run:
                self._notify_employee_expiry(
                    emp, "Certification", sc.certification_name, sc.certification_expiry
                )

    def _notify_employee_expiry(self, employee, doc_type: str, doc_ref: str, expiry_date: date):
        """Send a gentle reminder email to the employee."""
        try:
            from django.core.mail import send_mail
            from apps.employees.utils import _get_employee_email   # type: ignore[attr-defined]
        except ImportError:
            return

        email = getattr(employee, "personal_email", None) or getattr(
            getattr(employee, "user", None), "email", None
        )
        if not email:
            return

        days_left = (expiry_date - date.today()).days
        emp_name  = getattr(employee, "full_name", employee.employee_code)

        try:
            send_mail(
                subject=f"[HRMS] {doc_type} Expiry Reminder — {doc_ref}",
                message=(
                    f"Dear {emp_name},\n\n"
                    f"This is a reminder that your {doc_type} ({doc_ref}) "
                    f"will expire on {expiry_date} ({days_left} days from today).\n\n"
                    f"Please take necessary action to renew it and update the details "
                    f"in the HRMS Employee Self-Service portal.\n\n"
                    f"Contact HR if you need assistance."
                ),
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@hrms.local"),
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass
