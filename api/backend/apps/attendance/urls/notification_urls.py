"""URL routing for attendance notification APIs."""

from django.urls import path

from apps.attendance.views.admin.notifications.notification_views import AttendanceNotificationAPI


urlpatterns = [
    path("notifications/read-all", AttendanceNotificationAPI.mark_all_as_read, name="attendance-notifications-read-all"),
    path("notifications/unread-count", AttendanceNotificationAPI.unread_count, name="attendance-notifications-unread-count"),
    path("notifications/send", AttendanceNotificationAPI.send, name="attendance-notifications-send"),
    path("notifications/<uuid:notification_id>/read", AttendanceNotificationAPI.mark_as_read, name="attendance-notifications-read"),
    path("notifications/<uuid:notification_id>", AttendanceNotificationAPI.dismiss, name="attendance-notifications-dismiss"),
    path("notifications", AttendanceNotificationAPI.list_notifications, name="attendance-notifications-list"),
]
