"""
Roster Publish Log Model.

Tracks the publishing and unpublishing of shift rosters for employee visibility.
"""

from django.db import models
from apps.attendance.models.base import (
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    EmployeeAuditMixin,
    CompanyScopedMixin,
    MetaDataMixin,
)


class RosterPublishStatus(models.TextChoices):
    """Roster publish status."""
    DRAFT = "DRAFT", "Draft (Not Published)"
    PUBLISHED = "PUBLISHED", "Published (Visible to Employees)"


class EmpShiftRosterPublishLog(
    UUIDPrimaryKeyMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    EmployeeAuditMixin,
    CompanyScopedMixin,
    MetaDataMixin,
):
    """
    Shift roster publish audit log.
    
    Tracks publish/unpublish events for monthly rosters at company or department level.
    
    Columns:
    - id (UUID PK)
    - company_id (UUID FK)
    - publish_month (Integer) - Month (1-12)
    - publish_year (Integer) - Year (YYYY)
    - status (DRAFT | PUBLISHED)
    - published_count (Integer) - Number of rosters published
    - unpublished_count (Integer) - Number of rosters reverted to draft
    - department_ids (JSONB Array) - Departments published (empty = all)
    - is_locked (Boolean) - Whether roster is locked from edits
    - published_at (Timestamp) - When published
    - unpublished_at (Timestamp) - When unpublished/reverted
    - published_by_id (FK) - Who published
    - unpublished_by_id (FK) - Who reverted
    - note (Text) - Additional notes
    - created_at (Timestamp)
    - updated_at (Timestamp)
    - deleted_at (Timestamp) - Soft delete
    - created_by (FK)
    - updated_by (FK)
    - meta_data (JSONB)
    """

    publish_month = models.IntegerField(
        choices=[(i, f"Month {i}") for i in range(1, 13)],
        help_text="Month for which roster is published",
    )

    publish_year = models.IntegerField(
        help_text="Year for which roster is published",
    )

    status = models.CharField(
        max_length=20,
        choices=RosterPublishStatus.choices,
        default=RosterPublishStatus.DRAFT,
        help_text="Current publish status",
    )

    published_count = models.IntegerField(
        default=0,
        help_text="Number of rosters published in this event",
    )

    unpublished_count = models.IntegerField(
        default=0,
        help_text="Number of rosters reverted to draft",
    )

    department_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of department UUIDs published (empty = all departments)",
    )

    is_locked = models.BooleanField(
        default=False,
        help_text="Whether roster is locked from further edits",
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when published",
    )

    unpublished_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when unpublished/reverted",
    )

    published_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roster_publishes",
        db_column="published_by",
        help_text="Employee who published",
    )

    unpublished_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roster_unpublishes",
        db_column="unpublished_by",
        help_text="Employee who unpublished/reverted",
    )

    note = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or change log",
    )

    class Meta:
        db_table = "emp_shift_roster_publish_log"
        verbose_name = "Shift Roster Publish Log"
        verbose_name_plural = "Shift Roster Publish Logs"
        indexes = [
            models.Index(
                fields=["company", "publish_year", "publish_month"],
                name="idx_roster_company_period",
            ),
            models.Index(
                fields=["company", "status"],
                name="idx_roster_company_status",
            ),
            models.Index(
                fields=["published_at"],
                name="idx_roster_published_at",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "publish_year", "publish_month", "deleted_at"],
                condition=models.Q(deleted_at__isnull=True),
                name="uq_roster_publish_company_period",
            ),
        ]

    def __str__(self):
        return f"Roster {self.publish_month}/{self.publish_year} ({self.status})"
