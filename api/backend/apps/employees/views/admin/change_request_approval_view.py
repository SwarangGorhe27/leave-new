"""
Admin Views for Change Request Approval Workflow

Endpoints for HR/Admin to:
  1. List all pending change requests
  2. View detailed change request with diff
  3. Approve change request
  4. Reject change request
"""

import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
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
from apps.employees.serializers.employee import (
    AdminApproveSerializer,
    AdminRejectSerializer,
    AdminChangeRequestDetailSerializer,
    ChangeRequestReadSerializer,
)
from apps.employees.services.extended import ApprovalService
from apps.employees.utils import ESSPageNumberPagination, StandardResponse
from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasRBACPermission

logger = logging.getLogger(__name__)


@extend_schema_view(
    get=extend_schema(
        summary="List change requests (Admin)",
        tags=["Admin — Change Request Management"],
    ),
)
class ChangeRequestListAdminView(APIView):
    """
    GET  /api/admin/change-requests/    — List all change requests (paginated, filterable)
    
    Query Parameters:
      - status: PENDING, APPROVED, REJECTED, CANCELLED
      - module: PERSONAL, ADDRESS, FAMILY, etc.
      - employee: <uuid> — filter by employee
      - page: page number (default: 1)
    """
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_employee"]

    def get(self, request):
        qs = EmployeeChangeRequest.objects.select_related(
            "employee", "reviewed_by"
        ).order_by("-created_at")

        # Filter by status
        status_f = request.query_params.get("status", "").upper()
        if status_f:
            qs = qs.filter(status=status_f)

        # Filter by module
        module_f = request.query_params.get("module", "").upper()
        if module_f:
            qs = qs.filter(module=module_f)

        # Filter by employee
        employee_f = request.query_params.get("employee", "")
        if employee_f:
            try:
                qs = qs.filter(employee_id=employee_f)
            except ValueError:
                pass

        # Paginate
        paginator = ESSPageNumberPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ChangeRequestReadSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary="Get change request detail (Admin)",
        tags=["Admin — Change Request Management"],
    ),
)
class ChangeRequestDetailAdminView(APIView):
    """
    GET  /api/admin/change-request/<uuid:pk>/    — View change request with diff
    
    Shows side-by-side comparison of old_data vs request_data
    """
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.view_employee"]

    def get(self, request, pk):
        cr = get_object_or_404(
            EmployeeChangeRequest.objects.select_related("employee", "reviewed_by"),
            pk=pk
        )
        serializer = AdminChangeRequestDetailSerializer(cr)
        return Response(serializer.data)


@extend_schema_view(
    post=extend_schema(
        summary="Approve change request (Admin)",
        tags=["Admin — Change Request Management"],
    ),
)
class ChangeRequestApproveAdminView(APIView):
    """
    POST /api/admin/change-request/<uuid:pk>/approve/
    
    HR/Admin approves a change request.
    
    Request Body:
    {
        "admin_remarks": "Approved after verification"  (optional)
    }
    
    On Approval:
    - Status changes to APPROVED
    - reviewed_by set to current admin user
    - reviewed_at set to current timestamp
    - admin_remarks saved
    - Changes are applied to employee profile (automatic)
    """
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.edit_employee"]

    def post(self, request, pk):
        cr = get_object_or_404(EmployeeChangeRequest, pk=pk)

        # Check if already processed
        if cr.status != ChangeRequestStatus.PENDING:
            return Response(
                {"detail": f"Can only approve PENDING requests. Current status: {cr.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Deserialize approval payload
        serializer = AdminApproveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Approve
        try:
            admin_remarks = serializer.validated_data.get("admin_remarks", "")
            cr = ApprovalService.approve(
                change_request=cr,
                reviewed_by=request.user,
                remarks=admin_remarks,
            )

            logger.info(
                f"Change request {cr.id} approved by {request.user} | "
                f"Module: {cr.module} | Employee: {cr.employee.employee_code}"
            )

            return Response(
                {
                    "detail": "Change request approved successfully. Changes applied to employee profile.",
                    "request": ChangeRequestReadSerializer(cr).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.exception(f"Change request approval failed | cr_id={pk}")
            return StandardResponse.server_error()


@extend_schema_view(
    post=extend_schema(
        summary="Reject change request (Admin)",
        tags=["Admin — Change Request Management"],
    ),
)
class ChangeRequestRejectAdminView(APIView):
    """
    POST /api/admin/change-request/<uuid:pk>/reject/
    
    HR/Admin rejects a change request.
    
    Request Body (REMARKS REQUIRED):
    {
        "admin_remarks": "Documents not verified. Please resubmit with proof of address."
    }
    
    On Rejection:
    - Status changes to REJECTED
    - reviewed_by set to current admin user
    - reviewed_at set to current timestamp
    - admin_remarks saved (contains rejection reason)
    - NO changes applied to employee profile
    - Employee can submit new request
    """
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["employee.edit_employee"]

    def post(self, request, pk):
        cr = get_object_or_404(EmployeeChangeRequest, pk=pk)

        # Check if already processed
        if cr.status != ChangeRequestStatus.PENDING:
            return Response(
                {"detail": f"Can only reject PENDING requests. Current status: {cr.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Deserialize rejection payload
        serializer = AdminRejectSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Reject
        try:
            admin_remarks = serializer.validated_data["admin_remarks"]
            cr = ApprovalService.reject(
                change_request=cr,
                reviewed_by=request.user,
                remarks=admin_remarks,
            )

            logger.info(
                f"Change request {cr.id} rejected by {request.user} | "
                f"Module: {cr.module} | Employee: {cr.employee.employee_code} | "
                f"Reason: {admin_remarks}"
            )

            return Response(
                {
                    "detail": "Change request rejected.",
                    "request": ChangeRequestReadSerializer(cr).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.exception(f"Change request rejection failed | cr_id={pk}")
            return StandardResponse.server_error()
