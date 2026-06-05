import uuid
from django.apps import apps
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from ..helpers import get_employee_for_user, is_admin_user
from ..models.transactions.holiday_branch import HolidayBranchMap
from ..serializers.leave_holidays import (
    AdminHolidayCreateRequestSerializer,
    AdminHolidayCreateResponseSerializer,
    AdminHolidayListItemSerializer,
    AdminHolidayListRequestSerializer,
    AdminHolidayListResponseSerializer,
    CarryForwardSerializer,
    HolidayCalendarSerializer,
    HolidayGroupAssignmentSerializer,
)
from ..services.holiday_service import HolidayService
from apps.security.permissions import HasRBACPermission
from drf_spectacular.utils import extend_schema


# def get_company_id_for_request(request):
#     auth = getattr(request, "auth", None)

#     if auth:
#         try:
#             company_id = auth.get("company_id")
#             if company_id:
#                 return company_id
#         except AttributeError:
#             pass

#     company_id = getattr(request.user, "company_id", None)
#     if company_id:
#         return company_id

#     employee = getattr(request.user, "employee_profile", None)
#     if employee:
#         company_id = getattr(employee, "company_id", None)
#         if company_id:
#             return company_id

#         company = getattr(employee, "company", None)
#         if company:
#             return getattr(company, "id", None)

#     return None


# =========================
# HOLIDAY ADMIN LIST/CREATE
# =========================

@extend_schema(tags=["Admin (Leave)"])
class AdminHolidayListView(APIView):
    permission_classes = [IsAuthenticated]

    def _require_admin(self, request):
        if not is_admin_user(request.user):
            return Response(
                {"detail": "Admin or HR role required."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    @extend_schema(
        parameters=[AdminHolidayListRequestSerializer],
        responses={200: AdminHolidayListResponseSerializer},
        summary="Get admin holiday list",
    )
    def get(self, request):
        denied = self._require_admin(request)
        if denied:
            return denied

        request_serializer = AdminHolidayListRequestSerializer(
            data=request.query_params
        )
        request_serializer.is_valid(raise_exception=True)

        holidays = HolidayService.list_admin_holidays(
            request_serializer.validated_data
        )
        response_serializer = AdminHolidayListItemSerializer(
            holidays, many=True
        )

        return Response({
            "status": "success",
            "data": response_serializer.data,
        })

    @extend_schema(
        request=AdminHolidayCreateRequestSerializer,
        responses={200: AdminHolidayCreateResponseSerializer},
        summary="Add admin holiday",
    )
    def post(self, request):
        denied = self._require_admin(request)
        if denied:
            return denied

        request_serializer = AdminHolidayCreateRequestSerializer(
            data=request.data
        )
        request_serializer.is_valid(raise_exception=True)

        company_id = None
        try:
            employee = get_employee_for_user(request.user)
            company_id = getattr(employee, "company_id", None) or getattr(
                getattr(employee, "company", None), "id", None
            )
        except ValidationError:
            pass

        HolidayService.create_admin_holiday(
            request_serializer.validated_data,
            company_id=company_id,
            user_id=getattr(request.user, "id", None),
        )

        return Response(
            {"status": "success", "message": "Holiday added"},
            status=status.HTTP_200_OK,
        )


# =========================
# EMPLOYEE HOLIDAY CALENDAR
# =========================

@extend_schema(tags=["Employee (Leave)"])
class EmployeeHolidayCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: HolidayCalendarSerializer(many=True)},
        summary="Employee holiday calendar",
    )
    def get(self, request):
        employee = get_employee_for_user(request.user)
        year = request.query_params.get("year")

        # Try to get holidays from HolidayBranchMap first (branch-based)
        branch = getattr(employee, "branch", None)
        holidays = []

        if branch:
            queryset = HolidayBranchMap.objects.filter(branch=branch).select_related(
                "holiday"
            )
            if year:
                queryset = queryset.filter(holiday__date__year=year)

            for mapping in queryset:
                holiday = mapping.holiday
                holidays.append(
                    {
                        "id": str(getattr(holiday, "id", "")),
                        "date": getattr(holiday, "date", None),
                        "name": getattr(holiday, "name", str(holiday)),
                        "type": getattr(
                            holiday, "type", getattr(holiday, "holiday_type", None)
                        ),
                        "is_optional": getattr(holiday, "holiday_type", "") == "OPTIONAL",
                    }
                )

        # If no branch-based holidays found, fetch from HolidayCalendar/Holiday models
        if not holidays:
            try:
                Holiday = apps.get_model("employees", "Holiday")
                HolidayCalendar = apps.get_model("employees", "HolidayCalendar")

                # Get all active holiday calendars
                calendars = HolidayCalendar.objects.filter(is_active=True)
                if year:
                    calendars = calendars.filter(calendar_year=int(year))

                # Get holidays from these calendars
                holiday_ids = calendars.values_list('id', flat=True)
                holiday_queryset = Holiday.objects.filter(
                    holiday_calendar_id__in=holiday_ids,
                    is_active=True
                ).order_by('holiday_date')

                if year:
                    holiday_queryset = holiday_queryset.filter(holiday_date__year=int(year))

                for holiday in holiday_queryset:
                    holidays.append(
                        {
                            "id": str(holiday.id),
                            "date": holiday.holiday_date,
                            "name": holiday.name,
                            "type": holiday.holiday_type,
                            "is_optional": holiday.holiday_type == "OPTIONAL",
                        }
                    )
            except Exception:
                # If models don't exist, return empty list
                pass

        serializer = HolidayCalendarSerializer(holidays, many=True)
        return Response(serializer.data)


# =========================
# HOLIDAY GROUP ASSIGNMENT
# =========================

@extend_schema(tags=["Admin (Leave)"])
class AdminHolidayGroupAssignmentView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.manage_holiday_group_assignments"]

    @extend_schema(
        request=HolidayGroupAssignmentSerializer,
        responses={200: None},
        summary="Assign holiday group",
    )
    def post(self, request):
        # if not is_admin_user(request.user):
        #     return Response(
        #         {"detail": "Admin or HR role required."},
        #         status=status.HTTP_403_FORBIDDEN,
        #     )

        serializer = HolidayGroupAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            assignment_model = apps.get_model(
                "holiday",
                "HolidayGroupAssignment"
            )
        except LookupError:
            return Response(
                {"detail": "HolidayGroupAssignment model unavailable."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created = []
        for employee_id in data["employee_ids"]:
            assignment = assignment_model.objects.create(
                employee_id=employee_id,
                holiday_group_id=data["holiday_group_id"],
            )
            created.append(str(assignment.id))

        return Response({"created": created}, status=status.HTTP_200_OK)


# =========================
# CARRY FORWARD
# =========================

@extend_schema(tags=["Admin (Leave)"])
class AdminLeaveCarryForwardView(APIView):
    permission_classes = [IsAuthenticated, HasRBACPermission]
    required_permissions = ["leave.manage_carry_forward"]

    @extend_schema(
        request=CarryForwardSerializer,
        responses={202: None},
        summary="Carry forward leave",
    )
    def post(self, request):
        # if not is_admin_user(request.user):
        #     return Response(
        #         {"detail": "Admin or HR role required."},
        #         status=status.HTTP_403_FORBIDDEN,
        #     )

        serializer = CarryForwardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_id = uuid.uuid4()

        return Response(
            {"task_id": str(task_id)},
            status=status.HTTP_202_ACCEPTED,
        )