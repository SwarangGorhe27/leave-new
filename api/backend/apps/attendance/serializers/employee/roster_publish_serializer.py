"""
Serializers for Roster Publish Operations.

Handles publish, unpublish, and status check operations.
"""

from rest_framework import serializers
from typing import List, Optional
from uuid import UUID

from apps.attendance.models import EmpShiftRosterPublishLog, RosterPublishStatus
from apps.employees.models import Employee, Department


class RosterPublishSerializer(serializers.Serializer):
    """Serializer for publishing roster."""

    company_id = serializers.UUIDField(required=True)
    publish_month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    publish_year = serializers.IntegerField(required=True, min_value=2000, max_value=2099)
    department_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="Specific departments to publish for (empty = all)",
    )
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)
    published_by = serializers.UUIDField(required=True)

    def validate_published_by(self, value):
        """Validate publisher exists and is active."""
        try:
            emp = Employee.objects.get(id=value, is_active=True, deleted_at__isnull=True)
            return emp
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Publisher employee not found or inactive")

    def validate_department_ids(self, value):
        """Validate all departments exist."""
        if value:
            dept_ids = [str(d) for d in value]
            existing = Department.objects.filter(
                id__in=dept_ids, is_active=True, deleted_at__isnull=True
            ).count()
            if existing != len(value):
                raise serializers.ValidationError(f"Some departments not found or inactive")
        return value

    def validate(self, data):
        """Check for duplicate publish."""
        company_id = data.get("company_id")
        month = data.get("publish_month")
        year = data.get("publish_year")

        if all([company_id, month, year]):
            existing = EmpShiftRosterPublishLog.objects.filter(
                company_id=company_id,
                publish_month=month,
                publish_year=year,
                status=RosterPublishStatus.PUBLISHED,
                deleted_at__isnull=True,
            ).exists()

            if existing:
                raise serializers.ValidationError(
                    f"Roster already published for {month}/{year}"
                )

        return data


class RosterUnpublishSerializer(serializers.Serializer):
    """Serializer for unpublishing roster."""

    company_id = serializers.UUIDField(required=True)
    publish_month = serializers.IntegerField(required=True, min_value=1, max_value=12)
    publish_year = serializers.IntegerField(required=True, min_value=2000, max_value=2099)
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)
    unpublished_by = serializers.UUIDField(required=True)

    def validate_unpublished_by(self, value):
        """Validate who is unpublishing."""
        try:
            emp = Employee.objects.get(id=value, is_active=True, deleted_at__isnull=True)
            return emp
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found or inactive")

    def validate(self, data):
        """Check publish exists and is published."""
        company_id = data.get("company_id")
        month = data.get("publish_month")
        year = data.get("publish_year")

        if all([company_id, month, year]):
            exists = EmpShiftRosterPublishLog.objects.filter(
                company_id=company_id,
                publish_month=month,
                publish_year=year,
                status=RosterPublishStatus.PUBLISHED,
                deleted_at__isnull=True,
            ).exists()

            if not exists:
                raise serializers.ValidationError(
                    f"No published roster found for {month}/{year}"
                )

        return data


class RosterPublishStatusSerializer(serializers.ModelSerializer):
    """Serializer for roster publish status."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    published_by_name = serializers.CharField(
        source="published_by.first_name", read_only=True, allow_null=True
    )
    unpublished_by_name = serializers.CharField(
        source="unpublished_by.first_name", read_only=True, allow_null=True
    )

    class Meta:
        model = EmpShiftRosterPublishLog
        fields = [
            "id",
            "publish_month",
            "publish_year",
            "status",
            "status_display",
            "published_count",
            "unpublished_count",
            "is_locked",
            "published_at",
            "published_by_name",
            "unpublished_at",
            "unpublished_by_name",
            "department_ids",
            "note",
            "created_at",
        ]
        read_only_fields = fields


class RosterPublishListSerializer(serializers.ModelSerializer):
    """List view: minimal roster publish log fields."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = EmpShiftRosterPublishLog
        fields = [
            "id",
            "publish_month",
            "publish_year",
            "status",
            "status_display",
            "published_count",
            "published_at",
            "is_locked",
            "created_at",
        ]
        read_only_fields = fields


class RosterPublishDetailSerializer(serializers.ModelSerializer):
    """Detail view: full roster publish log with audit trail."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    published_by_detail = serializers.SerializerMethodField()
    unpublished_by_detail = serializers.SerializerMethodField()

    class Meta:
        model = EmpShiftRosterPublishLog
        fields = [
            "id",
            "publish_month",
            "publish_year",
            "status",
            "status_display",
            "published_count",
            "unpublished_count",
            "department_ids",
            "is_locked",
            "published_at",
            "published_by_detail",
            "unpublished_at",
            "unpublished_by_detail",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_published_by_detail(self, obj):
        if not obj.published_by:
            return None
        return {
            "id": str(obj.published_by.id),
            "name": f"{obj.published_by.first_name} {obj.published_by.last_name}",
            "email": obj.published_by.email,
        }

    def get_unpublished_by_detail(self, obj):
        if not obj.unpublished_by:
            return None
        return {
            "id": str(obj.unpublished_by.id),
            "name": f"{obj.unpublished_by.first_name} {obj.unpublished_by.last_name}",
            "email": obj.unpublished_by.email,
        }
