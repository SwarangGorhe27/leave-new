"""Compatibility aliases for legacy roster audit serializers."""

from rest_framework import serializers

from apps.attendance.serializers.audit_logs.audit_log_serializers import (
    AuditLogEntrySerializer,
    AuditLogListFilterSerializer,
)


class AuditLogActorSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True, allow_null=True)
    name = serializers.CharField(read_only=True, allow_null=True)
    email = serializers.EmailField(read_only=True, allow_null=True)


class AuditLogListItemSerializer(AuditLogEntrySerializer):
    pass


class AuditLogDetailSerializer(AuditLogEntrySerializer):
    pass


class RosterAuditLogFilterSerializer(AuditLogListFilterSerializer):
    pass
