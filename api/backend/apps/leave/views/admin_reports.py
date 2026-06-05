from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.security.permissions import HasRBACPermission
from ..services.report_service import LeaveReportService
from ..services.approval_service import ApprovalWorkflowService
from apps.security.permissions import HasRBACPermission


@extend_schema(tags=["Admin (Leave)"])
class AdminLeaveSummaryReportView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_leave_summary_report"]

    def get(self, request):

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        department_id = request.query_params.get("department_id")
        employee_id = request.query_params.get("employee_id")
        leave_type_id = request.query_params.get("leave_type_id")

        # Build filters
        filters = {}
        if start_date:
            try:
                filters['start_date'] = datetime.strptime(start_date, "%Y-%m-%d").date()
            except Exception:
                pass
        if end_date:
            try:
                filters['end_date'] = datetime.strptime(end_date, "%Y-%m-%d").date()
            except Exception:
                pass
        if department_id:
            filters['department_id'] = department_id
        if employee_id:
            filters['employee_id'] = employee_id
        if leave_type_id:
            filters['leave_type_id'] = leave_type_id

        summary = LeaveReportService.get_leave_summary_report(filters)
        employee_wise_data = []  # Could be extended to include per-employee breakdowns

        return Response({
            "status": "success",
            "data": {
                "summary": summary,
                "employee_wise_data": employee_wise_data
            }
        })


@extend_schema(tags=["Admin (Leave)"])
class AdminLeaveEncashmentReportView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_leave_encashment_report"]

    def get(self, request):

        calendar_period_id = request.query_params.get("calendar_period_id")
        employee_id = request.query_params.get("employee_id")

        report = LeaveReportService.get_leave_encashment_report(employee_id=employee_id)

        # If calendar_period_id provided, you could filter further based on your business logic
        # For now, return the general encashment report
        return Response({
            "status": "success",
            "data": report
        })


@extend_schema(tags=["Admin (Leave)"])
class AdminApprovalTATReportView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_approval_tat_report"]

    def get(self, request):

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        sd = None
        ed = None
        if start_date:
            try:
                sd = datetime.strptime(start_date, "%Y-%m-%d").date()
            except Exception:
                pass
        if end_date:
            try:
                ed = datetime.strptime(end_date, "%Y-%m-%d").date()
            except Exception:
                pass

        report = LeaveReportService.get_approval_tat_report(start_date=sd, end_date=ed)

        return Response({
            "status": "success",
            "data": report
        })


@extend_schema(tags=["Admin (Leave)"])
class AdminLeavePatternAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_leave_pattern_analytics"]

    def get(self, request):

        employee_id = request.query_params.get("employee_id")

        patterns = LeaveReportService.get_leave_patterns(employee_id=employee_id)

        return Response({
            "status": "success",
            "data": {
                "insights": [],
                "trends": patterns
            }
        })


@extend_schema(tags=["Admin (Leave)"])
class AdminWorkflowConfigCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.manage_workflow_configs"]

    def post(self, request):

        data = request.data or {}
        department_id = data.get("department_id")
        leave_type_id = data.get("leave_type_id")
        workflow = data.get("workflow")

        result = ApprovalWorkflowService.create_workflow_config(
            department_id=department_id,
            leave_type_id=leave_type_id,
            workflow=workflow
        )

        return Response({
            "status": "success",
            "message": result.get("message")
        })
