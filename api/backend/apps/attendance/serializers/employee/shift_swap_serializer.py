"""
Serializers for Shift Swap Requests.

Three-tier serializer pattern:
- List: Minimal fields, read-only
- Detail: Full relationships, read-only
- Create: Input validation, writable
"""

from rest_framework import serializers
from datetime import date
from uuid import UUID
from typing import List, Dict

from apps.attendance.models import (
    EmpShiftSwapRequest,
    ShiftSwapStatus,
    ShiftDefinition,
    EmployeeShiftRoster,
)
from apps.employees.models import Employee, Department, OfficeLocation


class ShiftSwapListSerializer(serializers.ModelSerializer):
    """List view: minimal fields for shift swap requests."""

    requester_code = serializers.CharField(source="requester.employee_code", read_only=True)
    requester_name = serializers.CharField(source="requester.first_name", read_only=True)
    target_code = serializers.CharField(source="target.employee_code", read_only=True)
    target_name = serializers.CharField(source="target.first_name", read_only=True)
    requester_shift_code = serializers.CharField(source="requester_shift.code", read_only=True)
    target_shift_code = serializers.CharField(source="target_shift.code", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = EmpShiftSwapRequest
        fields = [
            "id",
            "requester_code",
            "requester_name",
            "target_code",
            "target_name",
            "swap_date",
            "requester_shift_code",
            "target_shift_code",
            "status",
            "status_display",
            "created_at",
        ]
        read_only_fields = fields


class ShiftSwapDetailSerializer(serializers.ModelSerializer):
    """Detail view: full relationships and audit trail."""

    requester_detail = serializers.SerializerMethodField()
    target_detail = serializers.SerializerMethodField()
    requester_shift_detail = serializers.SerializerMethodField()
    target_shift_detail = serializers.SerializerMethodField()
    approved_by_name = serializers.CharField(
        source="approved_by.first_name", read_only=True, allow_null=True
    )
    rejected_by_name = serializers.CharField(
        source="rejected_by.first_name", read_only=True, allow_null=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = EmpShiftSwapRequest
        fields = [
            "id",
            "requester_detail",
            "target_detail",
            "swap_date",
            "requester_shift_detail",
            "target_shift_detail",
            "reason",
            "status",
            "status_display",
            "workflow_txn_id",
            "accepted_at",
            "accepted_note",
            "approved_at",
            "approved_by_name",
            "approval_note",
            "rejected_at",
            "rejected_by_name",
            "rejection_note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_requester_detail(self, obj):
        return {
            "id": str(obj.requester.id),
            "code": obj.requester.employee_code,
            "name": f"{obj.requester.first_name} {obj.requester.last_name}",
            "department": obj.requester.department.name if obj.requester.department else None,
        }

    def get_target_detail(self, obj):
        return {
            "id": str(obj.target.id),
            "code": obj.target.employee_code,
            "name": f"{obj.target.first_name} {obj.target.last_name}",
            "department": obj.target.department.name if obj.target.department else None,
        }

    def get_requester_shift_detail(self, obj):
        return {
            "id": str(obj.requester_shift.id),
            "code": obj.requester_shift.code,
            "start_time": str(obj.requester_shift.start_time),
            "end_time": str(obj.requester_shift.end_time),
        }

    def get_target_shift_detail(self, obj):
        return {
            "id": str(obj.target_shift.id),
            "code": obj.target_shift.code,
            "start_time": str(obj.target_shift.start_time),
            "end_time": str(obj.target_shift.end_time),
        }


class ShiftSwapCreateSerializer(serializers.Serializer):
    """Serializer for creating shift swap requests."""

    company_id = serializers.UUIDField(required=True)
    requester_employee_id = serializers.UUIDField(required=True)
    target_employee_id = serializers.UUIDField(required=True)
    swap_date = serializers.DateField(required=True)
    requester_shift_id = serializers.UUIDField(required=True)
    target_shift_id = serializers.UUIDField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_requester_employee_id(self, value):
        """Validate requester exists and is active."""
        try:
            emp = Employee.objects.get(id=value, is_active=True, deleted_at__isnull=True)
            return emp
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Requester employee not found or inactive")

    def validate_target_employee_id(self, value):
        """Validate target exists and is active."""
        try:
            emp = Employee.objects.get(id=value, is_active=True, deleted_at__isnull=True)
            return emp
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Target employee not found or inactive")

    def validate_requester_shift_id(self, value):
        """Validate shift exists and is active."""
        try:
            shift = ShiftDefinition.objects.get(id=value, is_active=True, deleted_at__isnull=True)
            return shift
        except ShiftDefinition.DoesNotExist:
            raise serializers.ValidationError("Requester shift not found or inactive")

    def validate_target_shift_id(self, value):
        """Validate shift exists and is active."""
        try:
            shift = ShiftDefinition.objects.get(id=value, is_active=True, deleted_at__isnull=True)
            return shift
        except ShiftDefinition.DoesNotExist:
            raise serializers.ValidationError("Target shift not found or inactive")

    def validate(self, data):
        """Cross-field validation."""
        requester = data.get("requester_employee_id")
        target = data.get("target_employee_id")
        swap_date = data.get("swap_date")

        # Same employee check
        if requester and target and requester.id == target.id:
            raise serializers.ValidationError("Cannot swap with same employee")

        # Past date check
        if swap_date and swap_date < date.today():
            raise serializers.ValidationError("Cannot request swap for past date")

        # Check for existing active swap
        if requester and target and swap_date:
            existing = EmpShiftSwapRequest.objects.filter(
                requester=requester,
                target=target,
                swap_date=swap_date,
                deleted_at__isnull=True,
                status__in=[
                    ShiftSwapStatus.PENDING_APPROVAL,
                    ShiftSwapStatus.ACCEPTED,
                    ShiftSwapStatus.APPROVED,
                ],
            ).exists()

            if existing:
                raise serializers.ValidationError("A swap request already exists for this pair on this date")

        return data


class ShiftSwapUpdateSerializer(serializers.Serializer):
    """Serializer for partial updates to shift swap requests."""

    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, data):
        """Validate partial update is allowed."""
        swap = self.context.get("swap_request")
        if swap and swap.status != ShiftSwapStatus.PENDING_APPROVAL:
            raise serializers.ValidationError("Can only update pending requests")
        return data
