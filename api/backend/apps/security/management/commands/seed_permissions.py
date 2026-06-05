"""
Seed master permissions for the Security module.

Creates:
    - Atomic permissions (mst_permission)

Usage:
    python manage.py seed_permissions

Safe to run multiple times.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.security.models import Permission


PERMISSIONS = [
    # =========================================================
    # EMPLOYEE
    # =========================================================
    {
        "module": "employee",
        "action": "view",
        "resource": "employee",
        "permission_code": "employee.view_employee",
        "description": "View employee records",
    },
    {
        "module": "employee",
        "action": "create",
        "resource": "employee",
        "permission_code": "employee.create_employee",
        "description": "Create employee records",
    },
    {
        "module": "employee",
        "action": "edit",
        "resource": "employee",
        "permission_code": "employee.edit_employee",
        "description": "Edit employee records",
    },
    {
        "module": "employee",
        "action": "delete",
        "resource": "employee",
        "permission_code": "employee.delete_employee",
        "description": "Delete employee records",
    },
    {
        "module": "employee",
        "action": "export",
        "resource": "employee",
        "permission_code": "employee.export_employee",
        "description": "Export employee records",
    },

    # =========================================================
    # LEAVE
    # =========================================================
    {
        "module": "leave",
        "action": "view",
        "resource": "leave_request",
        "permission_code": "leave.view_leave",
        "description": "View leave requests",
    },
    {
        "module": "leave",
        "action": "apply",
        "resource": "leave_request",
        "permission_code": "leave.apply_leave",
        "description": "Apply leave requests",
    },
    {
        "module": "leave",
        "action": "approve",
        "resource": "leave_request",
        "permission_code": "leave.approve_leave",
        "description": "Approve leave requests",
    },
    {
        "module": "leave",
        "action": "reject",
        "resource": "leave_request",
        "permission_code": "leave.reject_leave",
        "description": "Reject leave requests",
    },
    {
        "module": "leave",
        "action": "cancel",
        "resource": "leave_request",
        "permission_code": "leave.cancel_leave",
        "description": "Cancel leave requests",
    },

    # =========================================================
    # ATTENDANCE
    # =========================================================
    {
        "module": "attendance",
        "action": "view",
        "resource": "attendance",
        "permission_code": "attendance.view_attendance",
        "description": "View attendance",
    },
    {
        "module": "attendance",
        "action": "edit",
        "resource": "attendance",
        "permission_code": "attendance.edit_attendance",
        "description": "Edit attendance",
    },
    {
        "module": "attendance",
        "action": "regularize",
        "resource": "attendance",
        "permission_code": "attendance.regularize_attendance",
        "description": "Regularize attendance",
    },

    # =========================================================
    # PAYROLL
    # =========================================================
    {
        "module": "payroll",
        "action": "view",
        "resource": "payroll",
        "permission_code": "payroll.view_payroll",
        "description": "View payroll",
    },
    {
        "module": "payroll",
        "action": "process",
        "resource": "payroll",
        "permission_code": "payroll.process_payroll",
        "description": "Process payroll",
    },
    {
        "module": "payroll",
        "action": "approve",
        "resource": "payroll",
        "permission_code": "payroll.approve_payroll",
        "description": "Approve payroll",
    },

    # =========================================================
    # RECRUITMENT
    # =========================================================
    {
        "module": "recruitment",
        "action": "view",
        "resource": "candidate",
        "permission_code": "recruitment.view_candidate",
        "description": "View candidates",
    },
    {
        "module": "recruitment",
        "action": "create",
        "resource": "candidate",
        "permission_code": "recruitment.create_candidate",
        "description": "Create candidates",
    },
    {
        "module": "recruitment",
        "action": "schedule",
        "resource": "interview",
        "permission_code": "recruitment.schedule_interview",
        "description": "Schedule interviews",
    },

    # =========================================================
    # SECURITY
    # =========================================================
    {
        "module": "security",
        "action": "view",
        "resource": "roles",
        "permission_code": "security.view_roles",
        "description": "View roles",
    },
    {
        "module": "security",
        "action": "manage",
        "resource": "roles",
        "permission_code": "security.manage_roles",
        "description": "Manage roles",
    },
    {
        "module": "security",
        "action": "view",
        "resource": "permissions",
        "permission_code": "security.view_permissions",
        "description": "View permissions",
    },
    {
        "module": "security",
        "action": "assign",
        "resource": "roles",
        "permission_code": "security.assign_roles",
        "description": "Assign roles to employees",
    },

    # =========================================================
    # REPORTS
    # =========================================================
    {
        "module": "reports",
        "action": "view",
        "resource": "reports",
        "permission_code": "reports.view_reports",
        "description": "View reports",
    },
    {
        "module": "reports",
        "action": "export",
        "resource": "reports",
        "permission_code": "reports.export_reports",
        "description": "Export reports",
    },

    # =========================================================
    # SETTINGS
    # =========================================================
    {
        "module": "settings",
        "action": "view",
        "resource": "settings",
        "permission_code": "settings.view_settings",
        "description": "View settings",
    },
    {
        "module": "settings",
        "action": "edit",
        "resource": "settings",
        "permission_code": "settings.edit_settings",
        "description": "Edit settings",
    },
]


class Command(BaseCommand):
    help = "Seed master permissions"

    @transaction.atomic
    def handle(self, *args, **kwargs):

        created_count = 0
        updated_count = 0

        self.stdout.write(self.style.WARNING("Seeding permissions..."))

        for perm_data in PERMISSIONS:

            permission, created = Permission.objects.update_or_create(
                permission_code=perm_data["permission_code"],
                defaults={
                    "module": perm_data["module"],
                    "action": perm_data["action"],
                    "resource": perm_data["resource"],
                    "description": perm_data["description"],
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"CREATED  → {permission.permission_code}"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.NOTICE(
                        f"UPDATED  → {permission.permission_code}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created={created_count}, Updated={updated_count}"
            )
        )