"""Dashboard Presence Serializer - Employee presence data."""

from rest_framework import serializers


class EmployeePresenceItemSerializer(serializers.Serializer):
    """Serializer for individual employee presence data."""

    employee_id = serializers.UUIDField(
        help_text="Employee UUID",
    )
    employee_code = serializers.CharField(
        max_length=30,
        help_text="Employee code",
    )
    employee_name = serializers.CharField(
        max_length=200,
        help_text="Employee full name",
    )
    designation = serializers.CharField(
        max_length=150,
        help_text="Employee designation",
    )
    department = serializers.CharField(
        max_length=150,
        help_text="Department name",
    )
    check_in_time = serializers.TimeField(
        allow_null=True,
        help_text="Check-in time (HH:MM:SS)",
    )
    status = serializers.CharField(
        max_length=20,
        help_text="Presence status (On Time, Late, Not Yet In, etc.)",
    )
    work_hours = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        allow_null=True,
        help_text="Work hours worked so far today",
    )
    is_late = serializers.BooleanField(
        default=False,
        help_text="Whether employee is late",
    )


class DashboardWhosInSerializer(serializers.Serializer):
    """
    Serializer for Who's In Today widget.
    
    Returns:
    - Donut summary counts
    - Employee list with presence details
    """

    on_time_count = serializers.IntegerField(
        help_text="Number of employees on time",
    )
    late_in_count = serializers.IntegerField(
        help_text="Number of employees who checked in late",
    )
    not_yet_in_count = serializers.IntegerField(
        help_text="Number of employees not yet checked in",
    )
    total_employee_count = serializers.IntegerField(
        help_text="Total number of employees (excluding on leave)",
    )
    employee_list = EmployeePresenceItemSerializer(
        many=True,
        help_text="List of employee presence details",
    )
    generated_at = serializers.DateTimeField(
        help_text="Timestamp when the data was generated",
    )

    def validate(self, data):
        """Validate who's in data."""
        return data


class DashboardEmployeePresenceSerializer(serializers.Serializer):
    """
    Serializer for employee presence list.
    """

    results = EmployeePresenceItemSerializer(
        many=True,
        help_text="Employee presence list",
    )
    generated_at = serializers.DateTimeField(
        help_text="Timestamp when the data was generated",
    )

    def validate(self, data):
        """Validate employee presence data."""
        return data
