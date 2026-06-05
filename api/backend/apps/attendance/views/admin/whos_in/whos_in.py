# apps/attendance/views/admin/whos_in.py

from datetime import datetime
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.attendance.services.whos_in import (
    WhoIsInFilters,
    WhoIsInService,
    InvalidFilterError,
    UnauthorizedAccessError,
)
from apps.attendance.serializers.whos_in import (
    WhoIsInQuerySerializer,
    WhoIsInEmployeesQuerySerializer,
    WhoIsInSummaryResponseSerializer,
    WhoIsInEmployeeListResponseSerializer,
    WhoIsInLiveSnapshotResponseSerializer,
    EmployeeDailySummaryResponseSerializer,
    ManualPunchRequestSerializer,
)
from apps.attendance.serializers.swipe_logs.manual_punch_serializers import ManualPunchResponseSerializer
from apps.attendance.services.swipe_logs.manual_punch_service import ManualPunchService

class BaseWhoIsInAPIView(APIView):
    """
    Base view for all Who's In APIs.
    Centralizes filter parsing and error handling.
    """
    permission_classes = [IsAuthenticated]

    def _build_filters(self, request) -> WhoIsInFilters:
        serializer = WhoIsInQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        v_data = serializer.validated_data

        return WhoIsInFilters(
            attendance_date=v_data.get("date"),
            company_id=v_data.get("company_id"),
            shift_id=v_data.get("shift_id"),
            department_id=v_data.get("department_id"),
            work_mode_id=v_data.get("work_mode_id"),
            designation_id=v_data.get("designation_id"),
            team_id=v_data.get("team_id"),
            search=v_data.get("search"),
        )

    def handle_exception(self, exc):
        if isinstance(exc, (InvalidFilterError, serializers.ValidationError)):
            message = str(exc)
            if hasattr(exc, 'detail'):
                message = exc.detail
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": message}},
                status=status.HTTP_400_BAD_REQUEST
            )
        if isinstance(exc, UnauthorizedAccessError):
            return Response(
                {
                    "error": {
                        "code": "COMPANY_ACCESS_DENIED",
                        "message": str(exc),
                    },
                    "detail": str(exc),
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().handle_exception(exc)


@extend_schema(
    tags=["Attendance - Who's In"],
    parameters=[WhoIsInQuerySerializer],
    responses={200: WhoIsInSummaryResponseSerializer}
)
class WhoIsInSummaryAPIView(BaseWhoIsInAPIView):
    """GET /attendance/who-is-in/summary"""
    def get(self, request):
        filters = self._build_filters(request)
        service = WhoIsInService(request.user, filters)
        data = service.get_summary()
        serializer = WhoIsInSummaryResponseSerializer(instance=data)
        return Response(serializer.data)


@extend_schema(
    tags=["Attendance - Who's In"],
    parameters=[WhoIsInEmployeesQuerySerializer],
    responses={200: WhoIsInEmployeeListResponseSerializer}
)
class WhoIsInEmployeesAPIView(BaseWhoIsInAPIView):
    """GET /attendance/who-is-in/employees"""
    def get(self, request):
        serializer = WhoIsInEmployeesQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        v_data = serializer.validated_data

        filters = WhoIsInFilters(
            attendance_date=v_data.get("date"),
            company_id=v_data.get("company_id"),
            shift_id=v_data.get("shift_id"),
            department_id=v_data.get("department_id"),
            work_mode_id=v_data.get("work_mode_id"),
            designation_id=v_data.get("designation_id"),
            team_id=v_data.get("team_id"),
            search=v_data.get("search"),
        )
        
        service = WhoIsInService(request.user, filters)
        data = service.get_employees(
            status=v_data.get("status"), 
            page=v_data.get("page"), 
            limit=v_data.get("limit")
        )
        serializer_res = WhoIsInEmployeeListResponseSerializer(
            instance=data,
            context={"presence_map": data.get("presence_map", {})},
        )
        return Response(serializer_res.data)


@extend_schema(
    tags=["Attendance - Who's In"],
    parameters=[WhoIsInQuerySerializer],
    responses={200: WhoIsInLiveSnapshotResponseSerializer}
)
class WhoIsInLiveAPIView(BaseWhoIsInAPIView):
    """GET /attendance/who-is-in/live"""
    def get(self, request):
        filters = self._build_filters(request)
        service = WhoIsInService(request.user, filters)
        data = service.get_live_snapshot()
        serializer = WhoIsInLiveSnapshotResponseSerializer(instance=data)
        return Response(serializer.data)


@extend_schema(
    tags=["Attendance - Who's In"],
    parameters=[WhoIsInQuerySerializer],
    responses={200: EmployeeDailySummaryResponseSerializer}
)
class EmployeeDailySummaryAPIView(BaseWhoIsInAPIView):
    """GET /attendance/employees/{employee_id}/daily-summary"""
    def get(self, request, employee_id):
        filters = self._build_filters(request)
        service = WhoIsInService(request.user, filters)
        record = service.get_employee_daily_summary(employee_id, filters.attendance_date)
        serializer = EmployeeDailySummaryResponseSerializer(record)
        return Response(serializer.data)


@extend_schema(
    tags=["Attendance - Who's In"],
    request=ManualPunchRequestSerializer,
    responses={201: ManualPunchResponseSerializer}
)
class ManualPunchAPIView(BaseWhoIsInAPIView):
    """POST /attendance/punch"""
    def post(self, request):
        serializer = ManualPunchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        v_data = serializer.validated_data
        
        # company_id fallback logic
        company_id = v_data.get("company_id") or getattr(request.user, "company_id", None)
        if not company_id and hasattr(request.user, "employee_profile"):
            company_id = request.user.employee_profile.company_id

        if not company_id:
            raise InvalidFilterError("company_id is required.")

        payload = {
            "company_id": company_id,
            "employee_id": v_data.get("employee_id"),
            "punch_type": v_data.get("punch_type"),
            "punch_time": v_data.get("punch_time"),
            "manual_override_reason": v_data.get("remarks") or "Manual punch from Who's In",
            "location_id": v_data.get("location_id"),
            "ip_address": v_data.get("ip_address"),
            "remarks": v_data.get("remarks"),
        }

        punch = ManualPunchService.create_manual_punch(request.user, payload)
        return Response(ManualPunchResponseSerializer(punch).data, status=status.HTTP_201_CREATED)
