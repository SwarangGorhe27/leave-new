"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
    2. Other foreign-key needs to be configured later as we further develop all the modules.
"""

# apps/leave/models/master/reason.py

"""
================================================================================
MODEL: mst_reason
================================================================================

Purpose:
--------
Centralized Reason / Purpose Master used across multiple HRMS modules.

Instead of storing free-text reasons everywhere, this table provides:

    - standardized reason codes
    - configurable dropdown values
    - tenant-specific customization
    - reporting consistency
    - analytics standardization

Supported Modules:
------------------
- Leave
- Gate Pass
- Out Duty
- Attendance Regularization
- Comp Off
- Future workflow modules

Examples:
---------

LEAVE:
    SL_MEDICAL
    FAMILY_FUNCTION
    EMERGENCY

GATE PASS:
    GP_BANK_WORK
    GP_PERSONAL

OUT DUTY:
    CLIENT_VISIT
    FIELD_WORK

REGULARIZATION:
    SYSTEM_ISSUE
    MISSED_PUNCH

Why this table is important:
----------------------------
Without centralized reasons:
    - inconsistent reporting
    - typo issues
    - duplicate labels
    - difficult analytics

This table enables:
    - dynamic admin-managed reasons
    - reusable dropdowns
    - audit consistency
    - policy-based restrictions

Usage Across System:
--------------------
- Leave application forms
- Gate pass requests
- Attendance regularization
- Reporting dashboards
- Analytics & BI
- Approval workflows

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


# =========================================================
# ENUMS
# =========================================================


class ReasonModuleChoices(models.TextChoices):
    LEAVE = "leave", "Leave"
    GATE_PASS = "gate_pass", "Gate Pass"
    OUT_DUTY = "out_duty", "Out Duty"
    REGULARIZATION = "regularization", "Regularization"
    COMP_OFF = "comp_off", "Comp Off"


# =========================================================
# MODEL
# =========================================================


class Reason(models.Model):
    """
    Shared Reason Master across HRMS modules
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="reasons"
    # )

    # =========================================================
    # Reason Configuration
    # =========================================================

    module = models.CharField(max_length=50, choices=ReasonModuleChoices.choices)

    code = models.CharField(max_length=50, help_text="Short system code")

    label = models.CharField(max_length=150, help_text="Display label shown in UI")

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
        db_table = "mst_reason"

        ordering = ["module", "label"]

        indexes = [
            models.Index(fields=["module"]),
            models.Index(fields=["is_active"]),
        ]

        unique_together = [("module", "code")]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return f"{self.module} - {self.label}"
