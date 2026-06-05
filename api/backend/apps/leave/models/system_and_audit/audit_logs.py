# apps/core/models/audit/audit_logs.py

"""
================================================================================
MODEL: audit_logs
================================================================================

Purpose:
--------
Stores immutable audit trail of all important actions performed in the system.

Why this table is important:
----------------------------
This is one of the MOST IMPORTANT enterprise tables.

Without audit logs:
-------------------
- compliance fails
- investigations become impossible
- security tracing breaks
- approvals cannot be verified
- GDPR/SOC2 audits fail

Tracks:
-------
- who performed action
- what changed
- old values
- new values
- source IP
- API trace ID
- session tracking

Examples:
---------
- Leave approved
- Employee deleted
- Salary modified
- Payroll exported
- Permission changed

Production Importance:
----------------------
Critical for:
- SOC2
- ISO compliance
- GDPR
- forensic investigation
- admin accountability
- rollback analysis

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import JSONField


# =========================================================
# ENUMS
# =========================================================


class AuditActionCategoryChoices(models.TextChoices):
    CREATE = "create", "Create"
    UPDATE = "update", "Update"
    DELETE = "delete", "Delete"
    APPROVE = "approve", "Approve"
    REJECT = "reject", "Reject"
    EXPORT = "export", "Export"


class DataClassificationChoices(models.TextChoices):
    NORMAL = "normal", "Normal"
    PII = "pii", "PII"
    SENSITIVE = "sensitive", "Sensitive"


# =========================================================
# MODEL
# =========================================================


class AuditLogs(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="audit_logs"
    # )

    actor = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_actions",
    )

    session_id = models.CharField(max_length=100, null=True, blank=True)

    request_id = models.CharField(max_length=100, null=True, blank=True)

    module = models.CharField(max_length=100, null=True, blank=True)

    action = models.CharField(max_length=100)

    action_category = models.CharField(
        max_length=30, choices=AuditActionCategoryChoices.choices, null=True, blank=True
    )

    table_name = models.CharField(max_length=100)

    record_id = models.UUIDField()

    old_values = models.JSONField(null=True, blank=True)

    new_values = models.JSONField(null=True, blank=True)

    data_classification = models.CharField(
        max_length=20,
        choices=DataClassificationChoices.choices,
        default=DataClassificationChoices.NORMAL,
    )

    retention_until = models.DateField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    user_agent = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"

        indexes = [
            models.Index(fields=["actor"]),
            models.Index(fields=["module"]),
            models.Index(fields=["table_name"]),
            models.Index(fields=["record_id"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["request_id"]),
        ]

    def __str__(self):
        return f"{self.action} | " f"{self.table_name} | " f"{self.record_id}"
