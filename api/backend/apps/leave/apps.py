"""Django app configuration for the Leave module."""

from django.apps import AppConfig


class LeaveConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.leave"
    label = "leave"
    verbose_name = "Leave"

    def ready(self):
        import apps.leave.signals  # noqa: F401 — register signal handlers
