"""
Views for the seven other-request types.
Each type exposes:
  ESS:      POST   /ess/<type>/               create
            GET    /ess/<type>/               list mine
            PATCH  /ess/<type>/<id>/cancel/   cancel
  Manager:  GET    /manager/<type>/           list team
            POST   /manager/<type>/<id>/approve/
            POST   /manager/<type>/<id>/reject/
"""
from datetime import datetime

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.security.permissions import HasRBACPermission

from ..helpers import get_employee_for_user, get_team_employee_filter, paginate_queryset
from ..models.request_modules.comp_off import CompOffRequest
from ..models.request_modules.gate_pass_requests import GatePassRequest
from ..models.request_modules.out_duty_requests import OutDutyRequest
from ..models.request_modules.overtime_requests import OvertimeRequest
from ..models.request_modules.short_leave_requests import ShortLeaveRequest
from ..models.request_modules.week_off_shuffle_requests import WeeklyOffShuffleRequest
from ..models.request_modules.wfh_requests import WFHRequest
from ..serializers.other_requests import (
    CompOffRequestCreateSerializer,
    CompOffRequestSummarySerializer,
    GatePassRequestCreateSerializer,
    GatePassRequestSummarySerializer,
    OutDutyRequestCreateSerializer,
    OutDutyRequestSummarySerializer,
    OvertimeRequestCreateSerializer,
    OvertimeRequestSummarySerializer,
    RequestActionSerializer,
    ShortLeaveRequestCreateSerializer,
    ShortLeaveRequestSummarySerializer,
    WFHRequestCreateSerializer,
    WFHRequestSummarySerializer,
    WeeklyOffShuffleCreateSerializer,
    WeeklyOffShuffleSummarySerializer,
)


# ──────────────────────────────────────────────────────────────────────────────
# Mixins / base helpers
# ──────────────────────────────────────────────────────────────────────────────

def _action_request(request_obj, new_status: str, approver) -> None:
    """Set status + actioned_at + approved_by atomically."""
    request_obj.status = new_status
    request_obj.actioned_at = datetime.now()
    request_obj.approved_by = approver
    request_obj.save(update_fields=["status", "actioned_at", "approved_by", "updated_at"])


# ──────────────────────────────────────────────────────────────────────────────
# WFH
# ──────────────────────────────────────────────────────────────────────────────

class WFHRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.apply_leave"]

    def get(self, request):
        employee = get_employee_for_user(request.user)
        qs = WFHRequest.objects.filter(employee=employee).select_related("employee")
        status_p = request.query_params.get("status")
        if status_p:
            qs = qs.filter(status=status_p)
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": WFHRequestSummarySerializer(items, many=True).data, "total": total})

    @transaction.atomic
    def post(self, request):
        employee = get_employee_for_user(request.user)
        ser = WFHRequestCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        obj = WFHRequest.objects.create(
            employee=employee,
            from_date=d["from_date"],
            to_date=d["to_date"],
            total_days=d["total_days"],
            work_location_type=d["work_location_type"],
            vpn_confirmed=d.get("vpn_confirmed", False),
            connectivity_confirmed=d.get("connectivity_confirmed", False),
            reason=d.get("reason", ""),
            status="pending",
        )
        return Response({"id": str(obj.id)}, status=status.HTTP_201_CREATED)


class WFHRequestCancelView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.cancel_own_leave"]

    @transaction.atomic
    def patch(self, request, id):
        employee = get_employee_for_user(request.user)
        obj = get_object_or_404(WFHRequest, id=id, employee=employee)
        if obj.status != "pending":
            return Response({"detail": "Only pending WFH requests can be cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        obj.status = "cancelled"
        obj.save(update_fields=["status", "updated_at"])
        return Response(status=status.HTTP_200_OK)


class ManagerWFHListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_team_leave"]

    def get(self, request):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"items": [], "total": 0})
        qs = WFHRequest.objects.filter(**filters)
        status_p = request.query_params.get("status")
        if status_p:
            qs = qs.filter(status=status_p)
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": WFHRequestSummarySerializer(items, many=True).data, "total": total})


class ManagerWFHActionView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.approve_leave"]
    action_status: str = ""

    @transaction.atomic
    def post(self, request, id):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"detail": "Not part of your team."}, status=status.HTTP_403_FORBIDDEN)
        obj = get_object_or_404(WFHRequest, id=id, **filters)
        if obj.status != "pending":
            return Response({"detail": "Only pending requests can be actioned."}, status=status.HTTP_400_BAD_REQUEST)
        ser = RequestActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        approver = get_employee_for_user(request.user)
        _action_request(obj, self.action_status, approver)
        return Response(status=status.HTTP_200_OK)


class ManagerWFHApproveView(ManagerWFHActionView):
    action_status = "approved"


class ManagerWFHRejectView(ManagerWFHActionView):
    action_status = "rejected"


# ──────────────────────────────────────────────────────────────────────────────
# CompOff
# ──────────────────────────────────────────────────────────────────────────────

class CompOffRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.apply_leave"]

    def get(self, request):
        employee = get_employee_for_user(request.user)
        qs = CompOffRequest.objects.filter(employee=employee).select_related("employee")
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": CompOffRequestSummarySerializer(items, many=True).data, "total": total})

    @transaction.atomic
    def post(self, request):
        employee = get_employee_for_user(request.user)
        ser = CompOffRequestCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        obj = CompOffRequest.objects.create(
            employee=employee,
            worked_date=d["worked_date"],
            comp_off_type=d["comp_off_type"],
            earned_against_date_type=d["earned_against_date_type"],
            reason=d.get("reason", ""),
            proof_url=d.get("proof_url", ""),
            earned_days=d.get("earned_days", 1),
            expiry_date=d.get("expiry_date"),
            status="pending",
        )
        return Response({"id": str(obj.id)}, status=status.HTTP_201_CREATED)


class ManagerCompOffListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_team_leave"]

    def get(self, request):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"items": [], "total": 0})
        qs = CompOffRequest.objects.filter(**filters)
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": CompOffRequestSummarySerializer(items, many=True).data, "total": total})


class ManagerCompOffActionView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.approve_leave"]
    action_status: str = ""

    @transaction.atomic
    def post(self, request, id):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"detail": "Not part of your team."}, status=status.HTTP_403_FORBIDDEN)
        obj = get_object_or_404(CompOffRequest, id=id, **filters)
        if obj.status != "pending":
            return Response({"detail": "Only pending requests can be actioned."}, status=status.HTTP_400_BAD_REQUEST)
        approver = get_employee_for_user(request.user)
        _action_request(obj, self.action_status, approver)
        return Response(status=status.HTTP_200_OK)


class ManagerCompOffApproveView(ManagerCompOffActionView):
    action_status = "approved"


class ManagerCompOffRejectView(ManagerCompOffActionView):
    action_status = "rejected"


# ──────────────────────────────────────────────────────────────────────────────
# GatePass
# ──────────────────────────────────────────────────────────────────────────────

class GatePassRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.apply_leave"]

    def get(self, request):
        employee = get_employee_for_user(request.user)
        qs = GatePassRequest.objects.filter(employee=employee).select_related("employee")
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": GatePassRequestSummarySerializer(items, many=True).data, "total": total})

    @transaction.atomic
    def post(self, request):
        from ..models.masters.reason import Reason
        employee = get_employee_for_user(request.user)
        ser = GatePassRequestCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        purpose_type = get_object_or_404(Reason, id=d["purpose_type_id"])
        obj = GatePassRequest.objects.create(
            employee=employee,
            purpose=d["purpose"],
            purpose_type=purpose_type,
            movement_type=d["movement_type"],
            pass_type=d["pass_type"],
            from_location=d.get("from_location", ""),
            to_location=d.get("to_location", ""),
            start_time=d["start_time"],
            expected_return_time=d.get("expected_return_time"),
            duration_minutes=d["duration_minutes"],
            reason=d.get("reason", ""),
            status="pending",
        )
        return Response({"id": str(obj.id)}, status=status.HTTP_201_CREATED)


class ManagerGatePassListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_team_leave"]

    def get(self, request):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"items": [], "total": 0})
        qs = GatePassRequest.objects.filter(**filters)
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": GatePassRequestSummarySerializer(items, many=True).data, "total": total})


class ManagerGatePassActionView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.approve_leave"]
    action_status: str = ""

    @transaction.atomic
    def post(self, request, id):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"detail": "Not part of your team."}, status=status.HTTP_403_FORBIDDEN)
        obj = get_object_or_404(GatePassRequest, id=id, **filters)
        if obj.status != "pending":
            return Response({"detail": "Only pending requests can be actioned."}, status=status.HTTP_400_BAD_REQUEST)
        approver = get_employee_for_user(request.user)
        _action_request(obj, self.action_status, approver)
        return Response(status=status.HTTP_200_OK)


class ManagerGatePassApproveView(ManagerGatePassActionView):
    action_status = "approved"


class ManagerGatePassRejectView(ManagerGatePassActionView):
    action_status = "rejected"


# ──────────────────────────────────────────────────────────────────────────────
# OutDuty
# ──────────────────────────────────────────────────────────────────────────────

class OutDutyRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.apply_leave"]

    def get(self, request):
        employee = get_employee_for_user(request.user)
        qs = OutDutyRequest.objects.filter(employee=employee).select_related("employee")
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": OutDutyRequestSummarySerializer(items, many=True).data, "total": total})

    @transaction.atomic
    def post(self, request):
        from ..models.masters.reason import Reason
        from ..models.employees_proxy import get_employee_by_id
        employee = get_employee_for_user(request.user)
        ser = OutDutyRequestCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        purpose_type = get_object_or_404(Reason, id=d["purpose_type_id"])
        create_kwargs = dict(
            employee=employee,
            from_date=d["from_date"],
            to_date=d["to_date"],
            from_location=d.get("from_location", ""),
            to_location=d.get("to_location", ""),
            purpose_type=purpose_type,
            reason=d.get("reason", ""),
            travel_mode=d.get("travel_mode"),
            advance_amount=d.get("advance_amount"),
            status="pending",
        )
        if d.get("cc_manager_id"):
            from apps.employees.models import Employee
            create_kwargs["cc_manager"] = get_object_or_404(Employee, id=d["cc_manager_id"])
        obj = OutDutyRequest.objects.create(**create_kwargs)
        return Response({"id": str(obj.id)}, status=status.HTTP_201_CREATED)


class ManagerOutDutyListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_team_leave"]

    def get(self, request):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"items": [], "total": 0})
        qs = OutDutyRequest.objects.filter(**filters)
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": OutDutyRequestSummarySerializer(items, many=True).data, "total": total})


class ManagerOutDutyActionView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.approve_leave"]
    action_status: str = ""

    @transaction.atomic
    def post(self, request, id):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"detail": "Not part of your team."}, status=status.HTTP_403_FORBIDDEN)
        obj = get_object_or_404(OutDutyRequest, id=id, **filters)
        if obj.status != "pending":
            return Response({"detail": "Only pending requests can be actioned."}, status=status.HTTP_400_BAD_REQUEST)
        approver = get_employee_for_user(request.user)
        _action_request(obj, self.action_status, approver)
        return Response(status=status.HTTP_200_OK)


class ManagerOutDutyApproveView(ManagerOutDutyActionView):
    action_status = "approved"


class ManagerOutDutyRejectView(ManagerOutDutyActionView):
    action_status = "rejected"


# ──────────────────────────────────────────────────────────────────────────────
# ShortLeave
# ──────────────────────────────────────────────────────────────────────────────

class ShortLeaveRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.apply_leave"]

    def get(self, request):
        employee = get_employee_for_user(request.user)
        qs = ShortLeaveRequest.objects.filter(employee=employee).select_related("employee")
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": ShortLeaveRequestSummarySerializer(items, many=True).data, "total": total})

    @transaction.atomic
    def post(self, request):
        from ..models.masters.leave_policy import LeavePolicy
        employee = get_employee_for_user(request.user)
        ser = ShortLeaveRequestCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        policy = get_object_or_404(LeavePolicy, id=d["policy_id"])
        obj = ShortLeaveRequest.objects.create(
            employee=employee,
            policy=policy,
            leave_date=d["leave_date"],
            time_slot=d["time_slot"],
            start_time=d.get("start_time"),
            end_time=d.get("end_time"),
            duration_hours=d["duration_hours"],
            reason=d.get("reason", ""),
            status="pending",
        )
        return Response({"id": str(obj.id)}, status=status.HTTP_201_CREATED)


class ManagerShortLeaveListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_team_leave"]

    def get(self, request):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"items": [], "total": 0})
        qs = ShortLeaveRequest.objects.filter(**filters)
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": ShortLeaveRequestSummarySerializer(items, many=True).data, "total": total})


class ManagerShortLeaveActionView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.approve_leave"]
    action_status: str = ""

    @transaction.atomic
    def post(self, request, id):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"detail": "Not part of your team."}, status=status.HTTP_403_FORBIDDEN)
        obj = get_object_or_404(ShortLeaveRequest, id=id, **filters)
        if obj.status != "pending":
            return Response({"detail": "Only pending requests can be actioned."}, status=status.HTTP_400_BAD_REQUEST)
        approver = get_employee_for_user(request.user)
        _action_request(obj, self.action_status, approver)
        return Response(status=status.HTTP_200_OK)


class ManagerShortLeaveApproveView(ManagerShortLeaveActionView):
    action_status = "approved"


class ManagerShortLeaveRejectView(ManagerShortLeaveActionView):
    action_status = "rejected"


# ──────────────────────────────────────────────────────────────────────────────
# Overtime
# ──────────────────────────────────────────────────────────────────────────────

class OvertimeRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.apply_leave"]

    def get(self, request):
        employee = get_employee_for_user(request.user)
        qs = OvertimeRequest.objects.filter(employee=employee).select_related("employee")
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": OvertimeRequestSummarySerializer(items, many=True).data, "total": total})

    @transaction.atomic
    def post(self, request):
        employee = get_employee_for_user(request.user)
        ser = OvertimeRequestCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        obj = OvertimeRequest.objects.create(
            employee=employee,
            ot_date=d["ot_date"],
            ot_hours=d["ot_hours"],
            reason=d.get("reason", ""),
            grant_comp_off=d.get("grant_comp_off", False),
            status="pending",
        )
        return Response({"id": str(obj.id)}, status=status.HTTP_201_CREATED)


class ManagerOvertimeListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_team_leave"]

    def get(self, request):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"items": [], "total": 0})
        qs = OvertimeRequest.objects.filter(**filters)
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": OvertimeRequestSummarySerializer(items, many=True).data, "total": total})


class ManagerOvertimeActionView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.approve_leave"]
    action_status: str = ""

    @transaction.atomic
    def post(self, request, id):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"detail": "Not part of your team."}, status=status.HTTP_403_FORBIDDEN)
        obj = get_object_or_404(OvertimeRequest, id=id, **filters)
        if obj.status != "pending":
            return Response({"detail": "Only pending requests can be actioned."}, status=status.HTTP_400_BAD_REQUEST)
        approver = get_employee_for_user(request.user)
        _action_request(obj, self.action_status, approver)
        return Response(status=status.HTTP_200_OK)


class ManagerOvertimeApproveView(ManagerOvertimeActionView):
    action_status = "approved"


class ManagerOvertimeRejectView(ManagerOvertimeActionView):
    action_status = "rejected"


# ──────────────────────────────────────────────────────────────────────────────
# WeeklyOffShuffle
# ──────────────────────────────────────────────────────────────────────────────

class WeeklyOffShuffleListCreateView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.apply_leave"]

    def get(self, request):
        employee = get_employee_for_user(request.user)
        qs = WeeklyOffShuffleRequest.objects.filter(employee=employee).select_related("employee")
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": WeeklyOffShuffleSummarySerializer(items, many=True).data, "total": total})

    @transaction.atomic
    def post(self, request):
        employee = get_employee_for_user(request.user)
        ser = WeeklyOffShuffleCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        obj = WeeklyOffShuffleRequest.objects.create(
            employee=employee,
            week_start_date=d["week_start_date"],
            current_off_date=d["current_off_date"],
            requested_off_date=d["requested_off_date"],
            reason=d.get("reason", ""),
            impact_on_shift=d.get("impact_on_shift", ""),
            status="pending",
        )
        return Response({"id": str(obj.id)}, status=status.HTTP_201_CREATED)


class ManagerWeeklyOffShuffleListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_team_leave"]

    def get(self, request):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"items": [], "total": 0})
        qs = WeeklyOffShuffleRequest.objects.filter(**filters)
        items, total = paginate_queryset(qs.order_by("-created_at"), request)
        return Response({"items": WeeklyOffShuffleSummarySerializer(items, many=True).data, "total": total})


class ManagerWeeklyOffShuffleActionView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.approve_leave"]
    action_status: str = ""

    @transaction.atomic
    def post(self, request, id):
        filters = get_team_employee_filter(request.user)
        if filters is None:
            return Response({"detail": "Not part of your team."}, status=status.HTTP_403_FORBIDDEN)
        obj = get_object_or_404(WeeklyOffShuffleRequest, id=id, **filters)
        if obj.status != "pending":
            return Response({"detail": "Only pending requests can be actioned."}, status=status.HTTP_400_BAD_REQUEST)
        approver = get_employee_for_user(request.user)
        _action_request(obj, self.action_status, approver)
        return Response(status=status.HTTP_200_OK)


class ManagerWeeklyOffShuffleApproveView(ManagerWeeklyOffShuffleActionView):
    action_status = "approved"


class ManagerWeeklyOffShuffleRejectView(ManagerWeeklyOffShuffleActionView):
    action_status = "rejected"
