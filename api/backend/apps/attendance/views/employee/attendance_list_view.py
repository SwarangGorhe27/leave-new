from datetime import date

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.attendance.serializers.attendance_list_serializer import AttendanceListSerializer
from apps.attendance.services.employee.attendance_list_service import AttendanceListService
from apps.attendance.utils.api import api_error, api_success, get_request_employee


class AttendanceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)

        qp = request.query_params
        month = qp.get("month")
        page = int(qp.get("page", 1))
        per_page = int(qp.get("per_page", 20))
        status = qp.get("status")
        shift = qp.get("shift")
        search_date = qp.get("search_date")  # expect YYYY-MM-DD
        from_date = qp.get("from_date")
        to_date = qp.get("to_date")
        sort = qp.get("sort", "date_desc")

        service = AttendanceListService()

        try:
            data = service.get_list(
                employee_id=str(employee.id),
                month=month,
                page=page,
                per_page=per_page,
                status=status,
                shift=shift,
                search_date=search_date,
                from_date=from_date,
                to_date=to_date,
                sort=sort,
            )
        except ValueError as exc:
            return api_error(str(exc), status=400)

        serializer = AttendanceListSerializer(data)
        return api_success(serializer.data)


class AttendanceListCompatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee = get_request_employee(request)
        if not employee:
            return api_error("Employee profile not found for authenticated user", status=400)

        month_num = request.query_params.get("month")
        year = request.query_params.get("year")
        month = request.query_params.get("month_key")
        if not month and month_num and year:
            month = f"{int(year):04d}-{int(month_num):02d}"
        if not month:
            today = date.today()
            month = f"{today.year:04d}-{today.month:02d}"

        try:
            data = AttendanceListService().get_list(
                employee_id=str(employee.id),
                month=month,
                page=int(request.query_params.get("page", 1)),
                per_page=int(request.query_params.get("per_page", 50)),
                status=request.query_params.get("status"),
                shift=request.query_params.get("shift"),
                search_date=request.query_params.get("search_date"),
                from_date=request.query_params.get("from_date"),
                to_date=request.query_params.get("to_date"),
                sort=request.query_params.get("sort", "date_desc"),
            )
        except ValueError as exc:
            return api_error(str(exc), status=400)

        rows = []
        for record in data["records"]:
            status_value = str(record["status"]).upper()
            status_map = {
                "PRESENT": "PRESENT",
                "ABSENT": "ABSENT",
                "HALF_DAY": "HALF_DAY",
                "LEAVE": "LEAVE",
                "HOLIDAY": "HOLIDAY",
                "WEEK_OFF": "WEEK_OFF",
                "WORK_OFF": "WEEK_OFF",
                "LATE_IN": "PRESENT",
                "WORK_FROM_HOME": "PRESENT",
            }
            first_in = record["timing"].get("in")
            last_out = record["timing"].get("out")
            rows.append(
                {
                    "id": record.get("id") or f"{employee.id}-{record['date']}",
                    "employee_code": employee.employee_code,
                    "employee_name": employee.full_name,
                    "date": record["date"].isoformat() if hasattr(record["date"], "isoformat") else record["date"],
                    "shift_name": record.get("shift_name") or "General Shift",
                    "first_in": first_in,
                    "last_out": last_out,
                    "effective_hours": f"{record['work_hours']:.2f}",
                    "late_mins": record.get("late_mins", 0),
                    "early_leave_mins": record.get("early_exit_mins", 0),
                    "overtime_mins": record.get("ot_mins", 0),
                    "status": status_map.get(status_value, "NOT_COMPUTED"),
                    "is_regularized": False,
                    "remarks": "",
                }
            )
        return api_success({"results": rows, "count": data["total"]})


class AttendanceHolidayCompatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.employees.models.masters.hr_setup import Holiday
        
        employee = get_request_employee(request)
        if not employee:
            return Response({"results": []})
            
        holidays = Holiday.objects.filter(is_active=True).order_by("holiday_date")
        
        results = []
        for h in holidays:
            results.append({
                "id": str(h.id),
                "name": h.name,
                "date": h.holiday_date.isoformat(),
                "holiday_type": h.get_holiday_type_display() if hasattr(h, 'get_holiday_type_display') else h.holiday_type,
                "is_optional": h.holiday_type == "OPTIONAL",
            })
            
        return Response({"results": results})
