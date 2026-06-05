from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from apps.accounts.serializers import (
    TenantTokenObtainPairSerializer,
)


class LoginView(TokenObtainPairView):

    serializer_class = (
        TenantTokenObtainPairSerializer
    )