"""
Admin service for employee salary page.

Uses Django ORM only; no raw SQL is used.
"""

from decimal import Decimal
from typing import Any, Dict

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.employees.models.employee import Employee
from apps.employees.models.salary import EmployeeSalary


WRITE_FIELD_MAP = {
    "basicSalary": "basic_salary",
    "houseRentAllowance": "house_rent_allowance",
    "conveyanceAllowance": "conveyance_allowance",
    "medicalAllowance": "medical_allowance",
    "specialAllowance": "special_allowance",
    "providentFund": "provident_fund",
    "taxDeductedAtSource": "tax_deducted_at_source",
    "payFrequency": "pay_frequency",
    "effectiveFrom": "effective_from",
    "effectiveTo": "effective_to",
    "currency": "currency",
    "remarks": "remarks",
}


class EmployeeSalaryService:
    @staticmethod
    def get_salary(employee_id: str) -> EmployeeSalary:
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        return get_object_or_404(EmployeeSalary, employee=employee, is_active=True)

    @staticmethod
    def create_or_replace_salary(employee_id: str, validated_data: Dict[str, Any]) -> EmployeeSalary:
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        data = EmployeeSalaryService._prepare_data(validated_data)

        with transaction.atomic():
            salary, created = EmployeeSalary.objects.get_or_create(employee=employee)
            for field, value in data.items():
                setattr(salary, field, value)
            if not created and salary.created_at is None:
                salary.created_at = timezone.now()
            salary.save()
        return salary

    @staticmethod
    def update_salary(employee_id: str, validated_data: Dict[str, Any]) -> EmployeeSalary:
        salary = EmployeeSalaryService.get_salary(employee_id)
        data = EmployeeSalaryService._map_fields(validated_data)

        with transaction.atomic():
            for field, value in data.items():
                setattr(salary, field, value)
            EmployeeSalaryService._apply_calculations(salary)
            salary.save()
        return salary

    @staticmethod
    def delete_salary(employee_id: str) -> None:
        salary = EmployeeSalaryService.get_salary(employee_id)
        with transaction.atomic():
            salary.delete()

    @staticmethod
    def _prepare_data(validated_data: Dict[str, Any]) -> Dict[str, Any]:
        data = EmployeeSalaryService._map_fields(validated_data)
        salary = EmployeeSalary(**data)
        EmployeeSalaryService._apply_calculations(salary)
        data["gross_salary"] = salary.gross_salary
        data["total_deductions"] = salary.total_deductions
        data["net_salary"] = salary.net_salary
        data["annual_ctc"] = salary.annual_ctc
        return data

    @staticmethod
    def _map_fields(validated_data: Dict[str, Any]) -> Dict[str, Any]:
        data = {}
        for source, target in WRITE_FIELD_MAP.items():
            if source in validated_data:
                data[target] = validated_data[source]
        return data

    @staticmethod
    def _apply_calculations(salary: EmployeeSalary) -> None:
        gross = (
            (salary.basic_salary or Decimal("0.00"))
            + (salary.house_rent_allowance or Decimal("0.00"))
            + (salary.conveyance_allowance or Decimal("0.00"))
            + (salary.medical_allowance or Decimal("0.00"))
            + (salary.special_allowance or Decimal("0.00"))
        )
        deductions = (
            (salary.provident_fund or Decimal("0.00"))
            + (salary.tax_deducted_at_source or Decimal("0.00"))
        )
        salary.gross_salary = gross
        salary.total_deductions = deductions
        salary.net_salary = gross - deductions
        salary.annual_ctc = gross * Decimal("12")
