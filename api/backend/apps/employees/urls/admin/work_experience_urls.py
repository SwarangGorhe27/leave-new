"""URL routes for admin work experience (ESS records)."""

from django.urls import path

from apps.employees.views.admin.work_experience_view import WorkExperienceListView

urlpatterns = [
    path(
        "<uuid:employee_id>/work-experience",
        WorkExperienceListView.as_view(),
        name="work_experience_list",
    ),
]
