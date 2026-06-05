"""
Serializers for the seven other-request types:
  WFH, CompOff, GatePass, OutDuty, ShortLeave, Overtime, WeeklyOffShuffle
Each request type has:
  - CreateSerializer   (validated input)
  - SummarySerializer  (list response)
  - ActionSerializer   (approve / reject)
"""

from rest_framework import serializers

from ..models.request_modules.wfh_requests import (
    WFHRequest,
    WFHLocationTypeChoices,
)
from ..models.request_modules.comp_off import (
    CompOffRequest,
    CompOffTypeChoices,
    EarnedAgainstTypeChoices,
)
from ..models.request_modules.gate_pass_requests import (
    GatePassRequest,
    GatePassMovementTypeChoices,
    GatePassTypeChoices,
)
from ..models.request_modules.out_duty_requests import (
    OutDutyRequest,
    OutDutyTravelModeChoices,
)
from ..models.request_modules.short_leave_requests import (
    ShortLeaveRequest,
    ShortLeaveTimeSlotChoices,
)
from ..models.request_modules.overtime_requests import OvertimeRequest
from ..models.request_modules.week_off_shuffle_requests import WeeklyOffShuffleRequest


# ──────────────────────────────────────────────
# Shared
# ──────────────────────────────────────────────

class RequestActionSerializer(serializers.Serializer):
    """Approve / reject any other-request type."""
    remarks = serializers.CharField(allow_blank=True, required=False)


# ──────────────────────────────────────────────
# WFH
# ──────────────────────────────────────────────

class WFHRequestCreateSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    total_days = serializers.DecimalField(max_digits=5, decimal_places=2)
    work_location_type = serializers.ChoiceField(choices=WFHLocationTypeChoices.choices)
    vpn_confirmed = serializers.BooleanField(default=False)
    connectivity_confirmed = serializers.BooleanField(default=False)
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["from_date"] > attrs["to_date"]:
            raise serializers.ValidationError("from_date cannot be after to_date.")
        return attrs


class WFHRequestSummarySerializer(serializers.ModelSerializer):
    employee_id = serializers.UUIDField(source="employee.id", read_only=True)
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = WFHRequest
        fields = [
            "id", "employee_id", "employee_name",
            "from_date", "to_date", "total_days",
            "work_location_type", "vpn_confirmed", "connectivity_confirmed",
            "reason", "status", "actioned_at", "created_at",
        ]

    def get_employee_name(self, obj):
        return getattr(obj.employee, "full_name", None)


# ──────────────────────────────────────────────
# CompOff
# ──────────────────────────────────────────────

class CompOffRequestCreateSerializer(serializers.Serializer):
    worked_date = serializers.DateField()
    comp_off_type = serializers.ChoiceField(choices=CompOffTypeChoices.choices)
    earned_against_date_type = serializers.ChoiceField(choices=EarnedAgainstTypeChoices.choices)
    reason = serializers.CharField(required=False, allow_blank=True)
    proof_url = serializers.URLField(required=False, allow_blank=True)
    earned_days = serializers.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    expiry_date = serializers.DateField(required=False, allow_null=True)


class CompOffRequestSummarySerializer(serializers.ModelSerializer):
    employee_id = serializers.UUIDField(source="employee.id", read_only=True)
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = CompOffRequest
        fields = [
            "id", "employee_id", "employee_name",
            "worked_date", "comp_off_type", "earned_against_date_type",
            "earned_days", "used_days", "expiry_date",
            "reason", "status", "actioned_at", "created_at",
        ]

    def get_employee_name(self, obj):
        return getattr(obj.employee, "full_name", None)


# ──────────────────────────────────────────────
# GatePass
# ──────────────────────────────────────────────

class GatePassRequestCreateSerializer(serializers.Serializer):
    purpose = serializers.CharField(max_length=100)
    purpose_type_id = serializers.UUIDField()
    movement_type = serializers.ChoiceField(choices=GatePassMovementTypeChoices.choices)
    pass_type = serializers.ChoiceField(choices=GatePassTypeChoices.choices)
    from_location = serializers.CharField(required=False, allow_blank=True)
    to_location = serializers.CharField(required=False, allow_blank=True)
    start_time = serializers.TimeField()
    expected_return_time = serializers.TimeField(required=False, allow_null=True)
    duration_minutes = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(required=False, allow_blank=True)


class GatePassRequestSummarySerializer(serializers.ModelSerializer):
    employee_id = serializers.UUIDField(source="employee.id", read_only=True)
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = GatePassRequest
        fields = [
            "id", "employee_id", "employee_name",
            "request_date", "purpose", "movement_type", "pass_type",
            "from_location", "to_location",
            "start_time", "expected_return_time",
            "actual_departure_time", "actual_return_time",
            "duration_minutes", "reason", "status", "actioned_at", "created_at",
        ]

    def get_employee_name(self, obj):
        return getattr(obj.employee, "full_name", None)


# ──────────────────────────────────────────────
# OutDuty
# ──────────────────────────────────────────────

class OutDutyRequestCreateSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    from_location = serializers.CharField(required=False, allow_blank=True)
    to_location = serializers.CharField(required=False, allow_blank=True)
    purpose_type_id = serializers.UUIDField()
    reason = serializers.CharField(required=False, allow_blank=True)
    travel_mode = serializers.ChoiceField(
        choices=OutDutyTravelModeChoices.choices, required=False, allow_null=True
    )
    cc_manager_id = serializers.UUIDField(required=False, allow_null=True)
    advance_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )

    def validate(self, attrs):
        if attrs["from_date"] > attrs["to_date"]:
            raise serializers.ValidationError("from_date cannot be after to_date.")
        return attrs


class OutDutyRequestSummarySerializer(serializers.ModelSerializer):
    employee_id = serializers.UUIDField(source="employee.id", read_only=True)
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = OutDutyRequest
        fields = [
            "id", "employee_id", "employee_name",
            "from_date", "to_date", "actual_return_date",
            "from_location", "to_location",
            "reason", "travel_mode", "status",
            "advance_approved", "travel_expense_submitted",
            "actioned_at", "created_at",
        ]

    def get_employee_name(self, obj):
        return getattr(obj.employee, "full_name", None)


# ──────────────────────────────────────────────
# ShortLeave
# ──────────────────────────────────────────────

class ShortLeaveRequestCreateSerializer(serializers.Serializer):
    policy_id = serializers.UUIDField()
    leave_date = serializers.DateField()
    time_slot = serializers.ChoiceField(choices=ShortLeaveTimeSlotChoices.choices)
    start_time = serializers.TimeField(required=False, allow_null=True)
    end_time = serializers.TimeField(required=False, allow_null=True)
    duration_hours = serializers.DecimalField(max_digits=4, decimal_places=2)
    reason = serializers.CharField(required=False, allow_blank=True)


class ShortLeaveRequestSummarySerializer(serializers.ModelSerializer):
    employee_id = serializers.UUIDField(source="employee.id", read_only=True)
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = ShortLeaveRequest
        fields = [
            "id", "employee_id", "employee_name",
            "leave_date", "time_slot", "start_time", "end_time",
            "duration_hours", "reason", "status", "actioned_at", "created_at",
        ]

    def get_employee_name(self, obj):
        return getattr(obj.employee, "full_name", None)


# ──────────────────────────────────────────────
# Overtime
# ──────────────────────────────────────────────

class OvertimeRequestCreateSerializer(serializers.Serializer):
    ot_date = serializers.DateField()
    ot_hours = serializers.DecimalField(max_digits=4, decimal_places=2, min_value=0.25)
    reason = serializers.CharField(required=False, allow_blank=True)
    grant_comp_off = serializers.BooleanField(default=False)


class OvertimeRequestSummarySerializer(serializers.ModelSerializer):
    employee_id = serializers.UUIDField(source="employee.id", read_only=True)
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = OvertimeRequest
        fields = [
            "id", "employee_id", "employee_name",
            "ot_date", "ot_hours", "reason", "grant_comp_off",
            "status", "actioned_at", "created_at",
        ]

    def get_employee_name(self, obj):
        return getattr(obj.employee, "full_name", None)


# ──────────────────────────────────────────────
# WeeklyOffShuffle
# ──────────────────────────────────────────────

class WeeklyOffShuffleCreateSerializer(serializers.Serializer):
    week_start_date = serializers.DateField()
    current_off_date = serializers.DateField()
    requested_off_date = serializers.DateField()
    reason = serializers.CharField(required=False, allow_blank=True)
    impact_on_shift = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["current_off_date"] == attrs["requested_off_date"]:
            raise serializers.ValidationError(
                "current_off_date and requested_off_date must differ."
            )
        return attrs


class WeeklyOffShuffleSummarySerializer(serializers.ModelSerializer):
    employee_id = serializers.UUIDField(source="employee.id", read_only=True)
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = WeeklyOffShuffleRequest
        fields = [
            "id", "employee_id", "employee_name",
            "week_start_date", "current_off_date", "requested_off_date",
            "reason", "impact_on_shift", "status", "actioned_at", "created_at",
        ]

    def get_employee_name(self, obj):
        return getattr(obj.employee, "full_name", None)
