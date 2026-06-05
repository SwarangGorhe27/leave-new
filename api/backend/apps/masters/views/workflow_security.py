"""ViewSets for workflow, security, and notification master APIs."""

from apps.employees.models.masters.workflow_security import (
    ApprovalAction,
    AuditEventType,
    EscalationType,
    NotificationChannel,
    NotificationTemplate,
    NotificationTrigger,
    PasswordPolicy,
    SessionPolicy,
    WorkflowType,
)
from apps.masters.serializers.workflow_security import (
    ApprovalActionListSerializer,
    ApprovalActionSerializer,
    AuditEventTypeListSerializer,
    AuditEventTypeSerializer,
    EscalationTypeListSerializer,
    EscalationTypeSerializer,
    NotificationChannelListSerializer,
    NotificationChannelSerializer,
    NotificationTemplateListSerializer,
    NotificationTemplateSerializer,
    NotificationTriggerListSerializer,
    NotificationTriggerSerializer,
    PasswordPolicyListSerializer,
    PasswordPolicySerializer,
    SessionPolicyListSerializer,
    SessionPolicySerializer,
    WorkflowTypeListSerializer,
    WorkflowTypeSerializer,
)
from apps.masters.views.base import ActiveMasterViewSet


def _bool_param(request, name):
    value = request.query_params.get(name, "").lower()
    if value in ("true", "false"):
        return value == "true"
    return None


def _actor_employee_id(request):
    user = getattr(request, "user", None)
    employee = getattr(user, "employee_profile", None)
    return getattr(employee, "id", None)


class WorkflowSecurityMasterViewSet(ActiveMasterViewSet):
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]
    search_lookup_fields = ("code", "name")
    display_field = "name"

    def perform_create(self, serializer):
        actor_id = _actor_employee_id(self.request)
        save_kwargs = {}
        if actor_id:
            save_kwargs["created_by"] = actor_id
            save_kwargs["updated_by"] = actor_id
        serializer.save(**save_kwargs)

    def perform_update(self, serializer):
        actor_id = _actor_employee_id(self.request)
        if actor_id:
            serializer.save(updated_by=actor_id)
            return
        serializer.save()


class CompanyFilteredMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.request.query_params.get("company_id"):
            qs = qs.filter(company_id=company_id)
        return qs


class WorkflowTypeViewSet(WorkflowSecurityMasterViewSet):
    queryset = WorkflowType.objects.all()
    serializer_class = WorkflowTypeSerializer
    list_serializer_class = WorkflowTypeListSerializer
    search_fields = ["code", "name", "module"]

    def get_queryset(self):
        qs = super().get_queryset()
        if module := self.request.query_params.get("module"):
            qs = qs.filter(module__iexact=module)
        return qs


class ApprovalActionViewSet(WorkflowSecurityMasterViewSet):
    queryset = ApprovalAction.objects.all()
    serializer_class = ApprovalActionSerializer
    list_serializer_class = ApprovalActionListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        is_positive = _bool_param(self.request, "is_positive")
        if is_positive is not None:
            qs = qs.filter(is_positive=is_positive)
        return qs


class EscalationTypeViewSet(WorkflowSecurityMasterViewSet):
    queryset = EscalationType.objects.all()
    serializer_class = EscalationTypeSerializer
    list_serializer_class = EscalationTypeListSerializer


class AuditEventTypeViewSet(WorkflowSecurityMasterViewSet):
    queryset = AuditEventType.objects.all()
    serializer_class = AuditEventTypeSerializer
    list_serializer_class = AuditEventTypeListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if severity := self.request.query_params.get("severity", "").upper():
            qs = qs.filter(severity=severity)
        return qs


class PasswordPolicyViewSet(CompanyFilteredMixin, WorkflowSecurityMasterViewSet):
    queryset = PasswordPolicy.objects.all()
    serializer_class = PasswordPolicySerializer
    list_serializer_class = PasswordPolicyListSerializer
    search_fields = []
    ordering_fields = [
        "company_id",
        "min_length",
        "max_length",
        "expiry_days",
        "max_login_attempts",
        "created_at",
    ]
    ordering = ["company_id"]
    search_lookup_fields = ()
    display_field = "company_id"

    def get_queryset(self):
        qs = super().get_queryset()
        for field in ("min_length", "max_length", "expiry_days", "max_login_attempts"):
            if value := self.request.query_params.get(field):
                qs = qs.filter(**{field: value})
        return qs


class SessionPolicyViewSet(CompanyFilteredMixin, WorkflowSecurityMasterViewSet):
    queryset = SessionPolicy.objects.all()
    serializer_class = SessionPolicySerializer
    list_serializer_class = SessionPolicyListSerializer
    search_fields = []
    ordering_fields = [
        "company_id",
        "max_sessions",
        "idle_timeout_minutes",
        "absolute_timeout_hours",
        "created_at",
    ]
    ordering = ["company_id"]
    search_lookup_fields = ()
    display_field = "company_id"

    def get_queryset(self):
        qs = super().get_queryset()
        for field in ("max_sessions", "idle_timeout_minutes", "absolute_timeout_hours"):
            if value := self.request.query_params.get(field):
                qs = qs.filter(**{field: value})
        enforce_ip_whitelist = _bool_param(self.request, "enforce_ip_whitelist")
        if enforce_ip_whitelist is not None:
            qs = qs.filter(enforce_ip_whitelist=enforce_ip_whitelist)
        return qs


class NotificationChannelViewSet(WorkflowSecurityMasterViewSet):
    queryset = NotificationChannel.objects.all()
    serializer_class = NotificationChannelSerializer
    list_serializer_class = NotificationChannelListSerializer


class NotificationTemplateViewSet(CompanyFilteredMixin, WorkflowSecurityMasterViewSet):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    list_serializer_class = NotificationTemplateListSerializer
    search_fields = ["code", "name", "subject_template", "body_template"]

    def get_queryset(self):
        qs = super().get_queryset()
        if channel_id := self.request.query_params.get("channel_id"):
            qs = qs.filter(channel_id=channel_id)
        return qs


class NotificationTriggerViewSet(WorkflowSecurityMasterViewSet):
    queryset = NotificationTrigger.objects.all()
    serializer_class = NotificationTriggerSerializer
    list_serializer_class = NotificationTriggerListSerializer
    search_fields = ["trigger_event", "recipient_type"]
    ordering_fields = [
        "trigger_event",
        "recipient_type",
        "notification_template_id",
        "created_at",
    ]
    ordering = ["trigger_event", "recipient_type"]
    search_lookup_fields = ("trigger_event", "recipient_type")
    display_field = "trigger_event"

    def get_queryset(self):
        qs = super().get_queryset()
        if trigger_event := self.request.query_params.get("trigger_event"):
            qs = qs.filter(trigger_event__iexact=trigger_event)
        if template_id := self.request.query_params.get("notification_template_id"):
            qs = qs.filter(notification_template_id=template_id)
        if recipient_type := self.request.query_params.get("recipient_type", "").upper():
            qs = qs.filter(recipient_type=recipient_type)
        return qs
