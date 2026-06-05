from apps.attendance.serializers.manager.request_serializers import(
    ManagerOTListSerializer,
    ManagerOTDetailSerializer,
    ManagerRegularizationListSerializer,
    ManagerRegularizationDetailSerializer
)
from apps.attendance.serializers.manager.team_attendance import (
    TeamAttendanceMemberSerializer,
    TeamAttendanceOverrideResponseSerializer,
    TeamAttendanceOverrideSerializer,
    TeamMemberAnalyticsSerializer,
    TeamMemberAttendanceSerializer,
    TeamMemberProfileSerializer,
    TeamMemberStatsSerializer,
)



__all__ = [
    "ManagerOTListSerializer",
    "ManagerOTDetailSerializer",    
    "ManagerRegularizationListSerializer",
    "ManagerRegularizationDetailSerializer",
    "TeamAttendanceMemberSerializer",
    "TeamAttendanceOverrideResponseSerializer",
    "TeamAttendanceOverrideSerializer",
    "TeamMemberAnalyticsSerializer",
    "TeamMemberAttendanceSerializer",
    "TeamMemberProfileSerializer",
    "TeamMemberStatsSerializer",
]
