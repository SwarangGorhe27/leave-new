from django.urls import path

from apps.core.views import (
    TenantCreateView,
    TenantListView,
    TenantDetailView,
    TenantActivateView,
    TenantSuspendView,
    TenantDeleteView,
    TenantModulesUpdateView,
)

urlpatterns = [

    path("tenants/", TenantListView.as_view()),
    path("tenants/create/", TenantCreateView.as_view()),

    path("tenants/<uuid:tenant_id>/", TenantDetailView.as_view()),

    path(
        "tenants/<uuid:tenant_id>/activate/",
        TenantActivateView.as_view(),
    ),

    path(
        "tenants/<uuid:tenant_id>/suspend/",
        TenantSuspendView.as_view(),
    ),

    path(
        "tenants/<uuid:tenant_id>/delete/",
        TenantDeleteView.as_view(),
    ),

    path(
        "tenants/<uuid:tenant_id>/modules/",
        TenantModulesUpdateView.as_view(),
    ),
]