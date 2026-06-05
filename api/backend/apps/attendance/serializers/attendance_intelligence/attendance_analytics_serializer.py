"""
Attendance Intelligence API Serializers.

Serializers for dashboard, trends, anomaly detection, and analytics APIs.
"""

from rest_framework import serializers


class DashboardKPISerializer(serializers.Serializer):
    """Dashboard KPI metrics serializer."""

    date = serializers.DateField(read_only=True)
    total_employees = serializers.IntegerField(read_only=True)
    present = serializers.IntegerField(read_only=True)
    absent = serializers.IntegerField(read_only=True)
    late = serializers.IntegerField(read_only=True)
    leave = serializers.IntegerField(read_only=True)
    work_from_home = serializers.IntegerField(read_only=True)
    present_percentage = serializers.FloatField(read_only=True)
    absent_percentage = serializers.FloatField(read_only=True)
    online_devices = serializers.IntegerField(read_only=True)
    total_devices = serializers.IntegerField(read_only=True)
    device_online_percentage = serializers.FloatField(read_only=True)


class TrendDataPointSerializer(serializers.Serializer):
    """Single day trend data point."""

    date = serializers.DateField(read_only=True)
    total_employees = serializers.IntegerField(read_only=True)
    present = serializers.IntegerField(read_only=True)
    absent = serializers.IntegerField(read_only=True)
    late = serializers.IntegerField(read_only=True)
    present_percentage = serializers.FloatField(read_only=True)


class PeakHourSerializer(serializers.Serializer):
    """Peak hours data serializer."""

    hour = serializers.CharField(read_only=True)
    punch_count = serializers.IntegerField(read_only=True)


class DeviceDistributionSerializer(serializers.Serializer):
    """Device-wise punch distribution serializer."""

    device_id = serializers.IntegerField(read_only=True)
    device_code = serializers.CharField(read_only=True)
    device_name = serializers.CharField(read_only=True)
    punch_count = serializers.IntegerField(read_only=True)


class VerificationStatisticsSerializer(serializers.Serializer):
    """Verification statistics serializer."""

    total_punches = serializers.IntegerField(read_only=True)
    verified_punches = serializers.IntegerField(read_only=True)
    failed_verifications = serializers.IntegerField(read_only=True)
    verification_success_rate = serializers.FloatField(read_only=True)


class SpoofAlertSerializer(serializers.Serializer):
    """Spoof alert/suspicious punch serializer."""

    punch_id = serializers.UUIDField(read_only=True)
    employee_id = serializers.UUIDField(read_only=True)
    employee_name = serializers.CharField(read_only=True)
    punch_time = serializers.DateTimeField(read_only=True)
    device_id = serializers.IntegerField(read_only=True)
    punch_mode = serializers.CharField(read_only=True)
    face_verified = serializers.BooleanField(read_only=True)
    severity = serializers.CharField(read_only=True)


class LocationHeatmapSerializer(serializers.Serializer):
    """Location-wise punch distribution serializer."""

    location_id = serializers.UUIDField(read_only=True)
    location_name = serializers.CharField(read_only=True)
    punch_count = serializers.IntegerField(read_only=True)
    unique_employees = serializers.IntegerField(read_only=True)


class EmployeeSwipePatternSerializer(serializers.Serializer):
    """Employee swipe pattern analysis serializer."""

    employee_id = serializers.UUIDField(read_only=True)
    analysis_period_days = serializers.IntegerField(read_only=True)
    total_punches = serializers.IntegerField(read_only=True)
    average_punch_hour = serializers.FloatField(read_only=True, allow_null=True)
    average_punch_gap_hours = serializers.FloatField(read_only=True, allow_null=True)
    most_used_device_id = serializers.IntegerField(read_only=True, allow_null=True)
    punch_regularity = serializers.CharField(read_only=True)


class AnomalySerializer(serializers.Serializer):
    """Anomaly detection result serializer."""

    type = serializers.CharField(read_only=True)
    employee_id = serializers.UUIDField(read_only=True)
    severity = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)


class MissingPunchSerializer(serializers.Serializer):
    """Missing punch record serializer."""

    employee_id = serializers.UUIDField(read_only=True)
    employee_name = serializers.CharField(read_only=True)
    employee_code = serializers.CharField(read_only=True)
    attendance_date = serializers.DateField(read_only=True)
    status = serializers.CharField(read_only=True)


class AttendanceDashboardResponseSerializer(serializers.Serializer):
    """Complete dashboard response serializer."""

    kpis = DashboardKPISerializer(read_only=True)
    trends_7_days = TrendDataPointSerializer(many=True, read_only=True)
