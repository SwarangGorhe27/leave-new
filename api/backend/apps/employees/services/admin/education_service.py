"""
Education Details Service for Admin Side - Get and Edit Only.

Handles business logic for viewing and editing education records.
All queries use Django ORM for SQL injection protection.
"""

from typing import Dict, Any, Optional
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet

from apps.employees.models.education import EmployeeEducation
from apps.employees.models.employee import Employee


class EducationDetailsService:
    """Service class for education records GET and UPDATE operations."""
    
    @staticmethod
    def get_all_education_records(employee_id: str) -> QuerySet:
        """
        Fetch all education records for a specific employee.
        
        Args:
            employee_id (str): UUID of the employee
            
        Returns:
            QuerySet: All active education records with related masters loaded
            
        Note:
            Uses select_related() to prevent N+1 queries.
            SQL injection protected through Django ORM parametrized queries.
        """
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        
        return EmployeeEducation.objects.filter(
            employee=employee,
            is_active=True
        ).select_related(
            'education_level',
            'qualification',
            'specialization',
            'board',
            'study_mode',
            'education_status',
            'verified_by'
        ).order_by('sort_order', '-created_at')
    
    @staticmethod
    @transaction.atomic
    def update_education_record(
        employee_id: str,
        education_id: str,
        validated_data: Dict[str, Any],
        updated_by: Optional[Any] = None
    ) -> EmployeeEducation:
        """
        Update an existing education record.
        
        Args:
            employee_id (str): UUID of the employee
            education_id (str): UUID of the education record to update
            validated_data (Dict): Validated updated data from serializer
            updated_by: User object who updated the record
            
        Returns:
            EmployeeEducation: Updated education record object
            
        Note:
            Uses @transaction.atomic to ensure data consistency.
            All validations done by serializer before this point.
        """
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        
        education_record = get_object_or_404(
            EmployeeEducation,
            id=education_id,
            employee=employee,
            is_active=True
        )
        
        # Update fields
        for field, value in validated_data.items():
            setattr(education_record, field, value)
        
        education_record.save()
        
        return education_record
