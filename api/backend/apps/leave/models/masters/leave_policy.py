# apps/leave/models/master/leave_policy.py
"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
    2. Other foreign-key needs to be configured later as we further develop all the modules.
    3. employee_type, grade, and employee to be checked again when employee ORM is developed.
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


class AccrualProrationBasisChoices(models.TextChoices):
    CALENDAR_DAYS = "calendar_days", "Calendar Days"
    WORKING_DAYS = "working_days", "Working Days"


class RoundingRuleChoices(models.TextChoices):
    FLOOR = "FLOOR", "Floor"
    CEIL = "CEIL", "Ceil"
    ROUND = "ROUND", "Round"


# =========================================================
# mst_leave_policy
# =========================================================


class LeavePolicy(models.Model):
    """
    Master Leave Policy

    Example:
        - Corporate Employees Policy 2026
        - Factory Workers Policy
        - Contract Employees Leave Policy
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ###
    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="leave_policies"
    # )

    name = models.CharField(max_length=150)

    description = models.TextField(null=True, blank=True)

    # =========================================================
    # Spec-required fields (Section 1 — LeavePolicy)
    # =========================================================

    leave_type = models.ForeignKey(
        "leave.LeaveType",
        on_delete=models.CASCADE,
        related_name="leave_policies",
        null=True,
        blank=True,
    )

    applicable_roles = models.CharField(max_length=255, blank=True)

    days_per_year = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )

    carry_forward_days = models.DecimalField(
        max_digits=5, decimal_places=1, default=0
    )

    max_consecutive_days = models.PositiveIntegerField(null=True, blank=True)

    min_notice_days = models.PositiveIntegerField(default=0)

    allow_half_day = models.BooleanField(default=False)

    allow_negative_balance = models.BooleanField(default=False)

    # =========================================================
    # Date Range
    # =========================================================

    effective_from = models.DateField()

    effective_to = models.DateField(null=True, blank=True)

    # location = models.ForeignKey(
    #     "employees.State",
    #     on_delete=models.CASCADE,
    #     related_name="leave_policies"
    # )

    version = models.SmallIntegerField(default=1)

    is_active = models.BooleanField(default=True)

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

    class Meta:
        db_table = "mst_leave_policy"

        ordering = ["-effective_from"]

        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["effective_from"]),
            models.Index(fields=["effective_to"]),
        ]

    def __str__(self):
        return self.name


# =========================================================
# mst_leave_policy_rules
# =========================================================


class LeavePolicyRule(models.Model):
    """
    Rules mapped to Leave Policies + Leave Types
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    policy = models.ForeignKey(
        "leave.LeavePolicy", on_delete=models.CASCADE, related_name="policy_rules"
    )

    leave_type = models.ForeignKey(
        "leave.LeaveType", on_delete=models.CASCADE, related_name="policy_rules"
    )

    probation_restricted = models.BooleanField(default=False)

    notice_period_restricted = models.BooleanField(default=False)

    grade = models.ForeignKey(
        "employees.Grade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_policy_rules",
        help_text="NULL means applicable to all grades",
    )

    employee_type = models.ForeignKey(
        "employees.EmployeeType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_policy_rules",
        help_text="NULL means applicable to all employee types",
    )

    sandwich_policy_enabled = models.BooleanField(default=False)

    min_service_days = models.IntegerField(default=0)

    max_leaves_per_month = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )

    max_leaves_per_quarter = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )

    min_gap_between_leaves_days = models.IntegerField(null=True, blank=True)

    # =========================================================
    # Accrual Configuration
    # =========================================================

    accrual_enabled = models.BooleanField(default=False)

    accrual_frequency = models.CharField(
        max_length=20, choices=AccrualFrequencyChoices.choices, null=True, blank=True
    )

    accrual_days = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )

    accrual_proration = models.BooleanField(default=True, null=True, blank=True)

    accrual_proration_basis = models.CharField(
        max_length=20,
        choices=AccrualProrationBasisChoices.choices,
        default=AccrualProrationBasisChoices.CALENDAR_DAYS,
        null=True,
        blank=True,
    )

    rounding_rule = models.CharField(
        max_length=10,
        choices=RoundingRuleChoices.choices,
        default=RoundingRuleChoices.FLOOR,
        null=True,
        blank=True,
    )

    # =========================================================
    # Negative Balance
    # =========================================================

    allow_negative_balance = models.BooleanField(default=False, null=True, blank=True)

    negative_balance_cap = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )

    # =========================================================
    # Short Leave
    # =========================================================

    short_leave_monthly_cap = models.IntegerField(default=0, null=True, blank=True)

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

    version = models.SmallIntegerField(default=1)

    class Meta:
        db_table = "mst_leave_policy_rules"

        indexes = [
            models.Index(fields=["policy"]),
            models.Index(fields=["leave_type"]),
            models.Index(fields=["grade"]),
            models.Index(fields=["employee_type"]),
        ]

        unique_together = [("policy", "leave_type", "grade", "employee_type")]

    def __str__(self):
        return f"{self.policy.name} - {self.leave_type.name}"


# =========================================================
# mst_employee_leave_policies
# =========================================================


class EmployeeLeavePolicy(models.Model):
    """
    Employee ↔ Leave Policy Mapping
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="leave_policies"
    )

    policy = models.ForeignKey(
        "leave.LeavePolicy", on_delete=models.CASCADE, related_name="employee_policies"
    )

    effective_from = models.DateField()

    effective_to = models.DateField(null=True, blank=True)

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

    version = models.SmallIntegerField(default=1)

    class Meta:
        db_table = "mst_employee_leave_policies"

        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["policy"]),
            models.Index(fields=["effective_from"]),
        ]

        unique_together = [("employee", "policy", "effective_from")]

    def __str__(self):
        return f"{self.employee} -> {self.policy.name}"
