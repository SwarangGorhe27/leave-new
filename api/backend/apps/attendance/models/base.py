"""
Composable abstract bases for the Attendance app.

Design (v7 schema):
- Prefer small mixins (`UUIDPrimaryKeyMixin`, `TimeStampMixin`, …) and combine them
  per model instead of one “god” base.
- `AttendanceTenantModel` is an optional convenience abstract for the common
  tenant-scoped, audited, soft-deletable row shape used across many operational
  tables — use it only when that full shape matches the table; lean models
  (e.g. append-only logs) should compose fewer mixins.
"""

from __future__ import annotations

import uuid

from django.db import models


class UUIDPrimaryKeyMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class ActiveMixin(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class MetaDataMixin(models.Model):
    """Optional JSON bag for extensibility — attach only where needed."""

    meta_data = models.JSONField(null=True, blank=True, default=dict)

    class Meta:
        abstract = True


class CompanyScopedMixin(models.Model):
    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.PROTECT,
        db_column="company_id",
    )

    class Meta:
        abstract = True


class EmployeeAuditMixin(models.Model):
    """Schema: created_by / updated_by → employees(id)."""

    created_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        db_column="created_by",
    )
    updated_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        db_column="updated_by",
    )

    class Meta:
        abstract = True


class AttendanceTenantModel(
    UUIDPrimaryKeyMixin,
    CompanyScopedMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
):
    """
    Optional convenience base: UUID PK + company + timestamps + soft delete +
    is_active + employee audit FKs. Matches most `emp_*` / operational `mst_*` v7 rows.
    """

    class Meta:
        abstract = True


class AppendOnlyTimeStampMixin(models.Model):
    """Immutable ledger rows that only record insertion time."""

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
