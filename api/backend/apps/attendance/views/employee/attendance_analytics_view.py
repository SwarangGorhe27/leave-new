from datetime import date

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.attendance.serializers.attendance_analytics_serializer import AttendanceAnalyticsSerializer
from apps.attendance.services.employee.attendance_analytics_service import AttendanceAnalyticsService
from apps.attendance.utils.api import api_error, api_success, get_request_employee


def _current_month_yyyy_mm() -> str:
    today = date.today()
    return f"{today.year:04d}-{today.month:02d}"


class AttendanceAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)

        month = request.query_params.get("month", _current_month_yyyy_mm())

        service = AttendanceAnalyticsService()
        data = service.get_analytics(str(employee.id), month)

        serializer = AttendanceAnalyticsSerializer(data)
        return api_success(serializer.data)
