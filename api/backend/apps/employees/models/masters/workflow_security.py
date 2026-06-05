"""
Workflow, Security & Notification Masters — C.7 from HRMS_ADMIN_SIDE.md

Tables (12):
  mst_workflow_type         — Workflow Types (LEAVE/EXPENSE/TRANSFER/PROMOTION...)
  mst_approval_action       — Approval Actions (APPROVE/REJECT/RETURN/ESCALATE/DELEGATE)
  mst_escalation_type       — Escalation Types (TIME_BASED/NO_RESPONSE/SLA_BREACH)
  mst_audit_event_type      — Audit Event Types (LOGIN/CREATE/UPDATE/DELETE/APPROVE...)
  mst_permission            — Granular Permission Master
  mst_menu_item             — Navigation Menu Master
  mst_data_scope_type       — Row-Level Data Scope Types
  mst_password_policy       — Password Policy Master
  mst_session_policy        — Session Policy Master
  mst_notification_channel  — Notification Channel (EMAIL/SMS/WHATSAPP/PUSH/IN_APP)
  mst_notification_template — Notification Template
  mst_notification_trigger  — Event-to-Template Mapping

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from ..base import CompanyMasterModel, FullAuditMasterModel


# ---------------------------------------------------------------------------
# mst_workflow_type
# ---------------------------------------------------------------------------


class WorkflowType(FullAuditMasterModel):
    """
    Workflow Types — LEAVE / EXPENSE / TRANSFER / PROMOTION / SEPARATION /
    LOAN / RECRUITMENT. Global master.
    Workflow Master (explicit in prompt).
    """

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    module = models.CharField(max_length=50)

    class Meta:
        db_table = "mst_workflow_type"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_wftype_code"),
            models.Index(fields=["module"], name="idx_mst_wftype_module"),
        ]


# ---------------------------------------------------------------------------
# mst_approval_action
# ---------------------------------------------------------------------------


class ApprovalAction(FullAuditMasterModel):
    """
    Approval Actions — APPROVE / REJECT / RETURN / ESCALATE / DELEGATE.
    is_positive: True = forward-moving action.
    Workflow Master (explicit in prompt).
    """

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_positive = models.BooleanField(default=True)

    class Meta:
        db_table = "mst_approval_action"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_appaction_code"),
        ]


# ---------------------------------------------------------------------------
# mst_escalation_type
# ---------------------------------------------------------------------------


class EscalationType(FullAuditMasterModel):
    """
    Escalation Types — TIME_BASED / NO_RESPONSE / SLA_BREACH.
    Workflow Master (explicit in prompt).
    """

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "mst_escalation_type"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_escaltype_code"),
        ]


# ---------------------------------------------------------------------------
# mst_audit_event_type
# ---------------------------------------------------------------------------


class AuditEventType(FullAuditMasterModel):
    """
    Audit Event Types — LOGIN / CREATE / UPDATE / DELETE / APPROVE / EXPORT / IMPORT.
    severity CHECK IN (INFO, WARNING, CRITICAL).
    """

    class Severity(models.TextChoices):
        INFO = "INFO", "Info"
        WARNING = "WARNING", "Warning"
        CRITICAL = "CRITICAL", "Critical"

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    severity = models.CharField(max_length=10, choices=Severity.choices)

    class Meta:
        db_table = "mst_audit_event_type"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_audevtype_code"),
            models.Index(fields=["severity"], name="idx_mst_audevtype_sev"),
        ]


# ---------------------------------------------------------------------------
# mst_permission
# ---------------------------------------------------------------------------


# class Permission(FullAuditMasterModel):
#     """
#     Granular Permission Master — module.action.resource triple.
#     permission_code UNIQUE: e.g. LEAVE.APPROVE.OWN_DEPT.
#     """

#     module = models.CharField(max_length=50)
#     action = models.CharField(max_length=30)
#     resource = models.CharField(max_length=100)
#     permission_code = models.CharField(max_length=120, unique=True)
#     description = models.TextField(null=True, blank=True)

#     class Meta:
#         db_table = "mst_permission"
#         indexes = [
#             models.Index(fields=["permission_code"], name="idx_mst_perm_code"),
#             models.Index(fields=["module"], name="idx_mst_perm_module"),
#             models.Index(fields=["action"], name="idx_mst_perm_action"),
#         ]


# ---------------------------------------------------------------------------
# mst_menu_item
# ---------------------------------------------------------------------------


# class MenuItem(FullAuditMasterModel):
#     """
#     Navigation Menu Master — hierarchical, self-referential.
#     parent_menu_id: logical FK → mst_menu_item (self).
#     code UNIQUE: LEAVE.APPLY / PAYROLL.RUN.
#     """

#     code = models.CharField(max_length=80, unique=True)
#     name = models.CharField(max_length=150)
#     # Self-referential logical FK
#     parent_menu_id = models.UUIDField(null=True, blank=True)
#     route_path = models.CharField(max_length=300, null=True, blank=True)
#     icon = models.CharField(max_length=100, null=True, blank=True)
#     sort_order = models.SmallIntegerField(default=0)
#     module = models.CharField(max_length=50)

#     class Meta:
#         db_table = "mst_menu_item"
#         ordering = ["sort_order"]
#         indexes = [
#             models.Index(fields=["code"], name="idx_mst_menu_code"),
#             models.Index(fields=["parent_menu_id"], name="idx_mst_menu_parent"),
#             models.Index(fields=["module"], name="idx_mst_menu_module"),
#         ]


# # ---------------------------------------------------------------------------
# # mst_data_scope_type
# # ---------------------------------------------------------------------------


# class DataScopeType(FullAuditMasterModel):
#     """
#     Row-Level Data Scope Types — ALL / REPORTEES / DEPARTMENT / BRANCH / SELF.
#     Used for row-level security (RBAC).
#     """

#     code = models.CharField(max_length=20, unique=True)
#     name = models.CharField(max_length=100)

#     class Meta:
#         db_table = "mst_data_scope_type"
#         indexes = [
#             models.Index(fields=["code"], name="idx_mst_datascope_code"),
#         ]


# ---------------------------------------------------------------------------
# mst_password_policy
# ---------------------------------------------------------------------------


class PasswordPolicy(CompanyMasterModel):
    """
    Password Policy Master — complexity rules per company.
    max_login_attempts: lockout threshold.
    """

    min_length = models.SmallIntegerField(default=8)
    max_length = models.SmallIntegerField(default=50)
    require_uppercase = models.BooleanField(default=True)
    require_digits = models.BooleanField(default=True)
    require_special = models.BooleanField(default=True)
    expiry_days = models.SmallIntegerField(default=90)
    history_count = models.SmallIntegerField(default=5)
    max_login_attempts = models.SmallIntegerField(default=5)

    class Meta:
        db_table = "mst_password_policy"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_pwdpol_co"),
        ]


# ---------------------------------------------------------------------------
# mst_session_policy
# ---------------------------------------------------------------------------


class SessionPolicy(CompanyMasterModel):
    """
    Session Policy Master — concurrent session limits, idle/absolute timeouts.
    enforce_ip_whitelist: restricts to whitelisted IPs.
    """

    max_sessions = models.SmallIntegerField(default=3)
    idle_timeout_minutes = models.SmallIntegerField(default=30)
    absolute_timeout_hours = models.SmallIntegerField(default=8)
    enforce_ip_whitelist = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_session_policy"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_sesspol_co"),
        ]


# ---------------------------------------------------------------------------
# mst_notification_channel  (must be before mst_notification_template)
# ---------------------------------------------------------------------------


class NotificationChannel(FullAuditMasterModel):
    """
    Notification Channel Master — EMAIL / SMS / WHATSAPP / PUSH / IN_APP.
    config_keys JSONB: channel-specific configuration schema.
    """

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    config_keys = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        db_table = "mst_notification_channel"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_ntfchannel_code"),
        ]


# ---------------------------------------------------------------------------
# mst_notification_template
# ---------------------------------------------------------------------------


class NotificationTemplate(CompanyMasterModel):
    """
    Notification Template — e.g. LEAVE_APPROVED / PAYSLIP_PUBLISHED.
    channel_id: logical FK → mst_notification_channel.
    body_template supports {{placeholder}} syntax.
    """

    code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=200)
    # Logical FK → mst_notification_channel
    channel_id = models.UUIDField(null=False, blank=False)
    subject_template = models.TextField(null=True, blank=True)
    body_template = models.TextField()

    class Meta:
        db_table = "mst_notification_template"
        indexes = [
            models.Index(fields=["company_id"], name="idx_mst_ntftmpl_co"),
            models.Index(fields=["channel_id"], name="idx_mst_ntftmpl_channel"),
            models.Index(fields=["code"], name="idx_mst_ntftmpl_code"),
        ]


# ---------------------------------------------------------------------------
# mst_notification_trigger
# ---------------------------------------------------------------------------


class NotificationTrigger(FullAuditMasterModel):
    """
    Event-to-Template Mapping — which template fires on which event.
    trigger_event: e.g. LEAVE.APPROVED / PAYROLL.LOCKED.
    recipient_type CHECK IN (EMPLOYEE, MANAGER, HR, ADMIN).
    notification_template_id: logical FK → mst_notification_template.
    """

    class RecipientType(models.TextChoices):
        EMPLOYEE = "EMPLOYEE", "Employee"
        MANAGER = "MANAGER", "Manager"
        HR = "HR", "HR"
        ADMIN = "ADMIN", "Admin"

    trigger_event = models.CharField(max_length=100)
    # Logical FK → mst_notification_template
    notification_template_id = models.UUIDField(null=False, blank=False)
    recipient_type = models.CharField(max_length=30, choices=RecipientType.choices)

    class Meta:
        db_table = "mst_notification_trigger"
        indexes = [
            models.Index(fields=["trigger_event"], name="idx_mst_ntftrig_event"),
            models.Index(
                fields=["notification_template_id"],
                name="idx_mst_ntftrig_tmpl",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["trigger_event", "notification_template_id", "recipient_type"],
                name="uq_mst_ntftrig_event_tmpl_rcpt",
            ),
        ]
