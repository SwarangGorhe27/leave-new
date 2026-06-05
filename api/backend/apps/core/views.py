from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.core.models import Tenant

from apps.core.services.tenant_provision_service import (
    TenantProvisionService,
)

from apps.core.serializers.tenant_request_serializers import (
    TenantCreateRequestSerializer,
    TenantModulesUpdateRequestSerializer
)
from apps.core.serializers.tenant_response_serializers import (
    TenantResponseSerializer,
    TenantCreateResponseSerializer,
    TenantModulesUpdateResponseSerializer,
)

from drf_spectacular.utils import extend_schema

from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.core.permissions import (
    IsPublicSchema,
    IsPlatformSuperAdmin,
)

class PublicAdminAPIView(APIView):

    authentication_classes = [
        JWTAuthentication,
    ]

    permission_classes = [
        IsAuthenticated,
        IsPublicSchema,
        IsPlatformSuperAdmin,
    ]

class TenantCreateView(PublicAdminAPIView):
    serializer_class = TenantCreateRequestSerializer

    def post(self, request):

        serializer = TenantCreateRequestSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        tenant = TenantProvisionService.provision_tenant(
            company_name=serializer.validated_data["company_name"],
            slug=serializer.validated_data["slug"],
            domain=serializer.validated_data["domain"],
            plan_tier=serializer.validated_data["plan_tier"],
        )

        response_serializer = (
            TenantCreateResponseSerializer(
                {
                    "message": "Tenant created successfully",
                    "tenant_id": tenant.id,
                    "schema_name": tenant.schema_name,
                }
            )
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

@extend_schema(
    operation_id="list_tenants",
)
class TenantListView(PublicAdminAPIView):

    def get(self, request):

        tenants = Tenant.objects.all()

        serializer = TenantResponseSerializer(
            tenants,
            many=True,
        )

        return Response(serializer.data)

@extend_schema(
    operation_id="retrieve_tenants",
)
class TenantDetailView(PublicAdminAPIView):

    def get(self, request, tenant_id):

        tenant = Tenant.objects.get(id=tenant_id)

        serializer = TenantResponseSerializer(
            tenant
        )

        return Response(serializer.data)


class TenantActivateView(PublicAdminAPIView):

    def post(self, request, tenant_id):

        tenant = Tenant.objects.get(id=tenant_id)

        tenant.is_active = True
        tenant.save()

        return Response({
            "message": "Tenant activated",
        })


class TenantSuspendView(PublicAdminAPIView):

    def post(self, request, tenant_id):

        tenant = Tenant.objects.get(id=tenant_id)

        tenant.is_active = False
        tenant.save()

        return Response({
            "message": "Tenant suspended",
        })


class TenantDeleteView(PublicAdminAPIView):

    def delete(self, request, tenant_id):

        tenant = Tenant.objects.get(id=tenant_id)

        tenant.delete()

        return Response({
            "message": "Tenant deleted",
        })


class TenantModulesUpdateView(PublicAdminAPIView):
    serializer_class = TenantModulesUpdateRequestSerializer

    def patch(self, request, tenant_id):

        serializer = (
            TenantModulesUpdateRequestSerializer(
                data=request.data
            )
        )

        serializer.is_valid(raise_exception=True)

        tenant = Tenant.objects.get(id=tenant_id)

        modules = serializer.validated_data["modules"]

        subscription = tenant.subscription

        subscription.enabled_modules = modules
        subscription.save()

        response_serializer = (
            TenantModulesUpdateResponseSerializer(
                {
                    "message": "Modules updated",
                    "modules": modules,
                }
            )
        )

        return Response(
            response_serializer.data
        )