from rest_framework import serializers

from ..models.transactions.leave_balances import LeaveBalance
from ..models.transactions.leave_balance_ledger import LeaveBalanceLedger

from decimal import Decimal
from datetime import date

from django.apps import apps

from ..models.masters.leave_types import LeaveType


class EmployeeLeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_id = serializers.UUIDField(source="leave_type.id", read_only=True)
    leave_type = serializers.CharField(source="leave_type.name", read_only=True)
    opening = serializers.SerializerMethodField()
    accrued = serializers.DecimalField(
        max_digits=6, decimal_places=2, source="accrued_days", read_only=True
    )
    taken = serializers.DecimalField(
        max_digits=6, decimal_places=2, source="used_days", read_only=True
    )
    balance = serializers.SerializerMethodField()

    class Meta:
        model = LeaveBalance
        fields = [
            "leave_type_id",
            "leave_type",
            "opening",
            "accrued",
            "taken",
            "balance",
            "year",
        ]

    def get_opening(self, obj):
        return obj.allocated_days + obj.carried_forward

    def get_balance(self, obj):
        return obj.total_available_balance


class AdminLeaveBalanceSerializer(serializers.ModelSerializer):
    employee_id = serializers.UUIDField(source="employee.id", read_only=True)
    leave_type_id = serializers.UUIDField(source="leave_type.id", read_only=True)
    leave_type = serializers.CharField(source="leave_type.name", read_only=True)

    class Meta:
        model = LeaveBalance
        fields = [
            "id",
            "employee_id",
            "leave_type_id",
            "leave_type",
            "year",
            "allocated_days",
            "accrued_days",
            "carried_forward",
            "used_days",
            "pending_days",
            "encashed_days",
            "lapsed_days",
            "leave_year_start",
            "leave_year_end",
        ]


class ManagerLeaveBalanceSerializer(
    AdminLeaveBalanceSerializer
):
    employee_id = serializers.UUIDField(
        source="employee.id",
        read_only=True,
    )

    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True,
    )

    employee_name = serializers.SerializerMethodField()

    class Meta(AdminLeaveBalanceSerializer.Meta):
        fields = [
            *AdminLeaveBalanceSerializer.Meta.fields,
            "employee_id",
            "employee_code",
            "employee_name",
        ]

    def get_employee_name(self, obj):
        return getattr(obj.employee, "full_name", None)

class LeaveBalanceAdjustmentSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField()
    leave_type_id = serializers.UUIDField()
    days = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
    )
    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
    )


class LeaveBalanceCreditSerializer(LeaveBalanceAdjustmentSerializer):
    def validate_days(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError(
                "Credit days must be greater than zero."
            )
        return value


class LeaveBalanceDebitSerializer(LeaveBalanceAdjustmentSerializer):
    def validate_days(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError(
                "Debit days must be greater than zero."
            )
        return value

    def validate(self, attrs):
        employee_model = apps.get_model("employees", "Employee")

        employee = employee_model.objects.filter(
            id=attrs["employee_id"]
        ).first()
        if not employee:
            raise serializers.ValidationError(
                {"employee_id": "Employee not found."}
            )

        leave_type = LeaveType.objects.filter(
            id=attrs["leave_type_id"]
        ).first()
        if not leave_type:
            raise serializers.ValidationError(
                {"leave_type_id": "Leave type not found."}
            )

        from datetime import date

        year = date.today().year

        balance = LeaveBalance.objects.filter(
            employee=employee,
            leave_type=leave_type,
            year=year,
        ).first()

        if not balance:
            raise serializers.ValidationError(
                "No leave balance exists for this employee and leave type."
            )

        if balance.total_available_balance < attrs["days"]:
            raise serializers.ValidationError(
                {
                    "days": (
                        f"Insufficient leave balance. "
                        f"Available: {balance.total_available_balance}"
                    )
                }
            )

        return attrs
