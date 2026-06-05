"""Regularization, overtime, and compensatory-off requests (v7 Section I)."""

from django.db import models

from apps.attendance.models.base import AttendanceTenantModel, MetaDataMixin
from apps.attendance.models.enums import (
    CompOffLifecycleStatus,
    RegularizationType,
    RequestWorkflowStatus,
    RequestedAttendanceStatus,
)


class RegularizationRequest(AttendanceTenantModel, MetaDataMixin):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="regularization_requests",
    )
    attendance = models.ForeignKey(
        "attendance.DailyAttendance",
        on_delete=models.CASCADE,
        db_column="attendance_id",
        related_name="regularization_requests",
    )
    regularization_date = models.DateField()
    reg_type = models.CharField(max_length=25, choices=RegularizationType.choices)
    mode = models.CharField(max_length=30, null=True, blank=True)
    requested_in = models.DateTimeField(null=True, blank=True)
    requested_out = models.DateTimeField(null=True, blank=True)
    requested_status = models.CharField(
        max_length=15,
        choices=RequestedAttendanceStatus.choices,
        null=True,
        blank=True,
    )
    permission_mins = models.IntegerField(null=True, blank=True)
    leave_request = models.ForeignKey(
        "leave.LeaveRequest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="leave_request_id",
        related_name="regularization_requests",
    )
    reason_option = models.ForeignKey(
        "attendance.RegularizationReason",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="reason_id",
        related_name="regularization_requests",
    )
    justification = models.TextField(null=True, blank=True, db_column="reason")
    applied_on_behalf = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=RequestWorkflowStatus.choices,
        default=RequestWorkflowStatus.DRAFT,
    )
    workflow_txn_id = models.UUIDField(null=True, blank=True)
    request_number = models.CharField(
        max_length=20, unique=True, null=True, blank=True, db_column="request_number"
    )

    class Meta:
        db_table = "emp_regularization_request"
        indexes = [
            models.Index(fields=["employee", "status"], name="idx_emp_regreq_emp_st"),
            models.Index(fields=["company", "status"], name="idx_emp_regreq_co_st"),
        ]


class OvertimeRequest(AttendanceTenantModel, MetaDataMixin):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="attendance_overtime_requests",
    )
    attendance = models.ForeignKey(
        "attendance.DailyAttendance",
        on_delete=models.CASCADE,
        db_column="attendance_id",
        related_name="overtime_requests",
    )
    ot_date = models.DateField()
    claimed_ot_mins = models.IntegerField()
    approved_ot_mins = models.IntegerField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=RequestWorkflowStatus.choices,
        default=RequestWorkflowStatus.DRAFT,
    )
    approved_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="approved_by",
        related_name="overtime_requests_approved",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    workflow_txn_id = models.UUIDField(null=True, blank=True)
    request_number = models.CharField(
        max_length=20, unique=True, null=True, blank=True, db_column="request_number"
    )
    class Meta:
        db_table = "emp_overtime_request"
        indexes = [
            models.Index(fields=["employee", "status"], name="idx_emp_otreq_emp_st"),
        ]


REQUEST_TYPE_CHOICES = [
    ('missing_punch', 'Missing Punch Request'),
    ('late_login', 'Late Login Justification'),
    ('wfh', 'Work From Home Attendance Adjustment'),
    ('half_day', 'Half-Day Attendance Correction'),
    ('regularization', 'Attendance Regularization'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('fully_approved', 'Fully Approved'),
    ('pending_admin_approval', 'Pending Admin Approval'),
]

class AttendanceRequest(models.Model):
    employee = models.ForeignKey("employees.Employee", on_delete=models.CASCADE)
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPE_CHOICES)
    date = models.DateField()
    shift_time = models.CharField(max_length=50, blank=True)
    punch_in = models.TimeField(null=True, blank=True)
    punch_out = models.TimeField(null=True, blank=True)
    working_hours = models.CharField(max_length=20, blank=True)
    reason = models.TextField()
    supporting_document = models.FileField(upload_to='attendance_docs/', null=True, blank=True)
    manager_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    final_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance_requests"


class ApprovalWorkflow(models.Model):
    request = models.ForeignKey(AttendanceRequest, related_name='approval_workflow', on_delete=models.CASCADE)
    approver = models.ForeignKey("employees.Employee", on_delete=models.SET_NULL, null=True)
    stage = models.CharField(max_length=20)  # 'manager' or 'admin'
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    comment = models.TextField(blank=True)
    actioned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "approval_workflows"
