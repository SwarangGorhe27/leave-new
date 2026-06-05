"""
ISSUES:- 
    1. employee FK needs to be configured later.
"""

# apps/leave/models/communication/leave_comments.py
"""
================================================================================
MODEL: leave_comments
================================================================================

Purpose:
--------
Stores comments/discussion messages related to a leave request.

This table enables communication between:
    - employee
    - manager
    - HR
    - admin

during the leave approval lifecycle.

Examples:
---------
Employee:
    "Medical emergency. Attached doctor's prescription."

Manager:
    "Please ensure KT is completed before leave."

HR:
    "Document verified."

Why this table is important:
----------------------------
Without structured comments:
    - approvals lose context
    - audit discussions disappear
    - employee-manager communication becomes fragmented

Internal Comments:
------------------
`is_internal=True`

Used for:
    - HR-only notes
    - manager discussions
    - sensitive workflow remarks

These comments are hidden from employees.

Production Usage:
-----------------
- Approval discussions
- Audit support
- HR notes
- Escalation communication
- Employee clarification requests

================================================================================
"""

import uuid
from django.db import models


# =========================================================
# MODEL
# =========================================================


class LeaveComment(models.Model):
    """
    Comments associated with leave requests
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # =========================================================
    # Parent Leave Request
    # =========================================================

    leave_request = models.ForeignKey(
        "leave.LeaveRequest", on_delete=models.CASCADE, related_name="comments"
    )

    # =========================================================
    # Comment Information
    # =========================================================

    commenter = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="leave_comments"
    )

    comment = models.TextField()

    # =========================================================
    # Visibility
    # =========================================================

    is_internal = models.BooleanField(default=False, help_text="Hidden from employee")

    # =========================================================
    # Timestamp
    # =========================================================

    created_at = models.DateTimeField(auto_now_add=True)

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "leave_comments"

        ordering = ["created_at"]

        indexes = [
            models.Index(fields=["leave_request"]),
            models.Index(fields=["commenter"]),
            models.Index(fields=["is_internal"]),
            models.Index(fields=["created_at"]),
        ]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.commenter} | " f"{self.leave_request.id}"
