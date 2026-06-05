"""Tier-1 attendance policy masters (`mst_attendance_policy`, `mst_regularization_reason`)."""

import uuid

from django.db import models

from apps.employees.models.base import CompanyMasterModel


class AttendancePolicy(models.Model):
    """
    Versioned attendance policy row (v7). `is_current` marks the active row
    for a logical policy name within a company. `AttendanceScheme` links here
    via `attendance_policy_id`.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.CASCADE,
        db_column="company_id",
        related_name="attendance_policies",
    )
    name = models.TextField()
    version = models.PositiveIntegerField(default=1)
    is_current = models.BooleanField(default=True)
    employment_type = models.ForeignKey(
        "employees.EmployeeType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="employment_type_id",
        related_name="attendance_policies",
    )
    late_login_cycle_limit = models.PositiveIntegerField(default=3)
    late_login_grace_mins = models.PositiveIntegerField(default=0)
    late_login_max_grace_mins = models.PositiveIntegerField(default=0)
    early_exit_max_grace_mins = models.PositiveIntegerField(default=0)
    short_leave_max_mins = models.PositiveIntegerField(default=0)
    monthly_grace_instance_limit = models.PositiveIntegerField(default=0)
    half_day_min_work_mins = models.PositiveIntegerField(default=240)
    half_day_min_mins = models.PositiveIntegerField(default=240)
    half_day_max_mins = models.PositiveIntegerField(default=360)
    full_day_min_mins = models.PositiveIntegerField(default=480)
    lop_deduction_unit = models.DecimalField(max_digits=3, decimal_places=2, default="1.00")
    ot_enabled = models.BooleanField(default=False)
    ot_min_mins = models.PositiveIntegerField(null=True, blank=True)
    max_regularizations_month = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="created_by",
        related_name="attendance_policies_created",
    )
    updated_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="updated_by",
        related_name="attendance_policies_updated",
    )
    is_active = models.BooleanField(default=True)
    meta_data = models.JSONField(null=True, blank=True, default=dict)

    class Meta:
        db_table = "mst_attendance_policy"
        indexes = [
            models.Index(fields=["company", "name"], name="idx_mst_attpol_co_name"),
            models.Index(fields=["company", "is_current"], name="idx_mst_attpol_co_cur"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name", "version"],
                name="uq_mst_attpol_co_name_ver",
            ),
            models.UniqueConstraint(
                fields=["company", "name"],
                condition=models.Q(is_current=True),
                name="uq_mst_attpol_current_name",
            ),
        ]


class RegularizationReason(CompanyMasterModel):
    """
    Company-scoped pick-list — matches legacy `mst_regularization_reason` (UUID PK,
    `company_id`, full metadata block from `CompanyMasterModel`).
    """

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=150)

    class Meta:
        db_table = "mst_regularization_reason"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_regreason_co"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"],
                name="uq_mst_regreason_co_code",
            ),
        ]

    def __str__(self) -> str:
        return self.name
