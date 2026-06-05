from django.urls import path

from apps.accounts.views import LoginView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path("login/", LoginView.as_view()),
    path(
        "refresh/",
        TokenRefreshView.as_view(),
    ),
]