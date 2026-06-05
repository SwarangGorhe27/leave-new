"""
Leave Type Service
Handles all operations related to leave types (master data).
"""
from typing import Any, Dict, List, Optional
from django.db.models import Q, QuerySet
from rest_framework.exceptions import ValidationError, NotFound
from ..models.masters.leave_types import LeaveType
from .base_service import BaseLeaveService


class LeaveTypeService(BaseLeaveService):
    """
    Service for managing leave types.
    
    Operations:
    - Get all leave types
    - Get leave type by ID
    - Create leave type
    - Update leave type
    - Delete leave type (soft delete)
    - Filter by criteria
    """

    def list_all(self, active_only: bool = True):
        return self.get_all_leave_types(is_active=active_only)

    def create(self, data: Dict[str, Any]):
        return self.create_leave_type(data)

    def update(self, pk, data: Dict[str, Any]):
        return self.update_leave_type(str(pk), data)

    def deactivate(self, pk):
        self.soft_delete_leave_type(str(pk))

    @staticmethod
    def get_all_leave_types(filters: Optional[Dict[str, Any]] = None, 
                          is_active: bool = True) -> QuerySet:
        """
        Get all leave types with optional filters.
        
        Args:
            filters: Optional dictionary with filter criteria
            is_active: Only return active leave types
            
        Returns:
            QuerySet of LeaveType objects
        """
        queryset = LeaveType.objects.all()
        
        if is_active:
            queryset = queryset.filter(is_active=True)
        
        if filters:
            if 'code' in filters:
                queryset = queryset.filter(code__icontains=filters['code'])
            if 'name' in filters:
                queryset = queryset.filter(name__icontains=filters['name'])
            if 'employee_type_id' in filters:
                queryset = queryset.filter(employee_type_id=filters['employee_type_id'])
        
        return queryset.order_by('code')

    @staticmethod
    def get_leave_type_by_id(leave_type_id: str) -> LeaveType:
        """
        Get leave type by ID.
        
        Args:
            leave_type_id: UUID of leave type
            
        Returns:
            LeaveType object
            
        Raises:
            NotFound: If leave type doesn't exist
        """
        try:
            return LeaveType.objects.get(id=leave_type_id, is_active=True)
        except LeaveType.DoesNotExist:
            raise NotFound(f"Leave type with ID {leave_type_id} not found.")

    @staticmethod
    def create_leave_type(data: Dict[str, Any]) -> LeaveType:
        """
        Create a new leave type.
        
        Args:
            data: Dictionary containing leave type data
                - code (required): Code for leave type
                - name (required): Name of leave type
                - max_days_per_year (required): Maximum days allowed per year
                - description (optional): Description
                - employee_type_id (optional): Employee type applicability
                - carry_forward_enabled (optional): Allow carry forward
                - max_carry_forward_days (optional): Max carry forward limit
                - encashable (optional): Can be encashed
                - requires_attachment (optional): Requires documents
                - attachment_threshold_days (optional): Days after which attachment required
                - min_notice_days (optional): Minimum notice period
                - applicable_gender (optional): Gender applicability
                
        Returns:
            Created LeaveType object
            
        Raises:
            ValidationError: If data is invalid
        """
        required_fields = ['code', 'name', 'max_days_per_year']
        BaseLeaveService.validate_required_fields(data, required_fields)
        
        # Validate code uniqueness
        if LeaveType.objects.filter(code=data['code']).exists():
            raise ValidationError({'code': 'A leave type with this code already exists.'})
        
        # Validate numeric fields
        try:
            if float(data['max_days_per_year']) < 0:
                raise ValidationError({'max_days_per_year': 'Must be a positive number.'})
        except (ValueError, TypeError):
            raise ValidationError({'max_days_per_year': 'Must be a valid number.'})
        
        try:
            leave_type = LeaveType.objects.create(
                code=data['code'],
                name=data['name'],
                description=data.get('description'),
                max_days_per_year=data['max_days_per_year'],
                employee_type_id=data.get('employee_type_id'),
                carry_forward_enabled=data.get('carry_forward_enabled', False),
                max_carry_forward_days=data.get('max_carry_forward_days'),
                encashable=data.get('encashable', False),
                requires_attachment=data.get('requires_attachment', False),
                attachment_threshold_days=data.get('attachment_threshold_days', 2),
                min_notice_days=data.get('min_notice_days', 0),
                applicable_gender=data.get('applicable_gender', 'all'),
                is_active=True
            )
            return leave_type
        except Exception as e:
            raise ValidationError(f"Error creating leave type: {str(e)}")

    @staticmethod
    def update_leave_type(leave_type_id: str, data: Dict[str, Any]) -> LeaveType:
        """
        Update leave type.
        
        Args:
            leave_type_id: UUID of leave type to update
            data: Dictionary with fields to update
            
        Returns:
            Updated LeaveType object
            
        Raises:
            NotFound: If leave type doesn't exist
            ValidationError: If data is invalid
        """
        leave_type = LeaveTypeService.get_leave_type_by_id(leave_type_id)
        
        # Validate code uniqueness if code is being changed
        if 'code' in data and data['code'] != leave_type.code:
            if LeaveType.objects.filter(code=data['code']).exists():
                raise ValidationError({'code': 'A leave type with this code already exists.'})
        
        # Update fields
        updateable_fields = [
            'code', 'name', 'description', 'max_days_per_year',
            'carry_forward_enabled', 'max_carry_forward_days',
            'encashable', 'requires_attachment', 'attachment_threshold_days',
            'min_notice_days', 'applicable_gender'
        ]
        
        for field in updateable_fields:
            if field in data:
                setattr(leave_type, field, data[field])
        
        try:
            leave_type.save()
            return leave_type
        except Exception as e:
            raise ValidationError(f"Error updating leave type: {str(e)}")

    @staticmethod
    def soft_delete_leave_type(leave_type_id: str) -> None:
        """
        Soft delete a leave type.
        
        Args:
            leave_type_id: UUID of leave type to delete
            
        Raises:
            NotFound: If leave type doesn't exist
            ValidationError: If leave type is still in use
        """
        leave_type = LeaveTypeService.get_leave_type_by_id(leave_type_id)
        
        # Check if leave type has active requests
        from ..models.transactions.leave_requests import LeaveRequest
        active_requests = LeaveRequest.objects.filter(
            leave_type=leave_type,
            status__in=['pending', 'approved']
        ).exists()
        
        if active_requests:
            raise ValidationError(
                'Cannot delete leave type with active requests. Cancel pending requests first.'
            )
        
        leave_type.is_active = False
        leave_type.save()

    @staticmethod
    def restore_leave_type(leave_type_id: str) -> LeaveType:
        """
        Restore a soft-deleted leave type.
        
        Args:
            leave_type_id: UUID of leave type to restore
            
        Returns:
            Restored LeaveType object
        """
        try:
            leave_type = LeaveType.objects.get(id=leave_type_id, is_active=False)
            leave_type.is_active = True
            leave_type.save()
            return leave_type
        except LeaveType.DoesNotExist:
            raise NotFound(f"Inactive leave type with ID {leave_type_id} not found.")
