"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
"""

# apps/leave/models/master/accrual_schedule.py

"""
================================================================================
MODEL: mst_accrual_schedule
================================================================================

Purpose:
--------
Defines the ACTUAL execution schedule for the Leave Accrual Engine.

Why this table is needed:
-------------------------
The `accrual_frequency` field in mst_leave_policy_rules only tells
the logical frequency:

    - monthly
    - quarterly
    - annual

But in production HRMS systems, accrual execution requires
precise scheduling control.

This table provides cron-like scheduling support.

Examples:
---------

1. Monthly Accrual
------------------
Run on:
    Every 1st of month

2. Quarterly Accrual
--------------------
Run on:
    Jan / Apr / Jul / Oct

3. Annual Accrual
-----------------
Run on:
    April 1st every year

4. Joiner Proration
-------------------
Employee joins on:
    18th April

Accrual can be:
    - prorated
    - full
    - rounded

Usage Across System:
--------------------
- Celery Beat jobs
- Scheduled accrual engine
- Leave balance generation
- Mid-period proration
- Automated leave crediting
- Audit & reconciliation

Production Importance:
----------------------
Without this table:
    - accrual timing becomes hardcoded
    - multiple policies become difficult
    - cron management becomes messy

This table enables:
    - dynamic scheduling
    - tenant-wise accrual flexibility
    - future extensibility

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


# =========================================================
# ENUMS
# =========================================================


class AccrualFrequencyChoices(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    QUARTERLY = "quarterly", "Quarterly"
    ANNUAL = "annual", "Annual"


class RoundingRuleChoices(models.TextChoices):
    FLOOR = "FLOOR", "Floor"
    CEIL = "CEIL", "Ceil"
    ROUND_HALF = "ROUND_HALF", "Round Half"


# =========================================================
# MODEL
# =========================================================


class AccrualSchedule(models.Model):
    """
    Defines execution schedule for leave accrual processing
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    policy_rule = models.ForeignKey(
        "leave.LeavePolicyRule",
        on_delete=models.CASCADE,
        related_name="accrual_schedules",
    )

    # =========================================================
    # Schedule Configuration
    # =========================================================

    frequency = models.CharField(max_length=20, choices=AccrualFrequencyChoices.choices)

    run_day_of_month = models.SmallIntegerField(
        null=True, blank=True, help_text="Day of month for accrual execution"
    )

    run_month = models.SmallIntegerField(
        null=True, blank=True, help_text="Month for annual/quarterly accrual"
    )

    # =========================================================
    # Proration Configuration
    # =========================================================

    proration_on_join = models.BooleanField(default=True)

    rounding_rule = models.CharField(
        max_length=10,
        choices=RoundingRuleChoices.choices,
        default=RoundingRuleChoices.FLOOR,
    )

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
        db_table = "mst_accrual_schedule"

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["policy_rule"]),
            models.Index(fields=["frequency"]),
            models.Index(fields=["is_active"]),
        ]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.policy_rule.leave_type.name} " f"- {self.frequency}"
