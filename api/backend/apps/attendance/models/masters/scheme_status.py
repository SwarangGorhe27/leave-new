"""Tier-1 attendance scheme and day-status masters (`mst_attendance_scheme`, `mst_attendance_status`)."""

import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.employees.models.base import CompanyMasterModel


class AttendanceScheme(CompanyMasterModel):
    """
    Attendance scheme label — GENERAL / CONTRACT / PROBATION / TRAINEE.
    Links to `AttendancePolicy` when configured.
    """

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    attendance_policy = models.ForeignKey(
        "attendance.AttendancePolicy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="attendance_policy_id",
        related_name="attendance_schemes",
    )

    class Meta:
        db_table = "mst_attendance_scheme"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_attscheme_co"),
            models.Index(fields=["attendance_policy"], name="idx_mst_attscheme_pol"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "code"], name="uq_mst_attscheme_co_code"
            ),
        ]


class AttendanceStatus(models.Model):
    """
    Day-status master — matches legacy `mst_attendance_status` (UUID PK + metadata)
    created by `employees.0001_initial` so FKs from `emp_daily_attendance` stay uuid.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_paid = models.BooleanField(default=True)
    is_present_equivalent = models.BooleanField(default=False)
    counts_as_leave = models.BooleanField(default=False)
    sort_order = models.SmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.UUIDField(null=True, blank=True)
    updated_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    meta_data = models.JSONField(null=True, blank=True, default=dict)
    meta_version = models.IntegerField(default=1)
    created_by_system = models.CharField(
        max_length=50, default="SYSTEM", blank=True, null=True
    )
    updated_by_system = models.CharField(
        max_length=50, default="SYSTEM", blank=True, null=True
    )
    created_source = models.CharField(max_length=50, blank=True, null=True)
    updated_source = models.CharField(max_length=50, blank=True, null=True)
    meta_tags = ArrayField(models.TextField(), blank=True, null=True)
    extra_attributes = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        db_table = "mst_attendance_status"
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["code"], name="idx_mst_attstatus_code"),
        ]

    def __str__(self) -> str:
        return self.name
