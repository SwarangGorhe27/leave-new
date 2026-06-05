"""
URL routes for Fines & Damages Register admin APIs.

Mounted at: /api/admin/setup/   (via urls/admin/__init__.py)

Fines:
  GET  POST   setup/fines/
  GET  PUT  PATCH  DELETE   setup/fines/<fineId>/
  PATCH   setup/fines/<fineId>/status/
  GET     setup/fines/stats/
  GET     setup/fines/export/

Damages:
  GET  POST   setup/damages/
  GET  PUT  PATCH  DELETE   setup/damages/<damageId>/
  GET     setup/damages/stats/
  GET     setup/damages/export/

Employee helpers (also registered here for convenience):
  GET     employees/dropdown/
  GET     employees/search/
"""

from django.urls import path

from apps.employees.views.admin.fines_damages_view import (
    DamageDetailView,
    DamageExportView,
    DamageListCreateView,
    DamageStatsView,
    EmployeeDropdownView,
    EmployeeSearchView,
    FineDetailView,
    FineExportView,
    FineListCreateView,
    FineStatsView,
    FineStatusView,
)

urlpatterns = [
    # ── Fines ────────────────────────────────────────────────────────────
    path("fines/stats/", FineStatsView.as_view(), name="fine-stats"),
    path("fines/export/", FineExportView.as_view(), name="fine-export"),
    path("fines/", FineListCreateView.as_view(), name="fine-list-create"),
    path("fines/<uuid:fine_id>/status/", FineStatusView.as_view(), name="fine-status"),
    path("fines/<uuid:fine_id>/", FineDetailView.as_view(), name="fine-detail"),

    # ── Property Damages ─────────────────────────────────────────────────
    path("damages/stats/", DamageStatsView.as_view(), name="damage-stats"),
    path("damages/export/", DamageExportView.as_view(), name="damage-export"),
    path("damages/", DamageListCreateView.as_view(), name="damage-list-create"),
    path("damages/<uuid:damage_id>/", DamageDetailView.as_view(), name="damage-detail"),
]

# Employee helper URLs (mounted separately in __init__.py under employees/)
employee_urlpatterns = [
    path("dropdown/", EmployeeDropdownView.as_view(), name="employee-dropdown"),
    path("search/", EmployeeSearchView.as_view(), name="employee-search"),
]
