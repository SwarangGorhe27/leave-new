# apps/leave/models/transaction/wfh_requests.py

"""
================================================================================
MODEL: wfh_requests
================================================================================

Purpose:
--------
Dedicated Work From Home request table.

Why separate table:
-------------------
WFH contains validations that do not belong in leave_requests.

Examples:
---------
- VPN validation
- connectivity validation
- work location type
- remote work compliance

Keeping WFH separate:
    - keeps leave module clean
    - improves reporting
    - simplifies workflows

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class WFHLocationTypeChoices(models.TextChoices):
    HOME = "home", "Home"
    CLIENT_SITE = "client_site", "Client Site"
    CO_WORKING = "co_working", "Co Working"


class WFHStatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class WFHRequest(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="wfh_requests"
    # )

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.CASCADE, related_name="wfh_requests"
    )

    from_date = models.DateField()

    to_date = models.DateField()

    total_days = models.DecimalField(max_digits=5, decimal_places=2)

    work_location_type = models.CharField(
        max_length=30, choices=WFHLocationTypeChoices.choices
    )

    vpn_confirmed = models.BooleanField(default=False)

    connectivity_confirmed = models.BooleanField(default=False)

    reason = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=WFHStatusChoices.choices,
        default=WFHStatusChoices.PENDING,
    )

    approved_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_wfh_requests",
    )

    actioned_at = models.DateTimeField(null=True, blank=True)

    idempotency_key = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )

    # =========================================================
    # Metadata
    # =========================================================

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)

    created_by = models.UUIDField(null=True, blank=True)

    updated_by = models.UUIDField(null=True, blank=True)

    meta_data = models.JSONField(default=dict, blank=True)

    meta_tags = ArrayField(base_field=models.TextField(), default=list, blank=True)

    version = models.SmallIntegerField(default=1)

    class Meta:
        db_table = "wfh_requests"

        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["status"]),
        ]
