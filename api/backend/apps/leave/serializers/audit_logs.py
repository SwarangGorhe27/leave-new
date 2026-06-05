from rest_framework import serializers

from ..models.system_and_audit.audit_logs import AuditLogs


class AuditLogSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()

    class Meta:
        model = AuditLogs
        fields = [
            "id",
            "actor",
            "module",
            "action",
            "action_category",
            "table_name",
            "record_id",
            "old_values",
            "new_values",
            "data_classification",
            "created_at",
        ]

    def get_actor(self, obj):
        actor = obj.actor
        if actor is None:
            return None
        return {
            "id": str(actor.id),
            "employee_code": getattr(actor, "employee_code", None),
            "name": getattr(actor, "full_name", None) or str(actor),
        }
