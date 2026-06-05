"""
Admin serializers for Fines & Damages Register.

Naming convention: camelCase field names on the wire (matches existing pattern
in salary_serializer.py, employee_profile_serializer.py, etc.)
"""

from decimal import Decimal, InvalidOperation

from rest_framework import serializers

from apps.employees.models.fines_damages import EmployeeFine, EmployeePropertyDamage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_amount(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise serializers.ValidationError("Enter a valid amount.")
    if amount <= 0:
        raise serializers.ValidationError("Amount must be greater than zero.")
    if amount > Decimal("999999999999.99"):
        raise serializers.ValidationError("Amount is too large.")
    return amount.quantize(Decimal("0.01"))


# ---------------------------------------------------------------------------
# Employee inline (used in list responses)
# ---------------------------------------------------------------------------

class FineEmployeeSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    employeeNumber = serializers.CharField(source="employee_code", read_only=True)
    employeeName = serializers.SerializerMethodField(read_only=True)

    def get_employeeName(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


# ---------------------------------------------------------------------------
# Fine — Read serializer
# ---------------------------------------------------------------------------

class EmployeeFineSerializer(serializers.ModelSerializer):
    employeeId = serializers.UUIDField(source="employee_id", read_only=True)
    employeeNumber = serializers.CharField(
        source="employee.employee_code", read_only=True
    )
    employeeName = serializers.SerializerMethodField()
    offenceDate = serializers.DateField(source="offence_date", read_only=True)
    actOrOmission = serializers.CharField(source="act_or_omission", read_only=True)
    showCause = serializers.BooleanField(source="show_cause", read_only=True)
    showCauseDate = serializers.DateField(
        source="show_cause_date", read_only=True, allow_null=True
    )
    fineAmount = serializers.DecimalField(
        source="fine_amount", max_digits=14, decimal_places=2, read_only=True
    )
    realizedOn = serializers.DateField(
        source="realized_date", read_only=True, allow_null=True
    )
    remarks = serializers.CharField(read_only=True, allow_null=True)
    status = serializers.CharField(read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = EmployeeFine
        fields = [
            "id",
            "employeeId",
            "employeeNumber",
            "employeeName",
            "offenceDate",
            "actOrOmission",
            "showCause",
            "showCauseDate",
            "fineAmount",
            "realizedOn",
            "remarks",
            "status",
            "createdAt",
            "updatedAt",
        ]

    def get_employeeName(self, obj):
        emp = obj.employee
        return f"{emp.first_name} {emp.last_name}".strip()


# ---------------------------------------------------------------------------
# Fine — Write serializer (POST / PUT)
# ---------------------------------------------------------------------------

class EmployeeFineWriteSerializer(serializers.Serializer):
    employeeId = serializers.UUIDField()
    offenceDate = serializers.DateField()
    actOrOmission = serializers.CharField(max_length=2000)
    showCause = serializers.BooleanField(default=False)
    showCauseDate = serializers.DateField(required=False, allow_null=True)
    fineAmount = serializers.CharField()
    realizedDate = serializers.DateField(required=False, allow_null=True)
    remarks = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=1000
    )
    status = serializers.ChoiceField(
        choices=EmployeeFine.FineStatus.choices,
        default=EmployeeFine.FineStatus.PENDING,
        required=False,
    )

    def validate_fineAmount(self, value):
        return _validate_amount(value)

    def validate(self, attrs):
        show_cause = attrs.get("showCause", False)
        show_cause_date = attrs.get("showCauseDate")
        if show_cause and not show_cause_date:
            raise serializers.ValidationError(
                {"showCauseDate": "Required when showCause is Yes."}
            )
        return attrs


# ---------------------------------------------------------------------------
# Fine — Partial update serializer (PATCH)
# ---------------------------------------------------------------------------

class EmployeeFineUpdateSerializer(serializers.Serializer):
    offenceDate = serializers.DateField(required=False)
    actOrOmission = serializers.CharField(required=False, max_length=2000)
    showCause = serializers.BooleanField(required=False)
    showCauseDate = serializers.DateField(required=False, allow_null=True)
    fineAmount = serializers.CharField(required=False)
    realizedDate = serializers.DateField(required=False, allow_null=True)
    remarks = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=1000
    )
    status = serializers.ChoiceField(
        choices=EmployeeFine.FineStatus.choices, required=False
    )

    def validate_fineAmount(self, value):
        return _validate_amount(value)


# ---------------------------------------------------------------------------
# Fine — Status patch serializer
# ---------------------------------------------------------------------------

class EmployeeFineStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=EmployeeFine.FineStatus.choices)


# ---------------------------------------------------------------------------
# Fine — Stats serializer
# ---------------------------------------------------------------------------

class FineStatsSerializer(serializers.Serializer):
    totalFines = serializers.IntegerField()
    pendingFines = serializers.IntegerField()
    realizedFines = serializers.IntegerField()
    cancelledFines = serializers.IntegerField()
    totalFineAmount = serializers.DecimalField(max_digits=16, decimal_places=2)
    totalRealizedAmount = serializers.DecimalField(max_digits=16, decimal_places=2)
    pendingRecoveries = serializers.IntegerField()


# ---------------------------------------------------------------------------
# Property Damage — Read serializer
# ---------------------------------------------------------------------------

class EmployeePropertyDamageSerializer(serializers.ModelSerializer):
    employeeId = serializers.UUIDField(source="employee_id", read_only=True)
    employeeNumber = serializers.CharField(
        source="employee.employee_code", read_only=True
    )
    employeeName = serializers.SerializerMethodField()
    damageDate = serializers.DateField(source="damage_date", read_only=True)
    propertyName = serializers.CharField(source="property_name", read_only=True)
    damageDescription = serializers.CharField(
        source="damage_description", read_only=True
    )
    damageAmount = serializers.DecimalField(
        source="damage_amount", max_digits=14, decimal_places=2, read_only=True
    )
    installmentsCount = serializers.IntegerField(
        source="installments_count", read_only=True, allow_null=True
    )
    firstInstallmentDate = serializers.DateField(
        source="first_installment_date", read_only=True, allow_null=True
    )
    lastInstallmentDate = serializers.DateField(
        source="last_installment_date", read_only=True, allow_null=True
    )
    remarks = serializers.CharField(read_only=True, allow_null=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = EmployeePropertyDamage
        fields = [
            "id",
            "employeeId",
            "employeeNumber",
            "employeeName",
            "damageDate",
            "propertyName",
            "damageDescription",
            "damageAmount",
            "installmentsCount",
            "firstInstallmentDate",
            "lastInstallmentDate",
            "remarks",
            "createdAt",
            "updatedAt",
        ]

    def get_employeeName(self, obj):
        emp = obj.employee
        return f"{emp.first_name} {emp.last_name}".strip()


# ---------------------------------------------------------------------------
# Property Damage — Write serializer (POST / PUT)
# ---------------------------------------------------------------------------

class EmployeePropertyDamageWriteSerializer(serializers.Serializer):
    employeeId = serializers.UUIDField()
    damageDate = serializers.DateField()
    propertyName = serializers.CharField(max_length=255)
    damageDescription = serializers.CharField(max_length=2000)
    damageAmount = serializers.CharField()
    installmentsCount = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )
    firstInstallmentDate = serializers.DateField(required=False, allow_null=True)
    lastInstallmentDate = serializers.DateField(required=False, allow_null=True)
    remarks = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=1000
    )

    def validate_damageAmount(self, value):
        return _validate_amount(value)

    def validate(self, attrs):
        first = attrs.get("firstInstallmentDate")
        last = attrs.get("lastInstallmentDate")
        if first and last and last < first:
            raise serializers.ValidationError(
                {"lastInstallmentDate": "Must be on or after firstInstallmentDate."}
            )
        return attrs


# ---------------------------------------------------------------------------
# Property Damage — Partial update serializer (PATCH)
# ---------------------------------------------------------------------------

class EmployeePropertyDamageUpdateSerializer(serializers.Serializer):
    damageDate = serializers.DateField(required=False)
    propertyName = serializers.CharField(required=False, max_length=255)
    damageDescription = serializers.CharField(required=False, max_length=2000)
    damageAmount = serializers.CharField(required=False)
    installmentsCount = serializers.IntegerField(
        required=False, allow_null=True, min_value=1
    )
    firstInstallmentDate = serializers.DateField(required=False, allow_null=True)
    lastInstallmentDate = serializers.DateField(required=False, allow_null=True)
    remarks = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=1000
    )

    def validate_damageAmount(self, value):
        return _validate_amount(value)


# ---------------------------------------------------------------------------
# Damage — Stats serializer
# ---------------------------------------------------------------------------

class DamageStatsSerializer(serializers.Serializer):
    totalDamages = serializers.IntegerField()
    totalDamageAmount = serializers.DecimalField(max_digits=16, decimal_places=2)
    totalRecoveredAmount = serializers.DecimalField(max_digits=16, decimal_places=2)
    pendingRecoveries = serializers.IntegerField()


# ---------------------------------------------------------------------------
# Employee dropdown serializer
# ---------------------------------------------------------------------------

class EmployeeDropdownSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.SerializerMethodField()
    employeeNumber = serializers.CharField(source="employee_code", read_only=True)

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
