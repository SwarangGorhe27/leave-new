# apps/leave/models/transaction/comp_off_requests.py

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class CompOffTypeChoices(models.TextChoices):
    FULL_DAY = "full_day", "Full Day"
    HALF_DAY = "half_day", "Half Day"


class EarnedAgainstTypeChoices(models.TextChoices):
    HOLIDAY = "holiday", "Holiday"
    WEEKEND = "weekend", "Weekend"
    OVERTIME = "overtime", "Overtime"


class CompOffStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    EXPIRED = "expired", "Expired"
    USED = "used", "Used"


class CompOffRequest(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="comp_off_requests"
    # )

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="comp_off_requests"
    )

    worked_date = models.DateField()

    comp_off_type = models.CharField(
        max_length=20,
        choices=CompOffTypeChoices.choices,
        default=CompOffTypeChoices.FULL_DAY,
    )

    earned_against_date_type = models.CharField(
        max_length=20, choices=EarnedAgainstTypeChoices.choices
    )

    reason = models.TextField(null=True, blank=True)

    proof_url = models.TextField(null=True, blank=True)

    earned_days = models.DecimalField(max_digits=4, decimal_places=2, default=1.00)

    expiry_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=CompOffStatusChoices.choices)

    used_days = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    approved_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_comp_offs",
    )

    notification_sent_expiry = models.BooleanField(default=False)

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
        db_table = "comp_off_requests"


# apps/leave/models/transaction/comp_off_usage_map.py

import uuid
from django.db import models


class CompOffUsageMap(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    comp_off_request = models.ForeignKey(
        "leave.CompOffRequest", on_delete=models.CASCADE, related_name="usage_mappings"
    )

    leave_request = models.ForeignKey(
        "leave.LeaveRequest", on_delete=models.CASCADE, related_name="comp_off_usages"
    )

    days_used = models.DecimalField(max_digits=4, decimal_places=2)

    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comp_off_usage_map"
