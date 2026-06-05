"""
Leave Policy Service
Handles operations related to leave policies and policy management.
"""
from typing import Any, Dict, List, Optional
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError, NotFound
from ..models.masters.leave_policy import LeavePolicy, EmployeeLeavePolicy, LeavePolicyRule
from .base_service import BaseLeaveService


class LeavePolicyService(BaseLeaveService):
    """
    Service for managing leave policies.
    
    Operations:
    - Get all policies
    - Get policy by ID
    - Create policy
    - Update policy
    - Assign policy to employees
    - Get employee's applicable policy
    """

    @staticmethod
    def get_all_policies(is_active: bool = True) -> QuerySet:
        """
        Get all leave policies.
        
        Args:
            is_active: Filter by active status
            
        Returns:
            QuerySet of LeavePolicy objects
        """
        queryset = LeavePolicy.objects.all()
        
        if is_active:
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('name')

    @staticmethod
    def get_policy_by_id(policy_id: str) -> LeavePolicy:
        """
        Get leave policy by ID.
        
        Args:
            policy_id: UUID of policy
            
        Returns:
            LeavePolicy object
            
        Raises:
            NotFound: If policy doesn't exist
        """
        try:
            return LeavePolicy.objects.get(id=policy_id, is_active=True)
        except LeavePolicy.DoesNotExist:
            raise NotFound(f"Leave policy {policy_id} not found.")

    @staticmethod
    def create_policy(data: Dict[str, Any]) -> LeavePolicy:
        """
        Create a new leave policy.
        
        Args:
            data: Dictionary containing policy data
                - name (required): Policy name
                - description (optional): Description
                - employee_type_id (optional): Applicable employee type
                - rules (optional): List of policy rules
                
        Returns:
            Created LeavePolicy object
            
        Raises:
            ValidationError: If data is invalid
        """
        required_fields = ['name']
        BaseLeaveService.validate_required_fields(data, required_fields)
        
        if LeavePolicy.objects.filter(name=data['name']).exists():
            raise ValidationError({'name': 'A policy with this name already exists.'})
        
        try:
            policy = LeavePolicy.objects.create(
                name=data['name'],
                description=data.get('description'),
                is_active=True
            )
            
            # Add rules if provided
            if 'rules' in data:
                for rule_data in data['rules']:
                    LeavePolicyRule.objects.create(
                        policy=policy,
                        leave_type_id=rule_data.get('leave_type_id'),
                        grade_id=rule_data.get('grade_id'),
                        employee_type_id=rule_data.get('employee_type_id'),
                        probation_restricted=rule_data.get('probation_restricted', False),
                        notice_period_restricted=rule_data.get('notice_period_restricted', False),
                        sandwich_policy_enabled=rule_data.get('sandwich_policy_enabled', False),
                        min_service_days=rule_data.get('min_service_days', 0),
                        max_leaves_per_month=rule_data.get('max_leaves_per_month'),
                        max_leaves_per_quarter=rule_data.get('max_leaves_per_quarter'),
                        min_gap_between_leaves_days=rule_data.get('min_gap_between_leaves_days'),
                        accrual_enabled=rule_data.get('accrual_enabled', False),
                        accrual_frequency=rule_data.get('accrual_frequency'),
                        accrual_days=rule_data.get('accrual_days'),
                        accrual_proration=rule_data.get('accrual_proration', True),
                        accrual_proration_basis=rule_data.get('accrual_proration_basis'),
                        rounding_rule=rule_data.get('rounding_rule'),
                        allow_negative_balance=rule_data.get('allow_negative_balance', False),
                        negative_balance_cap=rule_data.get('negative_balance_cap'),
                        short_leave_monthly_cap=rule_data.get('short_leave_monthly_cap', 0),
                    )
            
            return policy
            
        except Exception as e:
            raise ValidationError(f"Error creating policy: {str(e)}")

    @staticmethod
    def update_policy(policy_id: str, data: Dict[str, Any]) -> LeavePolicy:
        """
        Update a leave policy.
        
        Args:
            policy_id: UUID of policy
            data: Dictionary with fields to update
            
        Returns:
            Updated LeavePolicy object
            
        Raises:
            NotFound: If policy doesn't exist
            ValidationError: If data is invalid
        """
        policy = LeavePolicyService.get_policy_by_id(policy_id)
        
        # Check name uniqueness if being changed
        if 'name' in data and data['name'] != policy.name:
            if LeavePolicy.objects.filter(name=data['name']).exists():
                raise ValidationError({'name': 'A policy with this name already exists.'})
        
        updateable_fields = ['name', 'description']
        
        for field in updateable_fields:
            if field in data:
                setattr(policy, field, data[field])
        
        try:
            policy.save()
            return policy
        except Exception as e:
            raise ValidationError(f"Error updating policy: {str(e)}")

    @staticmethod
    def assign_policy_to_employee(employee_id: str, policy_id: str,
                                 effective_date: Optional[str] = None) -> EmployeeLeavePolicy:
        """
        Assign a leave policy to an employee.
        
        Args:
            employee_id: UUID of employee
            policy_id: UUID of policy
            effective_date: Date from which policy is effective (optional)
            
        Returns:
            Created EmployeeLeavePolicy object
            
        Raises:
            NotFound: If employee or policy doesn't exist
        """
        policy = LeavePolicyService.get_policy_by_id(policy_id)
        
        # Check if already assigned
        existing = EmployeeLeavePolicy.objects.filter(
            employee_id=employee_id,
            policy=policy,
            end_date__isnull=True
        ).first()
        
        if existing:
            raise ValidationError(
                f"Employee already has this policy assigned."
            )
        
        try:
            from datetime import datetime
            eff_date = datetime.strptime(effective_date, '%Y-%m-%d').date() if effective_date else None
            
            assignment = EmployeeLeavePolicy.objects.create(
                employee_id=employee_id,
                policy=policy,
                start_date=eff_date
            )
            return assignment
        except Exception as e:
            raise ValidationError(f"Error assigning policy: {str(e)}")

    @staticmethod
    def get_employee_policy(employee_id: str) -> LeavePolicy:
        """
        Get the applicable leave policy for an employee.
        
        Args:
            employee_id: UUID of employee
            
        Returns:
            LeavePolicy object
            
        Raises:
            NotFound: If no policy is assigned
        """
        try:
            assignment = EmployeeLeavePolicy.objects.filter(
                employee_id=employee_id,
                end_date__isnull=True
            ).select_related('policy').first()
            
            if assignment:
                return assignment.policy
            
            # Fallback to default/first active policy
            default_policy = LeavePolicy.objects.filter(is_active=True).first()
            if default_policy:
                return default_policy
            
            raise NotFound("No leave policy assigned to this employee.")
        except Exception as e:
            raise ValidationError(f"Error fetching employee policy: {str(e)}")

    @staticmethod
    def get_policy_rules(policy_id: str) -> QuerySet:
        """
        Get all rules for a policy.
        
        Args:
            policy_id: UUID of policy
            
        Returns:
            QuerySet of LeavePolicyRule objects
        """
        policy = LeavePolicyService.get_policy_by_id(policy_id)
        return LeavePolicyRule.objects.filter(policy=policy, is_active=True)
