# apps/integrations/models/integration_logs.py

"""
================================================================================
MODEL: integration_logs
================================================================================

Purpose:
--------
Tracks all external system integration events and retries.

Supported Integrations:
-----------------------
- biometric devices
- payroll systems
- ERP systems
- third-party APIs
- attendance machines

Why this table is important:
----------------------------
External systems fail frequently.

Without this table:
-------------------
- sync failures become invisible
- retries are impossible
- payload debugging is lost
- reconciliation becomes difficult

Tracks:
-------
- payloads
- sync status
- retry attempts
- errors
- processing timestamps

Examples:
---------
- biometric punch sync failed
- payroll export completed
- leave pushed to ERP
- attendance import retried

Production Importance:
----------------------
Critical for:
- integration debugging
- retry workers
- reconciliation
- enterprise integrations
- monitoring dashboards

================================================================================
"""

import uuid
from django.db import models


# =========================================================
# ENUMS
# =========================================================


class IntegrationStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"


# =========================================================
# MODEL
# =========================================================


class IntegrationLogs(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="integration_logs"
    # )

    source_system = models.CharField(
        max_length=50, help_text="biometric/payroll/erp/api"
    )

    event_type = models.CharField(
        max_length=100, help_text="punch_sync/payroll_export/leave_sync"
    )

    payload = models.JSONField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=IntegrationStatusChoices.choices,
        default=IntegrationStatusChoices.PENDING,
    )

    error_message = models.TextField(null=True, blank=True)

    retry_count = models.SmallIntegerField(default=0)

    processed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "integration_logs"

        indexes = [
            models.Index(fields=["source_system"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.source_system} | " f"{self.event_type} | " f"{self.status}"
