"""
apps/attendance/urls/device_urls.py

URL routes for Attendance Device & Swipe Intelligence APIs.

Device endpoints:
  GET    api/v1/devices/                              -> DeviceListCreateView
  POST   api/v1/devices/                              -> DeviceListCreateView
  GET    api/v1/devices/locations/                    -> DeviceLocationListView
  GET    api/v1/devices/locations/<id>/devices/       -> DeviceLocationDevicesView
  GET    api/v1/devices/<id>/                         -> DeviceDetailView
  PATCH  api/v1/devices/<id>/                         -> DeviceDetailView
  DELETE api/v1/devices/<id>/                         -> DeviceDetailView
  GET    api/v1/devices/<id>/swipe-logs/              -> DeviceSwipeLogsView
  GET    api/v1/devices/<id>/stats/                   -> DeviceStatsView

Swipe Log extras:
  GET    api/v1/swipe-logs/sources/                   -> SwipeLogSourcesView
  GET    api/v1/swipe-logs/<id>/swipe-intelligence/   -> SwipeIntelligenceView
  GET    api/v1/swipe-logs/sync/status/live/          -> LiveSyncStatusView
  GET    api/v1/swipe-logs/sync/status/<batch_id>/    -> SwipeSyncView.get_sync_status
  GET    api/v1/swipe-logs/sync/history/              -> SwipeSyncView.get_sync_history
  POST   api/v1/swipe-logs/sync/trigger/              -> SwipeSyncView.trigger_device_sync
  POST   api/v1/swipe-logs/sync/trigger/<id>/         -> DeviceSyncTriggerView

NOTE: The prefix api/v1/ is added by tenant_urls.py, so these patterns are
      relative (no leading api/v1/).
"""

from django.urls import path

from apps.attendance.views.admin.device_views import (
    DeviceDetailView,
    DeviceListCreateView,
    DeviceLocationDevicesView,
    DeviceLocationListView,
    DeviceStatsView,
    DeviceSyncTriggerView,
    DeviceSwipeLogsView,
    LiveSyncStatusView,
    SwipeIntelligenceView,
    SwipeLogSourcesView,
)
from apps.attendance.views.admin.swipe_logs.swipe_sync_view import SwipeSyncView

# ── Device routes ──────────────────────────────────────────────────────────────
device_patterns = [
    # Static sub-routes MUST come before <uuid:device_id>
    path("devices/locations/", DeviceLocationListView.as_view(), name="device-location-list"),
    path("devices/locations/<int:location_id>/devices/", DeviceLocationDevicesView.as_view(), name="device-location-devices"),

    # Device list + create
    path("devices/", DeviceListCreateView.as_view(), name="device-list-create"),

    # Device CRUD (UUID PK)
    path("devices/<uuid:device_id>/", DeviceDetailView.as_view(), name="device-detail"),
    path("devices/<uuid:device_id>/swipe-logs/", DeviceSwipeLogsView.as_view(), name="device-swipe-logs"),
    path("devices/<uuid:device_id>/stats/", DeviceStatsView.as_view(), name="device-stats"),
]

# ── Swipe-log extras ───────────────────────────────────────────────────────────
swipe_extra_patterns = [
    # Sources enum endpoint
    path("swipe-logs/sources/", SwipeLogSourcesView.as_view(), name="swipe-log-sources"),

    # Intelligence on a specific punch log (BigAutoField PK → int)
    path("swipe-logs/<int:id>/swipe-intelligence/", SwipeIntelligenceView.as_view(), name="swipe-intelligence"),

    # Sync Endpoints  —  MUST be ordered carefully to avoid routing conflicts
    # Live sync status  —  MUST be before sync/status/<batch_id>/ to avoid clash
    path("swipe-logs/sync/status/live/", LiveSyncStatusView.as_view(), name="swipe-sync-status-live"),
    
    # General sync trigger (without device_id)
    path("swipe-logs/sync/trigger/", SwipeSyncView.trigger_device_sync, name="swipe-logs-sync-trigger"),
    
    # Sync status by batch_id (UUID path param)
    path("swipe-logs/sync/status/<uuid:batch_id>/", SwipeSyncView.get_sync_status, name="swipe-logs-sync-status"),
    
    # Sync history
    path("swipe-logs/sync/history/", SwipeSyncView.get_sync_history, name="swipe-logs-sync-history"),

    # Per-device sync trigger (UUID PK) - MUST be after general endpoints to avoid conflicts
    path("swipe-logs/sync/trigger/<uuid:device_id>/", DeviceSyncTriggerView.as_view(), name="swipe-sync-trigger-device"),
]

urlpatterns = device_patterns + swipe_extra_patterns
