"""
ISSUES:- 
    1. company.id might not be needed as we will be going for db-per-tenant or schema-per-tenant.
    2. employee FK needs to be configured later.
"""

# apps/leave/models/workflow/leave_delegations.py

"""
================================================================================
MODEL: leave_delegations
================================================================================

Purpose:
--------
Stores temporary approval delegation mappings.

This table enables one employee to delegate approval authority
to another employee for a specific period.

Why this table is important:
----------------------------
In enterprise systems, approvers may:
    - go on leave
    - travel
    - resign
    - become unavailable
    - change departments temporarily

Approval workflows must continue uninterrupted.

Example:
---------
Manager A:
    unavailable from 1 May → 10 May

Delegates approvals to:
    Manager B

Now:
    - leave approvals
    - gate pass approvals
    - workflow actions

can continue without bottlenecks.

Why separate delegation table:
------------------------------
Delegation is:
    - temporary
    - time-bound
    - scope-based
    - auditable

Storing this inside employee table becomes messy.

Scope Examples:
---------------
1. all
    Delegate everything

2. leave_only
    Only leave approvals

3. gate_pass_only
    Only gate pass approvals

Production Usage:
-----------------
Used heavily in:
    - approval workflow engine
    - escalation engine
    - manager inbox APIs
    - workflow routing
    - audit systems

Important Workflow Logic:
-------------------------
At runtime:
    If:
        approver unavailable
    AND:
        active delegation exists
    THEN:
        approval routed to delegate

Security Importance:
--------------------
Delegation must ALWAYS:
    - be time-bound
    - be auditable
    - respect tenant boundaries
    - support revocation

================================================================================
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


# =========================================================
# ENUMS
# =========================================================


class DelegationScopeChoices(models.TextChoices):
    ALL = "all", "All"
    LEAVE_ONLY = "leave_only", "Leave Only"
    GATE_PASS_ONLY = "gate_pass_only", "Gate Pass Only"


# =========================================================
# MODEL
# =========================================================


class LeaveDelegation(models.Model):
    """
    Temporary Approval Delegation Mapping
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # =========================================================
    # Tenant Scope
    # =========================================================

    # company = models.ForeignKey(
    #     "core.Company",
    #     on_delete=models.CASCADE,
    #     related_name="leave_delegations"
    # )

    # =========================================================
    # Delegation Information
    # =========================================================

    delegator = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="delegated_approvals",
        help_text="Original approver",
    )

    delegate = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="received_delegations",
        help_text="Temporary approver",
    )

    # =========================================================
    # Delegation Duration
    # =========================================================

    from_date = models.DateField()

    to_date = models.DateField()

    # =========================================================
    # Delegation Scope
    # =========================================================

    scope = models.CharField(
        max_length=50,
        choices=DelegationScopeChoices.choices,
        default=DelegationScopeChoices.ALL,
    )

    # =========================================================
    # Status
    # =========================================================

    is_active = models.BooleanField(default=True)

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

    # =========================================================
    # Meta Config
    # =========================================================

    class Meta:
        db_table = "leave_delegations"

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["delegator"]),
            models.Index(fields=["delegate"]),
            models.Index(fields=["from_date"]),
            models.Index(fields=["to_date"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["scope"]),
        ]

        unique_together = [("delegator", "delegate", "from_date", "to_date")]

    # =========================================================
    # String Representation
    # =========================================================

    def __str__(self):
        return (
            f"{self.delegator} → "
            f"{self.delegate} "
            f"({self.from_date} - {self.to_date})"
        )
