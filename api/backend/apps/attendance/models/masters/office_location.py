"""
Attendance workplace / geofence site (v7 `mst_office_location`).

The legacy `employees.OfficeLocation` already occupies `mst_office_location`
with a different primary-key and shape. This model uses a dedicated table so the
v7 UUID + geofence contract can be implemented without breaking Employee masters.
"""

from django.db import models

from apps.attendance.models.base import (
    ActiveMixin,
    CompanyScopedMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
    SoftDeleteMixin,
    TimeStampMixin,
    UUIDPrimaryKeyMixin,
)


class AttendanceOfficeLocation(
    UUIDPrimaryKeyMixin,
    CompanyScopedMixin,
    TimeStampMixin,
    SoftDeleteMixin,
    ActiveMixin,
    EmployeeAuditMixin,
    MetaDataMixin,
):
    branch = models.ForeignKey(
        "employees.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="branch_id",
        related_name="attendance_workplaces",
    )
    name = models.TextField()
    code = models.TextField()
    address_line1 = models.TextField(null=True, blank=True)
    address_line2 = models.TextField(null=True, blank=True)
    city = models.ForeignKey(
        "employees.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="city_id",
        related_name="attendance_workplaces",
    )
    state = models.ForeignKey(
        "employees.State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="state_id",
        related_name="attendance_workplaces",
    )
    country = models.ForeignKey(
        "employees.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="country_id",
        related_name="attendance_workplaces",
    )
    timezone = models.TextField(help_text="IANA zone, e.g. Asia/Kolkata")
    geofence_lat = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    geofence_lng = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    geofence_radius_m = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = "mst_attendance_office_location"
        indexes = [
            models.Index(fields=["company", "code"], name="idx_att_office_co_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="uq_att_office_co_code",
            ),
            models.CheckConstraint(
                check=models.Q(geofence_radius_m__gt=0)
                | models.Q(geofence_radius_m__isnull=True),
                name="chk_att_office_radius_pos",
            ),
        ]

    def __str__(self) -> str:
        return self.name
