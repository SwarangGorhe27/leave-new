"""TextChoices and small enums shared by the Attendance module (schema v7)."""

from django.db import models


class ShiftFamily(models.TextChoices):
    FIXED = "FIXED", "Fixed"
    FLEXIBLE = "FLEXIBLE", "Flexible"
    SPLIT = "SPLIT", "Split"
    NIGHT = "NIGHT", "Night"
    ROTATIONAL = "ROTATIONAL", "Rotational"


class PunchType(models.TextChoices):
    IN = "IN", "In"
    OUT = "OUT", "Out"
    UNKNOWN = "UNKNOWN", "Unknown"


class PunchSource(models.TextChoices):
    BIOMETRIC = "BIOMETRIC", "Biometric"
    MANUAL = "MANUAL", "Manual"
    WEB = "WEB", "Web Portal"
    MOBILE = "MOBILE", "Mobile App"


class FinalizationStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    FINALIZED = "FINALIZED", "Finalized"
    LOCKED = "LOCKED", "Locked"


class WorkMode(models.TextChoices):
    OFFICE = "OFFICE", "Office"
    REMOTE = "REMOTE", "Remote"
    HYBRID = "HYBRID", "Hybrid"
    CLIENT_SITE = "CLIENT_SITE", "Client Site"


class GraceCategory(models.TextChoices):
    LATE = "LATE", "Late"
    EARLY = "EARLY", "Early"
    SHORT_LEAVE = "SHORT_LEAVE", "Short Leave"


class RegularizationType(models.TextChoices):
    MISSING_PUNCH = "MISSING_PUNCH", "Missing Punch"
    SHORT_LEAVE = "SHORT_LEAVE", "Short Leave"
    PERMISSION = "PERMISSION", "Permission"
    WORK_FROM_HOME = "WORK_FROM_HOME", "Work From Home"


class RequestedAttendanceStatus(models.TextChoices):
    PRESENT = "PRESENT", "Present"
    HALF_DAY = "HALF_DAY", "Half Day"
    LEAVE = "LEAVE", "Leave"


class RequestWorkflowStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class CompOffLifecycleStatus(models.TextChoices):
    EARNED = "EARNED", "Earned"
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    CONSUMED = "CONSUMED", "Consumed"
    EXPIRED = "EXPIRED", "Expired"


class WorkflowTemplateType(models.TextChoices):
    LEAVE = "LEAVE", "Leave"
    OT = "OT", "Overtime"
    COMP_OFF = "COMP_OFF", "Compensatory Off"
    REGULARIZATION = "REGULARIZATION", "Regularization"


class ApproverRoleKind(models.TextChoices):
    REPORTING_MANAGER = "REPORTING_MANAGER", "Reporting Manager"
    DEPT_HEAD = "DEPT_HEAD", "Department Head"
    HR = "HR", "HR"
    CUSTOM = "CUSTOM", "Custom"


class ApprovalActionStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    SKIPPED = "SKIPPED", "Skipped"


class ExceptionSeverity(models.TextChoices):
    INFO = "INFO", "Info"
    WARNING = "WARNING", "Warning"
    CRITICAL = "CRITICAL", "Critical"


class LockCategory(models.TextChoices):
    ALL_ACTIVITIES = "ALL_ACTIVITIES", "All Activities"
    PUNCH = "PUNCH", "Punch"
    EDIT = "EDIT", "Edit"


class AuditActionType(models.TextChoices):
    INSERT = "INSERT", "Insert"
    UPDATE = "UPDATE", "Update"
    DELETE = "DELETE", "Delete"
    OVERRIDE = "OVERRIDE", "Override"


class AuditActionSource(models.TextChoices):
    HR_ADMIN = "HR_ADMIN", "HR Admin"
    SYSTEM = "SYSTEM", "System"
    API = "API", "API"
    JOB = "JOB", "Job"


class AttendanceJobType(models.TextChoices):
    DAILY_COMPUTE = "DAILY_COMPUTE", "Daily Compute"
    MONTHLY_CLOSE = "MONTHLY_CLOSE", "Monthly Close"
    LATE_CYCLE_RESET = "LATE_CYCLE_RESET", "Late Cycle Reset"
    LOCK_ATTENDANCE = "LOCK_ATTENDANCE", "Lock Attendance"
    ROSTER_GENERATE = "ROSTER_GENERATE", "Roster Generate"


class AttendanceJobStatus(models.TextChoices):
    QUEUED = "QUEUED", "Queued"
    RUNNING = "RUNNING", "Running"
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS", "Partial Success"


class NotificationKind(models.TextChoices):
    EXCEPTION_RAISED = "EXCEPTION_RAISED", "Exception Raised"
    REGULARIZATION_PENDING = "REGULARIZATION_PENDING", "Regularization Pending"
    OT_PENDING = "OT_PENDING", "Overtime Pending"
    COMP_OFF_EXPIRING = "COMP_OFF_EXPIRING", "Comp Off Expiring"
    LEAVE_PENDING = "LEAVE_PENDING", "Leave Pending"
    ATTENDANCE_LOCKED = "ATTENDANCE_LOCKED", "Attendance Locked"
    MISSING_PUNCH = "MISSING_PUNCH", "Missing Punch"
    LATE_ENTRY = "LATE_ENTRY", "Late Entry"
    SHIFT_SWAP = "SHIFT_SWAP", "Shift Swap"
    ROSTER_PUBLISH = "ROSTER_PUBLISH", "Roster Publish"
    APPROVAL_PENDING = "APPROVAL_PENDING", "Approval Pending"
    DUPLICATE_PUNCH = "DUPLICATE_PUNCH", "Duplicate Punch"
    SPOOF_ALERT = "SPOOF_ALERT", "Spoof Alert"
    SYSTEM_ALERT = "SYSTEM_ALERT", "System Alert"


class WeekendOverrideType(models.TextChoices):
    WORKING = "WORKING", "Working"
    OFF = "OFF", "Off"


class DeviceSourceType(models.TextChoices):
    BIOMAX = "BIOMAX", "BioMax-X300"
    MOBILE_APP = "MOBILE_APP", "Mobile App"
    WEB_LOGIN = "WEB_LOGIN", "Web Login"
    QR_ATTENDANCE = "QR_ATTENDANCE", "QR Attendance"
    RFID_BIO_CARD = "RFID_BIO_CARD", "RFID/BIO Card"


class DeviceStatus(models.TextChoices):
    ONLINE = "ONLINE", "Online"
    OFFLINE = "OFFLINE", "Offline"
    MAINTENANCE = "MAINTENANCE", "Maintenance"


class DeviceSyncStatus(models.TextChoices):
    SYNCED = "SYNCED", "Synced"
    SYNCING = "SYNCING", "Syncing"
    FAILED = "FAILED", "Failed"
    NEVER_SYNCED = "NEVER_SYNCED", "Never Synced"

