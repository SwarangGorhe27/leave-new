"""
ISSUES:- 
    1. employee FK needs to be configured later.
"""

# apps/leave/models/transactions/leave_resubmission_history.py

"""
================================================================================
MODEL: leave_resubmission_history
================================================================================

Purpose:
--------
Preserves rejected → resubmitted leave request chains.

Why this table matters:
-----------------------
If a rejected leave request is edited and resubmitted,
the original rejection history must NOT be lost.

This table preserves:
    - original request
    - new resubmitted request
    - exact changes made

================================================================================
"""

import uuid
from django.db import models


class LeaveResubmissionHistory(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    original_request = models.ForeignKey(
        "leave.LeaveRequest",
        on_delete=models.CASCADE,
        related_name="original_resubmissions",
    )

    resubmitted_request = models.ForeignKey(
        "leave.LeaveRequest", on_delete=models.CASCADE, related_name="new_resubmissions"
    )

    changes_made = models.JSONField(null=True, blank=True)

    resubmitted_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="leave_resubmissions",
    )

    resubmitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "leave_resubmission_history"

        indexes = [
            models.Index(fields=["original_request"]),
            models.Index(fields=["resubmitted_request"]),
            models.Index(fields=["resubmitted_by"]),
        ]
