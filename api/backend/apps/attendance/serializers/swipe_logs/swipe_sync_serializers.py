"""
Swipe Sync Serializers - Format device sync batch and device sync log data.
"""

from rest_framework import serializers
from datetime import datetime


class SwipeSyncBatchTriggerSerializer(serializers.Serializer):
    """
    Request serializer for triggering device sync.
    
    Used by: POST /api/v1/swipe-logs/sync/trigger
    """

    company_id = serializers.CharField(required=False, allow_blank=True)
    device_id = serializers.IntegerField(required=False, allow_null=True)
    device_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_null=True,
    )
    sync_from = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, data):
        """Ensure company context and at least one device target are provided."""
        company_id = data.get("company_id")
        device_id = data.get("device_id")
        device_ids = data.get("device_ids")

        if not company_id:
            data.pop("company_id", None)

        if not device_id and not device_ids:
            raise serializers.ValidationError(
                "Either device_id or device_ids must be provided."
            )

        return data


class SwipeSyncBatchResponseSerializer(serializers.Serializer):
    """
    Response for sync trigger.
    
    Returns:
    {
        "sync_batch_id": "...",
        "device_count": 2,
        "status": "SYNCING",
        "queued_at": "2024-01-15T10:30:00Z"
    }
    """

    sync_batch_id = serializers.CharField()
    device_count = serializers.IntegerField()
    status = serializers.CharField()
    queued_at = serializers.CharField()


class DeviceSyncLogSerializer(serializers.Serializer):
    """
    Serialize individual device sync log entry.
    """

    device_log_id = serializers.CharField()
    device_id = serializers.IntegerField()
    device_code = serializers.CharField()
    device_name = serializers.CharField()
    device_ip = serializers.IPAddressField(allow_null=True)
    status = serializers.CharField()
    punches_synced = serializers.IntegerField()
    battery_level = serializers.IntegerField(allow_null=True)
    signal_strength = serializers.IntegerField(allow_null=True)
    sync_started_at = serializers.CharField(allow_null=True)
    sync_completed_at = serializers.CharField(allow_null=True)
    duration_seconds = serializers.IntegerField(allow_null=True)
    error_message = serializers.CharField(allow_null=True)
    error_code = serializers.CharField(allow_null=True)


class SwipeSyncBatchStatusSerializer(serializers.Serializer):
    """
    Response for sync status check.
    
    Used by: GET /api/v1/swipe-logs/sync/status/{batch_id}
    """

    batch_id = serializers.CharField()
    company_id = serializers.CharField()
    status = serializers.CharField()  # SYNCING, SUCCESS, FAILED, PARTIAL
    sync_mode = serializers.CharField()
    device_count = serializers.IntegerField()
    devices_succeeded = serializers.IntegerField()
    devices_failed = serializers.IntegerField()
    total_punches_synced = serializers.IntegerField()
    sync_started_at = serializers.CharField(allow_null=True)
    sync_completed_at = serializers.CharField(allow_null=True)
    duration_seconds = serializers.IntegerField(allow_null=True)
    error_message = serializers.CharField(allow_null=True)
    created_at = serializers.CharField()


class SwipeSyncBatchHistoryItemSerializer(serializers.Serializer):
    """
    Single item in sync history list.
    """

    batch_id = serializers.CharField()
    status = serializers.CharField()
    sync_mode = serializers.CharField()
    device_count = serializers.IntegerField()
    devices_succeeded = serializers.IntegerField()
    devices_failed = serializers.IntegerField()
    total_punches_synced = serializers.IntegerField()
    sync_started_at = serializers.CharField(allow_null=True)
    sync_completed_at = serializers.CharField(allow_null=True)
    duration_seconds = serializers.IntegerField(allow_null=True)
    created_at = serializers.CharField()
    device_logs = DeviceSyncLogSerializer(many=True)


class SwipeSyncHistoryResponseSerializer(serializers.Serializer):
    """
    Response for sync history listing.
    
    Used by: GET /api/v1/swipe-logs/sync/history
    """

    data = SwipeSyncBatchHistoryItemSerializer(many=True)
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    limit = serializers.IntegerField()
    total_pages = serializers.IntegerField()
