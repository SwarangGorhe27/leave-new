import uuid

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission


def get_user_group_names(user):
    groups = set()
    if hasattr(user, "groups"):
        try:
            groups = {g.name.lower() for g in user.groups.all()}
        except Exception:
            pass
    return groups


def user_has_group(user, names):
    if not user or not hasattr(user, "is_authenticated") or not user.is_authenticated:
        return False
    allowed = {name.lower() for name in (names or [])}
    if user.is_superuser or getattr(user, "is_staff", False):
        return True
    return bool(get_user_group_names(user) & allowed)


def is_admin_user(user):
    """True for staff/superuser or employees with HR/security admin RBAC roles."""
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True

    employee = getattr(user, "employee_profile", None)
    if employee is None:
        return False

    from apps.security.services import get_employee_roles

    admin_codes = {"SUPER_ADMIN", "HR_ADMIN", "PAYROLL_ADMIN"}
    role_codes = set(get_employee_roles(employee).values_list("code", flat=True))
    return bool(role_codes & admin_codes)


def get_employee_for_user(user):
    if not user or not user.is_authenticated:
        raise ValidationError(
            "Authentication required to resolve employee record."
        )

    employee = getattr(user, "employee_profile", None)

    if employee is None:
        raise ValidationError(
            f"No employee profile linked to {user.email}"
        )

    return employee

def get_employee_model():
    try:
        return apps.get_model("employees", "Employees")
    except LookupError:
        return None


from apps.employees.models import Employee, EmployeeReportingRelationship
from django.db.models import Q


def get_team_employee_filter(user):
    """
    Returns filter for employees reporting to the logged-in manager.
    """

    try:
        manager = Employee.objects.get(user=user)
    except Employee.DoesNotExist:
        return None

    direct_report_ids = (
        EmployeeReportingRelationship.objects.filter(
            reports_to_employee=manager,
            relationship_type=EmployeeReportingRelationship.RelationshipType.PRIMARY,
            is_active=True,
        )
        .values_list("employee_id", flat=True)
    )

    return {
        "employee_id__in": direct_report_ids
    }


def parse_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def paginate_queryset(queryset, request, page_size=25):
    page = parse_int(request.query_params.get("page"), 1) or 1
    page = max(1, page)
    offset = (page - 1) * page_size
    return queryset[offset : offset + page_size], queryset.count()


# class IsManagerPermission(BasePermission):
#     def has_permission(self, request, view):
#         return bool(
#             request.user
#             and request.user.is_authenticated
#             and is_manager_user(request.user)
#         )


# class IsAdminOrHRPermission(BasePermission):
#     def has_permission(self, request, view):
#         return bool(
#             request.user
#             and request.user.is_authenticated
#             and is_admin_user(request.user)
#         )
