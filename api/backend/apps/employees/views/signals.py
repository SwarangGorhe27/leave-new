"""
HRMS ESS — Django Signals

Fires on EmployeeChangeRequest status transitions to:
  1. Notify HR when a new PENDING request is submitted
  2. Notify the employee when their request is APPROVED or REJECTED

Email sending is skipped gracefully if:
  - django.core.mail raises an exception
  - ESS_CONFIG["EMAIL_NOTIFY_*"] is False in settings

Signals are connected in apps.py → EmployeesConfig.ready()
"""

import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger("hrms.ess.signals")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _ess_config() -> dict:
    return getattr(settings, "ESS_CONFIG", {})


def _send_mail_safe(subject: str, body: str, to: list) -> None:
    """Send email without raising — logs on failure."""
    try:
        from django.core.mail import send_mail
        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@hrms.local"),
            recipient_list=to,
            fail_silently=False,
        )
    except Exception as exc:
        logger.warning("ESS email notification failed: %s", exc)


def _get_employee_email(employee) -> str | None:
    """Return the employee's personal or official email address."""
    personal = getattr(employee, "personal_email", None)
    official = getattr(employee, "official_email", None)
    user_email = getattr(getattr(employee, "user", None), "email", None)
    return personal or official or user_email


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL RECEIVER
# ─────────────────────────────────────────────────────────────────────────────

@receiver(post_save, sender="employees.EmployeeChangeRequest")
def on_change_request_saved(sender, instance, created, **kwargs):
    """
    Fires after every EmployeeChangeRequest save.

    - On creation (PENDING) → notify HR
    - On update to APPROVED  → notify employee
    - On update to REJECTED  → notify employee
    """
    cfg = _ess_config()

    # ── New request submitted ─────────────────────────────────────────────────
    if created and instance.status == "PENDING":
        if cfg.get("EMAIL_NOTIFY_HR_ON_NEW_REQUEST", False):
            hr_email = cfg.get("HR_NOTIFICATION_EMAIL", "")
            if hr_email:
                emp_name = getattr(instance.employee, "full_name", str(instance.employee))
                emp_code = getattr(instance.employee, "employee_code", "")
                subject  = f"[HRMS] New Change Request — {instance.module} — {emp_code}"
                body = (
                    f"A new change request has been submitted.\n\n"
                    f"Employee : {emp_name} ({emp_code})\n"
                    f"Module   : {instance.get_module_display()}\n"
                    f"Action   : {instance.get_action_display()}\n"
                    f"Remarks  : {instance.employee_remarks or '—'}\n\n"
                    f"Please review at: {_admin_url(instance.pk)}\n"
                )
                _send_mail_safe(subject, body, [hr_email])
                logger.info("HR notified of new CR | id=%s", instance.pk)

    # ── Request approved ──────────────────────────────────────────────────────
    elif not created and instance.status == "APPROVED":
        if cfg.get("EMAIL_NOTIFY_EMPLOYEE_ON_DECISION", False):
            emp_email = _get_employee_email(instance.employee)
            if emp_email:
                emp_name = getattr(instance.employee, "full_name", "")
                subject  = f"[HRMS] Your {instance.get_module_display()} change request has been approved"
                body = (
                    f"Dear {emp_name},\n\n"
                    f"Your change request for '{instance.get_module_display()}' has been "
                    f"APPROVED by HR.\n\n"
                    f"Your employee record has been updated accordingly.\n\n"
                    f"Remarks from HR: {instance.admin_remarks or '—'}\n\n"
                    f"If you have any questions, please contact HR.\n"
                )
                _send_mail_safe(subject, body, [emp_email])
                logger.info("Employee notified of approval | id=%s emp=%s",
                            instance.pk, instance.employee.employee_code)

    # ── Request rejected ──────────────────────────────────────────────────────
    elif not created and instance.status == "REJECTED":
        if cfg.get("EMAIL_NOTIFY_EMPLOYEE_ON_DECISION", False):
            emp_email = _get_employee_email(instance.employee)
            if emp_email:
                emp_name = getattr(instance.employee, "full_name", "")
                subject  = f"[HRMS] Your {instance.get_module_display()} change request has been rejected"
                body = (
                    f"Dear {emp_name},\n\n"
                    f"Your change request for '{instance.get_module_display()}' has been "
                    f"REJECTED by HR.\n\n"
                    f"Reason: {instance.admin_remarks or 'No reason provided.'}\n\n"
                    f"Please re-submit with the required corrections, or contact HR for assistance.\n"
                )
                _send_mail_safe(subject, body, [emp_email])
                logger.info("Employee notified of rejection | id=%s emp=%s",
                            instance.pk, instance.employee.employee_code)


def _admin_url(pk) -> str:
    """Best-effort admin URL — returns empty string if routing unavailable."""
    try:
        from django.urls import reverse
        return reverse("ess_admin:admin-cr-detail", kwargs={"pk": pk})
    except Exception:
        return f"/api/admin/change-request/{pk}/"
