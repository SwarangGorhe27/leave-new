"""
URL Configuration for Access Card API endpoints.

Routes:
    GET    /employees/{employee_id}/access-cards
    POST   /employees/{employee_id}/access-cards
    GET    /employees/{employee_id}/access-cards/{card_id}
    PATCH  /employees/{employee_id}/access-cards/{card_id}
    DELETE /employees/{employee_id}/access-cards/{card_id}
"""

from django.urls import path

from apps.employees.views.admin.access_card_view import (
    AccessCardListCreateView,
    AccessCardDetailView,
)

urlpatterns = [
    # List all access cards and create new access card
    path(
        "<uuid:employee_id>/access-cards",
        AccessCardListCreateView.as_view(),
        name="access_card_list_create"
    ),
    
    # Get, update, and delete specific access card
    path(
        "<uuid:employee_id>/access-cards/<uuid:card_id>",
        AccessCardDetailView.as_view(),
        name="access_card_detail"
    ),
]
