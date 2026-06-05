"""
ISSUES:- 
    1. employee FK needs to be configured later.
"""

# apps/leave/models/transactions/employee_leave_requests_cc.py

"""
================================================================================
MODEL: employee_leave_requests_cc
================================================================================

Purpose:
--------
Stores CC recipients for leave requests.

Examples:
---------
- Team members
- Project managers
- HRBP
- Backup employees

================================================================================
"""

import uuid
from django.db import models


class EmployeeLeaveRequestCC(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    leave_request = models.ForeignKey(
        "leave.LeaveRequest", on_delete=models.CASCADE, related_name="cc_employees"
    )

    cc_employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="cc_leave_requests"
    )

    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "employee_leave_requests_cc"

        unique_together = [("leave_request", "cc_employee")]

        indexes = [
            models.Index(fields=["leave_request"]),
            models.Index(fields=["cc_employee"]),
        ]
