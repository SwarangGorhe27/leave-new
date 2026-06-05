# apps/leave/models/audit/leave_status_history.py

"""
================================================================================
MODEL: leave_status_history
================================================================================

Purpose:
--------
Stores complete status transition history for leave requests.

This table acts as the AUDIT TRAIL for the leave lifecycle.

Why this table is important:
----------------------------
A leave request status changes multiple times during its lifecycle.

Example:
---------
pending
    ↓
approved
    ↓
cancelled

Or:

pending
    ↓
rejected
    ↓
resubmitted
    ↓
approved

Each transition must be historically preserved.

Why not store only current status?
----------------------------------
The `leave_requests.status` field stores only the CURRENT state.

But enterprises require:
    - audit trails
    - compliance tracking
    - dispute resolution
    - workflow debugging
    - historical analytics

This table stores EVERY status transition.

Production Benefits:
--------------------
- complete workflow traceability
- compliance support
- manager accountability
- employee dispute handling
- approval analytics
- SLA reporting
- debugging workflow issues

Golden Rule:
-------------
This table should behave like:
    - append-only audit logs
    - immutable history records

Never update historical transitions unless absolutely required.

Usage Across System:
--------------------
- approval workflows
- employee timeline UI
- audit reports
- escalation engine
- analytics dashboards
- compliance exports

================================================================================
"""

import uuid
from django.db import models


# =========================================================
# MODEL
# =========================================================


class LeaveStatusHistory(models.Model):
    """
    Leave Request Status Transition History
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # =========================================================
    # Parent Leave Request
    # =========================================================

    leave_request = models.ForeignKey(
        "leave.LeaveRequest", on_delete=models.CASCADE, related_name="status_history"
    )

    # =========================================================
    # Status Transition
    # =========================================================

    from_status = models.CharField(
        max_length=30, null=True, blank=True, help_text="Previous status"
    )

    to_status = models.CharField(max_length=30, help_text="New status")

    old_status = models.CharField(
        max_length=20,
        blank=True,
        help_text="Spec-mandated alias for from_status",
    )

    new_status = models.CharField(
        max_length=20,
        help_text="Spec-mandated alias for to_status",
        default="",
    )

    # =========================================================
    # Actor Information
    # =========================================================

    changed_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="leave_status_changes",
        help_text="Employee/System actor",
    )

    # =========================================================
    # Additional Information
    # =========================================================

    remarks = models.TextField(null=True, blank=True)

    # =========================================================
    # Timestamp
    # =========================================================

    changed_at = models.DateTimeField(auto_now_add=True)

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "leave_status_history"

        ordering = ["-changed_at"]

        indexes = [
            models.Index(fields=["leave_request"]),
            models.Index(fields=["from_status"]),
            models.Index(fields=["to_status"]),
            models.Index(fields=["changed_by"]),
            models.Index(fields=["changed_at"]),
            models.Index(fields=["leave_request", "changed_at"]),
        ]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.leave_request.id} | " f"{self.from_status} -> {self.to_status}"
