import uuid
from django.db import models, transaction
from apps.attendance.models.requests import AttendanceRequest, ApprovalWorkflow, RegularizationRequest
from apps.attendance.services.admin.requests.unified_requests import (
    get_regularization_queryset,
    regularization_to_request_dict,
    resolve_acting_employee,
    resolve_regularization,
    user_has_company_wide_requests_access,
)
from apps.attendance.services.regularization_service import RegularizationRequestService
from apps.core.temp_admin_access import user_has_temp_attendance_admin_access
from apps.employees.models.employee import Employee
from apps.employees.models.reporting import EmployeeReportingRelationship

class AttendanceRequestsService:
    @staticmethod
    def get_requests_queryset(user):
        """
        Enforce Role-Based Access Control (RBAC):
        - Admin (is_staff): All requests.
        - Manager (has reports): Own requests + direct reports' requests.
        - Employee: Only their own requests.
        """
        if not user.is_authenticated:
            return AttendanceRequest.objects.none()

        # Staff / HR admin roles see all company requests (incl. hr.admin + HR_ADMIN).
        if user_has_company_wide_requests_access(user):
            return AttendanceRequest.objects.select_related(
                "employee",
                "employee__employment_details",
                "employee__employment_details__department",
                "employee__employment_details__designation",
            ).order_by("-created_at")

        employee = getattr(user, "employee_profile", None)
        if not employee:
            return AttendanceRequest.objects.none()
            
        team_employee_ids = EmployeeReportingRelationship.objects.filter(
            reports_to_employee=employee,
            relationship_type="PRIMARY",
            is_active=True
        ).values_list("employee_id", flat=True)
        
        if team_employee_ids.exists():
            return AttendanceRequest.objects.filter(
                models.Q(employee=employee) | models.Q(employee_id__in=team_employee_ids)
            ).order_by('-created_at')
            
        return AttendanceRequest.objects.filter(employee=employee).order_by('-created_at')

    @staticmethod
    @transaction.atomic
    def create_request(user, validated_data):
        employee = getattr(user, 'employee_profile', None)
        if not employee:
            raise ValueError("Authenticated user does not have an employee profile.")
            
        validated_data['employee'] = employee
        validated_data.pop('employee_id', None)
        
        request_obj = AttendanceRequest.objects.create(**validated_data)
        return request_obj

    @staticmethod
    @transaction.atomic
    def approve_request(user, request_obj, comment="", stage=None):
        employee = getattr(user, 'employee_profile', None)
        if not employee:
            raise ValueError("Authenticated user does not have an employee profile.")
            
        if not stage:
            stage = (
                'admin'
                if user_has_company_wide_requests_access(user)
                else 'manager'
            )
            
        if stage == 'manager':
            request_obj.manager_status = 'approved'
            request_obj.final_status = 'pending_admin_approval'
        elif stage == 'admin':
            request_obj.final_status = 'fully_approved'
            
        request_obj.save()
        
        ApprovalWorkflow.objects.create(
            request=request_obj,
            approver=employee,
            stage=stage,
            status='approved',
            comment=comment
        )
        return request_obj

    @staticmethod
    @transaction.atomic
    def reject_request(user, request_obj, comment="", stage=None):
        employee = getattr(user, 'employee_profile', None)
        if not employee:
            raise ValueError("Authenticated user does not have an employee profile.")
            
        if not stage:
            stage = (
                'admin'
                if user_has_company_wide_requests_access(user)
                else 'manager'
            )
            
        if stage == 'manager':
            request_obj.manager_status = 'rejected'
            
        request_obj.final_status = 'rejected'
        request_obj.save()
        
        ApprovalWorkflow.objects.create(
            request=request_obj,
            approver=employee,
            stage=stage,
            status='rejected',
            comment=comment
        )
        return request_obj

    @staticmethod
    def get_dashboard_stats(user, company_id=None, query_params=None):
        qs = AttendanceRequestsService.get_requests_queryset(user)
        if company_id:
            try:
                uuid.UUID(str(company_id))
                qs = qs.filter(employee__company_id=company_id)
            except ValueError:
                pass

        params = query_params or {}
        if company_id and "company_id" not in params:
            params = {**params, "company_id": company_id}
        reg_qs = get_regularization_queryset(user, params)

        return {
            'pending_requests': (
                qs.filter(manager_status='pending').count()
                + reg_qs.filter(status='PENDING').count()
            ),
            'approved_by_manager': qs.filter(manager_status='approved').count(),
            'pending_admin': (
                qs.filter(final_status='pending_admin_approval').count()
                + reg_qs.filter(status='PENDING').count()
            ),
            'fully_approved': (
                qs.filter(final_status='fully_approved').count()
                + reg_qs.filter(status='APPROVED').count()
            ),
            'rejected': (
                qs.filter(final_status='rejected').count()
                + reg_qs.filter(status='REJECTED').count()
            ),
        }

    @staticmethod
    def list_unified_requests(user, query_params, attendance_queryset, http_request=None):
        from apps.attendance.serializers.admin.requests import AttendanceRequestSerializer

        att_serializer_data = AttendanceRequestSerializer(
            attendance_queryset,
            many=True,
            context={"request": http_request},
        ).data

        reg_rows = [
            regularization_to_request_dict(r)
            for r in get_regularization_queryset(user, query_params)
        ]
        merged = list(att_serializer_data) + reg_rows
        merged.sort(key=lambda row: row.get("created_at") or "", reverse=True)
        return merged

    @staticmethod
    def approve_regularization(user, reg_request, comment=""):
        actor = resolve_acting_employee(user, reg_request.company_id)
        if not actor:
            raise ValueError("Authenticated user does not have an employee profile for approval.")
        return RegularizationRequestService.approve(
            acting_employee=actor,
            reg_request=reg_request,
            remarks=comment or "",
        )

    @staticmethod
    def reject_regularization(user, reg_request, comment=""):
        actor = resolve_acting_employee(user, reg_request.company_id)
        if not actor:
            raise ValueError("Authenticated user does not have an employee profile for approval.")
        return RegularizationRequestService.reject(
            acting_employee=actor,
            reg_request=reg_request,
            remarks=comment or "",
        )

    @staticmethod
    def try_resolve_regularization(pk):
        return resolve_regularization(pk)
