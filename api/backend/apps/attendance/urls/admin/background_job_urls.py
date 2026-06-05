"""URL routing for attendance background job APIs."""

from django.urls import path

from apps.attendance.views.admin.jobs.background_job_views import AttendanceBackgroundJobAPI


urlpatterns = [
    path("jobs/trigger/daily-compute", AttendanceBackgroundJobAPI.trigger_daily_compute, name="attendance-jobs-trigger-daily-compute"),
    path("jobs/<uuid:job_id>/retry", AttendanceBackgroundJobAPI.retry_job, name="attendance-jobs-retry"),
    path("jobs/<uuid:job_id>", AttendanceBackgroundJobAPI.get_job_detail, name="attendance-jobs-detail"),
    path("jobs", AttendanceBackgroundJobAPI.list_jobs, name="attendance-jobs-list"),
]
