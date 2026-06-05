"""
Serializers for Weekend Configuration API endpoints.

Handles serialization and deserialization of weekend/weekly-off configurations.
"""

from rest_framework import serializers
from ..models.request_modules.weekends_config import WeekendConfig, WeekFrequencyChoices


class WeekendConfigSerializer(serializers.ModelSerializer):
    """
    Response serializer for weekend configuration.
    Returns all fields of WeekendConfig model.
    """

    branch_name = serializers.CharField(source="branch.name", read_only=True)
    day_of_week_display = serializers.SerializerMethodField()
    week_frequency_display = serializers.CharField(
        source="get_week_frequency_display", read_only=True
    )

    class Meta:
        model = WeekendConfig
        fields = [
            "id",
            "branch",
            "branch_name",
            "day_of_week",
            "day_of_week_display",
            "week_frequency",
            "week_frequency_display",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_day_of_week_display(self, obj):
        """Convert day_of_week number to day name."""
        days = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }
        return days.get(obj.day_of_week, "Unknown")


class WeekendConfigCreateSerializer(serializers.ModelSerializer):
    """
    Request serializer for creating weekend configurations.
    """

    class Meta:
        model = WeekendConfig
        fields = [
            "branch",
            "day_of_week",
            "week_frequency",
            "is_active",
        ]

    def validate_day_of_week(self, value):
        """Validate day_of_week is between 0-6."""
        if not (0 <= value <= 6):
            raise serializers.ValidationError("day_of_week must be between 0 (Monday) and 6 (Sunday).")
        return value

    def validate(self, data):
        """
        Validate that duplicate configurations don't exist.
        """
        branch = data.get("branch")
        day_of_week = data.get("day_of_week")
        week_frequency = data.get("week_frequency")

        # Check if configuration already exists
        existing = WeekendConfig.objects.filter(
            branch=branch,
            day_of_week=day_of_week,
            week_frequency=week_frequency,
            is_active=True,
        ).exists()

        if existing:
            raise serializers.ValidationError(
                "This weekend configuration already exists for the selected branch."
            )

        return data


class WeekendConfigUpdateSerializer(serializers.ModelSerializer):
    """
    Request serializer for updating weekend configurations.
    """

    class Meta:
        model = WeekendConfig
        fields = [
            "day_of_week",
            "week_frequency",
            "is_active",
        ]

    def validate_day_of_week(self, value):
        """Validate day_of_week is between 0-6."""
        if not (0 <= value <= 6):
            raise serializers.ValidationError("day_of_week must be between 0 (Monday) and 6 (Sunday).")
        return value


class WeekendConfigListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing weekend configurations.
    """

    branch_name = serializers.CharField(source="branch.name", read_only=True)
    day_of_week_display = serializers.SerializerMethodField()

    class Meta:
        model = WeekendConfig
        fields = [
            "id",
            "branch",
            "branch_name",
            "day_of_week",
            "day_of_week_display",
            "week_frequency",
            "is_active",
        ]

    def get_day_of_week_display(self, obj):
        """Convert day_of_week number to day name."""
        days = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }
        return days.get(obj.day_of_week, "Unknown")


class WeekendConfigBulkUpdateSerializer(serializers.Serializer):
    """
    Request serializer for bulk updating weekend configuration.
    Takes a list of weekend day names and applies them to all branches.
    
    Example:
    {
        "weekend_days": ["SATURDAY", "SUNDAY"]
    }
    """

    DAY_CHOICES = {
        "MONDAY": 0,
        "TUESDAY": 1,
        "WEDNESDAY": 2,
        "THURSDAY": 3,
        "FRIDAY": 4,
        "SATURDAY": 5,
        "SUNDAY": 6,
    }

    weekend_days = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of day names (e.g., ['SATURDAY', 'SUNDAY'])",
    )

    def validate_weekend_days(self, value):
        """Validate that all provided days are valid day names."""
        if not value:
            raise serializers.ValidationError("At least one weekend day must be provided.")

        valid_days = set(self.DAY_CHOICES.keys())
        invalid_days = [day.upper() for day in value if day.upper() not in valid_days]

        if invalid_days:
            raise serializers.ValidationError(
                f"Invalid day names: {invalid_days}. Valid options are: {', '.join(valid_days)}"
            )

        return [day.upper() for day in value]

    def get_day_of_week_numbers(self):
        """Convert day names to day of week numbers."""
        return [self.DAY_CHOICES[day] for day in self.validated_data["weekend_days"]]
