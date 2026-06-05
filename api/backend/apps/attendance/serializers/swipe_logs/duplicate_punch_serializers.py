"""
Duplicate Punch Serializers.

Handles request validation and response formatting for duplicate punch APIs.

Request serializers:
    - DuplicatePunchFilterSerializer (GET /duplicates)
    - DuplicateSummaryQuerySerializer (GET /duplicates/summary)
    - FlagDuplicateSerializer (POST /{id}/flag-duplicate)
    - UnflagDuplicateSerializer (POST /{id}/unflag-duplicate)
    - BulkDismissDuplicateSerializer (POST /duplicates/bulk-dismiss)

Response serializers:
    - DuplicatePunchResponseSerializer
    - DuplicateSummaryResponseSerializer
    - FlagDuplicateResponseSerializer
    - BulkDismissResponseSerializer
"""

from rest_framework import serializers


# ─────────────────────────────────────────────────────────────
# Request Query Parameter Serializers
# ─────────────────────────────────────────────────────────────

class DuplicatePunchFilterSerializer(serializers.Serializer):
    """Validates query parameters for listing duplicate punches."""

    company_id = serializers.UUIDField(required=True)
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)
    employee_id = serializers.UUIDField(required=False, allow_null=True)
    device_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        from_date = attrs.get("from_date")
        to_date = attrs.get("to_date")

        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError({
                "from_date": "from_date cannot be after to_date"
            })

        return attrs


class DuplicateSummaryQuerySerializer(serializers.Serializer):
    """Validates query parameters for duplicate summary analytics."""

    company_id = serializers.UUIDField(required=True)
    date = serializers.DateField(required=False, allow_null=True)
    from_date = serializers.DateField(required=False, allow_null=True)
    to_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        from_date = attrs.get("from_date")
        to_date = attrs.get("to_date")

        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError({
                "from_date": "from_date cannot be after to_date"
            })

        return attrs


# ─────────────────────────────────────────────────────────────
# Request Body Serializers (POST actions)
# ─────────────────────────────────────────────────────────────

class FlagDuplicateSerializer(serializers.Serializer):
    """Validates request body for manually flagging a punch as duplicate."""

    reason = serializers.CharField(
        required=True,
        min_length=3,
        max_length=500,
        error_messages={
            "required": "reason is required to flag a duplicate.",
            "blank": "reason cannot be blank.",
            "min_length": "reason must be at least 3 characters.",
        },
    )
    flagged_by = serializers.UUIDField(
        required=True,
        error_messages={
            "required": "flagged_by (employee UUID) is required.",
            "invalid": "flagged_by must be a valid UUID.",
        },
    )


class UnflagDuplicateSerializer(serializers.Serializer):
    """Validates request body for removing a duplicate flag."""

    reason = serializers.CharField(
        required=True,
        min_length=3,
        max_length=500,
        error_messages={
            "required": "reason is required to unflag a duplicate.",
            "blank": "reason cannot be blank.",
            "min_length": "reason must be at least 3 characters.",
        },
    )
    unflagged_by = serializers.UUIDField(
        required=True,
        error_messages={
            "required": "unflagged_by (employee UUID) is required.",
            "invalid": "unflagged_by must be a valid UUID.",
        },
    )


class BulkDismissDuplicateSerializer(serializers.Serializer):
    """Validates request body for bulk dismissing duplicate flags."""

    company_id = serializers.UUIDField(
        required=True,
        error_messages={
            "required": "company_id is required.",
            "invalid": "company_id must be a valid UUID.",
        },
    )
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        min_length=1,
        error_messages={
            "required": "ids list is required.",
            "min_length": "ids list must contain at least one ID.",
        },
    )
    reason = serializers.CharField(
        required=True,
        min_length=3,
        max_length=500,
        error_messages={
            "required": "reason is required for bulk dismiss.",
            "blank": "reason cannot be blank.",
        },
    )
    dismissed_by = serializers.UUIDField(
        required=True,
        error_messages={
            "required": "dismissed_by (employee UUID) is required.",
            "invalid": "dismissed_by must be a valid UUID.",
        },
    )

    def validate_ids(self, value):
        """Ensure no duplicate IDs in the list."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "ids list must not contain duplicate values."
            )
        return value


# ─────────────────────────────────────────────────────────────
# Response Data Serializers
# ─────────────────────────────────────────────────────────────

class DuplicatePunchResponseSerializer(serializers.Serializer):
    """Serializes a duplicate PunchLog record for API response."""

    id = serializers.IntegerField()
    employee_id = serializers.UUIDField(source="employee.id")
    employee_name = serializers.SerializerMethodField()
    punch_time = serializers.DateTimeField()
    punch_type = serializers.CharField()
    device_name = serializers.SerializerMethodField()
    original_punch_id = serializers.IntegerField(allow_null=True)
    duplicate_flag = serializers.BooleanField()
    spoof_detection_result = serializers.JSONField(allow_null=True)

    def get_employee_name(self, obj) -> str:
        first = getattr(obj.employee, "first_name", "") or ""
        last = getattr(obj.employee, "last_name", "") or ""
        return f"{first} {last}".strip()

    def get_device_name(self, obj) -> str:
        if obj.device_id:
            return f"Device {obj.device_id}"
        return "Unknown"


class DeviceDuplicateCountSerializer(serializers.Serializer):
    """Serializes per-device duplicate count."""

    device_id = serializers.IntegerField(allow_null=True)
    device_name = serializers.CharField()
    count = serializers.IntegerField()


class DuplicateSummaryResponseSerializer(serializers.Serializer):
    """Serializes duplicate analytics summary."""

    total_duplicates = serializers.IntegerField()
    auto_suppressed = serializers.IntegerField()
    under_review = serializers.IntegerField()
    by_device = DeviceDuplicateCountSerializer(many=True)


class FlagDuplicateResponseSerializer(serializers.Serializer):
    """Serializes flag/unflag operation response."""

    id = serializers.IntegerField()
    duplicate_flag = serializers.BooleanField()
    updated_at = serializers.CharField(allow_null=True)


class BulkDismissResponseSerializer(serializers.Serializer):
    """Serializes bulk dismiss response."""

    dismissed_count = serializers.IntegerField()
    failed_ids = serializers.ListField(
        child=serializers.IntegerField()
    )
    message = serializers.CharField()
