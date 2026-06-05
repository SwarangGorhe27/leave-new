"""
Manager views.

Manager sees ONLY requests where they are the current pending approver.
This is determined dynamically by ApprovalRequestAction — no role hardcoding.

Endpoints:
  GET        /manager/regularization/
  GET        /manager/regularization/<id>/
  POST       /manager/regularization/<id>/approve/
  POST       /manager/regularization/<id>/reject/
  GET        /manager/overtime/
  GET        /manager/overtime/<id>/
  POST       /manager/overtime/<id>/approve/
  POST       /manager/overtime/<id>/reject/
"""

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.attendance.models.requests import OvertimeRequest, RegularizationRequest
from apps.attendance.serializers.workflow_serializers import (
    ApproveRejectSerializer,
    OTApproveSerializer,
)
from apps.attendance.serializers.manager.request_serializers import (
    ManagerOTDetailSerializer,
    ManagerOTListSerializer,
    ManagerRegularizationDetailSerializer,
    ManagerRegularizationListSerializer,
)
from apps.attendance.services.overtime_service import OvertimeRequestService
from apps.attendance.services.regularization_service import RegularizationRequestService
from apps.attendance.services.workflow_engine import WorkflowEngineError
from apps.attendance.utils.api import get_request_employee


def _get_employee(request):
    return get_request_employee(request)


@extend_schema_view(
    list=extend_schema(tags=["Attendance - Manager - Regularization"]),
    retrieve=extend_schema(tags=["Attendance - Manager - Regularization"]),
    approve=extend_schema(tags=["Attendance - Manager - Regularization"]),
    reject=extend_schema(tags=["Attendance - Manager - Regularization"]),
)
class ManagerRegularizationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Manager reads and acts on regularization requests pending on their step.
    If the manager is not the current pending approver for a request,
    it will not appear in their list — enforced by the queryset.
    """

    tags = ["Attendance - Manager - Regularization"]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "employee__first_name",
        "employee__last_name",
        "employee__employee_code",
    ]

    def get_queryset(self):
        employee = _get_employee(self.request)
        if not employee:
            return RegularizationRequest.objects.none()

        qs = RegularizationRequestService.get_queryset_for_manager(employee)

        params = self.request.query_params
        if reg_type := params.get("reg_type"):
            qs = qs.filter(reg_type=reg_type)
        if status_val := params.get("status"):
            qs = qs.filter(status=status_val.upper())
        if date_from := params.get("date_from"):
            qs = qs.filter(regularization_date__gte=date_from)
        if date_to := params.get("date_to"):
            qs = qs.filter(regularization_date__lte=date_to)

        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ManagerRegularizationDetailSerializer
        return ManagerRegularizationListSerializer

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        obj = self.get_object()
        serializer = ApproveRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee = _get_employee(request)
        if not employee:
            return Response({"error": "No employee profile."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated = RegularizationRequestService.approve(
                acting_employee=employee,
                reg_request=obj,
                remarks=serializer.validated_data.get("remarks", ""),
            )
        except WorkflowEngineError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            ManagerRegularizationDetailSerializer(updated, context={"request": request}).data
        )

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        obj = self.get_object()
        serializer = ApproveRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee = _get_employee(request)
        if not employee:
            return Response({"error": "No employee profile."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated = RegularizationRequestService.reject(
                acting_employee=employee,
                reg_request=obj,
                remarks=serializer.validated_data.get("remarks", ""),
            )
        except WorkflowEngineError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            ManagerRegularizationDetailSerializer(updated, context={"request": request}).data
        )


@extend_schema_view(
    list=extend_schema(tags=["Attendance - Manager - Overtime"]),
    retrieve=extend_schema(tags=["Attendance - Manager - Overtime"]),
    approve=extend_schema(tags=["Attendance - Manager - Overtime"]),
    reject=extend_schema(tags=["Attendance - Manager - Overtime"]),
)
class ManagerOTViewSet(viewsets.ReadOnlyModelViewSet):
    tags = ["Attendance - Manager - Overtime"]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["employee__first_name", "employee__last_name", "employee__employee_code"]

    def get_queryset(self):
        employee = _get_employee(self.request)
        if not employee:
            return OvertimeRequest.objects.none()

        qs = OvertimeRequestService.get_queryset_for_manager(employee)

        params = self.request.query_params
        if status_val := params.get("status"):
            qs = qs.filter(status=status_val.upper())
        if date_from := params.get("date_from"):
            qs = qs.filter(ot_date__gte=date_from)
        if date_to := params.get("date_to"):
            qs = qs.filter(ot_date__lte=date_to)

        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ManagerOTDetailSerializer
        return ManagerOTListSerializer

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        obj = self.get_object()
        serializer = OTApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee = _get_employee(request)
        if not employee:
            return Response({"error": "No employee profile."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated = OvertimeRequestService.approve(
                acting_employee=employee,
                ot_request=obj,
                remarks=serializer.validated_data.get("remarks", ""),
                approved_ot_mins=serializer.validated_data.get("approved_ot_mins"),
            )
        except WorkflowEngineError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ManagerOTDetailSerializer(updated, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        obj = self.get_object()
        serializer = ApproveRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee = _get_employee(request)
        if not employee:
            return Response({"error": "No employee profile."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated = OvertimeRequestService.reject(
                acting_employee=employee,
                ot_request=obj,
                remarks=serializer.validated_data.get("remarks", ""),
            )
        except WorkflowEngineError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ManagerOTDetailSerializer(updated, context={"request": request}).data)
