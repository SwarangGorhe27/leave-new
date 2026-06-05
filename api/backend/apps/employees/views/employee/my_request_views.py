"""Employee My Request screen APIs."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

try:
    from drf_spectacular.utils import extend_schema, extend_schema_view
except ImportError:

    def extend_schema(*args, **kwargs):
        def decorator(cls):
            return cls

        return decorator

    def extend_schema_view(**kwargs):
        def decorator(cls):
            return cls

        return decorator

from apps.employees.constants import ChangeRequestStatus
from apps.employees.models import EmployeeChangeRequest
from apps.employees.permissions import IsActiveEmployee
from apps.employees.serializers.employee.my_request import (
    MyRequestDetailSerializer,
    MyRequestListItemSerializer,
    MyRequestSubmitSerializer,
    MyRequestUpdateSerializer,
)
from apps.employees.serializers.employee.extended import ChangeRequestSubmitSerializer
from apps.employees.services.extended import ChangeRequestService
from apps.employees.services.my_request import (
    STATUS_FILTERS,
    build_my_request_summary,
    get_my_request_sections,
    get_my_requests_queryset,
)

from .helpers import get_request_employee

_TAG = "Employee - My Request"


def _create_change_request(employee, data):
    return ChangeRequestService.create(
        employee,
        {
            "module": data["module"],
            "action": data.get("action", EmployeeChangeRequest.Action.UPDATE),
            "request_data": data["request_data"],
            "record_id": data.get("record_id"),
            "remarks": data["description"],
        },
    )


@extend_schema_view(
    get=extend_schema(
        summary="Get my requests",
        description="Returns My Request screen counts, section options, filters, and request cards.",
        tags=[_TAG],
    ),
    post=extend_schema(
        summary="Submit a profile update request",
        description="Creates a pending employee change request for admin review.",
        tags=[_TAG],
        request=MyRequestSubmitSerializer,
    ),
)
class MyRequestListCreateView(APIView):
    """GET/POST /api/employee/my-requests/"""

    permission_classes = [IsAuthenticated, IsActiveEmployee]

    def get(self, request):
        employee = get_request_employee(request)
        status_filter = request.query_params.get("status", "ALL")
        queryset = get_my_requests_queryset(employee, status_filter)
        return Response(
            {
                "summary": build_my_request_summary(employee),
                "sections": get_my_request_sections(),
                "filters": STATUS_FILTERS,
                "results": MyRequestListItemSerializer(queryset, many=True).data,
            }
        )

    def post(self, request):
        employee = get_request_employee(request)
        serializer = MyRequestSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        change_request = _create_change_request(employee, serializer.validated_data)
        return Response(
            {
                "detail": "Request submitted for admin approval.",
                "request": MyRequestDetailSerializer(change_request).data,
                "summary": build_my_request_summary(employee),
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    get=extend_schema(summary="Get my request detail", tags=[_TAG]),
    patch=extend_schema(
        summary="Edit my pending request",
        description="Only pending requests owned by the logged-in employee can be edited.",
        tags=[_TAG],
        request=MyRequestUpdateSerializer,
    ),
)
class MyRequestDetailView(APIView):
    """GET/PATCH /api/employee/my-requests/{id}/"""

    permission_classes = [IsAuthenticated, IsActiveEmployee]

    def get_object(self, employee, pk):
        return get_object_or_404(
            EmployeeChangeRequest.objects.select_related("employee"),
            pk=pk,
            employee=employee,
        )

    def get(self, request, pk):
        employee = get_request_employee(request)
        change_request = self.get_object(employee, pk)
        return Response(MyRequestDetailSerializer(change_request).data)

    def patch(self, request, pk):
        employee = get_request_employee(request)
        change_request = self.get_object(employee, pk)
        if change_request.status != ChangeRequestStatus.PENDING:
            return Response(
                {"detail": "Only pending requests can be edited."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MyRequestUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        description = data.get("description", change_request.employee_remarks or "")
        request_data = data.get("request_data", change_request.request_data or {})
        if "request_data" in data and not request_data:
            request_data = {"_request_only": True, "description": description}
        elif request_data.get("_request_only") is True:
            request_data["description"] = description

        change_request.module = data.get("module", change_request.module)
        change_request.action = data.get("action", change_request.action)
        change_request.record_id = data.get("record_id", change_request.record_id)
        change_request.employee_remarks = description
        change_request.request_data = request_data

        if request_data and request_data.get("_request_only") is not True:
            validation = ChangeRequestSubmitSerializer(
                data={
                    "module": change_request.module,
                    "action": change_request.action,
                    "request_data": request_data,
                    "record_id": change_request.record_id,
                    "remarks": description,
                }
            )
            validation.is_valid(raise_exception=True)

        change_request.save(
            update_fields=[
                "module",
                "action",
                "record_id",
                "employee_remarks",
                "request_data",
                "updated_at",
            ]
        )

        return Response(
            {
                "detail": "Request updated and remains pending admin approval.",
                "request": MyRequestDetailSerializer(change_request).data,
            }
        )
