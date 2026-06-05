# apps/subscriptions/models.py

import uuid
from django.db import models
from django.utils import timezone


# ──────────────────────────────────────────────
# Available Modules Registry
# ──────────────────────────────────────────────

AVAILABLE_MODULES = [
    "employees",
    "attendance",
    "leave",
    "payroll",
    "documents",
    "forms_builder",
    "biometric",
    "canteen",
    "hr_setup",
    "workflow",
    "recruitment",
    "performance",
    "training",
    "assets",
    "lifecycle",
    "security",
    "notifications",
]


MODULE_CHOICES = [
    ("employees", "Employees"),
    ("attendance", "Attendance"),
    ("leave", "Leave"),
    ("payroll", "Payroll"),
    ("documents", "Documents"),
    ("forms_builder", "Forms Builder"),
    ("biometric", "Biometric"),
    ("canteen", "Canteen"),
    ("hr_setup", "HR Setup"),
    ("workflow", "Workflow"),
    ("recruitment", "Recruitment"),
    ("performance", "Performance"),
    ("training", "Training"),
    ("assets", "Assets"),
    ("lifecycle", "Lifecycle"),
    ("security", "Security"),
    ("notifications", "Notifications"),
]


# ──────────────────────────────────────────────
# Plan-wise Default Modules
# ──────────────────────────────────────────────

PLAN_MODULES = {
    "STARTER": [
        "employees",
        "attendance",
        "leave",
    ],
    "PROFESSIONAL": [
        "employees",
        "attendance",
        "leave",
        "payroll",
        "documents",
        "workflow",
        "notifications",
        "recruitment",
    ],
    "ENTERPRISE": AVAILABLE_MODULES.copy(),
}


# ──────────────────────────────────────────────
# Subscription Model
# ──────────────────────────────────────────────


class Subscription(models.Model):

    class BillingCycle(models.TextChoices):
        MONTHLY = "MONTHLY", "Monthly"
        ANNUAL = "ANNUAL", "Annual"

    class Status(models.TextChoices):
        TRIAL = "TRIAL", "Trial"
        ACTIVE = "ACTIVE", "Active"
        SUSPENDED = "SUSPENDED", "Suspended"
        CANCELLED = "CANCELLED", "Cancelled"

    class PlanTier(models.TextChoices):
        STARTER = "STARTER", "Starter"
        PROFESSIONAL = "PROFESSIONAL", "Professional"
        ENTERPRISE = "ENTERPRISE", "Enterprise"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    client = models.OneToOneField(
        "core.Tenant",  # change if your app label differs
        on_delete=models.CASCADE,
        related_name="subscription",
    )

    plan_tier = models.CharField(
        max_length=20,
        choices=PlanTier.choices,
        default=PlanTier.STARTER,
    )

    billing_cycle = models.CharField(
        max_length=20,
        choices=BillingCycle.choices,
        default=BillingCycle.MONTHLY,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TRIAL,
    )

    enabled_modules = models.JSONField(
        default=list,
        help_text="List of enabled module codes",
    )

    current_period_start = models.DateField()

    current_period_end = models.DateField()

    is_trial = models.BooleanField(default=True)

    max_employees = models.PositiveIntegerField(
        default=50,
    )

    max_storage_gb = models.PositiveIntegerField(
        default=5,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "subscriptions"

    def __str__(self):
        return f"{self.client.company_name} - {self.plan_tier}"

    @property
    def is_active(self):
        return (
            self.status in ["TRIAL", "ACTIVE"]
            and self.current_period_end >= timezone.now().date()
        )

    def has_module(self, module_name: str) -> bool:
        return module_name in self.enabled_modules

    @property
    def modules(self):
        return self.enabled_modules


    def enable_module(self, module_name):

        if module_name not in self.enabled_modules:
            self.enabled_modules.append(module_name)
            self.save(update_fields=["enabled_modules"])


    def disable_module(self, module_name):

        self.enabled_modules = [
            module
            for module in self.enabled_modules
            if module != module_name
        ]

        self.save(update_fields=["enabled_modules"])