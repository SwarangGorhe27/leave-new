"""
Swipe Log Bulk Serializer - Serialization for bulk operations.

Handles:
- Bulk delete requests
- Bulk update requests
"""

from rest_framework import serializers


class SwipeLogBulkDeleteSerializer(serializers.Serializer):
    """
    Serializer for bulk delete operation.
    
    Used for POST /api/v1/swipe-logs/bulk-delete
    """

    company_id = serializers.UUIDField(required=True)
    deleted_by = serializers.UUIDField(required=False, allow_null=True)

    swipe_log_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        allow_empty=False,
        help_text="List of swipe log IDs to delete.",
    )

    reason = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Reason for bulk deletion.",
    )

    def validate_swipe_log_ids(self, value):
        """Validate swipe log IDs."""
        if len(value) == 0:
            raise serializers.ValidationError("At least one swipe log ID is required.")

        if len(value) > 10000:
            raise serializers.ValidationError(
                "Maximum 10000 swipe logs can be deleted at once."
            )

        return value


class SwipeLogBulkDeleteResponseSerializer(serializers.Serializer):
    """
    Response serializer for bulk delete operation.
    """

    job_id = serializers.UUIDField(
        help_text="Bulk deletion job ID for tracking.",
    )

    total_requested = serializers.IntegerField(
        help_text="Total swipe logs requested for deletion.",
    )

    total_deleted = serializers.IntegerField(
        help_text="Total swipe logs successfully deleted.",
    )

    total_failed = serializers.IntegerField(
        help_text="Total swipe logs that failed to delete.",
    )

    failed_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of swipe log IDs that failed to delete.",
    )

    processing_time_ms = serializers.IntegerField(
        help_text="Processing time in milliseconds.",
    )


class SwipeLogBulkUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk update operation.
    
    Used to update punch_type or other correctable fields in bulk.
    """

    swipe_log_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        allow_empty=False,
        help_text="List of swipe log IDs to update.",
    )

    punch_type = serializers.ChoiceField(
        choices=["IN", "OUT"],
        required=False,
        help_text="New punch type for all selected logs.",
    )

    is_trusted = serializers.BooleanField(
        required=False,
        help_text="Mark all selected logs as trusted/untrusted.",
    )

    reason = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Reason for bulk update.",
    )

    def validate(self, data):
        """Validate at least one field is being updated."""
        updatable_fields = {"punch_type", "is_trusted"}
        provided_fields = {
            k for k in updatable_fields if k in self.initial_data
        }

        if not provided_fields:
            raise serializers.ValidationError(
                "At least one field (punch_type, is_trusted) must be provided for update."
            )

        return data


class SwipeLogBulkUpdateResponseSerializer(serializers.Serializer):
    """
    Response serializer for bulk update operation.
    """

    job_id = serializers.UUIDField(
        help_text="Bulk update job ID for tracking.",
    )

    total_requested = serializers.IntegerField(
        help_text="Total swipe logs requested for update.",
    )

    total_updated = serializers.IntegerField(
        help_text="Total swipe logs successfully updated.",
    )

    total_failed = serializers.IntegerField(
        help_text="Total swipe logs that failed to update.",
    )

    failed_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of swipe log IDs that failed to update.",
    )

    processing_time_ms = serializers.IntegerField(
        help_text="Processing time in milliseconds.",
    )
