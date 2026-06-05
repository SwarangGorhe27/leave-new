"""
Add Employee URLs — Admin Side

Base: /api/admin/employees/

  POST  add/                    → Create new employee (all 8 sections)
  POST  rehire/                 → Rehire a former employee
  GET   former/                 → Search former employees for rehire panel
  POST  bulk-import/            → Upload Excel/CSV for bulk import
  GET   bulk-import/template/   → Download import template (.xlsx v1.2)
  POST  draft/                  → Save form draft
  GET   draft/<draft_id>/       → Retrieve saved draft
"""

from django.urls import path

from apps.employees.views.admin.add_employee_view import (
    AdminAddEmployeeView,
    AdminEmployeeDirectoryListView,
    BulkImportTemplateView,
    BulkImportView,
    FormerEmployeeListView,
    GetDraftView,
    RehireEmployeeView,
    SaveDraftView,
)

app_name = "admin_add_employee"

urlpatterns = [
    # Directory list
    path("list/", AdminEmployeeDirectoryListView.as_view(), name="admin_employee_list"),

    # New employee
    path("add/", AdminAddEmployeeView.as_view(), name="admin_employee_add"),

    # Rehire
    path("rehire/", RehireEmployeeView.as_view(), name="admin_employee_rehire"),
    path("former/", FormerEmployeeListView.as_view(), name="admin_employee_former"),

    # Bulk import — template must come before the upload path
    path("bulk-import/template/", BulkImportTemplateView.as_view(), name="admin_bulk_import_template"),
    path("bulk-import/", BulkImportView.as_view(), name="admin_bulk_import"),

    # Draft
    path("draft/", SaveDraftView.as_view(), name="admin_employee_draft_save"),
    path("draft/<uuid:draft_id>/", GetDraftView.as_view(), name="admin_employee_draft_get"),
]
