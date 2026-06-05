"""Shared fixtures for attendance app tests."""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from django_tenants.utils import schema_context
from rest_framework.test import APIClient

from apps.subscriptions.models.models import Subscription


def ensure_tenant_subscription(tenant) -> None:
    """Create an active subscription so tenant middleware allows API requests."""
    with schema_context("public"):
        if Subscription.objects.filter(client=tenant).exists():
            return
        today = date.today()
        Subscription.objects.create(
            client=tenant,
            plan_tier=Subscription.PlanTier.ENTERPRISE,
            billing_cycle=Subscription.BillingCycle.MONTHLY,
            status=Subscription.Status.ACTIVE,
            enabled_modules=["employees", "attendance", "leave", "payroll"],
            current_period_start=today - timedelta(days=30),
            current_period_end=today + timedelta(days=365),
            is_trial=False,
        )


def tenant_api_client(user, tenant_domain: str = "empatt.localhost") -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    host = tenant_domain if ":" in tenant_domain else f"{tenant_domain}:8000"
    client.defaults["HTTP_HOST"] = host
    return client


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()
