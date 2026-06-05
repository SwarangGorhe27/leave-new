"""
Admin setup employee segments.

Segments are saved targeting groups used by setup workflows such as policies,
communication, and approvals. A segment can be dynamic (rule/filter based) or a
manual list of employee members.
"""

from django.db import models

from apps.employees.models.base import BaseModel


class EmployeeSegment(BaseModel):
    class SourceMode(models.TextChoices):
        FILTER = "FILTER", "Based on employee filter criteria"
        MANUAL = "MANUAL", "Manual, ad hoc list of employees"

    company = models.ForeignKey(
        "employees.Company",
        on_delete=models.PROTECT,
        db_column="company_id",
        related_name="employee_segments",
    )
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=60)
    source_mode = models.CharField(
        max_length=20,
        choices=SourceMode.choices,
        default=SourceMode.FILTER,
    )
    employee_filter = models.ForeignKey(
        "employees.EmployeeFilter",
        on_delete=models.SET_NULL,
        db_column="employee_filter_id",
        related_name="segments",
        null=True,
        blank=True,
    )
    rule_config = models.JSONField(default=dict, blank=True)
    member_count = models.PositiveIntegerField(default=0)
    created_by = models.UUIDField(null=True, blank=True)
    updated_by = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "employee_segments"
        verbose_name = "Employee Segment"
        verbose_name_plural = "Employee Segments"
        ordering = ["title"]
        indexes = [
            models.Index(fields=["company", "source_mode", "is_active"], name="idx_empseg_co_src_actv"),
            models.Index(fields=["company", "code"], name="idx_empseg_co_code"),
            models.Index(fields=["employee_filter"], name="idx_empseg_filter"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="uq_empseg_co_code",
            ),
        ]

    def __str__(self) -> str:
        return self.title


class EmployeeSegmentMember(BaseModel):
    segment = models.ForeignKey(
        EmployeeSegment,
        on_delete=models.CASCADE,
        db_column="segment_id",
        related_name="member_links",
    )
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="segment_links",
    )

    class Meta:
        db_table = "employee_segment_members"
        verbose_name = "Employee Segment Member"
        verbose_name_plural = "Employee Segment Members"
        indexes = [
            models.Index(fields=["segment"], name="idx_empsegmem_segment"),
            models.Index(fields=["employee"], name="idx_empsegmem_employee"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["segment", "employee"],
                name="uq_empsegmem_segment_employee",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.segment_id} - {self.employee_id}"
