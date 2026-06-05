from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.attendance.serializers.manager.team_attendance import (
    TeamAttendanceMemberSerializer,
    TeamAttendanceOverrideResponseSerializer,
    TeamAttendanceOverrideSerializer,
    TeamMemberAnalyticsSerializer,
    TeamMemberAttendanceSerializer,
    TeamMemberProfileSerializer,
    TeamMemberStatsSerializer,
)
from apps.attendance.services.manager.team_attendance import TeamAttendanceService


class TeamAttendanceBaseView(APIView):
    permission_classes = [IsAuthenticated]
    service_class = TeamAttendanceService

    def get_manager(self, request):
        return self.service_class().get_manager_employee(request.user)

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(exc, PermissionDenied):
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)


class TeamAttendanceView(TeamAttendanceBaseView):
    def get(self, request):
        service = self.service_class()
        data = service.get_team(self.get_manager(request))
        return Response(TeamAttendanceMemberSerializer(data, many=True).data)


class TeamMemberAttendanceView(TeamAttendanceBaseView):
    def get(self, request, employee_id):
        service = self.service_class()
        data = service.get_attendance(
            self.get_manager(request),
            str(employee_id),
            month=request.query_params.get("month"),
            year=request.query_params.get("year"),
        )
        return Response(TeamMemberAttendanceSerializer(data).data)

    def post(self, request, employee_id):
        serializer = TeamAttendanceOverrideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = self.service_class()
        data = service.override_attendance(
            self.get_manager(request),
            str(employee_id),
            serializer.validated_data,
        )
        return Response(
            TeamAttendanceOverrideResponseSerializer(data).data,
            status=status.HTTP_201_CREATED,
        )


class TeamMemberStatsView(TeamAttendanceBaseView):
    def get(self, request, employee_id):
        service = self.service_class()
        data = service.get_stats(
            self.get_manager(request),
            str(employee_id),
            month=request.query_params.get("month"),
            year=request.query_params.get("year"),
        )
        return Response(TeamMemberStatsSerializer(data).data)


class TeamMemberAnalyticsView(TeamAttendanceBaseView):
    def get(self, request, employee_id):
        service = self.service_class()
        data = service.get_analytics(
            self.get_manager(request),
            str(employee_id),
            range_name=request.query_params.get("range"),
            from_date=request.query_params.get("from_date"),
            to_date=request.query_params.get("to_date"),
        )
        return Response(TeamMemberAnalyticsSerializer(data).data)


class TeamMemberProfileView(TeamAttendanceBaseView):
    def get(self, request, employee_id):
        service = self.service_class()
        data = service.get_profile(self.get_manager(request), str(employee_id))
        return Response(TeamMemberProfileSerializer(data).data)
