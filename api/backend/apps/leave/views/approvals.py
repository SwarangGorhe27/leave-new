from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from ..helpers import get_employee_for_user
from ..serializers.approvals import (
    ApprovalsBulkActionResponseSerializer,
    ApprovalsBulkActionSerializer,
    ApprovalsDelegateResponseSerializer,
    ApprovalsDelegateSerializer,    
)
from ..services.approval_service import ApprovalWorkflowService
from apps.security.permissions import HasRBACPermission


@extend_schema(tags=["Manager (Leave)"])
class ApprovalsBulkActionView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.approve_leave", "leave.reject_leave"]

    @extend_schema(
        request=ApprovalsBulkActionSerializer,
        responses={status.HTTP_200_OK: ApprovalsBulkActionResponseSerializer},
        summary="Approve or reject leave approvals in bulk",
    )
    def post(self, request):
        employee = get_employee_for_user(request.user)
        serializer = ApprovalsBulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        approval_ids = [
            str(approval_id)
            for approval_id in data["approval_ids"]
        ]

        result = ApprovalWorkflowService.bulk_action(
            data["action"],
            approval_ids,
            str(employee.id),
            data.get("remarks"),
        )

        return Response({"status": "success", "data": result})

@extend_schema(tags=["Manager (Leave)"])
class ApprovalsDelegateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = [
        "leave.delegate_authority",
        "leave.approve_leave",
    ]

    @extend_schema(
        request=ApprovalsDelegateSerializer,
        responses={status.HTTP_200_OK: ApprovalsDelegateResponseSerializer},
        summary="Delegate leave approval authority",
    )
    def post(self, request):
        employee = get_employee_for_user(request.user)
        serializer = ApprovalsDelegateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        result = ApprovalWorkflowService.delegate_authority(
            str(employee.id),
            str(data["delegate_to_user_id"]),
            data["start_date"],
            data["end_date"],
            data.get("reason"),
        )

        return Response({"status": "success", "message": result.get("message")})


@extend_schema(tags=["Manager (Leave)"])
class WorkflowConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee_id = request.query_params.get("employee_id")
        leave_type_id = request.query_params.get("leave_type_id")

        config = ApprovalWorkflowService.get_workflow_config(employee_id=employee_id, leave_type_id=leave_type_id)

        return Response({"status": "success", "data": {"workflow": config}})
