"""
Access Card Details Serializers for Admin Side.

Handles serialization of employee access card data for:
- POST: Create new access card
- GET: Retrieve all access cards for an employee
- PATCH: Update access card details
- DELETE: Deactivate access card

SQL injection protection through Django ORM parametrized queries.
Comprehensive validation to ensure data integrity.
"""

from rest_framework import serializers
from datetime import date
from apps.employees.models.access import EmployeeAccessCard
from apps.employees.models.employee import Employee


class AccessCardSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying and managing access cards on admin side.
    Shows all access card details with comprehensive validation.
    """
    
    employee_name = serializers.CharField(source='employee.first_name', read_only=True, allow_null=True)
    employee_id_display = serializers.CharField(source='employee.employee_id', read_only=True, allow_null=True)

    # Map API field names to model fields
    access_card_number = serializers.CharField(source='card_number')
    from_date = serializers.DateField(source='issued_date')
    to_date = serializers.DateField(source='expiry_date', allow_null=True)
    
    class Meta:
        model = EmployeeAccessCard
        fields = [
            'id',
            'employee',
            'employee_name',
            'employee_id_display',
            'access_card_number',
            'from_date',
            'to_date',
            'is_active',
        ]
        read_only_fields = ['id', 'employee_name', 'employee_id_display']
    
    def validate_access_card_number(self, value):
        """
        Validate access card number.
        - Must not be empty
        - Must be alphanumeric and within max length
        - Prevent SQL injection through input validation
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Access card number cannot be empty.")
        
        # Remove whitespace and validate
        cleaned_value = value.strip()
        
        if len(cleaned_value) > 50:
            raise serializers.ValidationError("Access card number cannot exceed 50 characters.")
        
        # Check if contains only alphanumeric, hyphens, and underscores
        if not all(c.isalnum() or c in '-_' for c in cleaned_value):
            raise serializers.ValidationError(
                "Access card number can only contain letters, numbers, hyphens, and underscores."
            )
        
        return cleaned_value
    
    def validate_from_date(self, value):
        """
        Validate from_date.
        - Must not be in the future
        """
        if value > date.today():
            raise serializers.ValidationError("From date cannot be in the future.")
        return value
    
    def validate(self, data):
        """
        Validate overall access card data.
        """
        # internal keys map to model fields because of `source` in field declarations
        from_date = data.get('issued_date')
        to_date = data.get('expiry_date')
        
        # If both dates are provided, to_date must be after or equal to from_date
        if from_date and to_date:
            if to_date < from_date:
                raise serializers.ValidationError({
                    'to_date': "To date must be on or after the from date."
                })
        
        # Check for duplicate access card number
        request = self.context.get('request')
        employee_id = self.context.get('employee_id')
        # card number lives under model key `card_number` in validated_data
        access_card_number = data.get('card_number') if data.get('card_number') is not None else (
            self.instance.card_number if self.instance else None
        )
        
        # For updates, exclude the current instance
        # adjust to model field `card_number`
        if self.instance:
            duplicate = EmployeeAccessCard.objects.filter(
                card_number=access_card_number,
                is_active=True
            ).exclude(id=self.instance.id).exists()
        else:
            duplicate = EmployeeAccessCard.objects.filter(
                card_number=access_card_number,
                is_active=True
            ).exists()
        
        if duplicate:
            raise serializers.ValidationError({
                'access_card_number': "This access card number is already in use."
            })
        
        return data


class AccessCardListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing access cards with employee details.
    """
    
    employee_name = serializers.SerializerMethodField()
    employee_id_display = serializers.CharField(source='employee.employee_id', read_only=True)
    access_card_number = serializers.CharField(source='card_number', read_only=True)
    from_date = serializers.DateField(source='issued_date', read_only=True)
    to_date = serializers.DateField(source='expiry_date', read_only=True, allow_null=True)
    
    class Meta:
        model = EmployeeAccessCard
        fields = [
            'id',
            'employee',
            'employee_id_display',
            'employee_name',
            'access_card_number',
            'from_date',
            'to_date',
            'is_active',
        ]
        read_only_fields = ['id', 'employee_id_display', 'employee_name']
    
    def get_employee_name(self, obj):
        """Get full name of the employee."""
        if obj.employee.first_name and obj.employee.last_name:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return obj.employee.first_name or ""


class AccessCardCreateSerializer(serializers.Serializer):
    """
    Serializer specifically for creating new access cards.
    Takes employee_id as input parameter.
    """
    
    access_card_number = serializers.CharField(
        max_length=50,
        required=True,
        help_text="Access Card Number (alphanumeric, hyphens, underscores allowed)"
    )
    from_date = serializers.DateField(
        required=True,
        help_text="From date (YYYY-MM-DD format)"
    )
    to_date = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="To date (YYYY-MM-DD format, optional)"
    )
    
    def validate_access_card_number(self, value):
        """Validate access card number format."""
        if not value or not value.strip():
            raise serializers.ValidationError("Access card number cannot be empty.")
        
        cleaned_value = value.strip()
        
        if len(cleaned_value) > 50:
            raise serializers.ValidationError("Access card number cannot exceed 50 characters.")
        
        if not all(c.isalnum() or c in '-_' for c in cleaned_value):
            raise serializers.ValidationError(
                "Access card number can only contain letters, numbers, hyphens, and underscores."
            )
        
        return cleaned_value
    
    def validate_from_date(self, value):
        """Validate from_date is not in the future."""
        if value > date.today():
            raise serializers.ValidationError("From date cannot be in the future.")
        return value
    
    def validate(self, data):
        """Validate from_date and to_date relationship."""
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        
        if from_date and to_date and to_date < from_date:
            raise serializers.ValidationError({
                'to_date': "To date must be on or after the from date."
            })
        
        # One active access card per employee
        employee_id = self.context.get("employee_id")
        if employee_id and EmployeeAccessCard.objects.filter(
            employee_id=employee_id,
            is_active=True,
        ).exists():
            raise serializers.ValidationError({
                "access_card_number": (
                    "An access card already exists for this employee. "
                    "Please edit the existing card."
                ),
            })

        # Check duplicate card number
        access_card_number = data.get('access_card_number')
        if EmployeeAccessCard.objects.filter(
            card_number=access_card_number,
            is_active=True
        ).exists():
            raise serializers.ValidationError({
                'access_card_number': "This access card number is already in use."
            })
        
        return data
