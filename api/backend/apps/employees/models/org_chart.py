"""
Org chart configuration per company (tenant-scoped via company FK).

Table: employee_org_chart_settings
"""

import uuid

from django.db import models

from apps.employees.models.base import MetadataMixin


class OrgChartSettings(MetadataMixin):
    """
    Stores the designated top-level (root) manager for org-chart visualization.
    One row per company.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.OneToOneField(
        "employees.Company",
        on_delete=models.CASCADE,
        db_column="company_id",
        related_name="org_chart_settings",
    )
    top_level_manager = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="top_level_manager_id",
        related_name="org_chart_root_for_companies",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_org_chart_settings"
        verbose_name = "Org Chart Settings"
        verbose_name_plural = "Org Chart Settings"

    def __str__(self) -> str:
        return f"OrgChartSettings({self.company_id})"
