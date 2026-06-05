"""
URL configuration for admin Passport and Visa APIs.
"""

from django.urls import path

from apps.employees.views.admin.passport_view import PassportVisaDetailsView


urlpatterns = [
    path(
        "<uuid:employee_id>/passport-visa",
        PassportVisaDetailsView.as_view(),
        name="admin_passport_visa_details",
    ),
]
