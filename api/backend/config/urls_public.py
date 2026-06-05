"""URL conf for PUBLIC schema."""

from django.contrib import admin
from django.urls import include, path

from config.views import root
 
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
 
public_schema_urlpatterns = [
 
    path("api/public/", include("apps.accounts.urls")),
 
    path("api/public/core/", include("apps.core.urls")),
]
 
 
urlpatterns = [
    path("", root, name="root"),
    path("admin/", admin.site.urls),
 
    *public_schema_urlpatterns,
 
    path("api/schema/", SpectacularAPIView.as_view( urlconf=public_schema_urlpatterns,
                                                    custom_settings={"TITLE": "HRMS Public APIs",},
                                                  ),
                                                  name="schema",
    ),
 
    path("api/docs/", SpectacularSwaggerView.as_view( url_name="schema"), name="swagger-ui",),
 
    path("api/redoc/", SpectacularRedocView.as_view( url_name="schema"), name="redoc"),
]
