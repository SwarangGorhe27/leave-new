# apps/leave/models/transaction/gate_pass_requests.py

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class GatePassMovementTypeChoices(models.TextChoices):
    WITHIN_OFFICE = "within_office", "Within Office"
    OUTSIDE_OFFICE = "outside_office", "Outside Office"
    CLIENT_LOCATION = "client_location", "Client Location"


class GatePassTypeChoices(models.TextChoices):
    START_OF_DAY = "start_of_day", "Start Of Day"
    END_OF_DAY = "end_of_day", "End Of Day"
    DURING_SHIFT = "during_shift", "During Shift"


class GatePassStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    ACTIVE = "active", "Active"
    RETURNED = "returned", "Returned"
    OVERDUE = "overdue", "Overdue"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class GatePassRequest(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey("core.Company", on_delete=models.CASCADE)

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="gate_pass_requests",
    )

    request_date = models.DateField(auto_now_add=True)

    purpose = models.CharField(max_length=100)

    purpose_type = models.ForeignKey("leave.Reason", on_delete=models.PROTECT)

    movement_type = models.CharField(
        max_length=30, choices=GatePassMovementTypeChoices.choices
    )

    from_location = models.CharField(max_length=200, null=True, blank=True)

    to_location = models.CharField(max_length=200, null=True, blank=True)

    pass_type = models.CharField(max_length=20, choices=GatePassTypeChoices.choices)

    start_time = models.TimeField()

    expected_return_time = models.TimeField(null=True, blank=True)

    actual_departure_time = models.TimeField(null=True, blank=True)

    actual_return_time = models.TimeField(null=True, blank=True)

    duration_minutes = models.IntegerField()

    delay_minutes = models.IntegerField(null=True, blank=True)

    impact_on_attendance = models.BooleanField(default=True)

    geo_lat_departure = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )

    geo_lng_departure = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )

    geo_lat_arrival = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )

    geo_lng_arrival = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )

    mobile_tracked = models.BooleanField(default=False)

    reason = models.TextField(null=True, blank=True)

    status = models.CharField(max_length=30, choices=GatePassStatusChoices.choices)

    approved_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_gate_pass_requests",
    )

    actioned_at = models.DateTimeField(null=True, blank=True)

    idempotency_key = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)

    created_by = models.UUIDField(null=True, blank=True)
    updated_by = models.UUIDField(null=True, blank=True)

    meta_data = models.JSONField(default=dict, blank=True)

    meta_tags = ArrayField(base_field=models.TextField(), default=list, blank=True)

    version = models.SmallIntegerField(default=1)

    class Meta:
        db_table = "gate_pass_requests"
