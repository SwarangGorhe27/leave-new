"""
Management command: seed_rbac

Seeds Permissions, PermissionGroups, MenuItems, and core Roles
for a given tenant schema.

Usage:
    python manage.py seed_rbac --schema=acme
    python manage.py seed_rbac --all-tenants
    python manage.py seed_rbac --schema=acme --roles-only
    python manage.py seed_rbac --schema=acme --dry-run
"""

from django.core.management.base import BaseCommand
from django.db import connection

from django_tenants.utils import get_tenant_model, tenant_context


# ---------------------------------------------------------------------------
# PERMISSION DEFINITIONS  (module, action, resource, code, description)
# ---------------------------------------------------------------------------

PERMISSIONS = [
    # ----- EMPLOYEE module -----
    ("EMPLOYEE", "view",   "employee",         "employee.view_employee",         "View employee profiles"),
    ("EMPLOYEE", "create", "employee",         "employee.create_employee",       "Create new employee records"),
    ("EMPLOYEE", "edit",   "employee",         "employee.edit_employee",         "Edit employee profiles"),
    ("EMPLOYEE", "delete", "employee",         "employee.delete_employee",       "Delete / terminate employee records"),
    ("EMPLOYEE", "export", "employee",         "employee.export_employee",       "Export employee data"),
    ("EMPLOYEE", "import", "employee",         "employee.import_employee",       "Bulk import employees"),
    ("EMPLOYEE", "view",   "salary",           "employee.view_salary",           "View employee salary information"),
    ("EMPLOYEE", "edit",   "salary",           "employee.edit_salary",           "Edit salary / CTC details"),
    ("EMPLOYEE", "view",   "documents",        "employee.view_documents",        "View employee documents"),
    ("EMPLOYEE", "manage", "documents",        "employee.manage_documents",      "Upload / delete employee documents"),

    # ----- ATTENDANCE module -----
    ("ATTENDANCE", "view",   "attendance",     "attendance.view_attendance",     "View attendance records"),
    ("ATTENDANCE", "edit",   "attendance",     "attendance.edit_attendance",     "Edit / correct attendance entries"),
    ("ATTENDANCE", "approve","attendance",     "attendance.approve_attendance",  "Approve attendance regularisations"),
    ("ATTENDANCE", "export", "attendance",     "attendance.export_attendance",   "Export attendance reports"),
    ("ATTENDANCE", "view",   "swipe_log",      "attendance.view_swipe_log",      "View raw biometric swipe logs"),
    ("ATTENDANCE", "edit",   "swipe_log",      "attendance.edit_swipe_log",      "Add / edit manual swipe entries"),

    # ----- LEAVE module -----
    ("LEAVE", "view",   "leave",              "leave.view_leave",               "View leave applications"),
    ("LEAVE", "apply",  "leave",              "leave.apply_leave",              "Submit own leave application"),
    ("LEAVE", "approve","leave",              "leave.approve_leave",            "Approve / reject leave applications"),
    ("LEAVE", "cancel", "leave",              "leave.cancel_leave",             "Cancel leave applications"),
    ("LEAVE", "edit",   "leave_policy",       "leave.edit_leave_policy",        "Edit company leave policies"),
    ("LEAVE", "view",   "leave_balance",      "leave.view_leave_balance",       "View leave balances"),
    ("LEAVE", "edit",   "leave_balance",      "leave.edit_leave_balance",       "Adjust leave balances manually"),
    ("LEAVE", "export", "leave",              "leave.export_leave",             "Export leave reports"),

    # ----- PAYROLL module -----
    ("PAYROLL", "view",   "payroll",          "payroll.view_payroll",           "View payroll records"),
    ("PAYROLL", "process","payroll",          "payroll.process_payroll",        "Run payroll processing"),
    ("PAYROLL", "approve","payroll",          "payroll.approve_payroll",        "Approve payroll run"),
    ("PAYROLL", "export", "payroll",          "payroll.export_payroll",         "Export payroll data / payslips"),
    ("PAYROLL", "view",   "payslip",          "payroll.view_payslip",           "View own payslip"),

    # ----- RECRUITMENT module -----
    ("RECRUITMENT", "view",   "job_posting",  "recruitment.view_job_posting",   "View job postings"),
    ("RECRUITMENT", "manage", "job_posting",  "recruitment.manage_job_posting", "Create / edit job postings"),
    ("RECRUITMENT", "view",   "candidate",    "recruitment.view_candidate",     "View candidate profiles"),
    ("RECRUITMENT", "manage", "candidate",    "recruitment.manage_candidate",   "Manage candidate pipeline"),

    # ----- PERFORMANCE module -----
    ("PERFORMANCE", "view",   "appraisal",    "performance.view_appraisal",     "View appraisals"),
    ("PERFORMANCE", "manage", "appraisal",    "performance.manage_appraisal",   "Create / edit appraisals"),
    ("PERFORMANCE", "approve","appraisal",    "performance.approve_appraisal",  "Approve final ratings"),

    # ----- REPORTS module -----
    ("REPORTS", "view",   "reports",          "reports.view_reports",           "Access standard reports"),
    ("REPORTS", "create", "reports",          "reports.create_custom_report",   "Create custom reports"),
    ("REPORTS", "export", "reports",          "reports.export_reports",         "Export report data"),

    # ----- RBAC / SECURITY module -----
    ("SECURITY", "view",   "rbac",            "security.view_rbac",             "View RBAC roles and permissions"),
    ("SECURITY", "manage", "rbac",            "security.manage_rbac",           "Manage roles, assignments, groups"),
    ("SECURITY", "view",   "audit_log",       "security.view_audit_log",        "View audit logs"),
    ("SECURITY", "view",   "sessions",        "security.view_sessions",         "View active sessions"),
    ("SECURITY", "manage", "sessions",        "security.manage_sessions",       "Revoke sessions"),
]

# ---------------------------------------------------------------------------
# PERMISSION GROUPS  (name, description, [permission_codes...])
# ---------------------------------------------------------------------------

PERMISSION_GROUPS = [
    (
        "Employee Management",
        "Full control over employee records and documents",
        [
            "employee.view_employee", "employee.create_employee",
            "employee.edit_employee", "employee.delete_employee",
            "employee.export_employee", "employee.import_employee",
            "employee.view_documents", "employee.manage_documents",
        ],
    ),
    (
        "Salary Viewer",
        "View-only access to salary and payroll information",
        ["employee.view_salary", "payroll.view_payroll", "payroll.view_payslip"],
    ),
    (
        "Attendance Management",
        "Full attendance and swipe-log management",
        [
            "attendance.view_attendance", "attendance.edit_attendance",
            "attendance.approve_attendance", "attendance.export_attendance",
            "attendance.view_swipe_log", "attendance.edit_swipe_log",
        ],
    ),
    (
        "Leave Management",
        "Full leave and policy management with approvals",
        [
            "leave.view_leave", "leave.apply_leave", "leave.approve_leave",
            "leave.cancel_leave", "leave.edit_leave_policy",
            "leave.view_leave_balance", "leave.edit_leave_balance",
            "leave.export_leave",
        ],
    ),
    (
        "Payroll Processing",
        "End-to-end payroll run and export",
        [
            "payroll.view_payroll", "payroll.process_payroll",
            "payroll.approve_payroll", "payroll.export_payroll",
        ],
    ),
    (
        "Reports & Analytics",
        "Access standard and custom reports with export",
        [
            "reports.view_reports", "reports.create_custom_report",
            "reports.export_reports",
        ],
    ),
    (
        "RBAC Administration",
        "Manage roles, permissions, assignments, and audit logs",
        [
            "security.view_rbac", "security.manage_rbac",
            "security.view_audit_log", "security.view_sessions",
            "security.manage_sessions",
        ],
    ),
]

# ---------------------------------------------------------------------------
# MENU ITEMS  (code, label, parent_code|None, route_path, icon, sort_order)
# ---------------------------------------------------------------------------

MENU_ITEMS = [
    # Root items
    ("dashboard",            "Dashboard",            None,              "/admin",                              "LayoutDashboard",  1),
    ("employees",            "Employees",            None,              "/admin/employees",                    "Users",            2),
    ("attendance",           "Attendance",           None,              "/admin/attendance",                   "Clock",            3),
    ("leave",                "Leave",                None,              "/admin/leave",                        "CalendarDays",     4),
    ("payroll",              "Payroll",              None,              "/admin/payroll",                      "Banknote",         5),
    ("recruitment",          "Recruitment",          None,              "/admin/recruitment",                  "UserPlus",         6),
    ("performance",          "Performance",          None,              "/admin/performance",                  "TrendingUp",       7),
    ("reports",              "Reports",              None,              "/admin/reports",                      "BarChart2",        8),
    ("settings",             "Settings",             None,              "/admin/settings",                     "Settings",         9),
    ("rbac",                 "Access Control",       None,              "/admin/rbac",                         "Shield",           10),

    # Employees children
    ("employees_list",       "Employee List",        "employees",       "/admin/employees/list",               "",                 1),
    ("employees_onboarding", "Onboarding",           "employees",       "/admin/employees/onboarding",         "",                 2),

    # Attendance children
    ("attendance_overview",  "Overview",             "attendance",      "/admin/attendance/overview",           "",                 1),
    ("attendance_approvals", "Approvals",            "attendance",      "/admin/attendance/approvals",          "",                 2),
    ("attendance_swipe_logs","Swipe Logs",           "attendance",      "/admin/attendance/swipe-logs",         "",                 3),

    # Leave children
    ("leave_applications",   "Applications",         "leave",           "/admin/leave/applications",            "",                 1),
    ("leave_approvals",      "Approvals",            "leave",           "/admin/leave/approvals",               "",                 2),
    ("leave_policies",       "Policies",             "leave",           "/admin/leave/policies",                "",                 3),
    ("leave_balances",       "Balances",             "leave",           "/admin/leave/balances",                "",                 4),

    # Payroll children
    ("payroll_runs",         "Payroll Runs",         "payroll",         "/admin/payroll/runs",                  "",                 1),
    ("payroll_payslips",     "Payslips",             "payroll",         "/admin/payroll/payslips",              "",                 2),

    # RBAC children
    ("rbac_roles",           "Roles",                "rbac",            "/admin/rbac/roles",                    "",                 1),
    ("rbac_employee_roles",  "Employee Assignments", "rbac",            "/admin/rbac/employee-roles",           "",                 2),
    ("rbac_audit_log",       "Audit Log",            "rbac",            "/admin/rbac/audit-log",                "",                 3),
    ("rbac_sessions",        "Active Sessions",      "rbac",            "/admin/rbac/sessions",                 "",                 4),
]

# ---------------------------------------------------------------------------
# CORE ROLES  (role_code, role_name, description, is_super_admin,
#              [permission_group_names...], [module→scope_type...])
# ---------------------------------------------------------------------------

CORE_ROLES = [
    {
        "role_code": "TENANT_SUPER_ADMIN",
        "role_name": "Tenant Super Admin",
        "description": "Full unrestricted access to all modules",
        "is_super_admin": True,
        "permission_groups": [],  # bypasses all — not needed
        "data_scopes": {},        # ALL implicit
    },
    {
        "role_code": "HR_ADMIN",
        "role_name": "HR Admin",
        "description": "Full HR management: employees, leave, attendance, payroll, RBAC",
        "is_super_admin": False,
        "permission_groups": [
            "Employee Management",
            "Salary Viewer",
            "Attendance Management",
            "Leave Management",
            "Payroll Processing",
            "Reports & Analytics",
            "RBAC Administration",
        ],
        "data_scopes": {
            "EMPLOYEE": "ALL", "LEAVE": "ALL", "ATTENDANCE": "ALL",
            "PAYROLL": "ALL", "REPORTS": "ALL",
        },
    },
    {
        "role_code": "HR_MANAGER",
        "role_name": "HR Manager",
        "description": "HR operations within own department scope",
        "is_super_admin": False,
        "permission_groups": [
            "Employee Management",
            "Attendance Management",
            "Leave Management",
            "Reports & Analytics",
        ],
        "data_scopes": {
            "EMPLOYEE": "DEPT", "LEAVE": "DEPT", "ATTENDANCE": "DEPT",
        },
    },
    {
        "role_code": "REPORTING_MANAGER",
        "role_name": "Reporting Manager",
        "description": "Approve leave and attendance for direct reportees",
        "is_super_admin": False,
        "permission_groups": ["Attendance Management", "Leave Management"],
        "data_scopes": {
            "EMPLOYEE": "REPORTEES", "LEAVE": "REPORTEES", "ATTENDANCE": "REPORTEES",
        },
    },
    {
        "role_code": "ATTENDANCE_ADMIN",
        "role_name": "Attendance Admin",
        "description": "Manage all attendance data company-wide",
        "is_super_admin": False,
        "permission_groups": ["Attendance Management"],
        "data_scopes": {"ATTENDANCE": "ALL"},
    },
    {
        "role_code": "LEAVE_ADMIN",
        "role_name": "Leave Admin",
        "description": "Manage leave policies and balances company-wide",
        "is_super_admin": False,
        "permission_groups": ["Leave Management"],
        "data_scopes": {"LEAVE": "ALL"},
    },
    {
        "role_code": "EMPLOYEE",
        "role_name": "Employee (Self-Service)",
        "description": "Basic self-service: apply leave, view own attendance, payslip",
        "is_super_admin": False,
        "permission_groups": [],
        "data_scopes": {
            "EMPLOYEE": "SELF", "LEAVE": "SELF",
            "ATTENDANCE": "SELF", "PAYROLL": "SELF",
        },
    },
]

# ---------------------------------------------------------------------------
# ROLE → MENU PERMISSIONS  (role_code → {menu_item_code: flags_dict})
# ---------------------------------------------------------------------------

ROLE_MENU_PERMISSIONS = {
    "TENANT_SUPER_ADMIN": {
        code: {"can_view": True, "can_edit": True, "can_export": True, "can_import": True, "can_approve": True}
        for code, *_ in MENU_ITEMS
    },
    "HR_ADMIN": {
        "dashboard": {"can_view": True},
        "employees": {"can_view": True, "can_edit": True, "can_export": True, "can_import": True},
        "employees_list": {"can_view": True, "can_edit": True, "can_export": True, "can_import": True},
        "employees_onboarding": {"can_view": True, "can_edit": True},
        "attendance": {"can_view": True, "can_edit": True, "can_approve": True, "can_export": True},
        "attendance_overview": {"can_view": True},
        "attendance_approvals": {"can_view": True, "can_approve": True},
        "attendance_swipe_logs": {"can_view": True, "can_edit": True},
        "leave": {"can_view": True, "can_edit": True, "can_approve": True, "can_export": True},
        "leave_applications": {"can_view": True},
        "leave_approvals": {"can_view": True, "can_approve": True},
        "leave_policies": {"can_view": True, "can_edit": True},
        "leave_balances": {"can_view": True, "can_edit": True},
        "payroll": {"can_view": True, "can_edit": True, "can_approve": True, "can_export": True},
        "payroll_runs": {"can_view": True, "can_edit": True, "can_approve": True},
        "payroll_payslips": {"can_view": True, "can_export": True},
        "reports": {"can_view": True, "can_export": True},
        "rbac": {"can_view": True, "can_edit": True},
        "rbac_roles": {"can_view": True, "can_edit": True},
        "rbac_employee_roles": {"can_view": True, "can_edit": True},
        "rbac_audit_log": {"can_view": True},
        "rbac_sessions": {"can_view": True, "can_edit": True},
    },
    "HR_MANAGER": {
        "dashboard": {"can_view": True},
        "employees": {"can_view": True, "can_edit": True},
        "employees_list": {"can_view": True, "can_edit": True},
        "attendance": {"can_view": True, "can_approve": True},
        "attendance_approvals": {"can_view": True, "can_approve": True},
        "leave": {"can_view": True, "can_approve": True},
        "leave_applications": {"can_view": True},
        "leave_approvals": {"can_view": True, "can_approve": True},
        "reports": {"can_view": True},
    },
    "REPORTING_MANAGER": {
        "dashboard": {"can_view": True},
        "attendance": {"can_view": True, "can_approve": True},
        "attendance_approvals": {"can_view": True, "can_approve": True},
        "leave": {"can_view": True, "can_approve": True},
        "leave_approvals": {"can_view": True, "can_approve": True},
    },
    "ATTENDANCE_ADMIN": {
        "dashboard": {"can_view": True},
        "attendance": {"can_view": True, "can_edit": True, "can_approve": True, "can_export": True},
        "attendance_overview": {"can_view": True},
        "attendance_approvals": {"can_view": True, "can_approve": True},
        "attendance_swipe_logs": {"can_view": True, "can_edit": True},
    },
    "LEAVE_ADMIN": {
        "dashboard": {"can_view": True},
        "leave": {"can_view": True, "can_edit": True, "can_approve": True, "can_export": True},
        "leave_applications": {"can_view": True},
        "leave_approvals": {"can_view": True, "can_approve": True},
        "leave_policies": {"can_view": True, "can_edit": True},
        "leave_balances": {"can_view": True, "can_edit": True},
    },
    "EMPLOYEE": {
        "dashboard": {"can_view": True},
        "leave": {"can_view": True},
        "leave_applications": {"can_view": True},
        "attendance": {"can_view": True},
        "attendance_overview": {"can_view": True},
    },
}


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------


class Command(BaseCommand):
    help = "Seed RBAC: permissions, permission groups, menu items, and core roles for a tenant."

    def add_arguments(self, parser):
        parser.add_argument("--schema", type=str, help="Target tenant schema name")
        parser.add_argument("--all-tenants", action="store_true", help="Run for all tenants")
        parser.add_argument("--dry-run", action="store_true", help="Print what would be done without saving")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be saved.\n"))

        if options["all_tenants"]:
            TenantModel = get_tenant_model()
            for tenant in TenantModel.objects.exclude(schema_name="public"):
                self.stdout.write(f"\n=== Seeding tenant: {tenant.schema_name} ===")
                with tenant_context(tenant):
                    self._seed(dry_run)
        elif options.get("schema"):
            TenantModel = get_tenant_model()
            try:
                tenant = TenantModel.objects.get(schema_name=options["schema"])
            except TenantModel.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Tenant '{options['schema']}' not found."))
                return
            with tenant_context(tenant):
                self._seed(dry_run)
        else:
            # Run in current schema (useful for local dev with acme schema always active)
            self._seed(dry_run)

    def _seed(self, dry_run: bool):
        self._seed_permissions(dry_run)
        self._seed_permission_groups(dry_run)
        self._seed_menu_items(dry_run)
        self._seed_roles(dry_run)
        self.stdout.write(self.style.SUCCESS("  ✓ RBAC seeding complete."))

    # ---------------------------------------------------------------- permissions

    def _seed_permissions(self, dry_run: bool):
        from apps.security.models import Permission
        count = 0
        for module, action, resource, code, description in PERMISSIONS:
            if not dry_run:
                _, created = Permission.objects.update_or_create(
                    permission_code=code,
                    defaults={
                        "module": module,
                        "action": action,
                        "resource": resource,
                        "description": description,
                        "is_active": True,
                    },
                )
                if created:
                    count += 1
            else:
                self.stdout.write(f"  [DRY] Permission: {code}")
        if not dry_run:
            self.stdout.write(f"  Permissions: {count} created / {len(PERMISSIONS) - count} updated.")

    # ---------------------------------------------------------------- permission groups

    def _seed_permission_groups(self, dry_run: bool):
        from apps.security.models import Permission
        from apps.security.models.permission import PermissionGroup, GroupPermission

        for name, description, codes in PERMISSION_GROUPS:
            if dry_run:
                self.stdout.write(f"  [DRY] PermissionGroup: {name} ({len(codes)} perms)")
                continue

            group, _ = PermissionGroup.objects.update_or_create(
                group_name=name,
                company=None,  # global groups
                defaults={"description": description, "is_active": True},
            )
            # Rebuild permissions for this group
            GroupPermission.objects.filter(group=group).delete()
            perms = Permission.objects.filter(permission_code__in=codes)
            GroupPermission.objects.bulk_create(
                [GroupPermission(group=group, permission=p) for p in perms],
                ignore_conflicts=True,
            )
        if not dry_run:
            self.stdout.write(f"  PermissionGroups: {len(PERMISSION_GROUPS)} upserted.")

    # ---------------------------------------------------------------- menu items

    def _seed_menu_items(self, dry_run: bool):
        from apps.security.models import MenuItem

        # Two passes: roots first, children second
        roots = [(c, l, None, rp, ic, so) for c, l, p, rp, ic, so in MENU_ITEMS if p is None]
        children = [(c, l, p, rp, ic, so) for c, l, p, rp, ic, so in MENU_ITEMS if p is not None]

        for code, label, parent_code, route_path, icon, sort_order in roots + children:
            if dry_run:
                self.stdout.write(f"  [DRY] MenuItem: {code}")
                continue

            parent = None
            if parent_code:
                parent = MenuItem.objects.filter(code=parent_code).first()

            MenuItem.objects.update_or_create(
                code=code,
                defaults={
                    "label": label,
                    "parent": parent,
                    "route_path": route_path,
                    "icon": icon,
                    "sort_order": sort_order,
                    "is_active": True,
                },
            )
        if not dry_run:
            self.stdout.write(f"  MenuItems: {len(MENU_ITEMS)} upserted.")

    # ---------------------------------------------------------------- roles

    def _seed_roles(self, dry_run: bool):
        from apps.security.models import Role, RoleMenuPermission, DataScopeRule, MenuItem
        from apps.security.models.permission import PermissionGroup, RolePermissionGroup

        # Need a company to attach the role to
        try:
            from apps.employees.models import Company
            company = Company.objects.filter(is_active=True).first()
        except Exception:
            company = None

        if company is None:
            self.stdout.write(
                self.style.WARNING("  No active Company found — skipping role seed.")
            )
            return

        for role_def in CORE_ROLES:
            if dry_run:
                self.stdout.write(f"  [DRY] Role: {role_def['role_code']}")
                continue

            role, _ = Role.objects.update_or_create(
                company=company,
                role_code=role_def["role_code"],
                defaults={
                    "role_name": role_def["role_name"],
                    "description": role_def["description"],
                    "is_super_admin": role_def["is_super_admin"],
                    "is_active": True,
                },
            )

            # Assign permission groups
            RolePermissionGroup.objects.filter(role=role).delete()
            groups = PermissionGroup.objects.filter(
                group_name__in=role_def["permission_groups"]
            )
            RolePermissionGroup.objects.bulk_create(
                [RolePermissionGroup(role=role, group=g) for g in groups],
                ignore_conflicts=True,
            )

            # Set data scopes
            DataScopeRule.objects.filter(role=role).delete()
            DataScopeRule.objects.bulk_create(
                [
                    DataScopeRule(role=role, module=module, scope_type=scope)
                    for module, scope in role_def["data_scopes"].items()
                ],
                ignore_conflicts=True,
            )

            # Set menu permissions
            menu_perms = ROLE_MENU_PERMISSIONS.get(role_def["role_code"], {})
            RoleMenuPermission.objects.filter(role=role).delete()
            menu_items = {m.code: m for m in MenuItem.objects.filter(code__in=menu_perms.keys())}
            objs = []
            for code, flags in menu_perms.items():
                mi = menu_items.get(code)
                if mi:
                    objs.append(RoleMenuPermission(
                        role=role,
                        menu_item=mi,
                        can_view=flags.get("can_view", False),
                        can_edit=flags.get("can_edit", False),
                        can_export=flags.get("can_export", False),
                        can_import=flags.get("can_import", False),
                        can_approve=flags.get("can_approve", False),
                    ))
            RoleMenuPermission.objects.bulk_create(objs, ignore_conflicts=True)

        if not dry_run:
            self.stdout.write(f"  Roles: {len(CORE_ROLES)} upserted.")
