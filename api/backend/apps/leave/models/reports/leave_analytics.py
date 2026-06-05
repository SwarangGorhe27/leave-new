# apps/analytics/models/leave_analytics_snapshots.py

"""
================================================================================
MODEL: leave_analytics_snapshots
================================================================================

Purpose:
--------
Stores pre-aggregated leave analytics snapshots.

Why this table is important:
----------------------------
Analytics queries on raw transactional tables are extremely expensive.

Example Raw Tables:
-------------------
- leave_requests
- leave_balances
- attendance_logs
- departments
- employees

Running analytics live on these tables causes:
----------------------------------------------
- slow dashboards
- high DB load
- lock contention
- reporting delays

This table stores:
------------------
Precomputed analytics snapshots for fast retrieval.

Examples:
---------
- department absenteeism %
- leave distribution trends
- monthly sick leave usage
- burnout indicators
- high absenteeism teams
- leave type utilization

Typical Flow:
-------------
1. Nightly analytics job runs
2. Aggregates leave data
3. Stores summarized JSON snapshot
4. Dashboards read snapshots instantly

Benefits:
---------
- extremely fast dashboards
- low DB pressure
- scalable analytics
- easier BI integration

Production Importance:
----------------------
Critical for:
- executive dashboards
- HR analytics
- workforce planning
- absenteeism tracking
- predictive analytics

================================================================================
"""

import uuid
from django.db import models


# =========================================================
# MODEL
# =========================================================


class LeaveAnalyticsSnapshots(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="leave_analytics_snapshots"
    # )

    snapshot_month = models.DateField(help_text="Usually first day of month")

    department = models.ForeignKey(
        "employees.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_analytics_snapshots",
    )

    snapshot_data = models.JSONField(
        help_text="""
        Stores pre-aggregated analytics data.

        Example:
        {
            "total_leave_days": 240,
            "avg_absenteeism_rate": 3.2,
            "top_leave_type": "Sick Leave",
            "high_risk_employees": 5
        }
        """
    )

    generated_at = models.DateTimeField(auto_now_add=True)

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "leave_analytics_snapshots"

        indexes = [
            models.Index(fields=["snapshot_month"]),
            models.Index(fields=["department"]),
            models.Index(fields=["generated_at"]),
        ]

        unique_together = [("snapshot_month", "department")]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.snapshot_month}"
