"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
"""

# apps/leave/models/master/leave_encashment_policy.py

"""
================================================================================
MODEL: mst_leave_encashment_policy
================================================================================

Purpose:
--------
Defines Leave Encashment Rules for a Leave Type.

Why this table is needed:
-------------------------
The `encashable` flag in mst_leave_types only tells whether a leave
CAN be encashed.

But actual encashment processing requires much more configuration:

1. Salary Formula Basis
   - Basic Salary
   - Gross Salary
   - CTC

2. Working Days Divisor
   - 26 Days
   - 30 Days

3. Annual Encashment Limits
   - Max encashable days per year

4. Payout Timing
   - Annual
   - On Exit
   - Custom cycle

5. Tax Handling
   - Taxable
   - Exempt
   - Partial exemption

6. Minimum Balance Retention
   - Prevent full balance exhaustion

Examples:
---------
Example Formula:

    Encashment Amount =
        (Monthly Basic Salary / 26)
        * Encashable Leave Days

Usage Across System:
--------------------
- Payroll integration
- Full & Final settlement
- Encashment approval workflows
- Tax calculations
- Leave balance validation
- Year-end leave processing

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


# =========================================================
# ENUMS (Should be edited later according to our organization)
# =========================================================


class FormulaBasisChoices(models.TextChoices):
    BASIC = "basic", "Basic Salary"
    GROSS = "gross", "Gross Salary"
    CTC = "ctc", "CTC"


class PayoutTimingChoices(models.TextChoices):
    ANNUAL = "annual", "Annual"
    ON_EXIT = "on_exit", "On Exit"
    CUSTOM = "custom", "Custom"


class TaxTreatmentChoices(models.TextChoices):
    TAXABLE = "taxable", "Taxable"
    EXEMPT = "exempt", "Exempt"
    PARTIAL = "partial", "Partial Exempt"


# =========================================================
# MODEL
# =========================================================


class LeaveEncashmentPolicy(models.Model):
    """
    Leave Encashment Policy Configuration
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="leave_encashment_policies"
    # )

    leave_type = models.ForeignKey(
        "leave.LeaveType", on_delete=models.CASCADE, related_name="encashment_policies"
    )

    # =========================================================
    # Encashment Formula
    # =========================================================

    formula_basis = models.CharField(max_length=20, choices=FormulaBasisChoices.choices)

    working_days_divisor = models.SmallIntegerField(
        default=26, help_text="Typically 26 or 30 based on company policy"
    )

    # =========================================================
    # Encashment Limits
    # =========================================================

    max_encashable_days_per_year = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    min_balance_to_retain = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )

    # =========================================================
    # Processing Configuration
    # =========================================================

    payout_timing = models.CharField(max_length=20, choices=PayoutTimingChoices.choices)

    tax_treatment = models.CharField(max_length=20, choices=TaxTreatmentChoices.choices)

    # =========================================================
    # System Fields
    # =========================================================

    is_active = models.BooleanField(default=True)

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
        db_table = "mst_leave_encashment_policy"

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["leave_type"]),
            models.Index(fields=["is_active"]),
        ]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.leave_type.name} " f"Encashment Policy"
