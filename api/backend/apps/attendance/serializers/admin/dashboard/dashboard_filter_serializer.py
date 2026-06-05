"""Dashboard Filter Serializer - Filter seed data."""

from rest_framework import serializers


class FilterItemSerializer(serializers.Serializer):
    """Serializer for individual filter item."""

    id = serializers.UUIDField(
        help_text="UUID of the filter item",
    )
    code = serializers.CharField(
        max_length=50,
        help_text="Code/identifier",
    )
    name = serializers.CharField(
        max_length=200,
        help_text="Display name",
    )


class DashboardFilterSerializer(serializers.Serializer):
    """
    Serializer for dashboard filter seed data.
    
    Returns dropdown lists for:
    - Departments
    - Designations
    - Teams
    """

    departments = FilterItemSerializer(
        many=True,
        help_text="List of departments",
    )
    designations = FilterItemSerializer(
        many=True,
        help_text="List of designations",
    )
    teams = FilterItemSerializer(
        many=True,
        help_text="List of teams (extracted from employee data)",
    )
    generated_at = serializers.DateTimeField(
        help_text="Timestamp when the filters were generated",
    )

    def validate(self, data):
        """Validate filter data."""
        return data
