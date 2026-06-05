"""
URL routes for Employee Document admin APIs.
"""

from django.urls import path

from apps.employees.views.admin.document_view import (
    DocumentTypeDetailView,
    DocumentTypeListView,
    EmployeeDocumentDetailView,
    EmployeeDocumentFileView,
    EmployeeDocumentListView,
)

urlpatterns = [
    path(
        "document-types/",
        DocumentTypeListView.as_view(),
        name="admin-document-type-list",
    ),
    path(
        "document-types/<int:document_type_id>/",
        DocumentTypeDetailView.as_view(),
        name="admin-document-type-detail",
    ),
    path(
        "<uuid:employee_id>/documents/",
        EmployeeDocumentListView.as_view(),
        name="employee-document-list",
    ),
    path(
        "<uuid:employee_id>/documents/<uuid:document_id>/",
        EmployeeDocumentDetailView.as_view(),
        name="employee-document-detail",
    ),
    path(
        "<uuid:employee_id>/documents/<uuid:document_id>/file/",
        EmployeeDocumentFileView.as_view(),
        name="employee-document-file",
    ),
]
