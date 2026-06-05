"""
RBAC Seed Data Script
=====================
Seeds the following tables:
- mst_permission (Permissions)
- mst_system_role (Roles)
- sec_permission_group (Permission Groups)
- sec_group_permission (Permission → Group mappings)
- sec_role_permission_group (Role → Group mappings)
- employee_role_assignments (Employee → Role assignments)

Usage:
    python manage.py shell < rbac_seed.py
    OR
    from rbac_seed import seed_rbac_data
    seed_rbac_data()
"""
import sys
import os
import django

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


from django.db import transaction
from django.utils import timezone
from datetime import date, timedelta
import uuid
from django_tenants.utils import schema_context

# Import your models
from .models.permission import (
    Permission,
    PermissionGroup,
    GroupPermission,
    # Role,
    RolePermissionGroup,
    # EmployeeRoleAssignment,
)
from .models.role import Role, EmployeeRoleAssignment
from apps.employees.models import Employee


# =========================================================================
# PERMISSION DATA (from your SQL file)
# =========================================================================

PERMISSIONS_DATA = [
    # EMPLOYEE MODULE
    {"module": "EMPLOYEE", "action": "view", "resource": "employee_profile", "permission_code": "employee.view_all_employee", "description": "View employee profiles"},
    {"module": "EMPLOYEE", "action": "view_own", "resource": "employee_profile", "permission_code": "employee.view_own_profile", "description": "View own employee profile"},
    {"module": "EMPLOYEE", "action": "create", "resource": "employee_profile", "permission_code": "employee.create_employee", "description": "Create employee"},
    {"module": "EMPLOYEE", "action": "edit", "resource": "employee_profile", "permission_code": "employee.edit_employee", "description": "Edit employee"},
    {"module": "EMPLOYEE", "action": "edit_own", "resource": "employee_profile", "permission_code": "employee.edit_own_profile", "description": "Edit own profile"},
    {"module": "EMPLOYEE", "action": "delete", "resource": "employee_profile", "permission_code": "employee.delete_employee", "description": "Delete employee"},
    {"module": "EMPLOYEE", "action": "activate", "resource": "employee_profile", "permission_code": "employee.activate_employee", "description": "Activate employee"},
    {"module": "EMPLOYEE", "action": "deactivate", "resource": "employee_profile", "permission_code": "employee.deactivate_employee", "description": "Deactivate employee"},
    {"module": "EMPLOYEE", "action": "terminate", "resource": "employee_profile", "permission_code": "employee.terminate_employee", "description": "Terminate employee"},
    {"module": "EMPLOYEE", "action": "transfer", "resource": "employee_profile", "permission_code": "employee.transfer_employee", "description": "Transfer employee"},
    {"module": "EMPLOYEE", "action": "promote", "resource": "employee_profile", "permission_code": "employee.promote_employee", "description": "Promote employee"},
    {"module": "EMPLOYEE", "action": "demote", "resource": "employee_profile", "permission_code": "employee.demote_employee", "description": "Demote employee"},
    {"module": "EMPLOYEE", "action": "change_reporting_manager", "resource": "employee_profile", "permission_code": "employee.change_reporting_manager", "description": "Change reporting manager"},
    {"module": "EMPLOYEE", "action": "assign_role", "resource": "employee_profile", "permission_code": "employee.assign_role", "description": "Assign RBAC role to employee"},
    {"module": "EMPLOYEE", "action": "remove_role", "resource": "employee_profile", "permission_code": "employee.remove_role", "description": "Remove RBAC role from employee"},
    {"module": "EMPLOYEE", "action": "view_salary", "resource": "employee_salary", "permission_code": "employee.view_salary", "description": "View salary information"},
    {"module": "EMPLOYEE", "action": "edit_salary", "resource": "employee_salary", "permission_code": "employee.edit_salary", "description": "Edit salary information"},
    {"module": "EMPLOYEE", "action": "view_documents", "resource": "employee_documents", "permission_code": "employee.view_documents", "description": "View employee documents"},
    {"module": "EMPLOYEE", "action": "manage_documents", "resource": "employee_documents", "permission_code": "employee.manage_documents", "description": "Manage employee documents"},
    {"module": "EMPLOYEE", "action": "upload_documents", "resource": "employee_documents", "permission_code": "employee.upload_documents", "description": "Upload employee documents"},
    {"module": "EMPLOYEE", "action": "delete_documents", "resource": "employee_documents", "permission_code": "employee.delete_documents", "description": "Delete employee documents"},
    {"module": "EMPLOYEE", "action": "export", "resource": "employee_profile", "permission_code": "employee.export_employee", "description": "Export employee data"},
    {"module": "EMPLOYEE", "action": "import", "resource": "employee_profile", "permission_code": "employee.import_employee", "description": "Import employee data"},
    {"module": "EMPLOYEE", "action": "view_org_chart", "resource": "organization", "permission_code": "employee.view_org_chart", "description": "View organization chart"},
    {"module": "EMPLOYEE", "action": "view_team", "resource": "employee_profile", "permission_code": "employee.view_team", "description": "View team members"},
    {"module": "EMPLOYEE", "action": "view_audit_logs", "resource": "employee_audit", "permission_code": "employee.view_audit_logs", "description": "View employee audit logs"},
    
    # ATTENDANCE MODULE
    {"module": "ATTENDANCE", "action": "view", "resource": "attendance", "permission_code": "attendance.view_attendance", "description": "View attendance"},
    {"module": "ATTENDANCE", "action": "view_own", "resource": "attendance", "permission_code": "attendance.view_own_attendance", "description": "View own attendance"},
    {"module": "ATTENDANCE", "action": "create", "resource": "attendance", "permission_code": "attendance.create_attendance", "description": "Create attendance record"},
    {"module": "ATTENDANCE", "action": "edit", "resource": "attendance", "permission_code": "attendance.edit_attendance", "description": "Edit attendance"},
    {"module": "ATTENDANCE", "action": "delete", "resource": "attendance", "permission_code": "attendance.delete_attendance", "description": "Delete attendance"},
    {"module": "ATTENDANCE", "action": "regularize", "resource": "attendance_regularization", "permission_code": "attendance.regularize_attendance", "description": "Regularize attendance"},
    {"module": "ATTENDANCE", "action": "approve_regularization", "resource": "attendance_regularization", "permission_code": "attendance.approve_regularization", "description": "Approve attendance regularization"},
    {"module": "ATTENDANCE", "action": "reject_regularization", "resource": "attendance_regularization", "permission_code": "attendance.reject_regularization", "description": "Reject attendance regularization"},
    {"module": "ATTENDANCE", "action": "mark_manual", "resource": "attendance", "permission_code": "attendance.mark_manual_attendance", "description": "Mark manual attendance"},
    {"module": "ATTENDANCE", "action": "override", "resource": "attendance", "permission_code": "attendance.override_attendance", "description": "Override attendance records"},
    {"module": "ATTENDANCE", "action": "approve_ot", "resource": "overtime", "permission_code": "attendance.approve_overtime", "description": "Approve overtime"},
    {"module": "ATTENDANCE", "action": "reject_ot", "resource": "overtime", "permission_code": "attendance.reject_overtime", "description": "Reject overtime"},
    {"module": "ATTENDANCE", "action": "apply_ot", "resource": "overtime", "permission_code": "attendance.apply_overtime", "description": "Apply overtime"},
    {"module": "ATTENDANCE", "action": "view_shift", "resource": "shift", "permission_code": "attendance.view_shift", "description": "View shifts"},
    {"module": "ATTENDANCE", "action": "assign_shift", "resource": "shift", "permission_code": "attendance.assign_shift", "description": "Assign shifts"},
    {"module": "ATTENDANCE", "action": "edit_shift", "resource": "shift", "permission_code": "attendance.edit_shift", "description": "Edit shifts"},
    {"module": "ATTENDANCE", "action": "delete_shift", "resource": "shift", "permission_code": "attendance.delete_shift", "description": "Delete shifts"},
    {"module": "ATTENDANCE", "action": "view_roster", "resource": "roster", "permission_code": "attendance.view_roster", "description": "View roster"},
    {"module": "ATTENDANCE", "action": "manage_roster", "resource": "roster", "permission_code": "attendance.manage_roster", "description": "Manage roster"},
    {"module": "ATTENDANCE", "action": "sync_biometric", "resource": "biometric", "permission_code": "attendance.sync_biometric", "description": "Sync biometric data"},
    {"module": "ATTENDANCE", "action": "manage_biometric", "resource": "biometric", "permission_code": "attendance.manage_biometric", "description": "Manage biometric devices"},
    {"module": "ATTENDANCE", "action": "view_logs", "resource": "attendance_logs", "permission_code": "attendance.view_logs", "description": "View attendance logs"},
    {"module": "ATTENDANCE", "action": "export", "resource": "attendance", "permission_code": "attendance.export_attendance", "description": "Export attendance data"},
    {"module": "ATTENDANCE", "action": "import", "resource": "attendance", "permission_code": "attendance.import_attendance", "description": "Import attendance data"},
    {"module": "ATTENDANCE", "action": "view_team", "resource": "attendance", "permission_code": "attendance.view_team_attendance", "description": "View team attendance"},
    
    # LEAVE MODULE
    {"module": "LEAVE", "action": "view", "resource": "leave", "permission_code": "leave.view_leave", "description": "View leave records"},
    {"module": "LEAVE", "action": "view_own", "resource": "leave", "permission_code": "leave.view_own_leave", "description": "View own leave records"},
    {"module": "LEAVE", "action": "view_team", "resource": "leave", "permission_code": "leave.view_team_leave", "description": "View team leave records"},
    {"module": "LEAVE", "action": "view_team_balance", "resource": "leave_balance", "permission_code": "leave.view_team_leave_balance", "description": "View team leave balances"},
    {"module": "LEAVE", "action": "apply", "resource": "leave_application", "permission_code": "leave.apply_leave", "description": "Apply leave"},
    {"module": "LEAVE", "action": "edit_own", "resource": "leave_application", "permission_code": "leave.edit_own_leave", "description": "Edit own leave application"},
    {"module": "LEAVE", "action": "cancel_own", "resource": "leave_application", "permission_code": "leave.cancel_own_leave", "description": "Cancel own leave application"},
    {"module": "LEAVE", "action": "approve", "resource": "leave_application", "permission_code": "leave.approve_leave", "description": "Approve leave application"},
    {"module": "LEAVE", "action": "reject", "resource": "leave_application", "permission_code": "leave.reject_leave", "description": "Reject leave application"},
    {"module": "LEAVE", "action": "withdraw", "resource": "leave_application", "permission_code": "leave.withdraw_leave", "description": "Withdraw leave application"},
    {"module": "LEAVE", "action": "override", "resource": "leave_application", "permission_code": "leave.override_leave", "description": "Override leave records"},
    {"module": "LEAVE", "action": "adjust_balance", "resource": "leave_balance", "permission_code": "leave.adjust_leave_balance", "description": "Adjust leave balance"},
    {"module": "LEAVE", "action": "adjust_balance", "resource": "leave_balance", "permission_code": "leave.adjust_leave_balance", "description": "Adjust leave balance"},
    {
    "module": "LEAVE",
    "action": "view_balance",
    "resource": "leave_balance",
    "permission_code": "leave.view_leave_balance",
    "description": "View leave balances"
    },
    {
    "module": "LEAVE",
    "action": "view_own_balance",
    "resource": "leave_balance",
    "permission_code": "leave.view_own_leave_balance",
    "description": "View own leave balance"
    },
    {
    "module": "LEAVE",
    "action": "delegate_authority",
    "resource": "leave_approvals",
    "permission_code": "leave.delegate_authority",
    "description": "Delegate leave authority"
    },
    {
    "module": "LEAVE",
    "action": "view_team_balance",
    "resource": "leave_balance",
    "permission_code": "leave.view_team_leave_balance",
    "description": "View team leave balances"
    },
    {"module": "LEAVE", "action": "manage_balance", "resource": "leave_balance", "permission_code": "leave.manage_leave_balance", "description": "Manage leave balances"},
    {"module": "LEAVE", "action": "view_projection", "resource": "leave_balance_projection", "permission_code": "leave.view_leave_balance_projection", "description": "View leave balance projections"},  
    {"module": "LEAVE", "action": "approve_encashment", "resource": "leave_encashment", "permission_code": "leave.approve_leave_encashment", "description": "Approve leave encashment"},
    {"module": "LEAVE", "action": "reject_encashment", "resource": "leave_encashment", "permission_code": "leave.reject_leave_encashment", "description": "Reject leave encashment"},
    {"module": "LEAVE", "action": "manage_policy", "resource": "leave_policy", "permission_code": "leave.manage_leave_policy", "description": "Manage leave policies"},
    {"module": "LEAVE", "action": "manage_holiday", "resource": "holiday_calendar", "permission_code": "leave.manage_holiday_calendar", "description": "Manage holiday calendar"},
    {"module": "LEAVE", "action": "assign_policy", "resource": "leave_policy", "permission_code": "leave.assign_leave_policy", "description": "Assign leave policies"},
    {"module": "LEAVE", "action": "run_accrual", "resource": "leave_accrual", "permission_code": "leave.run_leave_accrual", "description": "Run leave accrual jobs"},
    {"module": "LEAVE", "action": "view_calendar", "resource": "leave_calendar", "permission_code": "leave.view_leave_calendar", "description": "View leave calendar"},
    {"module": "LEAVE", "action": "export", "resource": "leave", "permission_code": "leave.export_leave", "description": "Export leave data"},
    {"module": "LEAVE", "action": "import", "resource": "leave", "permission_code": "leave.import_leave", "description": "Import leave data"},
    {"module": "LEAVE", "action": "view_audit_logs", "resource": "leave_audit", "permission_code": "leave.view_audit_logs", "description": "View leave audit logs"},
    {"module": "LEAVE", "action": "view", "resource": "leave_type", "permission_code": "leave.view_leave_type", "description": "View leave types"},
    {"module": "LEAVE", "action": "create", "resource": "leave_type", "permission_code": "leave.create_leave_type", "description": "Create leave types"},
    {"module": "LEAVE", "action": "update", "resource": "leave_type", "permission_code": "leave.update_leave_type", "description": "Update leave types"},
    {"module": "LEAVE", "action": "delete", "resource": "leave_type", "permission_code": "leave.delete_leave_type", "description": "Delete leave types"},
    {
        "module": "LEAVE",
        "action": "view",
        "resource": "holiday_list",
        "permission_code": "leave.view_holiday_list",
        "description": "View holiday list"
    },
    {
        "module": "LEAVE",
        "action": "view",
        "resource": "holiday_calendar",
        "permission_code": "leave.view_holiday_calendar",
        "description": "View holiday calendar"
    },
    {
        "module": "LEAVE",
        "action": "manage",
        "resource": "holiday_group_assignments",
        "permission_code": "leave.manage_holiday_group_assignments",
        "description": "Manage holiday group assignments"
    },
    {
        "module": "LEAVE",
        "action": "manage",
        "resource": "carry_forward",
        "permission_code": "leave.manage_carry_forward",
        "description": "Manage leave carry forward"
    },
    {
        "module": "LEAVE",
        "action": "view",
        "resource": "notification_templates",
        "permission_code": "leave.view_notification_templates",
        "description": "View notification templates"
    },
    {
        "module": "LEAVE",
        "action": "manage",
        "resource": "notification_templates",
        "permission_code": "leave.manage_notification_templates",
        "description": "Manage notification templates"
    },
    {
        "module": "LEAVE",
        "action": "view",
        "resource": "leave_policy",
        "permission_code": "leave.view_leave_policies",
        "description": "View leave policies"
    },
    {
        "module": "LEAVE",
        "action": "add",
        "resource": "leave_policy",
        "permission_code": "leave.add_leave_policy",
        "description": "Create leave policy"
    },
    {
        "module": "LEAVE",
        "action": "manage_assignments",
        "resource": "leave_policy",
        "permission_code": "leave.manage_leave_policy_assignments",
        "description": "Manage leave policy assignments"
    },
    {
        "module": "LEAVE",
        "action": "update",
        "resource": "leave_policy",
        "permission_code": "leave.update_leave_policy",
        "description": "Update leave policy"
    }
    
]
    


# =========================================================================
# ROLE DATA
# =========================================================================

ROLES_DATA = [
    {
        "code": "SUPER_ADMIN",
        "label": "Super Administrator",
        "description": "Full system access with all permissions"
    },
    {
        "code": "HR_ADMIN",
        "label": "HR Administrator",
        "description": "HR management with full employee, leave, and attendance control"
    },
    {
        "code": "HR_MANAGER",
        "label": "HR Manager",
        "description": "HR operations including approvals and policy management"
    },
    {
        "code": "MANAGER",
        "label": "Manager",
        "description": "Team management with approval rights for direct reports"
    },
    {
        "code": "EMPLOYEE",
        "label": "Employee",
        "description": "Basic employee access to own records and applications"
    },
    {
        "code": "RECRUITER",
        "label": "Recruiter",
        "description": "Recruitment focused access"
    },
    {
        "code": "PAYROLL_ADMIN",
        "label": "Payroll Administrator",
        "description": "Payroll and salary management access"
    },
]


# =========================================================================
# PERMISSION GROUP DATA
# =========================================================================

PERMISSION_GROUPS_DATA = [
    # Employee Management Groups
    {
        "group_name": "Employee - Self Service",
        "description": "Basic permissions for employees to manage their own data",
        "permissions": [
            "employee.view_own_profile",
            "employee.edit_own_profile",
            "employee.view_org_chart",
            "employee.view_team",
        ]
    },
    {
        "group_name": "Employee - View All",
        "description": "View all employee profiles and information",
        "permissions": [
            "employee.view_all_employee",
            "employee.view_org_chart",
            "employee.view_team",
            "employee.view_documents",
        ]
    },
    {
        "group_name": "Employee - Full Management",
        "description": "Complete employee lifecycle management",
        "permissions": [
            "employee.view_all_employee",
            "employee.create_employee",
            "employee.edit_employee",
            "employee.delete_employee",
            "employee.activate_employee",
            "employee.deactivate_employee",
            "employee.terminate_employee",
            "employee.transfer_employee",
            "employee.promote_employee",
            "employee.demote_employee",
            "employee.change_reporting_manager",
            "employee.view_documents",
            "employee.manage_documents",
            "employee.upload_documents",
            "employee.delete_documents",
            "employee.view_org_chart",
            "employee.view_team",
        ]
    },
    {
        "group_name": "Employee - RBAC Management",
        "description": "Assign and manage roles for employees",
        "permissions": [
            "employee.assign_role",
            "employee.remove_role",
            "employee.view_all_employee",
        ]
    },
    {
        "group_name": "Employee - Salary Management",
        "description": "View and manage employee salary information",
        "permissions": [
            "employee.view_salary",
            "employee.edit_salary",
        ]
    },
    {
        "group_name": "Employee - Data Operations",
        "description": "Import, export, and audit employee data",
        "permissions": [
            "employee.export_employee",
            "employee.import_employee",
            "employee.view_audit_logs",
        ]
    },
    
    # Attendance Management Groups
    {
        "group_name": "Attendance - Self Service",
        "description": "Employee self-service attendance features",
        "permissions": [
            "attendance.view_own_attendance",
            "attendance.regularize_attendance",
            "attendance.apply_overtime",
        ]
    },
    {
        "group_name": "Attendance - Team View",
        "description": "View team attendance records",
        "permissions": [
            "attendance.view_attendance",
            "attendance.view_team_attendance",
            "attendance.view_shift",
            "attendance.view_roster",
        ]
    },
    {
        "group_name": "Attendance - Approvals",
        "description": "Approve attendance regularizations and overtime",
        "permissions": [
            "attendance.view_attendance",
            "attendance.view_team_attendance",
            "attendance.approve_regularization",
            "attendance.reject_regularization",
            "attendance.approve_overtime",
            "attendance.reject_overtime",
        ]
    },
    {
        "group_name": "Attendance - Full Management",
        "description": "Complete attendance management including shifts and rosters",
        "permissions": [
            "attendance.view_attendance",
            "attendance.create_attendance",
            "attendance.edit_attendance",
            "attendance.delete_attendance",
            "attendance.mark_manual_attendance",
            "attendance.override_attendance",
            "attendance.approve_regularization",
            "attendance.reject_regularization",
            "attendance.approve_overtime",
            "attendance.reject_overtime",
            "attendance.view_shift",
            "attendance.assign_shift",
            "attendance.edit_shift",
            "attendance.delete_shift",
            "attendance.view_roster",
            "attendance.manage_roster",
            "attendance.view_logs",
            "attendance.view_team_attendance",
        ]
    },
    {
        "group_name": "Attendance - System Admin",
        "description": "System-level attendance administration",
        "permissions": [
            "attendance.sync_biometric",
            "attendance.manage_biometric",
            "attendance.export_attendance",
            "attendance.import_attendance",
        ]
    },
    
    # Leave Management Groups
    {
        "group_name": "Leave - Self Service",
        "description": "Employee self-service leave features",
        "permissions": [
            "leave.view_own_leave",
            "leave.view_own_leave_balance",
            "leave.apply_leave",
            "leave.edit_own_leave",
            "leave.cancel_own_leave",
            "leave.view_leave_calendar",
            "leave.view_holiday_calendar",
            "leave.view_holiday_list",
            "leave.encash_leave",
            "leave.view_notification_templates",
            "leave.view_leave_policies",
            "leave.view_leave_type",
        ]
    },
    {
        "group_name": "Leave - Team View",
        "description": "View team leave records and calendar",
        "permissions": [
            "leave.view_leave",
            "leave.view_team_leave",
            "leave.view_team_leave_balance",
            "leave.view_leave_calendar",
            "leave.view_leave_policies",
        ]
    },
    {
        "group_name": "Leave - Approvals",
        "description": "Approve and reject leave applications",
        "permissions": [
            "leave.delegate_authority"
            "leave.view_leave",
            "leave.view_team_leave",
             "leave.view_team_leave_balance",   
            "leave.approve_leave",
            "leave.reject_leave",
            "leave.approve_leave_encashment",
            "leave.reject_leave_encashment",
            "leave.view_leave_calendar",
        ]
    },
    {
        "group_name": "Leave - Full Management",
        "description": "Complete leave management including balance adjustments",
        "permissions": [
            "leave.view_leave",
            "leave.view_team_leave",
            "leave.view_team_leave_balance",
            "leave.approve_leave",
            "leave.reject_leave",
            "leave.withdraw_leave",
            "leave.override_leave",
            "leave.adjust_leave_balance",
            "leave.view_leave_balance",
            "leave.approve_leave_encashment",
            "leave.reject_leave_encashment",
            "leave.view_leave_calendar",
            "leave.view_leave_type",
            "leave.create_leave_type",
            "leave.update_leave_type",
            "leave.delete_leave_type",
            "leave.view_holiday_list",
            "leave.view_holiday_calendar",
            "leave.manage_holiday_group_assignments",
            "leave.manage_carry_forward",
            "leave.view_notification_templates",
            "leave.manage_notification_templates",

            "leave.view_leave_policies",
            "leave.add_leave_policy",
            "leave.update_leave_policy",
            "leave.manage_leave_policy_assignments",

            "leave.assign_leave_policy",
            "leave.manage_holiday_calendar"
        ]
    },
    {
        "group_name": "Leave - Policy Management",
        "description": "Manage leave policies and configurations",
        "permissions": [
            "leave.manage_leave_policy",
            "leave.manage_holiday_calendar",
            "leave.assign_leave_policy",
            "leave.run_leave_accrual",
            "leave.view_leave_policies",
            "leave.add_leave_policy",
            "leave.update_leave_policy",
            "leave.manage_leave_policy_assignments",
        ]
    },
    {
        "group_name": "Leave - Data Operations",
        "description": "Import, export, and audit leave data",
        "permissions": [
            "leave.export_leave",
            "leave.import_leave",
            "leave.view_audit_logs",
        ]
    },
]


# =========================================================================
# ROLE → PERMISSION GROUP MAPPINGS
# =========================================================================

ROLE_PERMISSION_GROUP_MAPPINGS = {
    "SUPER_ADMIN": [
        # All groups - super admin gets everything
        "Employee - Self Service",
        "Employee - View All",
        "Employee - Full Management",
        "Employee - RBAC Management",
        "Employee - Salary Management",
        "Employee - Data Operations",
        "Attendance - Self Service",
        "Attendance - Team View",
        "Attendance - Approvals",
        "Attendance - Full Management",
        "Attendance - System Admin",
        "Leave - Self Service",
        "Leave - Team View",
        "Leave - Approvals",
        "Leave - Full Management",
        "Leave - Policy Management",
        "Leave - Data Operations",
    ],
    "HR_ADMIN": [
        # HR Admin gets full access except RBAC management (reserved for super admin)
        "Employee - Self Service",
        "Employee - View All",
        "Employee - Full Management",
        "Employee - Salary Management",
        "Employee - Data Operations",
        "Attendance - Self Service",
        "Attendance - Team View",
        "Attendance - Approvals",
        "Attendance - Full Management",
        "Attendance - System Admin",
        "Leave - Self Service",
        "Leave - Team View",
        "Leave - Approvals",
        "Leave - Full Management",
        "Leave - Policy Management",
        "Leave - Data Operations",
    ],
    "HR_MANAGER": [
        # HR Manager - operational management without data ops
        "Employee - Self Service",
        "Employee - View All",
        "Employee - Full Management",
        "Employee - Salary Management",
        "Attendance - Self Service",
        "Attendance - Team View",
        "Attendance - Approvals",
        "Attendance - Full Management",
        "Leave - Self Service",
        "Leave - Team View",
        "Leave - Approvals",
        "Leave - Full Management",
        "Leave - Policy Management",
    ],
    "MANAGER": [
        # Manager - team management and approvals
        "Employee - Self Service",
        "Employee - View All",
        "Attendance - Self Service",
        "Attendance - Team View",
        "Attendance - Approvals",
        "Leave - Self Service",
        "Leave - Team View",
        "Leave - Approvals",
    ],
    "EMPLOYEE": [
        # Employee - only self-service
        "Employee - Self Service",
        "Attendance - Self Service",
        "Leave - Self Service",
    ],
    "RECRUITER": [
        # Recruiter - employee viewing and basic management
        "Employee - Self Service",
        "Employee - View All",
        "Employee - Full Management",
    ],
    "PAYROLL_ADMIN": [
        # Payroll - salary and attendance data
        "Employee - Self Service",
        "Employee - View All",
        "Employee - Salary Management",
        "Attendance - Team View",
        "Attendance - Full Management",
        "Leave - Team View",
    ],
}


# =========================================================================
# SEED FUNCTIONS
# =========================================================================

def seed_permissions():
    """Seed all permissions."""
    print("=" * 70)
    print("SEEDING PERMISSIONS")
    print("=" * 70)
    
    created_count = 0
    existing_count = 0
    
    for perm_data in PERMISSIONS_DATA:
        perm, created = Permission.objects.get_or_create(
            permission_code=perm_data["permission_code"],
            defaults={
                "module": perm_data["module"],
                "action": perm_data["action"],
                "resource": perm_data["resource"],
                "description": perm_data["description"],
            }
        )
        if created:
            created_count += 1
            print(f"  ✓ Created: {perm.permission_code}")
        else:
            existing_count += 1
    
    print(f"\n✓ Created {created_count} new permissions")
    print(f"✓ Found {existing_count} existing permissions")
    print(f"✓ Total permissions: {Permission.objects.count()}\n")


def seed_roles():
    """Seed all system roles."""
    print("=" * 70)
    print("SEEDING ROLES")
    print("=" * 70)
    
    created_count = 0
    existing_count = 0
    
    for role_data in ROLES_DATA:
        role, created = Role.objects.get_or_create(
            code=role_data["code"],
            defaults={
                "label": role_data["label"],
                "description": role_data["description"],
            }
        )
        if created:
            created_count += 1
            print(f"  ✓ Created: {role.code} - {role.label}")
        else:
            existing_count += 1
    
    print(f"\n✓ Created {created_count} new roles")
    print(f"✓ Found {existing_count} existing roles")
    print(f"✓ Total roles: {Role.objects.count()}\n")


def seed_permission_groups():
    """Seed permission groups and link them to permissions."""
    print("=" * 70)
    print("SEEDING PERMISSION GROUPS")
    print("=" * 70)
    
    # Build permission lookup cache
    permission_cache = {
        perm.permission_code: perm 
        for perm in Permission.objects.all()
    }
    
    created_groups = 0
    existing_groups = 0
    
    for group_data in PERMISSION_GROUPS_DATA:
        group, created = PermissionGroup.objects.get_or_create(
            group_name=group_data["group_name"],
            defaults={
                "description": group_data["description"],
            }
        )
        
        if created:
            created_groups += 1
            print(f"  ✓ Created: {group.group_name}")
        else:
            existing_groups += 1
            print(f"  → Existing: {group.group_name}")
        
        # Link permissions to group
        permission_objects = []
        for perm_code in group_data["permissions"]:
            if perm_code in permission_cache:
                permission_objects.append(permission_cache[perm_code])
            else:
                print(f"    ⚠ Warning: Permission '{perm_code}' not found!")
        
        # Clear existing and set new permissions
        group.permissions.set(permission_objects)
        print(f"    → Linked {len(permission_objects)} permissions")
    
    print(f"\n✓ Created {created_groups} new permission groups")
    print(f"✓ Found {existing_groups} existing permission groups")
    print(f"✓ Total permission groups: {PermissionGroup.objects.count()}\n")


def seed_role_permission_groups():
    """Link roles to permission groups."""
    print("=" * 70)
    print("SEEDING ROLE → PERMISSION GROUP MAPPINGS")
    print("=" * 70)
    
    # Build caches
    role_cache = {role.code: role for role in Role.objects.all()}
    group_cache = {
        group.group_name: group 
        for group in PermissionGroup.objects.all()
    }
    
    for role_code, group_names in ROLE_PERMISSION_GROUP_MAPPINGS.items():
        if role_code not in role_cache:
            print(f"  ⚠ Warning: Role '{role_code}' not found!")
            continue
        
        role = role_cache[role_code]
        print(f"\n  {role.label} ({role.code}):")
        
        group_objects = []
        for group_name in group_names:
            if group_name in group_cache:
                group_objects.append(group_cache[group_name])
            else:
                print(f"    ⚠ Warning: Group '{group_name}' not found!")
        
        # Use through model to link
        RolePermissionGroup.objects.filter(role=role).delete()  # Clear existing
        for group in group_objects:
            RolePermissionGroup.objects.get_or_create(
                role=role,
                group=group
            )
        
        print(f"    → Linked {len(group_objects)} permission groups")
    
    print(f"\n✓ Total role-group mappings: {RolePermissionGroup.objects.count()}\n")


def seed_employee_role_assignments(employee_email_role_mapping=None):
    """
    Seed employee role assignments.
    
    Args:
        employee_email_role_mapping: Dict mapping employee emails to role codes
        Example: {
            'admin@company.com': 'SUPER_ADMIN',
            'hr@company.com': 'HR_ADMIN',
            'manager@company.com': 'MANAGER',
        }
    """
    print("=" * 70)
    print("SEEDING EMPLOYEE ROLE ASSIGNMENTS")
    print("=" * 70)
    
    if not employee_email_role_mapping:
        print("  ⚠ No employee mapping provided. Skipping role assignments.")
        print("  ℹ To assign roles, pass employee_email_role_mapping parameter.\n")
        return
    
    role_cache = {role.code: role for role in Role.objects.all()}
    created_count = 0
    skipped_count = 0
    
    # Get a system user for assigned_by (first super admin or any employee)
    assigned_by_employee = Employee.objects.filter(
        role_assignments__role__code='SUPER_ADMIN'
    ).first() or Employee.objects.first()
    
    if not assigned_by_employee:
        print("  ⚠ No employees found in database. Cannot assign roles.\n")
        return
    
    for email, role_code in employee_email_role_mapping.items():
        try:
            employee = Employee.objects.get(user__email=email)
            
            if role_code not in role_cache:
                print(f"  ⚠ Role '{role_code}' not found. Skipping {email}")
                skipped_count += 1
                continue
            
            role = role_cache[role_code]
            
            # Check if assignment already exists
            existing = EmployeeRoleAssignment.objects.filter(
                employee=employee,
                role=role,
                is_active=True
            ).exists()
            
            if existing:
                print(f"  → Existing: {email} already has {role_code}")
                skipped_count += 1
                continue
            
            # Create assignment
            assignment = EmployeeRoleAssignment.objects.create(
                employee=employee,
                role=role,
                assigned_by=assigned_by_employee,
                effective_from=date.today(),
                is_active=True
            )
            created_count += 1
            print(f"  ✓ Assigned: {email} → {role.label}")
            
        except Employee.DoesNotExist:
            print(f"  ⚠ Employee '{email}' not found. Skipping.")
            skipped_count += 1
        except Exception as e:
            print(f"  ✗ Error assigning {email}: {str(e)}")
            skipped_count += 1
    
    print(f"\n✓ Created {created_count} role assignments")
    print(f"→ Skipped {skipped_count} assignments")
    print(f"✓ Total active assignments: {EmployeeRoleAssignment.objects.filter(is_active=True).count()}\n")


@transaction.atomic
def seed_rbac_data(employee_email_role_mapping=None, schema_name="acme"):
    """
    Main function to seed all RBAC data.
    
    Args:
        employee_email_role_mapping: Optional dict mapping employee emails to role codes
    """
    with schema_context(schema_name):
        print("\n" + "=" * 70)
        print("STARTING RBAC DATA SEEDING")
        print("=" * 70 + "\n")
        
        # Seed in order of dependencies
        seed_permissions()
        seed_roles()
        seed_permission_groups()
        seed_role_permission_groups()
        seed_employee_role_assignments(employee_email_role_mapping)
        
        print("=" * 70)
        print("RBAC SEEDING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nSummary:")
        print(f"  • Permissions: {Permission.objects.count()}")
        print(f"  • Roles: {Role.objects.count()}")
        print(f"  • Permission Groups: {PermissionGroup.objects.count()}")
        print(f"  • Role-Group Mappings: {RolePermissionGroup.objects.count()}")
        print(f"  • Employee Role Assignments: {EmployeeRoleAssignment.objects.filter(is_active=True).count()}")
        print("=" * 70 + "\n")


# =========================================================================
# USAGE EXAMPLES
# =========================================================================

if __name__ == "__main__":
    #First seed employee data then seed the rbac data.
    # Example 1: Seed without employee assignments
    # seed_rbac_data()
    
    # Example 2: Seed with employee assignments
    employee_mapping = {
        'admin@company.com': 'SUPER_ADMIN',
        'hr.admin@company.com': 'HR_ADMIN',
        'hr.manager@company.com': 'HR_MANAGER',
        'priya.singh@acme.com': 'MANAGER',
        'jane.employee@company.com': 'EMPLOYEE',
        'recruiter@company.com': 'RECRUITER',
        'payroll@company.com': 'PAYROLL_ADMIN',
    }
    # seed_rbac_data(schema_name="acme")
    seed_rbac_data(employee_email_role_mapping=employee_mapping, schema_name="acme")
