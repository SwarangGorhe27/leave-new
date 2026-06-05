"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
    2. employee FK needs to be configured later.
"""

# apps/leave/models/transaction/leave_balance_ledger.py

"""
================================================================================
MODEL: leave_balance_ledger
================================================================================

Purpose:
--------
Acts as the immutable transaction ledger for ALL leave balance movements.

This table is one of the MOST IMPORTANT audit tables in the
entire Leave Management System.

Think of it exactly like:
    - Bank transaction statement
    - Accounting ledger
    - Wallet transaction history

Why this table exists:
----------------------
The `leave_balances` table stores only the CURRENT snapshot.

But snapshots alone are NOT enough for:

    - dispute resolution
    - audit trails
    - rollback tracking
    - payroll reconciliation
    - debugging balance mismatches
    - compliance verification

This table stores EVERY single balance movement.

Examples:
---------

1. Allocation
--------------
+12 PL yearly allocation

2. Accrual
-----------
+1.5 leave credited monthly

3. Usage
---------
-2 leave deducted on approval

4. Carry Forward
-----------------
+5 CF from previous year

5. Encashment
--------------
-3 leave converted to payout

6. Reversal
------------
+2 leave restored after cancellation

Production Importance:
----------------------
Without this table:
    - balances become unverifiable
    - payroll disputes become impossible to debug
    - audit compliance fails
    - rollback recovery becomes risky

Golden Rule:
-------------
NEVER update/delete ledger entries in production.

Ledger entries should be:
    - append only
    - immutable
    - auditable

Corrections should happen via:
    adjustment/reversal entries

Usage Across System:
--------------------
- Leave approval engine
- Payroll integration
- Encashment engine
- Carry-forward jobs
- Accrual engine
- Audit reports
- Employee balance history
- Dispute resolution

================================================================================
"""

import uuid
from django.contrib.auth import get_user_model
from django.db import models


# =========================================================
# ENUMS
# =========================================================


class LeaveTransactionTypeChoices(models.TextChoices):
    PENDING_APPLICATION = "pending_application", "Pending Application"
    ALLOCATION = "allocation", "Allocation"
    OPENING_BALANCE = "opening_balance", "Opening Balance"
    ACCRUAL = "accrual", "Accrual"
    USAGE = "usage", "Usage"
    CARRY_FORWARD = "carry_forward", "Carry Forward"
    ENCASHMENT = "encashment", "Encashment"
    LAPSE = "lapse", "Lapse"
    ADJUSTMENT = "adjustment", "Adjustment"
    REVERSAL = "reversal", "Reversal"


# =========================================================
# MODEL
# =========================================================


class LeaveBalanceLedger(models.Model):
    """
    Immutable Leave Balance Transaction Ledger
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # =========================================================
    # Spec-required FK references
    # =========================================================

    leave_balance = models.ForeignKey(
        "leave.LeaveBalance",
        on_delete=models.CASCADE,
        related_name="ledger",
        null=True,
        blank=True,
    )

    leave_request = models.ForeignKey(
        "leave.LeaveRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ledger_entries",
    )

    performed_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_ledger_entries",
    )

    # =========================================================
    # Tenant Scope
    # =========================================================

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="leave_balance_ledger_entries"
    # )

    # =========================================================
    # Employee & Leave Type
    # =========================================================

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="leave_ledger_entries",
    )

    leave_type = models.ForeignKey(
        "leave.LeaveType", on_delete=models.CASCADE, related_name="ledger_entries"
    )

    # =========================================================
    # Leave Year
    # =========================================================

    year = models.SmallIntegerField()

    # =========================================================
    # Transaction Details
    # =========================================================

    transaction_type = models.CharField(
        max_length=30, choices=LeaveTransactionTypeChoices.choices
    )

    days = models.DecimalField(
        max_digits=6, decimal_places=2, help_text="Positive = Credit, Negative = Debit"
    )

    balance_before = models.DecimalField(max_digits=6, decimal_places=2)

    balance_after = models.DecimalField(max_digits=6, decimal_places=2)

    # =========================================================
    # Reference Tracking
    # =========================================================

    reference_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="leave_request / encashment / accrual / comp_off etc.",
    )

    reference_id = models.UUIDField(null=True, blank=True)

    # =========================================================
    # Policy Tracking
    # =========================================================

    policy_version = models.SmallIntegerField(null=True, blank=True)

    # =========================================================
    # Audit Notes
    # =========================================================

    remarks = models.TextField(null=True, blank=True)

    # =========================================================
    # Actor Tracking
    # =========================================================

    transacted_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_leave_transactions",
        help_text="System/User who triggered transaction",
    )

    transacted_at = models.DateTimeField(auto_now_add=True)

    # =========================================================
    # Metadata
    # =========================================================

    created_at = models.DateTimeField(auto_now_add=True)

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "leave_balance_ledger"

        ordering = ["-transacted_at"]

        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["leave_type"]),
            models.Index(fields=["year"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["reference_type", "reference_id"]),
            models.Index(fields=["transacted_at"]),
            models.Index(fields=["employee", "leave_type", "year"]),
        ]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return (
            f"{self.employee} | "
            f"{self.leave_type.name} | "
            f"{self.transaction_type} | "
            f"{self.days}"
        )
