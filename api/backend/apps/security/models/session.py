"""
Session tracking and audit log models.

Tables:
  hr_session    — active user sessions with device / IP info
  hr_audit_log  — immutable record of all admin / data-change events
"""

import uuid

from django.db import models

from apps.security.models.base import SecurityBaseModel


# ---------------------------------------------------------------------------
# HR Session
# ---------------------------------------------------------------------------


class HRSession(models.Model):
    """
    Tracks an active authenticated session for an employee.
    Table: hr_session

    session_token  — JWT jti or opaque token stored for revocation checks
    expires_at     — datetime after which the session is invalid
    is_revoked     — explicit revocation (logout, admin kick-out)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="hr_sessions",
    )
    session_token = models.CharField(max_length=500, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    device_fingerprint = models.TextField(blank=True)
    login_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False, db_index=True)
    revoked_reason = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "hr_session"
        verbose_name = "HR Session"
        verbose_name_plural = "HR Sessions"
        indexes = [
            models.Index(
                fields=["employee", "is_revoked"],
                name="idx_hr_session_emp_revoked",
            ),
        ]

    def __str__(self) -> str:
        return f"Session {self.id} — employee {self.employee_id}"


# ---------------------------------------------------------------------------
# Audit Log
# ---------------------------------------------------------------------------


class HRAuditLog(models.Model):
    """
    Immutable record of every admin action / data-change event.
    Table: hr_audit_log

    Do NOT update or delete rows — append only.

    event_type choices:
      LOGIN / LOGOUT / CREATE / UPDATE / DELETE / APPROVE / REJECT / EXPORT / IMPORT
    """

    EVENT_LOGIN = "LOGIN"
    EVENT_LOGOUT = "LOGOUT"
    EVENT_CREATE = "CREATE"
    EVENT_UPDATE = "UPDATE"
    EVENT_DELETE = "DELETE"
    EVENT_APPROVE = "APPROVE"
    EVENT_REJECT = "REJECT"
    EVENT_EXPORT = "EXPORT"
    EVENT_IMPORT = "IMPORT"
    EVENT_CHOICES = [
        (EVENT_LOGIN, "Login"),
        (EVENT_LOGOUT, "Logout"),
        (EVENT_CREATE, "Create"),
        (EVENT_UPDATE, "Update"),
        (EVENT_DELETE, "Delete"),
        (EVENT_APPROVE, "Approve"),
        (EVENT_REJECT, "Reject"),
        (EVENT_EXPORT, "Export"),
        (EVENT_IMPORT, "Import"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.CASCADE,
        db_column="company_id",
        related_name="audit_logs",
    )
    actor = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        db_column="actor_id",
        related_name="audit_logs_as_actor",
    )
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, db_index=True)
    module = models.CharField(max_length=50, db_index=True)
    entity_type = models.CharField(
        max_length=100,
        help_text="Model / table name, e.g. Employee or leave_application",
    )
    entity_id = models.UUIDField(null=True, blank=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session = models.ForeignKey(
        HRSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "hr_audit_log"
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ["-changed_at"]
        indexes = [
            models.Index(
                fields=["company", "module", "changed_at"],
                name="idx_hr_audit_co_mod_dt",
            ),
            models.Index(
                fields=["entity_type", "entity_id"],
                name="idx_hr_audit_entity",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} by {self.actor_id} at {self.changed_at}"
