"""
attendance/serializers/matrix.py

Serializers for the Attendance Matrix sub-module.

Design rules
------------
- Serializers are READ-ONLY (all matrix endpoints are GET except export/import).
- No ORM queries inside serializers — services pass pre-built dicts.
- cell_code is NOT a model field; it is computed in the service and passed as
  a plain dict key — serializers simply expose it.
- For export/import (write endpoints), only the request body is validated here;
  response serializers are thin.
"""

from __future__ import annotations

from rest_framework import serializers

from apps.attendance.constants.export_constants import ExportFormatChoices
from apps.attendance.models.masters.scheme_status import AttendanceStatus


# ---------------------------------------------------------------------------
# Date Header (grid column headers)
# ---------------------------------------------------------------------------

class DateHeaderSerializer(serializers.Serializer):
    date       = serializers.DateField()
    day_label  = serializers.CharField(max_length=3)
    is_weekend = serializers.BooleanField()
    is_holiday = serializers.BooleanField()


# ---------------------------------------------------------------------------
# Day Cell (each cell in the grid per employee per date)
# ---------------------------------------------------------------------------

class DayCellSerializer(serializers.Serializer):
    date             = serializers.DateField()
    cell_code        = serializers.CharField(allow_null=True)
    status_code      = serializers.CharField(allow_null=True)
    work_mode        = serializers.CharField(allow_null=True)
    leave_type       = serializers.CharField(allow_null=True)
    is_late          = serializers.BooleanField()
    actual_work_mins = serializers.IntegerField()
    is_locked        = serializers.BooleanField()


# ---------------------------------------------------------------------------
# Row Summary (P / A / L columns on the right of the grid)
# ---------------------------------------------------------------------------

class RowSummarySerializer(serializers.Serializer):
    present = serializers.FloatField()
    absent  = serializers.FloatField()
    leave   = serializers.FloatField()


class AttendanceStatusUpdateSerializer(serializers.Serializer):
    status_code = serializers.CharField(max_length=20, trim_whitespace=True)

    def validate_status_code(self, value: str) -> str:
        code = value.strip().upper()
        if not code:
            raise serializers.ValidationError("status_code is required.")
        if not AttendanceStatus.objects.filter(code=code, is_active=True).exists():
            raise serializers.ValidationError(f"Unknown attendance status code: {value}")
        return code


# ---------------------------------------------------------------------------
# Employee Row (one row in the grid)
# ---------------------------------------------------------------------------

class EmployeeRowSerializer(serializers.Serializer):
    employee_id    = serializers.UUIDField()
    employee_code  = serializers.CharField()
    full_name      = serializers.CharField()
    department     = serializers.CharField(allow_null=True)
    designation    = serializers.CharField(allow_null=True)
    avatar_initials = serializers.CharField()
    days           = DayCellSerializer(many=True)
    summary        = RowSummarySerializer()


# ---------------------------------------------------------------------------
# Grid Meta (cycle bounds + date headers + pagination)
# ---------------------------------------------------------------------------

class GridMetaSerializer(serializers.Serializer):
    total_records  = serializers.IntegerField()
    page           = serializers.IntegerField()
    page_size      = serializers.IntegerField()
    cycle_start    = serializers.DateField()
    cycle_end      = serializers.DateField()
    display_label  = serializers.CharField()
    dates          = DateHeaderSerializer(many=True)


# ---------------------------------------------------------------------------
# Full Grid Response
# ---------------------------------------------------------------------------

class MatrixGridSerializer(serializers.Serializer):
    meta = GridMetaSerializer()
    rows = EmployeeRowSerializer(many=True)


# ---------------------------------------------------------------------------
# Summary Cards
# ---------------------------------------------------------------------------

class MatrixSummarySerializer(serializers.Serializer):
    total_present        = serializers.IntegerField()
    present_change_today = serializers.IntegerField()
    total_absent         = serializers.IntegerField()
    absent_change_today  = serializers.IntegerField()
    on_leave             = serializers.IntegerField()
    leave_pending_count  = serializers.IntegerField()
    holidays_remaining   = serializers.IntegerField()
    next_holiday_date    = serializers.DateField(allow_null=True)
    next_holiday_name    = serializers.CharField(allow_null=True)
    avg_hours            = serializers.FloatField()
    avg_hours_goal       = serializers.FloatField()
    punctuality_percent  = serializers.FloatField()
    punctuality_change   = serializers.FloatField()


# ---------------------------------------------------------------------------
# Live Monitor
# ---------------------------------------------------------------------------

class MatrixLiveSerializer(serializers.Serializer):
    as_of          = serializers.CharField()   # ISO timestamp string
    present_count  = serializers.IntegerField()
    absent_count   = serializers.IntegerField()
    on_leave_count = serializers.IntegerField()
    present_delta  = serializers.IntegerField()
    absent_delta   = serializers.IntegerField()


# ---------------------------------------------------------------------------
# Department Filter
# ---------------------------------------------------------------------------

class DepartmentSerializer(serializers.Serializer):
    id             = serializers.UUIDField()
    name           = serializers.CharField()
    employee_count = serializers.IntegerField()


# ---------------------------------------------------------------------------
# Cycle Bounds
# ---------------------------------------------------------------------------

class CycleBoundsSerializer(serializers.Serializer):
    cycle_start   = serializers.DateField()
    cycle_end     = serializers.DateField()
    display_label = serializers.CharField()


# ---------------------------------------------------------------------------
# Punch Detail (inside employee day detail)
# ---------------------------------------------------------------------------

class PunchDetailSerializer(serializers.Serializer):
    punch_time    = serializers.CharField()   # ISO datetime string
    punch_type    = serializers.CharField()
    punch_source  = serializers.CharField()
    device_name   = serializers.CharField(allow_null=True)
    face_verified = serializers.BooleanField(allow_null=True)


# ---------------------------------------------------------------------------
# Leave Detail (inside employee day detail)
# ---------------------------------------------------------------------------

class LeaveSummarySerializer(serializers.Serializer):
    leave_type_code = serializers.CharField(allow_null=True)
    leave_type_name = serializers.CharField(allow_null=True)
    status          = serializers.CharField(allow_null=True)


# ---------------------------------------------------------------------------
# Regularization Detail (inside employee day detail)
# ---------------------------------------------------------------------------

class RegularizationSummarySerializer(serializers.Serializer):
    id       = serializers.UUIDField()
    status   = serializers.CharField()
    reg_type = serializers.CharField()


# ---------------------------------------------------------------------------
# Employee Day Detail
# ---------------------------------------------------------------------------

class EmployeeDayDetailSerializer(serializers.Serializer):
    employee_id          = serializers.UUIDField()
    date                 = serializers.DateField()
    status_code          = serializers.CharField()
    cell_code            = serializers.CharField()
    work_mode            = serializers.CharField(allow_null=True)
    shift_name           = serializers.CharField(allow_null=True)
    shift_start          = serializers.CharField(allow_null=True)   # "HH:MM"
    shift_end            = serializers.CharField(allow_null=True)   # "HH:MM"
    first_in             = serializers.CharField(allow_null=True)   # ISO datetime
    last_out             = serializers.CharField(allow_null=True)   # ISO datetime
    actual_work_mins     = serializers.IntegerField()
    late_in_mins         = serializers.IntegerField()
    early_exit_mins      = serializers.IntegerField()
    ot_mins              = serializers.IntegerField()
    lop_days             = serializers.FloatField()
    is_late              = serializers.BooleanField()
    is_grace             = serializers.BooleanField()
    grace_category       = serializers.CharField(allow_null=True)
    is_locked            = serializers.BooleanField()
    finalization_status  = serializers.CharField()
    punches              = PunchDetailSerializer(many=True)
    leave                = LeaveSummarySerializer(allow_null=True)
    regularization       = RegularizationSummarySerializer(allow_null=True)


# ---------------------------------------------------------------------------
# Employee Monthly Summary
# ---------------------------------------------------------------------------

class EmployeeMonthlySummarySerializer(serializers.Serializer):
    employee_id          = serializers.UUIDField()
    year                 = serializers.IntegerField()
    month                = serializers.IntegerField()
    present_days         = serializers.FloatField()
    absent_days          = serializers.FloatField()
    half_days            = serializers.FloatField()
    late_days            = serializers.IntegerField()
    leave_days           = serializers.FloatField()
    lwp_days             = serializers.FloatField()
    paid_days            = serializers.FloatField()
    total_work_mins      = serializers.IntegerField()
    ot_mins              = serializers.IntegerField()
    late_login_count     = serializers.IntegerField()
    early_exit_count     = serializers.IntegerField()
    grace_instances_used = serializers.IntegerField()
    is_locked            = serializers.BooleanField()


# ---------------------------------------------------------------------------
# Export — Request validation
# ---------------------------------------------------------------------------

class ExportRequestSerializer(serializers.Serializer):
    company_id    = serializers.UUIDField()
    year          = serializers.IntegerField(min_value=2000, max_value=2100)
    month         = serializers.IntegerField(min_value=1, max_value=12)
    # Use centralized format choices (filtered to exclude PDF for matrix exports)
    format        = serializers.ChoiceField(
        choices=[
            (ExportFormatChoices.CSV, ExportFormatChoices.CSV),
            (ExportFormatChoices.XLSX, ExportFormatChoices.XLSX),
        ]
    )
    department_id = serializers.UUIDField(required=False, allow_null=True)
    branch_id     = serializers.UUIDField(required=False, allow_null=True)


# ---------------------------------------------------------------------------
# Export — Job status response
# ---------------------------------------------------------------------------

class ExportJobStatusSerializer(serializers.Serializer):
    job_id       = serializers.UUIDField()
    status       = serializers.CharField()
    download_url = serializers.URLField(required=False, allow_null=True)
    expires_at   = serializers.CharField(required=False, allow_null=True)
    error        = serializers.CharField(required=False, allow_null=True)


# ---------------------------------------------------------------------------
# Import — Request validation (multipart)
# ---------------------------------------------------------------------------

class ImportRequestSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    year       = serializers.IntegerField(min_value=2000, max_value=2100)
    month      = serializers.IntegerField(min_value=1, max_value=12)
    file       = serializers.FileField()

    def validate_file(self, value):
        """
        Accept only .xlsx, .xls, .csv files under 10 MB.
        """
        max_size_bytes = 10 * 1024 * 1024  # 10 MB

        if value.size > max_size_bytes:
            raise serializers.ValidationError(
                "File too large. Maximum allowed size is 10 MB."
            )

        name = value.name.lower()
        allowed = (".xlsx", ".xls", ".csv")
        if not any(name.endswith(ext) for ext in allowed):
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed: {', '.join(allowed)}"
            )

        return value


# ---------------------------------------------------------------------------
# Import — Response
# ---------------------------------------------------------------------------

class ImportJobResponseSerializer(serializers.Serializer):
    job_id            = serializers.UUIDField()
    status            = serializers.CharField()
    rows_received     = serializers.IntegerField()
    validation_errors = serializers.ListField(child=serializers.DictField())
    message           = serializers.CharField()
