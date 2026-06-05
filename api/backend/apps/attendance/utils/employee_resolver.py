"""
attendance/utils/employee_resolver.py

Resolves an ESSL UserId (employee_code) to an HRMS Employee instance.

Used exclusively by the ingest service to resolve employee + company
before writing to att_punch_log.

Design decisions:
  - Uses select_related('company') in a single query — no N+1
  - Returns a typed result dataclass — no raw tuples passed around
  - Caches nothing — cache invalidation on employee updates is complex
    and punch ingest happens in bulk batches, not per-request hot paths
  - Only resolves ACTIVE employees by default — configurable via
    include_inactive flag for HR correction workflows
"""
from dataclasses import dataclass
from typing import Optional

from apps.employees.models import Employee


@dataclass(frozen=True)
class ResolvedEmployee:
    """
    Immutable result of a successful employee resolution.
    Carries only what the ingest service needs — no full ORM object passed around.
    """
    employee_id: int       # Employee PK (BigAutoField or UUID depending on base model)
    company_id: int        # Company PK — used to populate company FK on punch log
    employee_code: str     # For logging


@dataclass(frozen=True)
class ResolutionFailure:
    """Result when employee_code cannot be resolved."""
    employee_code: str
    reason: str


def resolve_employee(
    employee_code: str,
    include_inactive: bool = False,
) -> ResolvedEmployee | ResolutionFailure:
    """
    Resolves an ESSL UserId (employee_code) to a ResolvedEmployee.

    Args:
        employee_code:    The raw UserId string from ESSL e.g. 'PTSPL001'
        include_inactive: If True, resolves terminated/resigned employees too.
                          Used only for HR correction workflows.

    Returns:
        ResolvedEmployee  — on success
        ResolutionFailure — if not found or inactive
    """
    if not employee_code or not employee_code.strip():
        return ResolutionFailure(
            employee_code=employee_code,
            reason="Empty employee_code received from ESSL.",
        )

    code = employee_code.strip()

    try:
        qs = Employee.objects.select_related("company").filter(employee_code=code)

        if not include_inactive:
            qs = qs.filter(is_active=True)

        employee = qs.get()

        return ResolvedEmployee(
            employee_id=employee.pk,
            company_id=employee.company_id,
            employee_code=employee.employee_code,
        )

    except Employee.DoesNotExist:
        reason = (
            f"No {'active ' if not include_inactive else ''}employee found "
            f"with employee_code='{code}'."
        )
        return ResolutionFailure(employee_code=code, reason=reason)

    except Employee.MultipleObjectsReturned:
        # Should never happen — employee_code has a UniqueConstraint
        # but guard it anyway
        return ResolutionFailure(
            employee_code=code,
            reason=f"Multiple employees found with employee_code='{code}' — data integrity issue.",
        )


def resolve_employees_bulk(
    employee_codes: list[str],
    include_inactive: bool = False,
) -> dict[str, ResolvedEmployee | ResolutionFailure]:
    """
    Resolves a list of employee codes in a single DB query.

    Used by the ingest service to resolve an entire batch at once
    instead of one query per punch — avoids N+1 on large batches.

    Returns:
        dict mapping employee_code → ResolvedEmployee or ResolutionFailure
    """
    codes = [c.strip() for c in employee_codes if c and c.strip()]
    unique_codes = list(set(codes))

    qs = Employee.objects.select_related("company").filter(
        employee_code__in=unique_codes
    )
    if not include_inactive:
        qs = qs.filter(is_active=True)

    # Build lookup map from DB results
    found: dict[str, Employee] = {emp.employee_code: emp for emp in qs}

    result: dict[str, ResolvedEmployee | ResolutionFailure] = {}

    for code in unique_codes:
        if code in found:
            emp = found[code]
            result[code] = ResolvedEmployee(
                employee_id=emp.pk,
                company_id=emp.company_id,
                employee_code=emp.employee_code,
            )
        else:
            result[code] = ResolutionFailure(
                employee_code=code,
                reason=f"No {'active ' if not include_inactive else ''}employee found "
                       f"with employee_code='{code}'.",
            )

    return result