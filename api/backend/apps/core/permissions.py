from django.db import connection

from rest_framework.permissions import (
    BasePermission,
)


class IsPublicSchema(BasePermission):

    def has_permission(self, request, view):

        return connection.schema_name == "public"


class IsPlatformSuperAdmin(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )