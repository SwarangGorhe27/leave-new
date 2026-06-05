import uuid
from datetime import date, datetime

from django.apps import apps
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from ..helpers import (
    get_employee_for_user,
    get_team_employee_filter,
    paginate_queryset,
)
from apps.core.openapi import extend_schema, extend_schema_view
from ..models.transactions.leave_balances import LeaveBalance
from ..models.transactions.leave_balance_ledger import (
    LeaveBalanceLedger,
    LeaveTransactionTypeChoices,
)
from ..models.masters.leave_types import LeaveType
from ..serializers.leave_balances import (
    AdminLeaveBalanceSerializer,
    EmployeeLeaveBalanceSerializer,
    LeaveBalanceCreditSerializer,
    LeaveBalanceDebitSerializer,
    ManagerLeaveBalanceSerializer
)
from ..services.leave_balance_service import LeaveBalanceService
from apps.security.permissions import HasRBACPermission
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes


# =========================
# MANAGER TEAM BALANCE VIEW
# =========================

@extend_schema(
    tags=["Manager (Leave)"],
    responses={200: ManagerLeaveBalanceSerializer(many=True)},
)
class ManagerTeamLeaveBalanceView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_team_leave_balance"]

    def get(self, request):
        filters = get_team_employee_filter(request.user)

        if filters is None:
            return Response(
                {"items": [], "total": 0},
                status=status.HTTP_200_OK,
            )

        queryset = (
            LeaveBalance.objects
            .select_related(
                "employee",
                "leave_type",
            )
            .filter(**filters)
        )

        leave_type_id = request.query_params.get("leave_type_id")
        if leave_type_id:
            queryset = queryset.filter(
                leave_type_id=leave_type_id
            )

        results, total = paginate_queryset(
            queryset.order_by(
                "employee",
                "leave_type",
            ),
            request,
        )

        serializer = ManagerLeaveBalanceSerializer(
            results,
            many=True,
        )

        return Response(
            {
                "items": serializer.data,
                "total": total,
            }
        )


# =========================
# ADMIN BALANCE LIST VIEW
# =========================

@extend_schema(
    tags=["Admin (Leave)"],
    responses={200: AdminLeaveBalanceSerializer(many=True)},
)
class AdminLeaveBalanceListView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_leave_balance"]

    def get(self, request):
        queryset = LeaveBalance.objects.all()

        employee_id = request.query_params.get("employee_id")
        leave_type_id = request.query_params.get("leave_type_id")
        year = request.query_params.get("year")

        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if leave_type_id:
            queryset = queryset.filter(leave_type_id=leave_type_id)
        if year:
            queryset = queryset.filter(year=year)

        results, total = paginate_queryset(
            queryset.order_by("employee", "leave_type"),
            request,
        )

        serializer = AdminLeaveBalanceSerializer(results, many=True)

        return Response({"items": serializer.data, "total": total})


# =========================
# CREDIT BALANCE
# =========================

@extend_schema(
    tags=["Admin (Leave)"],
)
class AdminLeaveBalanceCreditView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.manage_leave_balance"]

    @extend_schema(
        request=LeaveBalanceCreditSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    @transaction.atomic
    def post(self, request):

        serializer = LeaveBalanceCreditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        employee_model = apps.get_model("employees", "Employee")
        employee = get_object_or_404(employee_model, pk=data["employee_id"])
        leave_type = get_object_or_404(LeaveType, pk=data["leave_type_id"])

        year = date.today().year

        balance, _ = LeaveBalance.objects.get_or_create(
            employee=employee,
            leave_type=leave_type,
            year=year,
            defaults={
                "leave_year_start": date(year, 1, 1),
                "leave_year_end": date(year, 12, 31),
            },
        )

        before = balance.total_available_balance
        balance.allocated_days += data["days"]
        balance.save()

        LeaveBalanceLedger.objects.create(
            id=uuid.uuid4(),
            employee=employee,
            leave_type=leave_type,
            year=balance.year,
            transaction_type=LeaveTransactionTypeChoices.ALLOCATION,
            days=data["days"],
            balance_before=before,
            balance_after=balance.total_available_balance,
            remarks=data.get("remarks", ""),
            transacted_by=get_employee_for_user(request.user),
        )

        return Response(
            {"balance": balance.total_available_balance},
            status=status.HTTP_201_CREATED,
        )


# =========================
# DEBIT BALANCE
# =========================

@extend_schema(
    tags=["Admin (Leave)"],
)
class AdminLeaveBalanceDebitView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.manage_leave_balance"]

    @extend_schema(
        request=LeaveBalanceDebitSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    @transaction.atomic
    def post(self, request):

        serializer = LeaveBalanceDebitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        employee_model = apps.get_model("employees", "Employee")
        employee = get_object_or_404(employee_model, pk=data["employee_id"])
        leave_type = get_object_or_404(LeaveType, pk=data["leave_type_id"])

        year = date.today().year

        balance = get_object_or_404(
            LeaveBalance,
            employee=employee,
            leave_type=leave_type,
            year=year,
        )

        before = balance.total_available_balance
        balance.used_days += abs(data["days"])
        balance.save()

        LeaveBalanceLedger.objects.create(
            id=uuid.uuid4(),
            employee=employee,
            leave_type=leave_type,
            year=balance.year,
            transaction_type=LeaveTransactionTypeChoices.ADJUSTMENT,
            days=-abs(data["days"]),
            balance_before=before,
            balance_after=balance.total_available_balance,
            remarks=data.get("remarks", ""),
            transacted_by=get_employee_for_user(request.user),
        )

        return Response(
            {"balance": balance.total_available_balance},
            status=status.HTTP_200_OK,
        )


# =========================
# EMPLOYEE BALANCE VIEW
# =========================

@extend_schema(
    tags=["Employee (Leave)"],
    responses={200: EmployeeLeaveBalanceSerializer(many=True)},
)
class EmployeeLeaveBalanceView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_own_leave_balance"]

    def get(self, request):
        employee = get_employee_for_user(request.user)
        year = request.query_params.get("year") or date.today().year

        queryset = LeaveBalance.objects.filter(employee=employee, year=year)
        serializer = EmployeeLeaveBalanceSerializer(queryset, many=True)

        return Response({"items": serializer.data}, status=status.HTTP_200_OK)


# =========================
# EMPLOYEE PROJECTION VIEW
# =========================

@extend_schema(
    tags=["Employee (Leave)"],
    responses={200: OpenApiTypes.OBJECT},
)
class EmployeeLeaveBalanceProjectionView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.view_leave_balance_projection"]

    def get(self, request):
        employee = get_employee_for_user(request.user)
        leave_type_id = request.query_params.get("leave_type_id")
        project_until = request.query_params.get("project_until")

        if not project_until:
            return Response(
                {"detail": "project_until is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            pu = datetime.strptime(project_until, "%Y-%m-%d").date()
        except Exception:
            return Response(
                {"detail": "project_until must be YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = LeaveBalanceService.project_leave_balance(
            str(employee.id),
            leave_type_id,
            pu,
        )

        return Response(
            {"status": "success", "data": result},
            status=status.HTTP_200_OK,
        )