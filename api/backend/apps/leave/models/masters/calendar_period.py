"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
"""

# apps/leave/models/master/calendar_period.py

"""
================================================================================
MODEL: mst_calendar_period
================================================================================

Purpose:
--------
Defines the Leave Calendar Period / Leave Year Configuration
for a tenant (company).

This table is extremely critical in Leave Management because it controls:

1. Leave Year Basis
   - Calendar Year
   - Fiscal Year
   - Custom Leave Cycle

2. Carry Forward Reset Logic
   - When carried-forward leaves expire/reset

3. Accrual Processing
   - When leave accrual starts
   - Joiner accrual handling

4. Leave Encashment Cycle
   - Annual encashment
   - Exit encashment
   - Custom encashment cycle

Examples:
---------
Calendar Year:
    Jan 1 → Dec 31

Fiscal Year:
    Apr 1 → Mar 31

Custom:
    Jul 15 → Jul 14

Usage Across System:
--------------------
- Leave balance calculation
- Carry forward jobs
- Leave expiry cron jobs
- Monthly accrual engine
- Payroll leave encashment
- Analytics & yearly reports

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


# =========================================================
# ENUMS
# =========================================================


class PeriodTypeChoices(models.TextChoices):
    CALENDAR = "calendar", "Calendar"
    FISCAL = "fiscal", "Fiscal"
    CUSTOM = "custom", "Custom"


class EncashmentCycleChoices(models.TextChoices):
    ANNUAL = "annual", "Annual"
    ON_EXIT = "on_exit", "On Exit"
    CUSTOM = "custom", "Custom"


# =========================================================
# MODEL
# =========================================================


class CalendarPeriod(models.Model):
    """
    Defines Leave Year Configuration for a Company
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="calendar_periods"
    # )

    # =========================================================
    # Leave Year Configuration
    # =========================================================

    period_type = models.CharField(max_length=20, choices=PeriodTypeChoices.choices)

    year_start_month = models.SmallIntegerField(
        help_text="Month Leave Year Starts (1-12)"
    )

    year_start_day = models.SmallIntegerField(
        default=1, help_text="Day Leave Year Starts"
    )

    # =========================================================
    # Carry Forward
    # =========================================================

    cf_reset_date = models.DateField(
        null=True, blank=True, help_text="Date when carry-forward balances expire/reset"
    )

    # =========================================================
    # Accrual
    # =========================================================

    accrual_start_month = models.SmallIntegerField(
        null=True, blank=True, help_text="Month accrual processing starts"
    )

    # =========================================================
    # Encashment
    # =========================================================

    encashment_cycle = models.CharField(
        max_length=20, choices=EncashmentCycleChoices.choices, null=True, blank=True
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
        db_table = "mst_calendar_period"

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["period_type"]),
        ]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.period_type} " f"({self.year_start_month}/{self.year_start_day})"
