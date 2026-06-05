"""
Serializers for Roster Lock/Freeze Operations.

Handles lock configuration and lock state management.
"""

from rest_framework import serializers
from typing import List
from uuid import UUID

from apps.attendance.models import RosterLockConfig, RosterLockState, RosterLockStatus
from apps.employees.models import Employee, Department


class RosterLockConfigSerializer(serializers.ModelSerializer):
    """Serializer for roster lock configuration."""

    class Meta:
        model = RosterLockConfig
        fields = [
            "id",
            "lock_date",
            "auto_lock_enabled",
            "grace_days",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RosterLockConfigCreateSerializer(serializers.Serializer):
    """Serializer for creating/updating lock configuration."""

    company_id = serializers.UUIDField(required=True)
    lock_date = serializers.IntegerField(required=True, min_value=1, max_value=31)
    auto_lock_enabled = serializers.BooleanField(required=True)
    grace_days = serializers.IntegerField(required=False, default=3, min_value=0, max_value=30)

    def validate_lock_date(self, value):
        """Validate lock date is valid day of month."""
        if not (1 <= value <= 31):
            raise serializers.ValidationError("Lock date must be between 1 and 31")
        return value


class RosterLockStateListSerializer(serializers.ModelSerializer):
    """List view: minimal lock state fields."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    locked_by_name = serializers.CharField(
        source="locked_by.first_name", read_only=True, allow_null=True
    )

    class Meta:
        model = RosterLockState
        fields = [
            "id",
            "lock_month",
            "lock_year",
            "status",
            "status_display",
            "is_locked",
            "locked_at",
            "locked_by_name",
        ]
        read_only_fields = fields


class RosterLockStateDetailSerializer(serializers.ModelSerializer):
    """Detail view: full lock state with audit trail."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    locked_by_detail = serializers.SerializerMethodField()
    unlocked_by_detail = serializers.SerializerMethodField()

    class Meta:
        model = RosterLockState
        fields = [
            "id",
            "lock_month",
            "lock_year",
            "department_ids",
            "status",
            "status_display",
            "is_locked",
            "locked_at",
            "locked_by_detail",
            "lock_reason",
            "unlocked_at",
            "unlocked_by_detail",
            "unlock_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_locked_by_detail(self, obj):
        if not obj.locked_by:
            return None
        return {
            "id": str(obj.locked_by.id),
            "name": f"{obj.locked_by.first_name} {obj.locked_by.last_name}",
            "email": obj.locked_by.email,
        }

    def get_unlocked_by_detail(self, obj):
        if not obj.unlocked_by:
            return None
        return {
            "id": str(obj.unlocked_by.id),
            "name": f"{obj.unlocked_by.first_name} {obj.unlocked_by.last_name}",
            "email": obj.unlocked_by.email,
        }


class RosterLockSerializer(serializers.Serializer):
    """Serializer for locking a roster."""

    company_id = serializers.UUIDField(required=True)
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True, min_value=2000, max_value=2099)
    department_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="Specific departments to lock (empty = all)",
    )
    lock_reason = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_department_ids(self, value):
        """Validate all departments exist."""
        if value:
            dept_ids = [str(d) for d in value]
            existing = Department.objects.filter(
                id__in=dept_ids, is_active=True, deleted_at__isnull=True
            ).count()
            if existing != len(value):
                raise serializers.ValidationError("Some departments not found or inactive")
        return value


class RosterUnlockSerializer(serializers.Serializer):
    """Serializer for unlocking a roster."""

    company_id = serializers.UUIDField(required=True)
    month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    year = serializers.IntegerField(required=True, min_value=2000, max_value=2099)
    unlock_reason = serializers.CharField(required=False, allow_blank=True, max_length=500)
