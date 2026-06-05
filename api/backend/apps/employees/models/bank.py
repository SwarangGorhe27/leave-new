"""
Employee bank accounts model.

Table: employee_bank_accounts

Bank account records for salary credit.
Multiple accounts per employee; exactly one is_primary per employee.
IFSC validated at application layer.

Post-audit additive column per ADMIN_SIDE.md:
  payment_type_id — FK to mst_payment_type (deferred to payroll module)

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionPIIBaseModel


class EmployeeBankAccount(TransactionPIIBaseModel):
    """
    Bank account record for an employee.

    account_number is PII — store encrypted at rest.
    ifsc_code format: 4-char bank prefix + 0 + 6-char branch code (11 chars total).
    is_primary marks the active salary credit account.
    PII fields inherited from TransactionPIIBaseModel.

    Post-audit additive:
      payment_type_id: UUID FK to payroll module's mst_payment_type
                       Stored as nullable UUID (no DB-level FK to avoid cross-schema FK).
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="bank_accounts",
    )

    # -------------------------------------------------------- bank master
    bank = models.ForeignKey(
        "employees.Bank",
        on_delete=models.PROTECT,
        db_column="bank_id",
        related_name="emp_bank_accounts",
    )
    account_type = models.ForeignKey(
        "employees.AccountType",
        on_delete=models.PROTECT,
        db_column="account_type_id",
        related_name="emp_bank_accounts",
    )

    # -------------------------------------------------------- account data (PII)
    account_number = models.CharField(
        max_length=30,
        help_text="Account number — store encrypted at rest",
    )
    ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    micr_code = models.CharField(max_length=9, blank=True, null=True)
    branch_name = models.CharField(max_length=150, blank=True, null=True)
    branch_address = models.TextField(blank=True, null=True)

    # -------------------------------------------------------- account holder
    account_holder_name = models.CharField(max_length=150, blank=True, null=True)

    # -------------------------------------------------------- status
    bank_status = models.ForeignKey(
        "employees.BankStatus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="bank_status_id",
        related_name="emp_bank_accounts",
    )

    # -------------------------------------------------------- flags
    is_primary = models.BooleanField(default=False)
    is_salary_account = models.BooleanField(default=True)

    # -------------------------------------------------------- verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="verified_by",
        related_name="verified_emp_bank_accounts",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # Post-audit additive column: UUID FK to payroll module mst_payment_type
    payment_type_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="FK to payroll.mst_payment_type — no DB-level constraint (cross-module)",
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_bank_accounts"
        verbose_name = "Employee Bank Account"
        verbose_name_plural = "Employee Bank Accounts"
        indexes = [
            models.Index(
                fields=["employee", "is_primary"],
                name="idx_emp_bank_employee_primary",
            ),
            models.Index(fields=["employee"], name="idx_emp_bank_employee"),
        ]

    def __str__(self) -> str:
        return f"Bank [{self.bank_id}] — {self.employee_id} (primary={self.is_primary})"
