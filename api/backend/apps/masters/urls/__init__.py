from django.urls import include, path

app_name = "masters"

urlpatterns = [
    path("audit-additions/", include("apps.masters.urls.audit_additions")),
    path("passport-visa/", include("apps.masters.urls.passport_visa")),
    path("personal/", include("apps.masters.urls.personal")),
    path("education/", include("apps.masters.urls.education")),
    path("employment/", include("apps.masters.urls.employment")),
    path("hr-setup/", include("apps.masters.urls.hr_setup")),
    path("insurance/", include("apps.masters.urls.insurance")),
    path("location/", include("apps.masters.urls.location")),
    path("misc/", include("apps.masters.urls.misc")),
    path("organization/", include("apps.masters.urls.organization")),
    path("payroll/", include("apps.masters.urls.payroll")),
    path("performance-training/", include("apps.masters.urls.performance_training")),
    path("recruitment/", include("apps.masters.urls.recruitment")),
    path("workflow-security/", include("apps.masters.urls.workflow_security")),
    # Generic/unified master endpoints (catch-all for dynamic master names)
    # These should be LAST so they don't override the specific paths above
    path("", include("apps.masters.urls.generic")),
]

__all__ = ["app_name", "urlpatterns"]
