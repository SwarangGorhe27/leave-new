"""
HRMS ESS — DRF Filters
"""
import django_filters
from django.db.models import Q
from apps.employees.models import EmployeeChangeRequest
from apps.employees.constants import ESSModule, ChangeRequestStatus


class ChangeRequestFilter(django_filters.FilterSet):
    """
    Filter set for EmployeeChangeRequest.

    Query params:
        status          PENDING | APPROVED | REJECTED | CANCELLED
        module          PROFILE | PERSONAL | ADDRESS | ...
        action          CREATE | UPDATE | DELETE
        employee_code   exact
        employee_name   icontains
        date_from       created_at >=
        date_to         created_at <=
        reviewed_from   reviewed_at >=
        reviewed_to     reviewed_at <=
        pending_only    true/false
    """

    status = django_filters.MultipleChoiceFilter(
        choices=[(s, s) for s in [
            ChangeRequestStatus.PENDING, ChangeRequestStatus.APPROVED,
            ChangeRequestStatus.REJECTED, ChangeRequestStatus.CANCELLED,
        ]],
        field_name="status",
    )
    module        = django_filters.MultipleChoiceFilter(choices=[(m, m) for m in ESSModule.ALL], field_name="module")
    action        = django_filters.CharFilter(field_name="action", lookup_expr="iexact")
    employee_code = django_filters.CharFilter(field_name="employee__employee_code", lookup_expr="iexact")
    employee_name = django_filters.CharFilter(method="filter_employee_name")
    date_from     = django_filters.DateFilter(field_name="created_at", lookup_expr="date__gte")
    date_to       = django_filters.DateFilter(field_name="created_at", lookup_expr="date__lte")
    reviewed_from = django_filters.DateFilter(field_name="reviewed_at", lookup_expr="date__gte")
    reviewed_to   = django_filters.DateFilter(field_name="reviewed_at", lookup_expr="date__lte")
    pending_only  = django_filters.BooleanFilter(method="filter_pending_only")

    class Meta:
        model  = EmployeeChangeRequest
        fields = ["status","module","action","employee_code","employee_name",
                  "date_from","date_to","reviewed_from","reviewed_to","pending_only"]

    def filter_employee_name(self, qs, name, value):
        return qs.filter(
            Q(employee__first_name__icontains=value) | Q(employee__last_name__icontains=value)
        )

    def filter_pending_only(self, qs, name, value):
        return qs.filter(status=ChangeRequestStatus.PENDING) if value else qs
