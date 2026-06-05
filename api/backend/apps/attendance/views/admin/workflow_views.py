"""
Admin views.

Endpoints:
  GET/POST   /admin/workflow-templates/
  GET/PUT    /admin/workflow-templates/<id>/
  GET        /admin/regularization/
  GET        /admin/regularization/<id>/
  POST       /admin/regularization/<id>/approve/
  POST       /admin/regularization/<id>/reject/
  GET        /admin/overtime/
  GET        /admin/overtime/<id>/
  POST       /admin/overtime/<id>/approve/
  POST       /admin/overtime/<id>/reject/
"""

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.attendance.models.requests import OvertimeRequest, RegularizationRequest
from apps.attendance.models.workflow import ApprovalWorkflowTemplate
from apps.attendance.serializers.workflow_serializers import (
    AdminOTDetailSerializer,
    AdminOTListSerializer,
    AdminRegularizationDetailSerializer,
    AdminRegularizationListSerializer,
    ApprovalWorkflowTemplateSerializer,
    ApproveRejectSerializer,
    OTApproveSerializer,
)
from apps.attendance.services.admin.requests.unified_requests import (
    get_regularization_queryset,
    resolve_acting_employee,
    resolve_company_id,
)
from apps.attendance.services.overtime_service import OvertimeRequestService
from apps.attendance.services.regularization_service import RegularizationRequestService
from apps.attendance.services.workflow_engine import WorkflowEngineError


class IsAdminOrHRAdmin(IsAuthenticated):
    """Allow Django staff or tenant HR admin roles (e.g. hr.admin + HR_ADMIN)."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        from apps.attendance.services.admin.requests.unified_requests import (
            user_has_company_wide_requests_access,
        )
        return user_has_company_wide_requests_access(request.user)


# ------------------------------------------------------------------
# Workflow Template — Admin only
# ------------------------------------------------------------------

@extend_schema_view(
    list=extend_schema(tags=["Attendance - Admin - Workflow Templates"]),
    create=extend_schema(tags=["Attendance - Admin - Workflow Templates"]),
    retrieve=extend_schema(tags=["Attendance - Admin - Workflow Templates"]),
    update=extend_schema(tags=["Attendance - Admin - Workflow Templates"]),
    partial_update=extend_schema(tags=["Attendance - Admin - Workflow Templates"]),
    destroy=extend_schema(tags=["Attendance - Admin - Workflow Templates"]),
)
class WorkflowTemplateViewSet(viewsets.ModelViewSet):
    """
    CRUD for approval workflow templates.
    Admin creates one template per request type per company.
    The template drives ALL approval routing dynamically.
    """

    tags = ["Attendance - Admin - Workflow Templates"]
    permission_classes = [IsAdminOrHRAdmin]
    serializer_class = ApprovalWorkflowTemplateSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "workflow_type"]

    def get_queryset(self):
        employee = getattr(self.request.user, "employee_profile", None)
        if not employee:
            return ApprovalWorkflowTemplate.objects.none()
        return (
            ApprovalWorkflowTemplate.objects.filter(company=employee.company)
            .prefetch_related("steps")
            .order_by("workflow_type")
        )

    def perform_create(self, serializer):
        employee = getattr(self.request.user, "employee_profile", None)
        serializer.save(company=employee.company)


# ------------------------------------------------------------------
# Admin Regularization ViewSet
# ------------------------------------------------------------------

@extend_schema_view(
    list=extend_schema(tags=["Attendance - Admin - Regularization"]),
    retrieve=extend_schema(tags=["Attendance - Admin - Regularization"]),
    approve=extend_schema(tags=["Attendance - Admin - Regularization"]),
    reject=extend_schema(tags=["Attendance - Admin - Regularization"]),
)
class AdminRegularizationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin read + approve/reject regularization requests across the company.
    Uses the same WorkflowEngine — admin is just another step in the template.
    """

    tags = ["Admin - Regularization"]
    permission_classes = [IsAdminOrHRAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "employee__first_name",
        "employee__last_name",
        "employee__employee_code",
    ]

    def get_queryset(self):
        qs = get_regularization_queryset(self.request.user, self.request.query_params)

        # Filters
        params = self.request.query_params
        if reg_type := params.get("reg_type"):
            qs = qs.filter(reg_type=reg_type)
        if status_val := params.get("status"):
            qs = qs.filter(status=status_val)
        if date_from := params.get("date_from"):
            qs = qs.filter(regularization_date__gte=date_from)
        if date_to := params.get("date_to"):
            qs = qs.filter(regularization_date__lte=date_to)
        if emp_id := params.get("employee_id"):
            qs = qs.filter(employee_id=emp_id)

        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AdminRegularizationDetailSerializer
        return AdminRegularizationListSerializer

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        obj = self.get_object()
        serializer = ApproveRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company_id = resolve_company_id(request.user, request.query_params.get("company_id"))
        acting_employee = resolve_acting_employee(request.user, company_id)
        if not acting_employee:
            return Response({"error": "No employee profile."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated = RegularizationRequestService.approve(
                acting_employee=acting_employee,
                reg_request=obj,
                remarks=serializer.validated_data.get("remarks", ""),
            )
        except WorkflowEngineError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            AdminRegularizationDetailSerializer(updated, context={"request": request}).data
        )

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        obj = self.get_object()
        serializer = ApproveRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company_id = resolve_company_id(request.user, request.query_params.get("company_id"))
        acting_employee = resolve_acting_employee(request.user, company_id)
        if not acting_employee:
            return Response({"error": "No employee profile."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated = RegularizationRequestService.reject(
                acting_employee=acting_employee,
                reg_request=obj,
                remarks=serializer.validated_data.get("remarks", ""),
            )
        except WorkflowEngineError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            AdminRegularizationDetailSerializer(updated, context={"request": request}).data
        )
    
    @action(detail=False, methods=["get"])
    def stats(self, request):
        from django.utils import timezone
        today = timezone.now().date()
        qs = self.get_queryset()
        return Response({
            "pending": qs.filter(status="PENDING").count(),
            "approved": qs.filter(status="APPROVED").count(),
            "rejected": qs.filter(status="REJECTED").count(),
            "approved_today": qs.filter(
                status="APPROVED",
                updated_at__date=today
            ).count(),
        })


# ------------------------------------------------------------------
# Admin OT ViewSet
# ------------------------------------------------------------------

@extend_schema_view(
    list=extend_schema(tags=["Attendance - Admin - Overtime"]),
    retrieve=extend_schema(tags=["Attendance - Admin - Overtime"]),
    approve=extend_schema(tags=["Attendance - Admin - Overtime"]),
    reject=extend_schema(tags=["Attendance - Admin - Overtime"]),
)
class AdminOTViewSet(viewsets.ReadOnlyModelViewSet):
    tags = ["Attendance - Admin - Overtime"]
    permission_classes = [IsAdminOrHRAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ["employee__first_name", "employee__last_name", "employee__employee_code"]

    def get_queryset(self):
        employee = getattr(self.request.user, "employee_profile", None)
        if not employee:
            return OvertimeRequest.objects.none()

        qs = OvertimeRequestService.get_queryset_for_admin(employee.company_id)

        params = self.request.query_params
        if status_val := params.get("status"):
            qs = qs.filter(status=status_val)
        if date_from := params.get("date_from"):
            qs = qs.filter(ot_date__gte=date_from)
        if date_to := params.get("date_to"):
            qs = qs.filter(ot_date__lte=date_to)

        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AdminOTDetailSerializer
        return AdminOTListSerializer

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        obj = self.get_object()
        serializer = OTApproveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        acting_employee = getattr(request.user, "employee_profile", None)
        if not acting_employee:
            return Response({"error": "No employee profile."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated = OvertimeRequestService.approve(
                acting_employee=acting_employee,
                ot_request=obj,
                remarks=serializer.validated_data.get("remarks", ""),
                approved_ot_mins=serializer.validated_data.get("approved_ot_mins"),
            )
        except WorkflowEngineError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(AdminOTDetailSerializer(updated, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        obj = self.get_object()
        serializer = ApproveRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        acting_employee = getattr(request.user, "employee_profile", None)
        if not acting_employee:
            return Response({"error": "No employee profile."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated = OvertimeRequestService.reject(
                acting_employee=acting_employee,
                ot_request=obj,
                remarks=serializer.validated_data.get("remarks", ""),
            )
        except WorkflowEngineError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(AdminOTDetailSerializer(updated, context={"request": request}).data)