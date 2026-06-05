"""Access Card Details read helpers for employee self-service."""

from typing import Any, Dict, List

from apps.employees.models.access import EmployeeAccessCard
from apps.employees.models.employee import Employee


def _format_date(value) -> str | None:
    return value.isoformat() if value else None


def build_access_card_details(employee: Employee) -> List[Dict[str, Any]]:
    """Build access card rows for the employee Access Card Details UI."""
    rows = []
    cards = (
        EmployeeAccessCard.objects.filter(employee=employee, is_active=True)
        .select_related("office_location", "floor")
        .order_by("-issued_date", "card_number")
    )

    for card in cards:
        rows.append(
            {
                "id": str(card.id),
                "employee_id": employee.employee_code,
                "access_card_number": card.card_number,
                "from_date": _format_date(card.issued_date),
                "to_date": _format_date(card.expiry_date),
            }
        )

    if not rows:
        rows.append(
            {
                "id": None,
                "employee_id": employee.employee_code,
                "access_card_number": "",
                "from_date": None,
                "to_date": None,
            }
        )

    return rows
