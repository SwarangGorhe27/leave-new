"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
    2. employee FK needs to be configured later.
"""

# apps/leave/models/transaction/leave_balances.py
"""
================================================================================
MODEL: leave_balances
================================================================================

Purpose:
--------
Stores the CURRENT leave balance snapshot for an employee
for a specific leave type and leave year.

This is one of the most critical transactional tables in the
entire Leave Management System.

Why this table exists:
----------------------
Instead of recalculating balances from all leave transactions
every time, this table stores the running balance snapshot.

This enables:
    - fast leave balance checks
    - real-time API performance
    - scalable leave calculations
    - dashboard summaries
    - payroll integrations

Key Concepts:
-------------

1. Allocated Days
-----------------
Initial leave allocation.

Example:
    12 PL assigned yearly

2. Accrued Days
---------------
Leaves earned progressively.

Example:
    1.5 leaves/month

3. Carried Forward
------------------
Balance carried from previous leave year.

4. Used Days
------------
Approved and deducted leaves.

5. Pending Days
---------------
Applied but not yet approved.

6. Encashed Days
----------------
Leaves converted into payout.

7. Lapsed Days
---------------
Expired unused leaves.

8. Optimistic Locking
---------------------
`version` field prevents concurrent update corruption.

Production Importance:
----------------------
This table becomes HIGHLY active in production systems.

Common Operations:
    - apply leave
    - approve leave
    - cancel leave
    - accrual engine
    - carry forward job
    - encashment
    - payroll sync

Performance Notes:
------------------
- Heavy read/write table
- Requires indexing
- Requires transaction-safe updates
- Requires row-level locking
- Avoid full-table scans

Usage Across System:
--------------------
- Leave APIs
- Employee dashboard
- Manager approvals
- Payroll
- Analytics
- Carry forward jobs
- Accrual engine

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


# =========================================================
# MODEL
# =========================================================


class LeaveBalance(models.Model):
    """
    Employee Leave Balance Snapshot
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # =========================================================
    # Tenant Scope
    # =========================================================

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="leave_balances"
    # )

    # =========================================================
    # Employee & Leave Type
    # =========================================================

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="leave_balances"
    )

    leave_type = models.ForeignKey(
        "leave.LeaveType", on_delete=models.CASCADE, related_name="employee_balances"
    )

    # =========================================================
    # Leave Year Information
    # =========================================================

    year = models.SmallIntegerField()

    leave_year_start = models.DateField()

    leave_year_end = models.DateField()

    # =========================================================
    # Balance Components
    # =========================================================

    allocated_days = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    accrued_days = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    carried_forward = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    used_days = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    pending_days = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    encashed_days = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    lapsed_days = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    # =========================================================
    # Accrual Tracking
    # =========================================================

    cf_expiry_date = models.DateField(null=True, blank=True)

    last_accrual_date = models.DateField(null=True, blank=True)

    next_accrual_date = models.DateField(null=True, blank=True)

    # =========================================================
    # Optimistic Locking
    # =========================================================

    version = models.SmallIntegerField(default=1)

    # =========================================================
    # Metadata
    # =========================================================

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)

    created_by = models.UUIDField(null=True, blank=True)

    updated_by = models.UUIDField(null=True, blank=True)

    meta_data = models.JSONField(default=dict, blank=True)

    meta_tags = ArrayField(base_field=models.TextField(), default=list, blank=True)

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "leave_balances"

        ordering = ["employee", "leave_type"]

        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["leave_type"]),
            models.Index(fields=["year"]),
            models.Index(fields=["employee", "leave_type"]),
        ]

        unique_together = [("employee", "leave_type", "year")]

    # =========================================================
    # Computed Properties
    # =========================================================

    @property
    def total_available_balance(self):
        """
        Total currently available leave balance
        """

        total_credits = self.allocated_days + self.accrued_days + self.carried_forward

        total_deductions = (
            self.used_days + self.pending_days + self.encashed_days + self.lapsed_days
        )

        return total_credits - total_deductions

    @property
    def available_days(self):
        """
        Available leave days (spec-mandated alias for total_available_balance).
        Includes allocated + accrued + carried_forward minus all deductions.
        """
        return (
            self.allocated_days
            + self.accrued_days
            + self.carried_forward
            - self.used_days
            - self.pending_days
            - self.encashed_days
            - self.lapsed_days
        )

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.employee} - " f"{self.leave_type.name} - " f"{self.year}"
