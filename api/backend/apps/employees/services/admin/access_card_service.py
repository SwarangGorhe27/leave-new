"""
Access Card Service for Admin Side.

Handles business logic for viewing, creating, updating, and deleting access cards.
All queries use Django ORM for SQL injection protection.
Comprehensive error handling and validation.
"""

from typing import Dict, Any, Optional, List
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from datetime import date

from apps.employees.models.access import EmployeeAccessCard
from apps.employees.models.employee import Employee
from apps.employees.models.masters.location import OfficeLocation


class AccessCardService:
    """Service class for access card CRUD operations with comprehensive business logic."""
    
    @staticmethod
    def get_all_access_cards(employee_id: str) -> QuerySet:
        """
        Fetch all access cards for a specific employee.
        
        Args:
            employee_id (str): UUID of the employee
            
        Returns:
            QuerySet: All active access cards
            
        Note:
            Uses select_related() to prevent N+1 queries.
            SQL injection protected through Django ORM parametrized queries.
        
        Raises:
            Employee.DoesNotExist: If employee not found
        """
        employee = get_object_or_404(Employee, id=employee_id)
        
        return EmployeeAccessCard.objects.filter(
            employee=employee,
            is_active=True
        ).select_related('employee').order_by('-created_at')
    
    @staticmethod
    @transaction.atomic
    def create_access_card(
        employee_id: str,
        validated_data: Dict[str, Any],
        created_by: Optional[Any] = None
    ) -> EmployeeAccessCard:
        """
        Create a new access card for an employee.
        
        Args:
            employee_id (str): UUID of the employee
            validated_data (Dict): Validated data from serializer
                - access_card_number (str): Card number
                - from_date (date): Issuance date
                - to_date (date, optional): Expiry date
            created_by: User object who created the record
            
        Returns:
            EmployeeAccessCard: Created access card object
            
        Note:
            Uses @transaction.atomic to ensure data consistency.
            All validations done by serializer before this point.
        
        Raises:
            Employee.DoesNotExist: If employee not found
        """
        employee = get_object_or_404(Employee, id=employee_id)

        # Determine office_location to satisfy DB NOT NULL if present in schema.
        # Prefer headquarter, else first active office, else leave NULL.
        office_location = None
        try:
            office_location = OfficeLocation.objects.filter(is_headquarter=True, is_active=True).first()
            if not office_location:
                office_location = OfficeLocation.objects.filter(is_active=True).first()
        except Exception:
            office_location = None

        access_card = EmployeeAccessCard.objects.create(
            employee=employee,
            card_number=validated_data.get('access_card_number'),
            issued_date=validated_data.get('from_date'),
            expiry_date=validated_data.get('to_date'),
            office_location=office_location,
            is_active=True
        )
        
        return access_card
    
    @staticmethod
    @transaction.atomic
    def update_access_card(
        employee_id: str,
        card_id: str,
        validated_data: Dict[str, Any],
        updated_by: Optional[Any] = None
    ) -> EmployeeAccessCard:
        """
        Update an existing access card's details.
        
        Args:
            employee_id (str): UUID of the employee
            card_id (str): UUID of the access card to update
            validated_data (Dict): Validated updated data from serializer
                - access_card_number (str, optional): New card number
                - from_date (date, optional): New from date
                - to_date (date, optional): New to date
                - is_active (bool, optional): Active status
            updated_by: User object who updated the record
            
        Returns:
            EmployeeAccessCard: Updated access card object
            
        Note:
            Uses @transaction.atomic to ensure data consistency.
            All validations done by serializer before this point.
        
        Raises:
            Employee.DoesNotExist: If employee not found
            EmployeeAccessCard.DoesNotExist: If card not found
        """
        employee = get_object_or_404(Employee, id=employee_id)
        
        access_card = get_object_or_404(
            EmployeeAccessCard,
            id=card_id,
            employee=employee,
            is_active=True
        )
        
        # Update fields only if provided. Accept either API keys or model keys.
        update_fields = []

        # card number
        if 'access_card_number' in validated_data:
            access_card.card_number = validated_data['access_card_number']
            update_fields.append('card_number')
        elif 'card_number' in validated_data:
            access_card.card_number = validated_data['card_number']
            update_fields.append('card_number')

        # issued / from date
        if 'from_date' in validated_data:
            access_card.issued_date = validated_data['from_date']
            update_fields.append('issued_date')
        elif 'issued_date' in validated_data:
            access_card.issued_date = validated_data['issued_date']
            update_fields.append('issued_date')

        # expiry / to date
        if 'to_date' in validated_data:
            access_card.expiry_date = validated_data['to_date']
            update_fields.append('expiry_date')
        elif 'expiry_date' in validated_data:
            access_card.expiry_date = validated_data['expiry_date']
            update_fields.append('expiry_date')

        # is_active
        if 'is_active' in validated_data:
            access_card.is_active = validated_data['is_active']
            update_fields.append('is_active')

        if update_fields:
            access_card.save(update_fields=update_fields)
        
        return access_card
    
    @staticmethod
    @transaction.atomic
    def deactivate_access_card(employee_id: str, card_id: str) -> EmployeeAccessCard:
        """
        Soft delete (deactivate) an access card.
        
        Args:
            employee_id (str): UUID of the employee
            card_id (str): UUID of the access card to deactivate
            
        Returns:
            EmployeeAccessCard: Deactivated access card object
            
        Note:
            Soft delete by marking is_active=False
            Uses @transaction.atomic to ensure data consistency.
        
        Raises:
            Employee.DoesNotExist: If employee not found
            EmployeeAccessCard.DoesNotExist: If card not found
        """
        employee = get_object_or_404(Employee, id=employee_id)
        
        access_card = get_object_or_404(
            EmployeeAccessCard,
            id=card_id,
            employee=employee,
            is_active=True
        )
        
        access_card.is_active = False
        access_card.save(update_fields=['is_active'])
        
        return access_card
    
    @staticmethod
    def get_access_card_by_id(employee_id: str, card_id: str) -> EmployeeAccessCard:
        """
        Fetch a specific access card by ID.
        
        Args:
            employee_id (str): UUID of the employee
            card_id (str): UUID of the access card
            
        Returns:
            EmployeeAccessCard: Access card object
            
        Note:
            SQL injection protected through Django ORM parametrized queries.
        
        Raises:
            Employee.DoesNotExist: If employee not found
            EmployeeAccessCard.DoesNotExist: If card not found
        """
        employee = get_object_or_404(Employee, id=employee_id)
        
        return get_object_or_404(
            EmployeeAccessCard,
            id=card_id,
            employee=employee,
            is_active=True
        )
    
    @staticmethod
    def validate_card_number_unique(card_number: str, exclude_card_id: Optional[str] = None) -> bool:
        """
        Check if a card number is unique among active cards.
        
        Args:
            card_number (str): Card number to check
            exclude_card_id (str, optional): Card ID to exclude from check (for updates)
            
        Returns:
            bool: True if unique, False if already exists
        """
        query = EmployeeAccessCard.objects.filter(
            card_number=card_number,
            is_active=True
        )
        
        if exclude_card_id:
            query = query.exclude(id=exclude_card_id)
        
        return not query.exists()
    
    @staticmethod
    def get_expiring_cards(days_until_expiry: int = 30) -> QuerySet:
        """
        Get access cards that are expiring soon.
        
        Args:
            days_until_expiry (int): Number of days to look ahead (default 30)
            
        Returns:
            QuerySet: Cards expiring within the specified period
        """
        from datetime import timedelta
        
        expiry_date = date.today() + timedelta(days=days_until_expiry)
        
        return EmployeeAccessCard.objects.filter(
            expiry_date__lte=expiry_date,
            expiry_date__gte=date.today(),
            is_active=True
        ).select_related('employee').order_by('expiry_date')
    
    @staticmethod
    def get_expired_cards() -> QuerySet:
        """
        Get all expired access cards.
        
        Returns:
            QuerySet: All expired active cards
        """
        return EmployeeAccessCard.objects.filter(
            expiry_date__lt=date.today(),
            is_active=True
        ).select_related('employee').order_by('-expiry_date')
