"""Django app configuration for the Subscriptions module. Add AppConfig and startup hooks when required."""

# apps/subscriptions/apps.py

from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.subscriptions"
