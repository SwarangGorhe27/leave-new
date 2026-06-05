# apps/analytics/models/report_cache.py

"""
================================================================================
MODEL: report_cache
================================================================================

Purpose:
--------
Stores pre-generated report results with expiration support (TTL cache).

Why this table is important:
----------------------------
Enterprise HRMS reports are expensive.

Examples:
---------
- Attendance Muster Report
- Monthly Leave Summary
- Payroll Variance Report
- Department Absenteeism Report

For large organizations:
------------------------
10K+ employees can generate:
- millions of attendance rows
- heavy joins
- aggregation bottlenecks

Without caching:
----------------
- reports timeout
- dashboards become slow
- DB CPU spikes
- concurrency issues increase

This table enables:
-------------------
- report caching
- async report generation
- reusable report outputs
- scheduled report refresh
- performance optimization

Typical Flow:
--------------
1. User requests report
2. System checks cache
3. If valid cache exists -> return instantly
4. Else regenerate report
5. Store result in cache

Production Importance:
----------------------
Critical for:
- dashboard speed
- analytics scalability
- large tenant performance
- reducing DB load
- async reporting systems

================================================================================
"""

import uuid
from django.db import models


# =========================================================
# MODEL
# =========================================================


class ReportCache(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="report_caches"
    # )

    report_key = models.CharField(max_length=150, help_text="Unique report identifier")

    parameters = models.JSONField(help_text="Input filters/parameters used for report")

    result_data = models.JSONField(help_text="Cached report output")

    generated_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "report_cache"

        indexes = [
            models.Index(fields=["report_key"]),
            models.Index(fields=["generated_at"]),
            models.Index(fields=["expires_at"]),
        ]

    # =========================================================
    # Utility
    # =========================================================

    @property
    def is_expired(self):
        from django.utils import timezone

        return timezone.now() > self.expires_at

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.report_key}"
