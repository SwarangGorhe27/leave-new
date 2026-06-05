"""Project-level views (root health, dev entry points)."""

from django.http import JsonResponse


def root(request):
    """Landing page for the dev server — confirms the API is up."""
    base = request.build_absolute_uri("/").rstrip("/")

    return JsonResponse(
        {
            "status": "ok",
            "message": "HRMS API server is running",
            "tenant_host": request.get_host(),
            "base_url": base,
            "entrypoints": {
                "swagger": f"{base}/api/docs/",
                "redoc": f"{base}/api/redoc/",
                "openapi_schema": f"{base}/api/schema/",
                "django_admin": f"{base}/admin/",
                "employee_login": f"{base}/api/employees/login/",
                "org_chart_tree": f"{base}/api/employees/org-chart/tree/",
                "employee_search": f"{base}/api/employees/employees/search/",
            },
            "note": "Use http:// (not https://) for the Django development server.",
        }
    )
