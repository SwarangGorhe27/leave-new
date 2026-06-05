"""Admin registrations for Leave models."""

from django.contrib import admin

from .models import LeaveApproval, LeaveBalance, LeaveMapping, LeaveRequest, LeaveType


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "max_days_per_year", "carry_forward_enabled", "is_active")
    list_filter = ("is_active", "carry_forward_enabled", "encashable")
    search_fields = ("name", "code")


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "year", "allocated_days", "used_days", "pending_days")
    list_filter = ("year", "leave_type")
    search_fields = ("employee__employee_code", "employee__first_name", "employee__last_name", "leave_type__name")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "from_date", "to_date", "total_days", "status", "applied_at")
    list_filter = ("status", "leave_type", "from_date")
    search_fields = ("employee__employee_code", "employee__first_name", "employee__last_name", "reason")


@admin.register(LeaveApproval)
class LeaveApprovalAdmin(admin.ModelAdmin):
    list_display = ("leave_request", "approver", "status", "actioned_at")
    list_filter = ("status", "approval_level")
    search_fields = ("leave_request__id", "approver__employee_code", "remarks")


@admin.register(LeaveMapping)
class LeaveMappingAdmin(admin.ModelAdmin):
    list_display = ("role", "leave_type", "allowed_days")
    list_filter = ("role", "leave_type")
    search_fields = ("role", "leave_type__name", "leave_type__code")
