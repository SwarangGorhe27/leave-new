"""Builders for employee salary self-service details."""

from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

from apps.employees.models import EmployeeSalaryAssignment, PayComponentGroup


DEDUCTION_CODE_HINTS = {"PF", "PF_EE", "EPF", "TDS", "PT", "ESI", "LWF"}


def _money(value):
    return value or Decimal("0.00")


def _is_earning(component, group_map):
    group = group_map.get(component.component_group_id)
    if group is not None:
        return group.is_earning
    return component.code.upper() not in DEDUCTION_CODE_HINTS


def get_current_salary_assignment(employee):
    today = timezone.localdate()
    return (
        EmployeeSalaryAssignment.objects.filter(
            employee=employee,
            is_active=True,
            effective_from__lte=today,
        )
        .filter(Q(effective_to__isnull=True) | Q(effective_to__gte=today))
        .select_related("employee", "salary_structure")
        .prefetch_related("component_values__pay_component")
        .order_by("-is_current", "-effective_from", "-created_at")
        .first()
    )


def build_salary_details(employee):
    assignment = get_current_salary_assignment(employee)
    if not assignment:
        return None

    component_values = list(assignment.component_values.all())
    group_ids = {
        value.pay_component.component_group_id
        for value in component_values
        if value.pay_component.component_group_id
    }
    group_map = {
        group.id: group for group in PayComponentGroup.objects.filter(id__in=group_ids)
    }

    earnings = []
    deductions = []
    gross_salary = Decimal("0.00")
    total_deductions = Decimal("0.00")

    for value in component_values:
        component = value.pay_component
        row = {
            "code": component.code,
            "name": component.name,
            "amount": _money(value.amount_monthly),
            "amount_annual": _money(value.amount_annual),
        }
        if _is_earning(component, group_map):
            earnings.append(row)
            gross_salary += row["amount"]
        else:
            deductions.append(row)
            total_deductions += row["amount"]

    net_salary = gross_salary - total_deductions

    return {
        "employee": {
            "id": employee.id,
            "employee_code": employee.employee_code,
            "full_name": employee.full_name,
        },
        "currency": assignment.currency_code,
        "period": "MONTHLY",
        "salary_assignment": {
            "id": assignment.id,
            "ctc_annual": assignment.ctc_annual,
            "effective_from": assignment.effective_from,
            "effective_to": assignment.effective_to,
            "salary_structure": {
                "id": assignment.salary_structure_id,
                "code": assignment.salary_structure.code,
                "name": assignment.salary_structure.name,
            },
        },
        "summary": {
            "gross_salary": gross_salary,
            "total_deductions": total_deductions,
            "net_salary": net_salary,
        },
        "earnings": earnings,
        "deductions": deductions,
        "totals": {
            "gross_earnings": gross_salary,
            "total_deductions": total_deductions,
            "net_take_home": net_salary,
        },
    }
