"""Serializers for attendance notification APIs."""

from __future__ import annotations

from rest_framework import serializers

from apps.attendance.models import AttendanceNotification
from apps.attendance.validators.notification_validators import (
    validate_notification_type,
    validate_reference_table,
)


class NotificationListFilterSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    recipient_id = serializers.UUIDField(required=True)
    is_read = serializers.BooleanField(required=False)
    notification_type = serializers.CharField(required=False, allow_blank=False)

    def validate_notification_type(self, value):
        return validate_notification_type(value)


class NotificationRecipientActionSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    recipient_id = serializers.UUIDField(required=True)


class NotificationReadAllSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    recipient_id = serializers.UUIDField(required=True)
    notification_type = serializers.CharField(required=False, allow_blank=False)

    def validate_notification_type(self, value):
        return validate_notification_type(value)


class NotificationSendSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=True)
    recipient_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )
    notification_type = serializers.CharField(required=True)
    reference_table = serializers.CharField(required=True)
    reference_id = serializers.UUIDField(required=True)
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    triggered_by_id = serializers.UUIDField(required=False, allow_null=True)

    def validate_notification_type(self, value):
        return validate_notification_type(value)

    def validate_reference_table(self, value):
        return validate_reference_table(value)


class NotificationListItemSerializer(serializers.ModelSerializer):
    triggered_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceNotification
        fields = [
            "id",
            "notification_type",
            "reference_table",
            "reference_id",
            "message",
            "triggered_by",
            "triggered_by_name",
            "sent_at",
            "is_read",
            "read_at",
        ]

    def get_triggered_by_name(self, obj):
        if not obj.triggered_by:
            return None
        return obj.triggered_by.full_name


class NotificationUnreadCountSerializer(serializers.Serializer):
    unread_count = serializers.IntegerField()
    by_type = serializers.ListField()


class NotificationSendResponseSerializer(serializers.Serializer):
    sent_count = serializers.IntegerField()
    notification_ids = serializers.ListField(child=serializers.UUIDField())
