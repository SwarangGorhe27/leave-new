from datetime import date

from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.employees.models.employee import Employee
from apps.security.models.role import Role, EmployeeRoleAssignment
from apps.employees.models.masters.organization import Company
# from apps.employees.models.roles import EmployeeRoleAssignment
from apps.employees.serializers.admin.role_mapping_serializer import ACCESS_LEVELS, EMPLOYEE_SOURCES

SystemRole = Role


def actor_employee(user):
    return getattr(user, "employee_profile", None)


def company_from_request(request):
    employee = actor_employee(request.user)
    if employee and getattr(employee, "company_id", None):
        return employee.company
    company_id = request.query_params.get("company_id")
    if not company_id and request.method not in {"GET", "HEAD", "OPTIONS"}:
        company_id = request.data.get("company_id")
    if not company_id:
        raise ValidationError({"company_id": "company_id is required for admin users without employee profile."})
    return get_object_or_404(Company, id=company_id, is_active=True)


class RoleMappingService:
    @staticmethod
    def option_payload(company):
        roles = RoleMappingService.role_queryset(company)
        return {
            "accessLevels": [
                {"value": value, "label": label}
                for value, label in ACCESS_LEVELS.items()
            ],
            "employeeSources": [
                {"value": value, "label": label}
                for value, label in EMPLOYEE_SOURCES.items()
            ],
            "roles": roles,
        }

    @staticmethod
    def role_queryset(company):
        return (
            SystemRole.objects.filter(is_active=True)
            .annotate(
                activeUsers=Count(
                    "emp_role_assignments",
                    filter=Q(
                        emp_role_assignments__company=company,
                        emp_role_assignments__is_active=True,
                    ),
                    distinct=True,
                )
            )
            .order_by("label")
        )

    @staticmethod
    def get_role(role_id):
        return get_object_or_404(SystemRole, id=role_id, is_active=True)

    @staticmethod
    def create_role(data):
        code = data["code"]
        if SystemRole.objects.filter(code__iexact=code).exists():
            raise ValidationError({"code": "Role code already exists."})
        return SystemRole.objects.create(
            code=code,
            label=data["roleName"],
            description=data.get("description"),
            access_level=data["accessLevel"],
            is_custom=True,
        )

    @staticmethod
    def update_role(role_id, data):
        role = RoleMappingService.get_role(role_id)
        if not role.is_custom:
            raise ValidationError({"role": "Only custom roles can be edited."})
        code = data.get("code", role.code)
        if SystemRole.objects.filter(code__iexact=code).exclude(id=role.id).exists():
            raise ValidationError({"code": "Role code already exists."})
        role.code = code
        role.label = data.get("roleName", role.label)
        role.description = data.get("description", role.description)
        role.access_level = data.get("accessLevel", role.access_level)
        role.save()
        return role

    @staticmethod
    def delete_role(company, role_id):
        role = RoleMappingService.get_role(role_id)
        active_count = EmployeeRoleAssignment.objects.filter(
            company=company,
            role=role,
            is_active=True,
        ).count()
        if active_count:
            raise ValidationError({"role": "Cannot delete a role with active users. Revoke assignments first."})
        if not role.is_custom:
            raise ValidationError({"role": "System roles cannot be deleted."})
        role.is_active = False
        role.save(update_fields=["is_active", "updated_at"])

    @staticmethod
    def employee_queryset(company, params):
        active_assignments = (
            EmployeeRoleAssignment.objects.filter(is_active=True)
            .select_related("role")
            .order_by("role__label")
        )
        queryset = (
            Employee.objects.filter(company=company, is_active=True)
            .select_related(
                "employment_details__department",
                "employment_details__designation",
            )
            .prefetch_related(
                Prefetch(
                    "role_assignments",
                    queryset=active_assignments,
                    to_attr="prefetched_active_role_assignments",
                )
            )
            .order_by("employee_code", "first_name")
        )
        source = (params.get("source") or params.get("status") or "CURRENT").strip().upper()
        if source not in {"CURRENT", "PAST", "ALL"}:
            raise ValidationError({"source": "Use CURRENT, PAST, or ALL."})
        if source == "CURRENT":
            queryset = queryset.filter(status=Employee.StatusChoices.ACTIVE)
        elif source == "PAST":
            queryset = queryset.exclude(status=Employee.StatusChoices.ACTIVE)
        search = (params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(
                Q(employee_code__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(employment_details__department__name__icontains=search)
                | Q(employment_details__designation__title__icontains=search)
            )
        role_id = params.get("role_id") or params.get("roleId")
        if role_id:
            queryset = queryset.filter(role_assignments__role_id=role_id, role_assignments__is_active=True)
        return queryset.distinct()

    @staticmethod
    def get_employee(company, employee_id):
        return get_object_or_404(
            Employee.objects.select_related(
                "employment_details__department",
                "employment_details__designation",
            ),
            id=employee_id,
            company=company,
            is_active=True,
        )

    @staticmethod
    def employee_assignments(company, employee_id):
        employee = RoleMappingService.get_employee(company, employee_id)
        assignments = (
            EmployeeRoleAssignment.objects.filter(employee=employee, company=company, is_active=True)
            .select_related("role", "employee", "company", "assigned_by")
            .order_by("role__label")
        )
        return employee, assignments

    @staticmethod
    def assign_role(company, employee_id, data, user=None):
        employee = RoleMappingService.get_employee(company, employee_id)
        role = RoleMappingService.get_role(data["roleId"])
        if EmployeeRoleAssignment.objects.filter(
            employee=employee,
            company=company,
            role=role,
            is_active=True,
        ).exists():
            raise ValidationError({"roleId": "This employee already has this active role."})
        with transaction.atomic():
            assignment = EmployeeRoleAssignment.objects.create(
                employee=employee,
                company=company,
                role=role,
                assigned_by=actor_employee(user),
                effective_from=data.get("effectiveFrom") or date.today(),
                effective_to=data.get("effectiveTo"),
            )
        return assignment

    @staticmethod
    def sync_employee_roles(company, employee_id, data, user=None):
        employee = RoleMappingService.get_employee(company, employee_id)
        role_ids = data.get("roleIds", [])
        roles = list(SystemRole.objects.filter(id__in=role_ids, is_active=True))
        found_role_ids = {role.id for role in roles}
        missing_role_ids = [str(role_id) for role_id in role_ids if role_id not in found_role_ids]
        if missing_role_ids:
            raise ValidationError({"roleIds": f"Invalid role ids: {', '.join(missing_role_ids)}"})

        current_assignments = list(
            EmployeeRoleAssignment.objects.filter(
                employee=employee,
                company=company,
                is_active=True,
            ).select_related("role")
        )
        current_by_role_id = {assignment.role_id: assignment for assignment in current_assignments}
        requested_role_ids = set(found_role_ids)
        actor = actor_employee(user)

        with transaction.atomic():
            for assignment in current_assignments:
                if assignment.role_id not in requested_role_ids:
                    assignment.is_active = False
                    assignment.revoked_by = actor
                    assignment.revoked_at = timezone.now()
                    assignment.revoke_reason = "Role mapping updated."
                    assignment.save(
                        update_fields=[
                            "is_active",
                            "revoked_by",
                            "revoked_at",
                            "revoke_reason",
                            "updated_at",
                        ]
                    )

            for role in roles:
                if role.id in current_by_role_id:
                    continue
                EmployeeRoleAssignment.objects.create(
                    employee=employee,
                    company=company,
                    role=role,
                    assigned_by=actor,
                    effective_from=data.get("effectiveFrom") or date.today(),
                    effective_to=data.get("effectiveTo"),
                )

        return (
            EmployeeRoleAssignment.objects.filter(employee=employee, company=company, is_active=True)
            .select_related("role", "employee", "company", "assigned_by")
            .order_by("role__label")
        )

    @staticmethod
    def revoke_assignment(company, assignment_id, data=None, user=None):
        assignment = get_object_or_404(
            EmployeeRoleAssignment.objects.select_related("employee", "company", "role"),
            id=assignment_id,
            company=company,
            is_active=True,
        )
        with transaction.atomic():
            assignment.is_active = False
            assignment.revoked_by = actor_employee(user)
            assignment.revoked_at = timezone.now()
            assignment.revoke_reason = (data or {}).get("revokeReason")
            assignment.save(update_fields=["is_active", "revoked_by", "revoked_at", "revoke_reason", "updated_at"])
        return assignment
