"""Employee salary details response serializers."""

from rest_framework import serializers


class SalaryEmployeeSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    employee_code = serializers.CharField()
    full_name = serializers.CharField()


class SalaryStructureSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()


class SalaryAssignmentSummarySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    ctc_annual = serializers.DecimalField(max_digits=14, decimal_places=2)
    effective_from = serializers.DateField()
    effective_to = serializers.DateField(allow_null=True)
    salary_structure = SalaryStructureSummarySerializer()


class SalaryAmountRowSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    amount_annual = serializers.DecimalField(max_digits=14, decimal_places=2)


class SalarySummarySerializer(serializers.Serializer):
    gross_salary = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_salary = serializers.DecimalField(max_digits=14, decimal_places=2)


class SalaryTotalsSerializer(serializers.Serializer):
    gross_earnings = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_take_home = serializers.DecimalField(max_digits=14, decimal_places=2)


class EmployeeSalaryDetailsSerializer(serializers.Serializer):
    employee = SalaryEmployeeSerializer()
    currency = serializers.CharField()
    period = serializers.CharField()
    salary_assignment = SalaryAssignmentSummarySerializer()
    summary = SalarySummarySerializer()
    earnings = SalaryAmountRowSerializer(many=True)
    deductions = SalaryAmountRowSerializer(many=True)
    totals = SalaryTotalsSerializer()
