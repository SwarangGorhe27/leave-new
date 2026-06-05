"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
    2. employee FK needs to be configured later.
"""

# apps/leave/models/audit/accrual_transaction_log.py

"""
================================================================================
MODEL: accrual_transaction_log
================================================================================

Purpose:
--------
Stores EVERY leave accrual event.

Why this table is critical:
---------------------------
Without this table:
    - accrual reconciliation becomes impossible
    - payroll audits fail
    - debugging balance mismatches becomes difficult

This acts as:
    - accrual audit ledger
    - accrual history
    - reconciliation source

================================================================================
"""

import uuid
from django.db import models


class AccrualRunTypeChoices(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    MANUAL = "manual", "Manual"
    CORRECTION = "correction", "Correction"


class AccrualTransactionLog(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="accrual_logs"
    # )

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="accrual_logs"
    )

    leave_type = models.ForeignKey(
        "leave.LeaveType", on_delete=models.CASCADE, related_name="accrual_logs"
    )

    policy_rule = models.ForeignKey(
        "leave.LeavePolicyRule", on_delete=models.CASCADE, related_name="accrual_logs"
    )

    accrual_date = models.DateField()

    days_accrued = models.DecimalField(max_digits=4, decimal_places=2)

    balance_before = models.DecimalField(max_digits=6, decimal_places=2)

    balance_after = models.DecimalField(max_digits=6, decimal_places=2)

    run_type = models.CharField(max_length=20, choices=AccrualRunTypeChoices.choices)

    run_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_accrual_runs",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accrual_transaction_log"

        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["leave_type"]),
            models.Index(fields=["accrual_date"]),
            models.Index(fields=["run_type"]),
        ]
