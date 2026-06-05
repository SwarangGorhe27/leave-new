# apps/core/models/system/system_settings.py

"""
================================================================================
MODEL: system_settings
================================================================================

Purpose:
--------
Stores tenant-level runtime configuration values.

Why this table is important:
----------------------------
Hardcoding business settings inside code is dangerous.

This table allows:
------------------
- dynamic configuration
- company-specific settings
- runtime feature changes
- admin-controlled behavior

Examples:
---------
- leave.auto_approve_after_hours = 48
- payroll.lock_past_month = true
- attendance.grace_minutes = 15
- leave.max_attachment_size_mb = 5

Production Importance:
----------------------
Critical for:
- SaaS customization
- admin configuration panel
- runtime config changes
- reducing deployments for config updates

================================================================================
"""

import uuid
from django.db import models


class SystemSettings(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="system_settings"
    # )

    key = models.CharField(max_length=150)

    value = models.TextField()

    description = models.TextField(null=True, blank=True)

    updated_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_system_settings",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_settings"

        unique_together = [("key")]

        indexes = [
            models.Index(fields=["key"]),
        ]

    def __str__(self):
        return f"{self.company} - {self.key}"
