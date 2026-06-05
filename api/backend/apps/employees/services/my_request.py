"""Employee My Request screen helpers."""

from django.db.models import Count

from apps.employees.constants import ChangeRequestStatus
from apps.employees.models import EmployeeChangeRequest
from apps.employees.serializers.employee.my_request import REQUEST_SECTION_LABELS


STATUS_FILTERS = [
    {"value": "ALL", "label": "All"},
    {"value": ChangeRequestStatus.PENDING, "label": "Pending"},
    {"value": ChangeRequestStatus.APPROVED, "label": "Approved"},
    {"value": ChangeRequestStatus.REJECTED, "label": "Rejected"},
]


def get_my_request_sections():
    return [
        {"value": value, "label": label}
        for value, label in REQUEST_SECTION_LABELS.items()
    ]


def build_my_request_summary(employee):
    counts = {
        item["status"]: item["count"]
        for item in EmployeeChangeRequest.objects.filter(employee=employee)
        .values("status")
        .annotate(count=Count("id"))
    }
    return {
        "total": sum(counts.values()),
        "pending": counts.get(ChangeRequestStatus.PENDING, 0),
        "approved": counts.get(ChangeRequestStatus.APPROVED, 0),
        "rejected": counts.get(ChangeRequestStatus.REJECTED, 0),
    }


def get_my_requests_queryset(employee, status_filter=None):
    qs = EmployeeChangeRequest.objects.filter(employee=employee).select_related("employee")
    if status_filter and status_filter.upper() != "ALL":
        qs = qs.filter(status=status_filter.upper())
    return qs.order_by("-created_at")
