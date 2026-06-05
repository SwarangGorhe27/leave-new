from django.urls import path

from apps.employees.views.admin.policies_forms_view import (
    PolicyFormCategoryDetailView,
    PolicyFormCategoryListCreateView,
    PolicyFormDashboardView,
    PolicyFormDocumentDetailView,
    PolicyFormDocumentFileView,
    PolicyFormDocumentListCreateView,
)

urlpatterns = [
    path(
        "policies-forms/",
        PolicyFormDashboardView.as_view(),
        name="admin-policy-form-dashboard",
    ),
    path(
        "policies-forms/categories/",
        PolicyFormCategoryListCreateView.as_view(),
        name="admin-policy-form-category-list",
    ),
    path(
        "policies-forms/categories/<uuid:category_id>/",
        PolicyFormCategoryDetailView.as_view(),
        name="admin-policy-form-category-detail",
    ),
    path(
        "policies-forms/documents/",
        PolicyFormDocumentListCreateView.as_view(),
        name="admin-policy-form-document-list",
    ),
    path(
        "policies-forms/documents/<uuid:document_id>/",
        PolicyFormDocumentDetailView.as_view(),
        name="admin-policy-form-document-detail",
    ),
    path(
        "policies-forms/documents/<uuid:document_id>/file/",
        PolicyFormDocumentFileView.as_view(),
        name="admin-policy-form-document-file",
    ),
]
