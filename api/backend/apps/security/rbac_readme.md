# Role Based Access Control (RBAC)

## Overview

This project uses a Role-Based Access Control (RBAC) system to control access to APIs and application features.

The RBAC implementation is based on the following hierarchy:

```text
Role
  └── Permission Group
          └── Permission
```

Example:

```text
HR_ADMIN
   ├── Employee - Full Management
   │      ├── employee.view_employee
   │      ├── employee.create_employee
   │      └── employee.update_employee
   │
   └── Leave - Full Management
          ├── leave.view_leave
          ├── leave.approve_leave
          └── leave.override_leave
```

---

# RBAC Database Structure

The RBAC system uses the following tables:

| Table                     | Purpose                    |
| ------------------------- | -------------------------- |
| mst_permission            | Stores all permissions     |
| mst_system_role           | Stores system roles        |
| sec_permission_group      | Groups related permissions |
| sec_group_permission      | Maps permissions to groups |
| sec_role_permission_group | Maps groups to roles       |
| employee_role_assignments | Assigns roles to employees |

---

# Permission Structure

A permission consists of:

```python
{
    "module": "LEAVE",
    "action": "view",
    "resource": "leave_application",
    "permission_code": "leave.view_leave",
    "description": "View leave applications"
}
```

### Permission Naming Convention

Always follow:

```text
<module>.<action>_<resource>
```

Examples:

```text
leave.view_leave
leave.approve_leave
leave.override_leave

employee.view_employee
employee.create_employee
employee.update_employee

attendance.view_attendance
attendance.approve_attendance
```

---

# Permission Groups

Permissions should never be assigned directly to Roles.

Instead:

```text
Permission
    ↓
Permission Group
    ↓
Role
```

Example:

```python
{
    "group_name": "Leave - Full Management",
    "permissions": [
        "leave.view_leave",
        "leave.approve_leave",
        "leave.reject_leave",
        "leave.override_leave"
    ]
}
```

This allows multiple roles to reuse the same group.

---

# Roles

Roles represent business responsibilities.

Examples:

```text
SUPER_ADMIN
HR_ADMIN
HR_MANAGER
PAYROLL_ADMIN
```

A role can contain multiple Permission Groups.

Example:

```python
ROLE_PERMISSION_GROUP_MAPPINGS = {
    "HR_ADMIN": [
        "Employee - Full Management",
        "Leave - Full Management",
        "Attendance - Full Management",
    ]
}
```

---

# JWT Integration

When a user logs in, their RBAC information is embedded into the JWT token.

The token contains:

```json
{
  "employee_id": "123",
  "roles": [
    "HR_ADMIN"
  ],
  "permissions": [
    "employee.view_employee",
    "employee.create_employee",
    "leave.view_leave",
    "leave.approve_leave"
  ]
}
```

This allows authorization checks without querying RBAC tables on every request.

Benefits:

* Faster API authorization
* Reduced database queries
* Stateless permission validation

---

# Protecting APIs

Every secured API must:

1. Require authentication.
2. Require RBAC permission validation.
3. Declare required permissions.

Example:

```python
from rest_framework.permissions import IsAuthenticated

class AdminLeaveApplicationListView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasRBACPermission
    ]

    required_permissions = [
        "leave.view_leave"
    ]

    def get(self, request):
        ...
```

---

## Multiple Permissions

```python
class LeaveApprovalView(APIView):
    permission_classes = [
        IsAuthenticated,
        HasRBACPermission
    ]

    required_permissions = [
        "leave.approve_leave"
    ]

    def post(self, request):
        ...
```

---

## Important

Every API that requires authorization MUST define:

```python
permission_classes = [
    IsAuthenticated,
    HasRBACPermission
]

required_permissions = [...]
```

Failure to define `required_permissions` may expose endpoints unintentionally.

---

# Adding a New Permission

Whenever a new feature is introduced, a corresponding permission must be created.

Example:

Suppose a new API allows exporting leave reports.

---

## Step 1: Add Permission

Update `PERMISSIONS_DATA` inside:

```text
apps/security/rbac_seed.py
```

Example:

```python
{
    "module": "LEAVE",
    "action": "export",
    "resource": "leave_report",
    "permission_code": "leave.export_leave_report",
    "description": "Export leave reports"
}
```

---

## Step 2: Add Permission to a Group

Locate the appropriate permission group.

Example:

```python
{
    "group_name": "Leave - Data Operations",
    "permissions": [
        "leave.export_leave",
        "leave.import_leave",
        "leave.export_leave_report"
    ]
}
```

If no suitable group exists, create a new permission group.

---

## Step 3: Assign Group to Roles

Update:

```python
ROLE_PERMISSION_GROUP_MAPPINGS
```

Example:

```python
"HR_ADMIN": [
    "Leave - Data Operations"
]
```

---

## Step 4: Reseed RBAC Data

Run:

```bash
python -m apps.security.rbac_seed
```

This will:

* Create new permissions
* Create missing groups
* Create missing roles
* Create role-group mappings

---

# Adding a New Permission Group

Example:

```python
{
    "group_name": "Leave - Reports",
    "description": "Leave reporting permissions",
    "permissions": [
        "leave.export_leave_report",
        "leave.view_leave_report"
    ]
}
```

Then map it to roles:

```python
ROLE_PERMISSION_GROUP_MAPPINGS = {
    "HR_ADMIN": [
        "Leave - Reports"
    ]
}
```

Reseed:

```bash
python -m apps.security.rbac_seed
```

---

# Adding a New Role

Add to:

```python
ROLES_DATA
```

Example:

```python
{
    "code": "LEAVE_ADMIN",
    "label": "Leave Administrator",
    "description": "Manage leave operations"
}
```

Then map groups:

```python
ROLE_PERMISSION_GROUP_MAPPINGS = {
    "LEAVE_ADMIN": [
        "Leave - Team View",
        "Leave - Full Management"
    ]
}
```

Reseed:

```bash
python -m apps.security.rbac_seed
```

---

# Assigning Roles to Employees

Roles are assigned through:

```text
employee_role_assignments
```

Example:

```python
employee_mapping = {
    "admin@company.com": "SUPER_ADMIN",
    "hr@company.com": "HR_ADMIN"
}
```

Then run:

```python
seed_rbac_data(
    employee_email_role_mapping=employee_mapping,
    schema_name="acme"
)
```

---

# Tenant Support

The RBAC seed script is tenant-aware.

Example:

```python
seed_rbac_data(schema_name="acme")
```

Internally:

```python
with schema_context(schema_name):
    ...
```

This ensures RBAC data is seeded within the correct tenant schema.

---

# Recommended Development Workflow

Whenever a new API is introduced:

### 1. Create permission

```python
leave.export_leave_report
```

### 2. Add permission to PERMISSIONS_DATA

### 3. Add permission to a Permission Group

### 4. Map group to appropriate Role(s)

### 5. Run RBAC seed

```bash
python -m apps.security.rbac_seed
```

### 6. Protect API

```python
permission_classes = [
    IsAuthenticated,
    HasRBACPermission
]

required_permissions = [
    "leave.export_leave_report"
]
```

### 7. Test with users having and lacking the permission

---

# Best Practices

### Do

✅ Reuse permission groups whenever possible

✅ Create granular permissions

✅ Protect every business API with RBAC

✅ Follow permission naming conventions

✅ Reseed RBAC after changes

---

### Don't

❌ Hardcode role names inside APIs

Bad:

```python
if request.user.role == "HR_ADMIN":
```

Good:

```python
required_permissions = [
    "leave.approve_leave"
]
```

---

❌ Assign permissions directly to users

Use:

```text
User
  → Role
      → Permission Group
          → Permission
```

---

❌ Skip permission checks on sensitive APIs

All protected APIs should use:

```python
HasRBACPermission
```

---

# Summary

The authorization flow is:

```text
Employee
    ↓
Assigned Role
    ↓
Permission Groups
    ↓
Permissions
    ↓
Embedded into JWT
    ↓
Validated by HasRBACPermission
    ↓
API Access Granted / Denied
```

For every new feature:

```text
Create Permission
    ↓
Add to Permission Group
    ↓
Assign Group to Role
    ↓
Run RBAC Seed
    ↓
Protect API using required_permissions
```

This ensures all authorization remains centralized, scalable, and consistent across the platform.
