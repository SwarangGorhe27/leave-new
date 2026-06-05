from datetime import date

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.attendance.serializers.attendance_summary_serializer import AttendanceSummarySerializer
from apps.attendance.services.employee.attendance_summary_service import AttendanceSummaryService
from apps.attendance.utils.api import api_error, api_success, get_request_employee


def _current_month_yyyy_mm() -> str:
    today = date.today()
    return f"{today.year:04d}-{today.month:02d}"


class AttendanceSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)

        month = request.query_params.get("month", _current_month_yyyy_mm())

        service = AttendanceSummaryService()
        data = service.get_summary(str(employee.id), month)

        serializer = AttendanceSummarySerializer(data)
        return api_success(serializer.data)
