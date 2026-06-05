"""
Education Details serializer for admin employee details.

Security Note: All serializers use Django ORM parameterized queries only.
No raw SQL is used to prevent SQL injection attacks.
"""

from rest_framework import serializers
from apps.employees.models.education import EmployeeEducation
from apps.employees.models.employee import Employee


class EducationDetailSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for EmployeeEducation.
    Used for retrieving and displaying education records.
    """
    education_level_name = serializers.CharField(
        source='education_level.name',
        read_only=True
    )
    qualification_name = serializers.CharField(
        source='qualification.name',
        read_only=True,
        allow_null=True
    )
    specialization_name = serializers.CharField(
        source='specialization.name',
        read_only=True,
        allow_null=True
    )
    board_name = serializers.CharField(
        source='board.name',
        read_only=True,
        allow_null=True
    )
    study_mode_name = serializers.CharField(
        source='study_mode.name',
        read_only=True,
        allow_null=True
    )
    education_status_name = serializers.CharField(
        source='education_status.name',
        read_only=True,
        allow_null=True
    )
    verified_by_name = serializers.SerializerMethodField()
    from_date = serializers.DateField(source='start_date', read_only=True, allow_null=True)
    to_date = serializers.DateField(source='end_date', read_only=True, allow_null=True)
    
    class Meta:
        model = EmployeeEducation
        fields = [
            'id',
            'employee',
            'education_level',
            'education_level_name',
            'qualification',
            'qualification_name',
            'specialization',
            'specialization_name',
            'board',
            'board_name',
            'institution_name',
            'university_name',
            'start_year',
            'end_year',
            'start_date',
            'end_date',
            'from_date',
            'to_date',
            'study_mode',
            'study_mode_name',
            'education_status',
            'education_status_name',
            'grade_or_cgpa',
            'percentage',
            'roll_number',
            'certificate_number',
            'is_highest',
            'is_verified',
            'verified_by',
            'verified_by_name',
            'verified_at',
            'is_active',
            'sort_order',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'employee',
            'is_active',
            'created_at',
            'updated_at',
        ]

    def get_verified_by_name(self, obj):
        """Return verifier's full name."""
        if obj.verified_by:
            return f"{obj.verified_by.first_name} {obj.verified_by.last_name}"
        return None


class EducationWriteSerializer(serializers.ModelSerializer):
    """
    Write serializer for EmployeeEducation.
    Handles creation and updates with validation.
    """
    
    from_date = serializers.DateField(
        source='start_date',
        required=False,
        allow_null=True,
        input_formats=['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'],
    )
    to_date = serializers.DateField(
        source='end_date',
        required=False,
        allow_null=True,
        input_formats=['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'],
    )

    class Meta:
        model = EmployeeEducation
        fields = [
            'education_level',
            'qualification',
            'specialization',
            'board',
            'institution_name',
            'university_name',
            'start_year',
            'end_year',
            'start_date',
            'end_date',
            'from_date',
            'to_date',
            'study_mode',
            'education_status',
            'grade_or_cgpa',
            'percentage',
            'roll_number',
            'certificate_number',
            'is_highest',
            'sort_order',
        ]

    def validate_education_level(self, value):
        """Validate education level is provided."""
        if not value:
            raise serializers.ValidationError("Education level is required.")
        return value

    def validate_percentage(self, value):
        """Validate percentage is between 0-100."""
        if value is not None:
            if value < 0 or value > 100:
                raise serializers.ValidationError(
                    "Percentage must be between 0 and 100."
                )
        return value

    def validate(self, data):
        """
        Validate the entire record.
        """
        start_year = data.get('start_year')
        end_year = data.get('end_year')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Check if start_year and end_year logic
        if start_year and end_year:
            if start_year > end_year:
                raise serializers.ValidationError({
                    'end_year': 'End year must be equal to or greater than start year.'
                })

        # Check if start_date and end_date logic
        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be on or after the start date.'
                })

        return data
