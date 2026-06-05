"""
Attendance Intelligence API Views.

Endpoints for dashboard analytics, trends, anomaly detection,
and attendance insights.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.utils import timezone

from apps.attendance.services.attendance_intelligence.attendance_analytics_service import (
    AttendanceAnalyticsService,
)
from apps.attendance.serializers.attendance_intelligence.attendance_analytics_serializer import (
    DashboardKPISerializer,
    TrendDataPointSerializer,
    PeakHourSerializer,
    DeviceDistributionSerializer,
    VerificationStatisticsSerializer,
    SpoofAlertSerializer,
    LocationHeatmapSerializer,
    EmployeeSwipePatternSerializer,
    AnomalySerializer,
    MissingPunchSerializer,
)

logger = logging.getLogger(__name__)

def _get_company_id(request):
    """Return company_id from query params or authenticated user."""
    company_id = request.query_params.get("company_id")
    if company_id:
        return company_id
    user = request.user
    if hasattr(user, "employee") and user.employee:
        return user.employee.company_id
    if hasattr(user, "employee_profile") and user.employee_profile:
        return user.employee_profile.company_id
    return None

class AttendanceDashboardAPIView(APIView):
    """
    API endpoint for attendance dashboard analytics.

    GET /api/v1/attendance/intelligence/dashboard/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get dashboard KPIs and analytics."""
        try:
            company_id = _get_company_id(request)
            if not company_id:
                return Response(
                    {"detail": "Company context not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            date_str = request.query_params.get("date")

            date = None
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str).date()
                except ValueError:
                    return Response(
                        {"detail": "Invalid date format. Use ISO format (YYYY-MM-DD)."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            kpis = AttendanceAnalyticsService.get_dashboard_kpis(
                company_id=company_id,
                date=date,
            )
            trends = AttendanceAnalyticsService.get_attendance_trends(
                company_id=company_id,
                days=7,
            )

            serializer = DashboardKPISerializer(kpis)
            trends_serializer = TrendDataPointSerializer(trends, many=True)

            return Response(
                {
                    "kpis": serializer.data,
                    "trends_7_days": trends_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Dashboard API error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AttendanceTrendAPIView(APIView):
    """
    API endpoint for attendance trends.

    GET /api/v1/attendance/intelligence/trends/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get attendance trends."""
        try:
            company_id = _get_company_id(request)
            if not company_id:
                return Response(
                    {"detail": "Company context not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            days = int(request.query_params.get("days", 30))

            if days < 1 or days > 365:
                return Response(
                    {"detail": "Days must be between 1 and 365."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            trends = AttendanceAnalyticsService.get_attendance_trends(
                company_id=company_id,
                days=days,
            )

            serializer = TrendDataPointSerializer(trends, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Trends API error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AttendancePeakHoursAPIView(APIView):
    """
    API endpoint for peak hours analytics.

    GET /api/v1/attendance/intelligence/peak-hours/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get peak hours punch distribution."""
        try:
            company_id = _get_company_id(request)
            if not company_id:
                return Response(
                    {"detail": "Company context not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            days = int(request.query_params.get("days", 7))

            if days < 1 or days > 90:
                return Response(
                    {"detail": "Days must be between 1 and 90."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            peak_hours = AttendanceAnalyticsService.get_peak_hours(
                company_id=company_id,
                days=days,
            )

            return Response(
                {
                    "analysis_period_days": days,
                    "peak_hours": peak_hours,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Peak hours API error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AttendanceDeviceDistributionAPIView(APIView):
    """
    API endpoint for device-wise punch distribution.

    GET /api/v1/attendance/intelligence/device-distribution/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get device-wise punch distribution."""
        try:
            company_id = _get_company_id(request)
            if not company_id:
                return Response(
                    {"detail": "Company context not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            days = int(request.query_params.get("days", 7))

            if days < 1 or days > 90:
                return Response(
                    {"detail": "Days must be between 1 and 90."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            distribution = AttendanceAnalyticsService.get_device_punch_distribution(
                company_id=company_id,
                days=days,
            )

            serializer = DeviceDistributionSerializer(distribution, many=True)
            return Response(
                {
                    "analysis_period_days": days,
                    "devices": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Device distribution API error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerificationStatsAPIView(APIView):
    """
    API endpoint for verification statistics.

    GET /api/v1/attendance/intelligence/verification-stats/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get verification statistics."""
        try:
            company_id = _get_company_id(request)
            if not company_id:
                return Response(
                    {"detail": "Company context not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            days = int(request.query_params.get("days", 30))

            if days < 1 or days > 365:
                return Response(
                    {"detail": "Days must be between 1 and 365."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            stats = AttendanceAnalyticsService.get_verification_statistics(
                company_id=company_id,
                days=days,
            )

            serializer = VerificationStatisticsSerializer(stats)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Verification stats API error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SpoofAlertAPIView(APIView):
    """
    API endpoint for spoof detection alerts.

    GET /api/v1/attendance/intelligence/spoof-alerts/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get spoof alerts."""
        try:
            company_id = _get_company_id(request)
            if not company_id:
                return Response(
                    {"detail": "Company context not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            days = int(request.query_params.get("days", 30))
            limit = int(request.query_params.get("limit", 50))

            if days < 1 or days > 365:
                return Response(
                    {"detail": "Days must be between 1 and 365."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            alerts = AttendanceAnalyticsService.get_spoof_alerts(
                company_id=company_id,
                days=days,
            )

            serializer = SpoofAlertSerializer(alerts[:limit], many=True)
            return Response(
                {
                    "analysis_period_days": days,
                    "total_alerts": len(alerts),
                    "alerts": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Spoof alerts API error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LocationHeatmapAPIView(APIView):
    """
    API endpoint for location-wise punch heatmap.

    GET /api/v1/attendance/intelligence/location-heatmap/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get location heatmap."""
        try:
            company_id = _get_company_id(request)
            if not company_id:
                return Response(
                    {"detail": "Company context not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            date_str = request.query_params.get("date")

            date = None
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str).date()
                except ValueError:
                    return Response(
                        {"detail": "Invalid date format. Use ISO format (YYYY-MM-DD)."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            heatmap = AttendanceAnalyticsService.get_location_heatmap(
                company_id=company_id,
                date=date,
            )

            serializer = LocationHeatmapSerializer(heatmap, many=True)
            return Response(
                {
                    "date": (date or timezone.now().date()).isoformat(),
                    "locations": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Location heatmap API error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class EmployeeSwipePatternAPIView(APIView):
    """
    API endpoint for employee swipe patterns.

    GET /api/v1/attendance/intelligence/employee-swipe-pattern/{employee_id}/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, employee_id=None):
        """Get employee swipe pattern."""
        try:
            if not employee_id:
                return Response(
                    {"detail": "Employee ID is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            days = int(request.query_params.get("days", 30))

            if days < 1 or days > 365:
                return Response(
                    {"detail": "Days must be between 1 and 365."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            pattern = AttendanceAnalyticsService.get_employee_swipe_pattern(
                employee_id=employee_id,
                days=days,
            )

            serializer = EmployeeSwipePatternSerializer(pattern)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Employee swipe pattern API error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class AnomalyDetectionAPIView(APIView):
    """
    API endpoint for anomaly detection.

    GET /api/v1/attendance/intelligence/anomalies/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get detected anomalies."""
        try:
            company_id = _get_company_id(request)
            if not company_id:
                return Response(
                    {"detail": "Company context not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            days = int(request.query_params.get("days", 7))
            anomaly_type = request.query_params.get("type")  # Optional filter

            if days < 1 or days > 90:
                return Response(
                    {"detail": "Days must be between 1 and 90."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            anomalies = AttendanceAnalyticsService.detect_anomalies(
                company_id=company_id,
                days=days,
            )

            # Filter by type if specified
            if anomaly_type:
                anomalies = [a for a in anomalies if a["type"] == anomaly_type]

            serializer = AnomalySerializer(anomalies, many=True)
            return Response(
                {
                    "analysis_period_days": days,
                    "total_anomalies": len(anomalies),
                    "anomalies": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Anomaly detection API error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MissingPunchesAPIView(APIView):
    """
    API endpoint for missing punches.

    GET /api/v1/attendance/intelligence/missing-punches/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get employees with missing punches."""
        try:
            company_id = _get_company_id(request)
            if not company_id:
                return Response(
                    {"detail": "Company context not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            date_str = request.query_params.get("date")

            date = None
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str).date()
                except ValueError:
                    return Response(
                        {"detail": "Invalid date format. Use ISO format (YYYY-MM-DD)."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            missing = AttendanceAnalyticsService.get_missing_punches(
                company_id=company_id,
                date=date,
            )

            serializer = MissingPunchSerializer(missing, many=True)
            return Response(
                {
                    "date": (date or timezone.now().date()).isoformat(),
                    "total_missing": len(missing),
                    "employees": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Missing punches API error: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
