# apps/leave/models/master/leave_types.py
"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
    2. Other foreign-key needs to be configured later as we further develop all the modules.
"""
import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class LeaveYearType(models.TextChoices):
    CALENDAR = "calendar", "Calendar"
    FISCAL = "fiscal", "Fiscal"
    CUSTOM = "custom", "Custom"


class GenderApplicability(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    ALL = "all", "All"


class LeaveType(models.Model):
    """
    Master Leave Type Configuration
    Example:
        - Sick Leave (SL)
        - Casual Leave (CL)
        - Privilege Leave (PL)
        - Maternity Leave (ML)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ###might not be needed as we will be going for db-per-tenant or schema-per-tenant
    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="leave_types"
    # )

    code = models.CharField(max_length=20)

    name = models.CharField(max_length=100)

    employee_type = models.ForeignKey(
        "employees.EmployeeType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_types",
        help_text="NULL means applicable to all employee types",
    )

    description = models.TextField(null=True, blank=True)

    # =========================
    # Leave Limits
    # =========================

    max_days_per_year = models.DecimalField(max_digits=5, decimal_places=2)

    max_consecutive_days = models.IntegerField(null=True, blank=True)

    # =========================
    # Carry Forward
    # =========================

    carry_forward_enabled = models.BooleanField(default=False)

    max_carry_forward_days = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    # =========================
    # Encashment
    # =========================

    encashable = models.BooleanField(default=False)

    # =========================
    # Attachment Rules
    # =========================

    requires_attachment = models.BooleanField(default=False)

    attachment_threshold_days = models.IntegerField(default=2, null=True, blank=True)

    # =========================
    # Application Rules
    # =========================

    min_notice_days = models.IntegerField(default=0)

    applicable_gender = models.CharField(
        max_length=20,
        choices=GenderApplicability.choices,
        default=GenderApplicability.ALL,
    )

    has_expiry = models.BooleanField(default=False)

    expiry_days = models.IntegerField(null=True, blank=True)

    is_paid = models.BooleanField(default=True)

    allow_half_day = models.BooleanField(default=False)

    allow_hourly = models.BooleanField(default=False)

    # =========================
    # Clubbing Rules
    # =========================

    is_clubbing_allowed = models.BooleanField(default=True, null=True, blank=True)

    clubbing_restricted_with = ArrayField(
        base_field=models.UUIDField(),
        null=True,
        blank=True,
        default=list,
        help_text="List of leave type UUIDs that cannot be clubbed",
    )

    # =========================
    # Backdate / Future Apply
    # =========================

    backdate_allowed_days = models.IntegerField(default=0, null=True, blank=True)

    future_apply_cap_days = models.IntegerField(null=True, blank=True)

    # =========================
    # Leave Year
    # =========================

    leave_year_type = models.CharField(
        max_length=20, choices=LeaveYearType.choices, null=True, blank=True
    )

    # =========================
    # UI Config
    # =========================

    color_code = models.CharField(
        max_length=7, null=True, blank=True, help_text="HEX Color Code"
    )

    # =========================
    # System Fields
    # =========================

    is_active = models.BooleanField(default=True)

    version = models.SmallIntegerField(default=1)

    # =========================
    # Metadata
    # =========================

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)

    created_by = models.UUIDField(null=True, blank=True)

    updated_by = models.UUIDField(null=True, blank=True)

    meta_data = models.JSONField(default=dict, blank=True)

    meta_tags = ArrayField(base_field=models.TextField(), default=list, blank=True)

    class Meta:
        db_table = "mst_leave_types"

        ordering = ["name"]

        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["code"]),
            models.Index(fields=["leave_year_type"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
