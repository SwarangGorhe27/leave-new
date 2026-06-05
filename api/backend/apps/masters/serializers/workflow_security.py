"""Serializers for workflow, security, and notification master APIs."""

from rest_framework import serializers

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


AUDIT_FIELDS = [
    "is_active",
    "created_by",
    "updated_by",
    "created_at",
    "updated_at",
    "deleted_at",
    "meta_data",
    "meta_version",
    "created_by_system",
    "updated_by_system",
    "created_source",
    "updated_source",
    "meta_tags",
    "extra_attributes",
]

READ_ONLY_AUDIT_FIELDS = [
    "id",
    "created_by",
    "updated_by",
    "created_at",
    "updated_at",
    "deleted_at",
]


def _validate_unique_code(value, model, instance=None, company_id=None):
    value = value.strip().upper()
    qs = model.objects.filter(code__iexact=value)
    if company_id:
        qs = qs.filter(company_id=company_id)
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError(
            f"A record with code '{value}' already exists."
        )
    return value


class GlobalCodeMixin:
    def validate_code(self, value):
        return _validate_unique_code(value, self.Meta.model, self.instance)


class CompanyScopedCodeMixin:
    def validate_code(self, value):
        company_id = (
            self.initial_data.get("company_id")
            or getattr(self.instance, "company_id", None)
        )
        return _validate_unique_code(
            value,
            self.Meta.model,
            self.instance,
            company_id=company_id,
        )


class NameListSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "code", "name", "is_active"]


class WorkflowTypeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = WorkflowType
        fields = ["id", "code", "name", "module", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class WorkflowTypeListSerializer(NameListSerializer):
    class Meta(NameListSerializer.Meta):
        model = WorkflowType
        fields = ["id", "code", "name", "module", "is_active"]


class ApprovalActionSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = ApprovalAction
        fields = ["id", "code", "name", "is_positive", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class ApprovalActionListSerializer(NameListSerializer):
    class Meta(NameListSerializer.Meta):
        model = ApprovalAction
        fields = ["id", "code", "name", "is_positive", "is_active"]


class EscalationTypeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = EscalationType
        fields = ["id", "code", "name", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class EscalationTypeListSerializer(NameListSerializer):
    class Meta(NameListSerializer.Meta):
        model = EscalationType


class AuditEventTypeSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = AuditEventType
        fields = ["id", "code", "name", "severity", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class AuditEventTypeListSerializer(NameListSerializer):
    class Meta(NameListSerializer.Meta):
        model = AuditEventType
        fields = ["id", "code", "name", "severity", "is_active"]


class PasswordPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordPolicy
        fields = [
            "id",
            "company_id",
            "min_length",
            "max_length",
            "require_uppercase",
            "require_digits",
            "require_special",
            "expiry_days",
            "history_count",
            "max_login_attempts",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate(self, attrs):
        min_length = attrs.get("min_length", getattr(self.instance, "min_length", None))
        max_length = attrs.get("max_length", getattr(self.instance, "max_length", None))
        if min_length is not None and max_length is not None and max_length < min_length:
            raise serializers.ValidationError(
                {"max_length": "max_length must be greater than or equal to min_length."}
            )
        return attrs


class PasswordPolicyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordPolicy
        fields = [
            "id",
            "company_id",
            "min_length",
            "max_length",
            "expiry_days",
            "max_login_attempts",
            "is_active",
        ]


class SessionPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionPolicy
        fields = [
            "id",
            "company_id",
            "max_sessions",
            "idle_timeout_minutes",
            "absolute_timeout_hours",
            "enforce_ip_whitelist",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class SessionPolicyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionPolicy
        fields = [
            "id",
            "company_id",
            "max_sessions",
            "idle_timeout_minutes",
            "absolute_timeout_hours",
            "enforce_ip_whitelist",
            "is_active",
        ]


class NotificationChannelSerializer(GlobalCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = NotificationChannel
        fields = ["id", "code", "name", "config_keys", *AUDIT_FIELDS]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class NotificationChannelListSerializer(NameListSerializer):
    class Meta(NameListSerializer.Meta):
        model = NotificationChannel
        fields = ["id", "code", "name", "config_keys", "is_active"]


class NotificationTemplateSerializer(CompanyScopedCodeMixin, serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "channel_id",
            "subject_template",
            "body_template",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS


class NotificationTemplateListSerializer(NameListSerializer):
    class Meta(NameListSerializer.Meta):
        model = NotificationTemplate
        fields = [
            "id",
            "company_id",
            "code",
            "name",
            "channel_id",
            "is_active",
        ]


class NotificationTriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTrigger
        fields = [
            "id",
            "trigger_event",
            "notification_template_id",
            "recipient_type",
            *AUDIT_FIELDS,
        ]
        read_only_fields = READ_ONLY_AUDIT_FIELDS

    def validate(self, attrs):
        trigger_event = attrs.get(
            "trigger_event",
            getattr(self.instance, "trigger_event", None),
        )
        notification_template_id = attrs.get(
            "notification_template_id",
            getattr(self.instance, "notification_template_id", None),
        )
        recipient_type = attrs.get(
            "recipient_type",
            getattr(self.instance, "recipient_type", None),
        )
        if not (trigger_event and notification_template_id and recipient_type):
            return attrs

        qs = NotificationTrigger.objects.filter(
            trigger_event__iexact=trigger_event,
            notification_template_id=notification_template_id,
            recipient_type=recipient_type,
        )
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A notification trigger already exists for this event, template, and recipient."
            )
        return attrs


class NotificationTriggerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTrigger
        fields = [
            "id",
            "trigger_event",
            "notification_template_id",
            "recipient_type",
            "is_active",
        ]
