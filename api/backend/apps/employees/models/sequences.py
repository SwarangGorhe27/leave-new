"""
Employee code sequences model.

Table: employee_code_sequences

Auto-increment employee code generator per company.
Supports prefix, year suffix, padding, reset frequency.
last_sequence_no MUST be updated with SELECT ... FOR UPDATE to prevent races.

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import MetadataMixin


class EmployeeCodeSequence(MetadataMixin):
    """
    Sequence configuration for employee code auto-generation per company.

    Example: prefix=EMP, separator=-, suffix_format=YYYY, padding_length=4
    → EMP-2024-0001

    last_sequence_no must be incremented atomically using:
        SELECT ... FOR UPDATE SKIP LOCKED
    to prevent duplicate codes under concurrent employee creation.

    reset_frequency controls when the sequence counter resets:
      NEVER   — never reset, ever-increasing
      YEARLY  — reset to 0 at the start of each year
      MONTHLY — reset to 0 at the start of each month
    """

    class ResetFrequency(models.TextChoices):
        NEVER = "NEVER", "Never"
        YEARLY = "YEARLY", "Yearly"
        MONTHLY = "MONTHLY", "Monthly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.PROTECT,
        db_column="company_id",
        related_name="code_sequences",
    )
    employee_type = models.ForeignKey(
        "employees.EmployeeType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="employee_type_id",
        related_name="code_sequences",
        help_text="NULL = applies to all employee types",
    )

    # -------------------------------------------------------- format config
    prefix = models.CharField(max_length=20, blank=True, null=True)
    suffix_format = models.CharField(
        max_length=50, default="YYYY", blank=True, null=True
    )
    separator = models.CharField(max_length=1, default="-")
    padding_length = models.SmallIntegerField(default=4)

    # -------------------------------------------------------- sequence state
    last_sequence_no = models.IntegerField(default=0)
    reset_frequency = models.CharField(
        max_length=10,
        choices=ResetFrequency.choices,
        default=ResetFrequency.YEARLY,
    )
    last_reset_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_code_sequences"
        verbose_name = "Employee Code Sequence"
        verbose_name_plural = "Employee Code Sequences"
        indexes = [
            # Critical path for code generation — must be very fast
            models.Index(
                fields=["company", "employee_type"],
                name="idx_emp_code_seq_company_type",
                condition=models.Q(is_active=True),
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(padding_length__gte=1)
                & models.Q(padding_length__lte=10),
                name="chk_emp_code_seq_padding_range",
            ),
        ]

    def __str__(self) -> str:
        return f"Sequence [{self.prefix}] — Company {self.company_id}"
