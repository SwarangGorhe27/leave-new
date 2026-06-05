"""
Employee views.

Employee can:
  - Submit regularization / OT requests
  - View their own requests with timeline + current pending step info

Endpoints:
  GET/POST   /employee/regularization/
  GET        /employee/regularization/<id>/
  GET/POST   /employee/overtime/
  GET        /employee/overtime/<id>/
"""

from rest_framework import filters, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.attendance.models.requests import OvertimeRequest, RegularizationRequest
from apps.attendance.serializers.employee.request_serializers import (
    EmployeeOTCreateSerializer,
    EmployeeOTDetailSerializer,
    EmployeeOTListSerializer,
    EmployeeRegularizationCreateSerializer,
    EmployeeRegularizationDetailSerializer,
    EmployeeRegularizationListSerializer,
)
from apps.attendance.services.overtime_service import OvertimeRequestService
from apps.attendance.services.regularization_service import RegularizationRequestService
from apps.attendance.services.workflow_engine import WorkflowEngineError


def _get_employee(request):
    return getattr(request.user, "employee_profile", None)


@extend_schema_view(
    list=extend_schema(tags=["Attendance - Employee - Regularization"]),
    retrieve=extend_schema(tags=["Attendance - Employee - Regularization"]),
    create=extend_schema(tags=["Attendance - Employee - Regularization"]),
)
class EmployeeRegularizationViewSet(viewsets.GenericViewSet):
    """
    Employee submits and views their own regularization requests.
    No approve/reject here — that belongs to manager/admin.
    """

    tags = ["Attendance - Employee - Regularization"]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["regularization_date", "created_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        employee = _get_employee(self.request)
        if not employee:
            return RegularizationRequest.objects.none()

        qs = RegularizationRequestService.get_queryset_for_employee(employee)

        params = self.request.query_params
        if reg_type := params.get("reg_type"):
            qs = qs.filter(reg_type=reg_type)
        if status_val := params.get("status"):
            qs = qs.filter(status=status_val)
        if date_from := params.get("date_from"):
            qs = qs.filter(regularization_date__gte=date_from)
        if date_to := params.get("date_to"):
            qs = qs.filter(regularization_date__lte=date_to)

        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return EmployeeRegularizationCreateSerializer
        if self.action == "retrieve":
            return EmployeeRegularizationDetailSerializer
        return EmployeeRegularizationListSerializer

    def list(self, request):
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def create(self, request):
        employee = _get_employee(request)
        if not employee:
            return Response({"error": "No employee profile."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmployeeRegularizationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reg_request = RegularizationRequestService.create(
                employee=employee,
                validated_data=serializer.validated_data,
            )
        except WorkflowEngineError as e:
            # Workflow not configured — surface a clear error
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            EmployeeRegularizationDetailSerializer(reg_request, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    list=extend_schema(tags=["Attendance - Employee - Overtime"]),
    retrieve=extend_schema(tags=["Attendance - Employee - Overtime"]),
    create=extend_schema(tags=["Attendance - Employee - Overtime"]),
)
class EmployeeOTViewSet(viewsets.GenericViewSet):
    tags = ["Attendance - Employee - Overtime"]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["ot_date", "created_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        employee = _get_employee(self.request)
        if not employee:
            return OvertimeRequest.objects.none()

        qs = OvertimeRequestService.get_queryset_for_employee(employee)

        params = self.request.query_params
        if status_val := params.get("status"):
            qs = qs.filter(status=status_val)
        if date_from := params.get("date_from"):
            qs = qs.filter(ot_date__gte=date_from)
        if date_to := params.get("date_to"):
            qs = qs.filter(ot_date__lte=date_to)

        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return EmployeeOTCreateSerializer
        if self.action == "retrieve":
            return EmployeeOTDetailSerializer
        return EmployeeOTListSerializer

    def list(self, request):
        qs = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def create(self, request):
        employee = _get_employee(request)
        if not employee:
            return Response({"error": "No employee profile."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmployeeOTCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ot_request = OvertimeRequestService.create(
                employee=employee,
                validated_data=serializer.validated_data,
            )
        except WorkflowEngineError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            EmployeeOTDetailSerializer(ot_request, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )