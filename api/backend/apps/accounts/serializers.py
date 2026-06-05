from django.db import connection

from django_tenants.utils import (
    get_public_schema_name,
)

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)

from apps.security.services import (
    build_jwt_security_claims,
)


class TenantTokenObtainPairSerializer(
    TokenObtainPairSerializer
):

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        # ---------------------------------------------------------
        # CORE USER FIELDS
        # ---------------------------------------------------------

        token["email"] = user.email
        token["user_id"] = str(user.id)

        # ---------------------------------------------------------
        # PUBLIC SCHEMA
        # ---------------------------------------------------------

        if (
            connection.schema_name
            == get_public_schema_name()
        ):

            token["is_platform_user"] = True

            return token

        # ---------------------------------------------------------
        # TENANT SCHEMA
        # ---------------------------------------------------------

        token["is_platform_user"] = False

        employee = getattr(
            user,
            "employee_profile",
            None,
        )

        # User may exist without employee profile
        if not employee:
            return token

        token["employee_id"] = str(employee.id)

        token["employee_code"] = (
            employee.employee_code
        )

        token["company_id"] = str(
            employee.company.id
        )

        # ---------------------------------------------------------
        # RBAC CLAIMS
        # ---------------------------------------------------------

        try:
            rbac = build_jwt_security_claims(
                employee
            )
            token["roles"] = rbac["roles"]
            token["permissions"] = (
                rbac["permissions"]
            )
            # token["menu_permissions"] = rbac["menu_permissions"]
            # token["data_scopes"] = rbac["data_scopes"]
            token["is_super_admin"] = (
                rbac.get(
                    "is_super_admin",
                    False,
                )
            )

        except Exception:
            # Graceful fallback during migrations
            token["roles"] = []
            token["permissions"] = []
            # token["menu_permissions"] = {}
            # token["data_scopes"] = {}
            token["is_super_admin"] = False

        return token