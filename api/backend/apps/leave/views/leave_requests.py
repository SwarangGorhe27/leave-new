from datetime import date

from django.apps import apps
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.security.permissions import HasRBACPermission
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
    JSONParser,
)
from decimal import Decimal
from apps.core.openapi import (
    detail_response_schema,
    empty_ok_response,
    extend_schema,
    extend_schema_view,
    paginated_list_schema,
)
from apps.security.permissions import HasRBACPermission
from ..helpers import (
    get_employee_for_user,
    get_team_employee_filter,
    is_admin_user,
    paginate_queryset,
)
from ..models.transactions.leave_approvals import ApprovalStatusChoices, LeaveApproval
from ..models.transactions.leave_documents import LeaveDocument
from ..models.transactions.leave_requests import (
    LeaveRequest,
    LeaveDurationTypeChoices,
    LeaveRequestDay ,
    LeaveStatusChoices,
    ApplicationSourceChoices,
    LeaveSessionChoices
)
from ..services.file_service import upload_leave_document
from ..models.masters.leave_policy import EmployeeLeavePolicy
from ..models.masters.leave_types import LeaveType
from ..serializers.leave_requests import (
    LeaveApplicationActionSerializer,
    LeaveApplicationCancelSerializer,
    LeaveApplicationCommentSerializer,
    LeaveApplicationCreateSerializer,
    LeaveApplicationResubmitSerializer,
    LeaveApplicationSummarySerializer,
    LeaveApplicationUpdateSerializer,
    EmployeeLeaveApplicationDetailSerializer,
    ManagerLeaveApplicationSummarySerializer,
)
from ..services.leave_request_service import LeaveApplicationService    
from ..models.masters.reason import Reason
from ..serializers.master_serializers import ReasonSerializer

_LeaveApplicationIdResponse = detail_response_schema(
    name="LeaveApplicationIdResponse",
    extra_fields={"application_id": serializers.UUIDField()},
)
_LeaveApplicationListResponse = paginated_list_schema(LeaveApplicationSummarySerializer)


@extend_schema_view(
    post=extend_schema(
        request=LeaveApplicationCreateSerializer,
        responses={
            status.HTTP_202_ACCEPTED: _LeaveApplicationIdResponse
        },
        tags=["Employee (Leave)"],
        summary="Submit Leave Application",
    )
)
class EmployeeLeaveApplicationCreateView(APIView):
    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.apply_leave"]
    def post(self, request):

        serializer = LeaveApplicationCreateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        employee = get_employee_for_user(
            request.user
        )

        try:

            leave_request = (
                LeaveApplicationService.apply_leave(
                    employee=employee,

                    leave_type_id=serializer.validated_data[
                        "leave_type_id"
                    ],

                    from_date=serializer.validated_data[
                        "from_date"
                    ],

                    to_date=serializer.validated_data[
                        "to_date"
                    ],

                    from_session=serializer.validated_data[
                        "from_session"
                    ],

                    to_session=serializer.validated_data[
                        "to_session"
                    ],

                    reason=serializer.validated_data.get(
                        "reason"
                    ),

                    attachment=serializer.validated_data.get(
                        "attachment"
                    ),

                    contact_during_leave=serializer.validated_data.get(
                        "contact_during_leave"
                    ),

                    ip_address=request.META.get(
                        "REMOTE_ADDR"
                    ),
                )
            )

        except ValueError as exc:

            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "application_id": str(
                    leave_request.id
                )
            },
            status=status.HTTP_202_ACCEPTED,
        )

@extend_schema_view(
    get=extend_schema(
        responses={status.HTTP_200_OK: _LeaveApplicationListResponse},
        tags=["Employee (Leave)"],
        operation_id="leave_ess_applications_list",
        summary="List my leave applications",
    ),
)
class EmployeeLeaveApplicationListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]

    def get(self, request):
        employee = get_employee_for_user(request.user)

        queryset = (
            LeaveRequest.objects
            .select_related("leave_type")
            .filter(employee=employee)
        )

        status_param = request.query_params.get("status")
        year = request.query_params.get("year")

        if status_param:
            queryset = queryset.filter(status=status_param)

        if year:
            queryset = queryset.filter(from_date__year=year)

        results, total = paginate_queryset(
            queryset.order_by("-applied_at"),
            request,
        )

        serializer = LeaveApplicationSummarySerializer(
            results,
            many=True,
        )

        return Response(
            {
                "items": serializer.data,
                "total": total,
            }
        )


@extend_schema_view(
    get=extend_schema(
        responses={status.HTTP_200_OK: EmployeeLeaveApplicationDetailSerializer},
        tags=["Employee (Leave)"],
        operation_id="leave_ess_applications_detail",
        summary="Get leave application detail",
    ),
)
class EmployeeLeaveApplicationDetailView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_own_leave"]

    def get(self, request, id):
        employee = request.user.employee_profile
        leave_application = LeaveApplicationService.get_leave_application_for_employee(
            leave_application_id=id,
            employee=employee,
        )
        serializer = EmployeeLeaveApplicationDetailSerializer(leave_application)
        return Response(serializer.data)


@extend_schema_view(
    patch=extend_schema(
        request=LeaveApplicationUpdateSerializer,
        responses={status.HTTP_200_OK: _LeaveApplicationIdResponse},
        tags=["Employee (Leave)"],
        summary="Update a pending leave application",
    ),
)
class EmployeeLeaveApplicationUpdateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.edit_own_leave"]

    @transaction.atomic
    def patch(self, request, id):
        employee = request.user.employee_profile
        leave_request = LeaveApplicationService.get_leave_application_for_employee(
            leave_application_id=id,
            employee=employee,
        )

        if leave_request.status != LeaveStatusChoices.PENDING:
            return Response(
                {"detail": "Only pending leave requests can be updated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = LeaveApplicationUpdateSerializer(
            leave_request,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # ── Leave type ────────────────────────────────────────────────────────
        if "leave_type_id" in validated_data:
            leave_type = get_object_or_404(
                LeaveType,
                id=validated_data["leave_type_id"],
                is_active=True,
            )
            leave_request.leave_type = leave_type

        # ── Dates & sessions ──────────────────────────────────────────────────
        from_date = validated_data.get("from_date", leave_request.from_date)
        to_date = validated_data.get("to_date", leave_request.to_date)
        from_session = validated_data.get("from_session", leave_request.from_session)
        to_session = validated_data.get("to_session", leave_request.to_session)

        # Derive total_days from sessions
        # Half day  → same date, single session
        # Full days → span (to_date - from_date).days + 1
        # Adjust for half-day boundary sessions:
        #   from_session=SECOND_HALF subtracts 0.5 from start
        #   to_session=FIRST_HALF    subtracts 0.5 from end
        if from_date == to_date and from_session == to_session:
            total_days = Decimal("0.5")
        else:
            total_days = Decimal((to_date - from_date).days + 1)
            if from_session == LeaveSessionChoices.SECOND_HALF:
                total_days -= Decimal("0.5")
            if to_session == LeaveSessionChoices.FIRST_HALF:
                total_days -= Decimal("0.5")

        if total_days <= 0:
            return Response(
                {"detail": "Invalid leave duration."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        leave_request.from_date = from_date
        leave_request.to_date = to_date
        leave_request.from_session = from_session
        leave_request.to_session = to_session
        leave_request.total_days = total_days

        # ── Optional fields ───────────────────────────────────────────────────
        for field in ("reason", "contact_number", "mode_of_work", "notify_team"):
            if field in validated_data:
                setattr(leave_request, field, validated_data[field])

        if "backup_employee_id" in validated_data:
            leave_request.backup_employee_id = validated_data["backup_employee_id"]

        # persist changes first
        leave_request.save()

        # If dates or sessions changed, regenerate per-day entries
        if any(k in validated_data for k in ("from_date", "to_date", "from_session", "to_session")):
            # remove existing day entries
            LeaveRequestDay.objects.filter(leave_request=leave_request).delete()
            # generate new day payload using same logic as apply
            total_days, leave_days_payload = LeaveApplicationService._generate_leave_days(
                from_date=leave_request.from_date,
                to_date=leave_request.to_date,
                from_session=leave_request.from_session,
                to_session=leave_request.to_session,
            )
            for item in leave_days_payload:
                item.leave_request = leave_request
            LeaveRequestDay.objects.bulk_create(leave_days_payload)

        remove_document_ids = validated_data.get("remove_document_ids", [])
        attachment_files = validated_data.get("attachments", [])

        if hasattr(request.FILES, "getlist"):
            attachment_files = list(attachment_files) + list(
                request.FILES.getlist("attachments")
            )

        if remove_document_ids:
            LeaveDocument.objects.filter(
                leave_request=leave_request,
                id__in=remove_document_ids,
            ).delete()

        for attachment in attachment_files:
            document_metadata = upload_leave_document(attachment)
            LeaveDocument.objects.create(
                leave_request=leave_request,
                file_name=document_metadata["file_name"],
                file_url=document_metadata["file_url"],
                file_type=document_metadata.get("file_type"),
                file_size_kb=document_metadata.get("file_size_kb"),
                uploaded_by=employee,
            )

        return Response(
            {
                "detail": "Leave request updated successfully.",
                "application_id": str(leave_request.id),
            },
            status=status.HTTP_200_OK,
        )

@extend_schema_view(
    patch=extend_schema(
        request=LeaveApplicationCancelSerializer,
        responses=empty_ok_response(),
        tags=["Employee (Leave)"],
        summary="Cancel a leave application",
    ),
)
class EmployeeLeaveApplicationCancelView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.cancel_own_leave"]
    @transaction.atomic
    def patch(self, request, id):
        employee = get_employee_for_user(request.user)
        leave_request = get_object_or_404(LeaveRequest, id=id, employee=employee)
        serializer = LeaveApplicationCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if leave_request.status not in [
            LeaveStatusChoices.PENDING,
            LeaveStatusChoices.APPROVED,
        ]:
            return Response(
                {"detail": "Only pending or approved leave may be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        leave_request.status = LeaveStatusChoices.CANCELLED
        leave_request.cancellation_reason = serializer.validated_data["reason"]
        leave_request.save(
            update_fields=["status", "cancellation_reason", "updated_at"]
        )
        return Response(status=status.HTTP_200_OK)



@extend_schema_view(
    post=extend_schema(
        request=LeaveApplicationResubmitSerializer,
        responses={status.HTTP_200_OK: _LeaveApplicationIdResponse},
        tags=["Employee (Leave)"],
        summary="Resubmit a rejected leave application",
    ),
)
class EmployeeLeaveApplicationResubmitView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]

    required_permissions = ["leave.resubmit_rejected_leave"]

    @transaction.atomic
    def post(self, request, id):
        employee = get_employee_for_user(request.user)

        leave_request = get_object_or_404(
            LeaveRequest,
            id=id,
            employee=employee,
        )

        if leave_request.status != LeaveStatusChoices.REJECTED:
            return Response(
                {"detail": "Only rejected leave requests can be resubmitted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = LeaveApplicationResubmitSerializer(
            leave_request,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        if "leave_type_id" in validated_data:
            leave_type = get_object_or_404(
                LeaveType,
                id=validated_data["leave_type_id"],
                is_active=True,
            )
            leave_request.leave_type = leave_type

        from_date = validated_data.get(
            "from_date",
            leave_request.from_date,
        )

        to_date = validated_data.get(
            "to_date",
            leave_request.to_date,
        )

        is_half_day = validated_data.get(
            "is_half_day",
            leave_request.duration_type
            == LeaveDurationTypeChoices.HALF_DAY,
        )

        total_days = (
            0.5
            if is_half_day
            else (to_date - from_date).days + 1
        )

        if total_days <= 0:
            return Response(
                {"detail": "Invalid leave duration."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        leave_request.from_date = from_date
        leave_request.to_date = to_date
        leave_request.duration_type = (
            LeaveDurationTypeChoices.HALF_DAY
            if is_half_day
            else LeaveDurationTypeChoices.FULL_DAY
        )
        leave_request.total_days = total_days

        if "reason" in validated_data:
            leave_request.reason = validated_data["reason"]

        leave_request.status = LeaveStatusChoices.PENDING
        leave_request.rejection_reason = None

        leave_request.save()

        LeaveApproval.objects.filter(
            leave_request=leave_request
        ).update(
            status=ApprovalStatusChoices.PENDING,
            actioned_at=None,
            remarks=None,
        )

        return Response(
            {
                "detail": "Leave request resubmitted successfully.",
                "application_id": str(leave_request.id),
            },
            status=status.HTTP_200_OK,
        )


_CommentCreatedResponse = detail_response_schema(
    name="LeaveCommentCreatedResponse",
    extra_fields={"comment_id": serializers.UUIDField()},
)


@extend_schema_view(
    post=extend_schema(
        request=LeaveApplicationCommentSerializer,
        responses={status.HTTP_201_CREATED: _CommentCreatedResponse},
        tags=["Employee (Leave)"],
        summary="Add a comment to a leave application",
    ),
)
class EmployeeLeaveApplicationCommentView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.add_comment"]
    @transaction.atomic
    def post(self, request, id):
        employee = get_employee_for_user(request.user)

        leave_request = get_object_or_404(
            LeaveRequest,
            id=id,
            employee=employee,
        )

        serializer = LeaveApplicationCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        LeaveComment = apps.get_model(
            "leave",
            "LeaveComment",
        )

        comment = LeaveComment.objects.create(
            leave_request=leave_request,
            employee=employee,
            comment=serializer.validated_data["comment"],
        )

        return Response(
            {
                "detail": "Comment added successfully.",
                "comment_id": str(comment.id),
            },
            status=status.HTTP_201_CREATED,
        )

@extend_schema_view(
    get=extend_schema(
        responses={status.HTTP_200_OK: ManagerLeaveApplicationSummarySerializer(many=True)},
        tags=["Manager (Leave)"],
        summary="List team leave applications",
    ),
)
class ManagerTeamLeaveApplicationListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]

    required_permissions = ["leave.view_team_leave"]

    def get(self, request):
        filters = get_team_employee_filter(request.user)

        if filters is None:
            return Response(
                {"items": [], "total": 0},
                status=status.HTTP_200_OK,
            )

        queryset = LeaveRequest.objects.filter(**filters)

        status_param = request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        results, total = paginate_queryset(
            queryset.order_by("-applied_at"),
            request,
        )

        serializer = ManagerLeaveApplicationSummarySerializer(
            results,
            many=True,
        )

        return Response(
            {
                "items": serializer.data,
                "total": total,
            }
        )
    

@extend_schema_view(
    post=extend_schema(
        request=LeaveApplicationActionSerializer,
        responses=empty_ok_response(),
        tags=["Manager (Leave)"],
        summary="Approve or reject a team leave application",
    ),
)
class ManagerLeaveApplicationActionView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.approve_leave", "leave.reject_leave"]

    action_status = None

    @transaction.atomic
    def post(self, request, id):
        team_filters = get_team_employee_filter(request.user)

        # If the manager has no employee record, they have no team at all
        if team_filters is None:
            return Response(
                {"detail": "Leave application is not part of your team."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verify the leave request both exists AND belongs to the manager's team
        # in one query — avoids leaking existence of out-of-team requests
        leave_request = get_object_or_404(
            LeaveRequest, id=id, **team_filters
        )

        if leave_request.status not in [LeaveStatusChoices.PENDING]:
            return Response(
                {
                    "detail": "Leave application cannot be actioned in its current state."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = LeaveApplicationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee = get_employee_for_user(request.user)

        approval = LeaveApproval.objects.filter(
            leave_request=leave_request,
            approver=employee,
            approval_level=1,
        ).first()

        if not approval:
            return Response(
                {"detail": "Approval record not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        approval.status = self.action_status
        approval.remarks = serializer.validated_data.get(
            "remarks",
            "",
        )
        approval.save(
            update_fields=[
                "status",
                "remarks",
                "updated_at",
            ]
        )

        leave_request.status = (
            LeaveStatusChoices.APPROVED
            if self.action_status == ApprovalStatusChoices.APPROVED
            else LeaveStatusChoices.REJECTED
        )
        leave_request.save(update_fields=["status", "updated_at"])

        return Response(status=status.HTTP_200_OK)


class ManagerLeaveApplicationApproveView(ManagerLeaveApplicationActionView):
    action_status = ApprovalStatusChoices.APPROVED


class ManagerLeaveApplicationRejectView(ManagerLeaveApplicationActionView):
    action_status = ApprovalStatusChoices.REJECTED

@extend_schema_view(
    get=extend_schema(
        responses={status.HTTP_200_OK: _LeaveApplicationListResponse},
        tags=["Admin (Leave)"],
        summary="List leave applications (admin)",
    ),
)
class AdminLeaveApplicationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_admin_user(request.user):
            return Response(
                {"detail": "Admin or HR role required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = LeaveRequest.objects.all()
        employee_id = request.query_params.get("employee_id")
        status_param = request.query_params.get("status")
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if from_date:
            queryset = queryset.filter(from_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(to_date__lte=to_date)

        results, total = paginate_queryset(queryset.order_by("-applied_at"), request)
        serializer = LeaveApplicationSummarySerializer(results, many=True)
        return Response({"items": serializer.data, "total": total})

@extend_schema_view(
    get=extend_schema(
        responses={status.HTTP_200_OK: ReasonSerializer(many=True)},
        tags=["Employee (Leave)"],
        summary="List active leave reasons",
    ),
)
class ReasonListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]

    def get(self, request):

        category = request.query_params.get("category")

        queryset = Reason.objects.filter(
            is_active=True,
        )

        if category:
            queryset = queryset.filter(
                module=category.lower()
            )

        serializer = ReasonSerializer(
            queryset.order_by("label"),
            many=True,
        )

        return Response(serializer.data)
