"""
URL configuration for admin Bank, PF, and ESI APIs.
"""

from django.urls import path

from apps.employees.views.admin.bank_statutory_view import (
    BankAccountAdminView,
    BankAccountItemAdminView,
    BankStatutoryCreateView,
    BankStatutoryDetailsView,
    StatutoryContributionsAdminView,
)


urlpatterns = [
    path(
        "bank-statutory",
        BankStatutoryCreateView.as_view(),
        name="admin_bank_statutory_create",
    ),
    path(
        "bank-statutory/",
        BankStatutoryCreateView.as_view(),
        name="admin_bank_statutory_create_slash",
    ),
    path(
        "<uuid:employee_id>/bank-statutory",
        BankStatutoryDetailsView.as_view(),
        name="admin_bank_statutory_details",
    ),
    path(
        "<uuid:employee_id>/bank-statutory/",
        BankStatutoryDetailsView.as_view(),
        name="admin_bank_statutory_details_slash",
    ),
    path(
        "<uuid:employee_id>/bank-statutory/bank-account",
        BankAccountAdminView.as_view(),
        name="admin_bank_account_update",
    ),
    path(
        "<uuid:employee_id>/bank-statutory/bank-account/",
        BankAccountAdminView.as_view(),
        name="admin_bank_account_update_slash",
    ),
    path(
        "<uuid:employee_id>/bank-statutory/bank-account/<uuid:account_id>",
        BankAccountItemAdminView.as_view(),
        name="admin_bank_account_delete",
    ),
    path(
        "<uuid:employee_id>/bank-statutory/bank-account/<uuid:account_id>/",
        BankAccountItemAdminView.as_view(),
        name="admin_bank_account_delete_slash",
    ),
    path(
        "<uuid:employee_id>/bank-statutory/contributions",
        StatutoryContributionsAdminView.as_view(),
        name="admin_statutory_contributions",
    ),
    path(
        "<uuid:employee_id>/bank-statutory/contributions/",
        StatutoryContributionsAdminView.as_view(),
        name="admin_statutory_contributions_slash",
    ),
]
