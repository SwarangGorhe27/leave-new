# apps/leave/models/transaction/short_leave_requests.py

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class ShortLeaveTimeSlotChoices(models.TextChoices):
    DAY_IN = "day_in", "Day In"
    DAY_OUT = "day_out", "Day Out"
    IN_BETWEEN = "in_between", "In Between"


class ShortLeaveStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class ShortLeaveRequest(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE
    # )

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="short_leave_requests",
    )

    policy = models.ForeignKey("leave.LeavePolicy", on_delete=models.PROTECT)

    policy_rule = models.ForeignKey(
        "leave.LeavePolicyRule", on_delete=models.SET_NULL, null=True, blank=True
    )

    leave_date = models.DateField()

    time_slot = models.CharField(
        max_length=30, choices=ShortLeaveTimeSlotChoices.choices
    )

    start_time = models.TimeField(null=True, blank=True)

    end_time = models.TimeField(null=True, blank=True)

    duration_hours = models.DecimalField(max_digits=4, decimal_places=2)

    reason = models.TextField(null=True, blank=True)

    reason_master = models.ForeignKey(
        "leave.Reason", on_delete=models.SET_NULL, null=True, blank=True
    )

    status = models.CharField(max_length=20, choices=ShortLeaveStatusChoices.choices)

    approved_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_short_leave_requests",
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
        db_table = "short_leave_requests"
