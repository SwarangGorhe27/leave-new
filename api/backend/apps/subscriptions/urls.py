"""API routes for the Subscriptions module. Register routers and custom endpoints here."""
from django.urls import path

from apps.subscriptions.views import (
    SubscriptionDetailView,
    SubscriptionUpdateView,
    SubscriptionCancelView,
    SubscriptionRenewView,
)

urlpatterns = [

    path(
        "<uuid:tenant_id>/",
        SubscriptionDetailView.as_view(),
    ),

    path(
        "<uuid:tenant_id>/update/",
        SubscriptionUpdateView.as_view(),
    ),

    path(
        "<uuid:tenant_id>/cancel/",
        SubscriptionCancelView.as_view(),
    ),

    path(
        "<uuid:tenant_id>/renew/",
        SubscriptionRenewView.as_view(),
    ),
]