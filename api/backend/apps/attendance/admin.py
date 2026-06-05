"""Admin registrations for Attendance models. Register tenant-safe models and admin actions here."""

from django.contrib import admin

from apps.attendance.models.swipe_log_export_job import SwipeLogExportJob
from apps.attendance.models.masters.policy_masters import *
from apps.attendance.models.workflow import *
from apps.attendance.models.requests import *
from apps.attendance.models.punch_and_daily import *
from apps.attendance.models.device import AttendanceDevice
from apps.attendance.models.masters.company_config import AttendanceCompanyConfig
from apps.attendance.models.masters.policy_masters import AttendancePolicy
from apps.attendance.models.configuration import EmployeeAttendanceConfig, EmployeeShiftRoster,EmployeeWeekendOverride
from apps.attendance.models.weekly_off import WeeklyOff
from django.contrib import admin
from django import forms
from django.utils import timezone
from zoneinfo import ZoneInfo

from apps.attendance.models.punch_and_daily import PunchLog


IST = ZoneInfo("Asia/Kolkata")

@admin.register(SwipeLogExportJob)
class SwipeLogExportJobAdmin(admin.ModelAdmin):
    """Admin for SwipeLogExportJob model."""

    list_display = [
        "id",
        "company",
        "export_format",
        "status",
        "total_records",
        "processed_records",
        "created_at",
        "completed_at",
    ]

    list_filter = [
        "status",
        "export_format",
        "created_at",
        "company",
    ]

    search_fields = [
        "id",
        "company__name",
        "requested_by__employee_code",
        "requested_by__full_name",
    ]

    readonly_fields = [
        "id",
        "created_at",
        "started_at",
        "completed_at",
        "file_size",
    ]

    fieldsets = (
        ("Job Info", {
            "fields": ("id", "company", "requested_by", "export_format", "status"),
        }),
        ("Filters", {
            "fields": (
                "employee_ids",
                "department_ids",
                "punch_types",
                "punch_sources",
                "from_date",
                "to_date",
            ),
        }),
        ("Options", {
            "fields": (
                "include_employee_details",
                "include_device_details",
                "include_verification_details",
                "include_geofence_details",
            ),
        }),
        ("Progress", {
            "fields": (
                "total_records",
                "processed_records",
            ),
        }),
        ("Result", {
            "fields": (
                "file_path",
                "file_url",
                "file_size",
            ),
        }),
        ("Error Handling", {
            "fields": (
                "error_message",
                "error_details",
            ),
            "classes": ("collapse",),
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "started_at",
                "completed_at",
            ),
            "classes": ("collapse",),
        }),
        ("Task Tracking", {
            "fields": ("celery_task_id",),
            "classes": ("collapse",),
        }),
    )

    ordering = ["-created_at"]



admin.site.register(RegularizationReason)
admin.site.register(RegularizationRequest)
admin.site.register(ApprovalRequestAction)
admin.site.register(ApprovalWorkflowStep)
admin.site.register(ApprovalWorkflow)
admin.site.register(AttendanceDevice)
admin.site.register(AttendanceCompanyConfig)
admin.site.register(AttendancePolicy)
admin.site.register(EmployeeAttendanceConfig)
admin.site.register(EmployeeWeekendOverride)
admin.site.register(WeeklyOff)






@admin.register(EmployeeShiftRoster)
class EmployeeShiftRosterAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "roster_date",
        "shift",
        "cycle",
        "is_week_off",
    )

    list_filter = (
        "employee",
        "roster_date",
        "shift",
        "is_week_off",
    )

    search_fields = (
        "employee__employee_code",
        "employee__full_name",
    )

    date_hierarchy = "roster_date"




class PunchLogAdminForm(forms.ModelForm):
    class Meta:
        model = PunchLog
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Display existing UTC values in IST
        if self.instance and self.instance.pk and self.instance.punch_time:
            self.initial["punch_time"] = timezone.localtime(
                self.instance.punch_time,
                IST,
            )

    def clean_punch_time(self):
        """
        User enters IST time in admin.
        Convert to UTC before saving so existing backend
        functionality remains unchanged.
        """
        punch_time = self.cleaned_data["punch_time"]

        if timezone.is_naive(punch_time):
            punch_time = timezone.make_aware(
                punch_time,
                timezone=IST,
            )

        return punch_time.astimezone(ZoneInfo("UTC"))


@admin.register(PunchLog)
class PunchLogAdmin(admin.ModelAdmin):
    form = PunchLogAdminForm

    list_display = (
        "employee",
        "punch_time",
        "punch_type",
        "punch_source",
    )

    list_filter = (
        "employee",
        "punch_type",
        "punch_source",
        "punch_time",
    )

    search_fields = (
        "employee__employee_code",
        "employee__full_name",
    )

    date_hierarchy = "punch_time"


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "attendance_date",
        "status",
        "shift",
        "actual_work_mins",
    )

    list_filter = (
        "employee",
        "attendance_date",
        "status",
        "shift",
        "finalization_status",
    )

    search_fields = (
        "employee__employee_code",
        "employee__full_name",
    )

    date_hierarchy = "attendance_date"