"""Serializers for bulk shift assignment operations."""

from rest_framework import serializers
from datetime import date, timedelta


class BulkAssignmentItemSerializer(serializers.Serializer):
    """Serializer for individual items in bulk assignment."""
    
    employee_id = serializers.UUIDField(required=True)
    shift_id = serializers.UUIDField(required=True)
    is_week_off = serializers.BooleanField(default=False, required=False)
    override_reason = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
    )


class BulkAssignmentCreateSerializer(serializers.Serializer):
    """Serializer for bulk shift assignment creation."""
    
    ASSIGNMENT_TYPE_CHOICES = [
        ("single_date", "Single Date"),
        ("date_range", "Date Range"),
        ("recurring", "Recurring Days"),
    ]
    
    assignment_type = serializers.ChoiceField(
        choices=ASSIGNMENT_TYPE_CHOICES,
        default="single_date",
    )
    cycle_id = serializers.UUIDField(required=True)
    company_id = serializers.UUIDField(required=False)
    
    # For single_date and recurring
    roster_date = serializers.DateField(required=False)
    
    # For date_range
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    
    # For recurring
    recurring_days = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6),
        required=False,
        help_text="List of weekday numbers (0=Monday, 6=Sunday)",
    )
    
    # Assignment data
    assignments = serializers.ListField(
        child=BulkAssignmentItemSerializer(),
        required=True,
        min_length=1,
    )
    
    # Options
    skip_duplicates = serializers.BooleanField(default=True)
    skip_overlapping = serializers.BooleanField(default=True)
    skip_inactive_employees = serializers.BooleanField(default=True)
    async_mode = serializers.BooleanField(default=True)
    notify_employees = serializers.BooleanField(default=False)
    
    def validate(self, data):
        """Validate bulk assignment data."""
        assignment_type = data.get("assignment_type")
        
        if assignment_type == "single_date":
            if not data.get("roster_date"):
                raise serializers.ValidationError(
                    {"roster_date": "roster_date is required for single_date assignment type."}
                )
            if data["roster_date"] < date.today():
                raise serializers.ValidationError(
                    {"roster_date": "Roster date cannot be in the past."}
                )
        
        elif assignment_type == "date_range":
            if not data.get("date_from") or not data.get("date_to"):
                raise serializers.ValidationError(
                    {
                        "date_from": "date_from and date_to are required for date_range assignment type."
                    }
                )
            if data["date_from"] > data["date_to"]:
                raise serializers.ValidationError(
                    {"date_from": "date_from cannot be greater than date_to."}
                )
            if data["date_from"] < date.today():
                raise serializers.ValidationError(
                    {"date_from": "date_from cannot be in the past."}
                )
            # Maximum 90 days for bulk assignment
            date_diff = (data["date_to"] - data["date_from"]).days
            if date_diff > 90:
                raise serializers.ValidationError(
                    {"date_to": "Date range cannot exceed 90 days."}
                )
        
        elif assignment_type == "recurring":
            if not data.get("recurring_days"):
                raise serializers.ValidationError(
                    {"recurring_days": "recurring_days is required for recurring assignment type."}
                )
            if not data.get("roster_date"):
                raise serializers.ValidationError(
                    {"roster_date": "roster_date is required for recurring assignment type (start date)."}
                )
        
        return data


class BulkAssignmentValidationSerializer(serializers.Serializer):
    """Serializer for pre-validation of bulk assignments."""
    
    cycle_id = serializers.UUIDField(required=True)
    company_id = serializers.UUIDField(required=False)
    date_from = serializers.DateField(required=True)
    date_to = serializers.DateField(required=True)
    assignments = serializers.ListField(
        child=BulkAssignmentItemSerializer(),
        required=True,
        min_length=1,
    )
    check_duplicates = serializers.BooleanField(default=True)
    check_overlapping = serializers.BooleanField(default=True)
    check_inactive = serializers.BooleanField(default=True)

    def validate(self, data):
        """Validate date range."""
        if data["date_from"] > data["date_to"]:
            raise serializers.ValidationError(
                "date_from cannot be greater than date_to."
            )
        return data


class BulkAssignmentValidationResultSerializer(serializers.Serializer):
    """Serializer for bulk assignment validation results."""
    
    total_assignments = serializers.IntegerField()
    valid_assignments = serializers.IntegerField()
    invalid_assignments = serializers.IntegerField()
    duplicates_found = serializers.IntegerField()
    overlapping_found = serializers.IntegerField()
    inactive_employees = serializers.IntegerField()
    warnings = serializers.ListField(child=serializers.CharField())
    errors = serializers.ListField(child=serializers.CharField())
    can_proceed = serializers.BooleanField()


class BulkAssignmentJobStatusSerializer(serializers.Serializer):
    """Serializer for bulk assignment job status."""
    
    job_id = serializers.UUIDField()
    status = serializers.CharField(
        max_length=20,
        help_text="Job status: PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED",
    )
    progress = serializers.IntegerField(min_value=0, max_value=100)
    total_items = serializers.IntegerField()
    processed_items = serializers.IntegerField()
    success_count = serializers.IntegerField()
    failure_count = serializers.IntegerField()
    skip_count = serializers.IntegerField()
    started_at = serializers.DateTimeField(required=False)
    completed_at = serializers.DateTimeField(required=False)
    duration_seconds = serializers.IntegerField(required=False)
    error_message = serializers.CharField(required=False, allow_blank=True)
    created_by_id = serializers.UUIDField()
    created_by_name = serializers.CharField()


class BulkAssignmentResultSerializer(serializers.Serializer):
    """Serializer for bulk assignment results."""
    
    job_id = serializers.UUIDField()
    status = serializers.CharField()
    summary = serializers.DictField()
    successful_assignments = serializers.ListField()
    failed_assignments = serializers.ListField()
    skipped_assignments = serializers.ListField()
    execution_time = serializers.FloatField()
