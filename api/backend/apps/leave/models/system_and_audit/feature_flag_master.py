# apps/core/models/system/feature_flag_master.py

"""
================================================================================
MODEL: feature_flag_master
================================================================================

Purpose:
--------
Controls feature enablement across SaaS plans and tenants.

Why this table is important:
----------------------------
Modern SaaS systems require:
- gradual rollouts
- beta testing
- plan-based restrictions
- feature toggles
- emergency feature disabling

This table enables:
-------------------
- Premium-only modules
- Beta feature rollout
- Company-specific overrides
- Kill switches

Examples:
---------
Flag:
    advanced_leave_analytics

Enabled For:
    enterprise_plan

Flag:
    ai_leave_predictions

Enabled For:
    beta_customers

Production Importance:
----------------------
Critical for:
- SaaS monetization
- subscription plans
- feature rollout safety
- enterprise enablement

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


# =========================================================
# ENUMS
# =========================================================


class FeatureFlagTypeChoices(models.TextChoices):
    BOOLEAN = "boolean", "Boolean"
    VALUE = "value", "Value"


class FeatureFlagScopeChoices(models.TextChoices):
    GLOBAL = "global", "Global"
    COMPANY = "company", "Company"
    BRANCH = "branch", "Branch"
    EMPLOYEE = "employee", "Employee"


# =========================================================
# MODEL
# =========================================================


class FeatureFlagMaster(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    flag_key = models.CharField(max_length=100, unique=True)

    flag_type = models.CharField(max_length=20, choices=FeatureFlagTypeChoices.choices)

    default_value = models.TextField()

    scope = models.CharField(max_length=20, choices=FeatureFlagScopeChoices.choices)

    description = models.TextField(null=True, blank=True)

    plan_tiers_enabled = ArrayField(
        base_field=models.CharField(max_length=50),
        null=True,
        blank=True,
        help_text="enterprise/pro/business etc.",
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "feature_flag_master"

        indexes = [
            models.Index(fields=["flag_key"]),
            models.Index(fields=["scope"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.flag_key
