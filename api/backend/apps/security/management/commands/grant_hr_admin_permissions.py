"""
Management command: grant_hr_admin_permissions

Grants the HR_ADMIN role to a user by email, giving full access to all
employee sections (view, create, edit, delete, salary, documents, etc.).

Usage:
    python manage.py grant_hr_admin_permissions --email hr.admin@company.com
    python manage.py grant_hr_admin_permissions --email hr.admin@company.com --schema acme

The command is idempotent - safe to run multiple times.
"""

from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


# All permission codes the HR_ADMIN role needs for employee sections.
EMPLOYEE_SECTION_PERMISSIONS = [
    "employee.view_employee",
    "employee.create_employee",
    "employee.edit_employee",
    "employee.delete_employee",
    "employee.export_employee",
    "employee.import_employee",
    "employee.view_salary",
    "employee.edit_salary",
    "employee.view_documents",
    "employee.manage_documents",
    "employee.upload_documents",
    "employee.delete_documents",
    "employee.view_org_chart",
    "employee.view_team",
    "employee.assign_role",
    "employee.remove_role",
    "employee.view_all_employee",
    "employee.activate_employee",
    "employee.deactivate_employee",
    "employee.terminate_employee",
    "employee.transfer_employee",
    "employee.promote_employee",
    "employee.demote_employee",
    "employee.change_reporting_manager",
    "employee.view_audit_logs",
]

TARGET_ROLE_CODE = "HR_ADMIN"


class Command(BaseCommand):
    help = "Grant HR_ADMIN role + all employee-section permissions to a user by email."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            default="hr.admin@company.com",
            help="Work email of the user to promote (default: hr.admin@company.com)",
        )
        parser.add_argument(
            "--schema",
            type=str,
            default=None,
            help="Tenant schema name (omit to use the currently active schema)",
        )

    def handle(self, *args, **options):
        email: str = options["email"].strip().lower()
        schema: str | None = options.get("schema")

        if schema:
            try:
                from django_tenants.utils import get_tenant_model, tenant_context
                TenantModel = get_tenant_model()
                tenant = TenantModel.objects.get(schema_name=schema)
                with tenant_context(tenant):
                    self._run(email)
            except Exception as exc:
                raise CommandError(str(exc)) from exc
        else:
            self._run(email)

    @transaction.atomic
    def _run(self, email: str):
        from apps.employees.models import Employee
        from apps.security.models import Permission, Role
        from apps.security.models.permission import (
            GroupPermission,
            PermissionGroup,
            RolePermissionGroup,
        )
        from apps.security.models.role import EmployeeRoleAssignment

        # -- 1. Resolve employee ----------------------------------------------
        employee = self._find_employee(email, Employee)

        self.stdout.write(
            self.style.SUCCESS(f"Found employee: {employee.first_name} {employee.last_name} ({email})")
        )

        # -- 2. Ensure all required permissions exist -------------------------
        self._ensure_permissions(Permission)

        # -- 3. Ensure HR_ADMIN role exists -----------------------------------
        role = self._ensure_role(Role)

        # -- 4. Ensure "Employee Management" permission group exists ----------
        group = self._ensure_permission_group(PermissionGroup, GroupPermission, Permission)

        # 5. Link group to role
        self._ensure_role_permission_group(RolePermissionGroup, role, group)

        # -- 6. Assign role to employee ---------------------------------------
        self._ensure_role_assignment(EmployeeRoleAssignment, employee, role)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(
            self.style.SUCCESS(
                f"  OK {email} now has HR_ADMIN role with full employee permissions."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"  OK Permissions granted: {len(EMPLOYEE_SECTION_PERMISSIONS)}"
            )
        )
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(
            "  -> Log out and log back in for the new JWT claims to take effect."
        )

    # -- Helpers --------------------------------------------------------------

    def _find_employee(self, email, Employee):
        """Resolve employee by official_email (contacts), employee_code, or linked User.email."""
        from apps.employees.models.contact import EmployeeContacts

        # Try via EmployeeContacts.official_email
        contact = EmployeeContacts.objects.filter(official_email__iexact=email).first()
        if contact:
            try:
                employee = contact.employee
                if employee and employee.is_active:
                    return employee
            except Exception:
                pass

        # Try via EmployeeContacts.personal_email
        contact = EmployeeContacts.objects.filter(personal_email__iexact=email).first()
        if contact:
            try:
                employee = contact.employee
                if employee and employee.is_active:
                    return employee
            except Exception:
                pass

        # Try via linked User model
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(email__iexact=email).first()
        if user:
            try:
                employee = user.employee_profile
                if employee and employee.is_active:
                    return employee
            except AttributeError:
                pass

        raise CommandError(
            f"No active employee found with email '{email}'.\n"
            "Check that the email matches official_email or personal_email in EmployeeContacts."
        )

    def _ensure_permissions(self, Permission):
        """Create any missing permission codes."""
        created = []
        for code in EMPLOYEE_SECTION_PERMISSIONS:
            _, was_created = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "module": code.split(".")[0].upper(),
                    "action": "manage",
                    "resource": "employee",
                    "description": f"Auto-created: {code}",
                },
            )
            if was_created:
                created.append(code)

        if created:
            self.stdout.write(
                self.style.WARNING(f"  Created {len(created)} missing permissions: {created}")
            )
        else:
            self.stdout.write(f"  All {len(EMPLOYEE_SECTION_PERMISSIONS)} permissions already exist.")

    def _ensure_role(self, Role):
        role, created = Role.objects.get_or_create(
            code=TARGET_ROLE_CODE,
            defaults={
                "label": "HR Admin",
                "description": "Full HR management: employees, leave, attendance, payroll, RBAC",
                "access_level": "ALL",
                "is_custom": False,
            },
        )
        if created:
            self.stdout.write(self.style.WARNING(f"  Created role: {TARGET_ROLE_CODE}"))
        else:
            self.stdout.write(f"  Role '{TARGET_ROLE_CODE}' exists.")
        return role

    def _ensure_permission_group(self, PermissionGroup, GroupPermission, Permission):
        group, created = PermissionGroup.objects.get_or_create(
            group_name="Employee Management",
            defaults={"description": "Full employee lifecycle management"},
        )
        if created:
            self.stdout.write(self.style.WARNING("  Created permission group: Employee Management"))

        # Attach all required permissions to the group
        perms = Permission.objects.filter(permission_code__in=EMPLOYEE_SECTION_PERMISSIONS)
        for perm in perms:
            GroupPermission.objects.get_or_create(group=group, permission=perm)

        self.stdout.write(
            f"  Permission group 'Employee Management' has {perms.count()} permissions linked."
        )
        return group

    def _ensure_role_permission_group(self, RolePermissionGroup, role, group):
        _, created = RolePermissionGroup.objects.get_or_create(role=role, group=group)
        if created:
            self.stdout.write(
                self.style.WARNING(f"  Linked group '{group.group_name}' to role '{role.code}'")
            )
        else:
            self.stdout.write(f"  Group '{group.group_name}' already linked to role '{role.code}'.")

    def _ensure_role_assignment(self, EmployeeRoleAssignment, employee, role):
        existing = EmployeeRoleAssignment.objects.filter(
            employee=employee,
            role=role,
            is_active=True,
        ).first()

        if existing:
            self.stdout.write(
                f"  Employee already has active '{role.code}' assignment (id={existing.id})."
            )
            return

        EmployeeRoleAssignment.objects.create(
            employee=employee,
            role=role,
            effective_from=date.today(),
            is_active=True,
        )
        self.stdout.write(
            self.style.SUCCESS(f"  OK Assigned role '{role.code}' to {employee.work_email}")
        )
