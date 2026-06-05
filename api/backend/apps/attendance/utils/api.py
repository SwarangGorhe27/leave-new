from __future__ import annotations

from rest_framework.response import Response


def api_success(data=None, message: str = "", status: int = 200) -> Response:
    return Response(
        {
            "success": True,
            "message": message,
            "data": {} if data is None else data,
            "errors": None,
        },
        status=status,
    )


def api_error(message: str, errors=None, status: int = 400) -> Response:
    return Response(
        {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors or {},
        },
        status=status,
    )


def get_request_employee(request):
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return None

    employee = getattr(user, "employee_profile", None)
    if employee:
        return employee

    employee_id = getattr(user, "employee_id", None)
    if employee_id:
        from apps.employees.models import Employee

        return Employee.objects.filter(id=employee_id, is_active=True).first()

    return None
