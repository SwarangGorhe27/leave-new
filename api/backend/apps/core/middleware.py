# import logging

# from django.conf import settings
# from django.http import Http404

# from django_tenants.middleware.main import TenantMainMiddleware
# from django_tenants.utils import (
#     get_public_schema_name,
#     get_tenant_model,
# )

# logger = logging.getLogger(__name__)


# class CustomTenantMiddleware(TenantMainMiddleware):

#     def get_tenant(self, domain_model, hostname):

#         TenantModel = get_tenant_model()

#         hostname = hostname.lower().split(":")[0]

#         public_schema = get_public_schema_name()

#         logger.debug(
#             "Resolving tenant for hostname='%s'",
#             hostname,
#         )

#         # ---------------------------------------------------------
#         # PUBLIC SCHEMA (plain localhost / 127.0.0.1 only)
#         # ---------------------------------------------------------
#         # *.localhost (e.g. acme.localhost) uses domain or subdomain fallback below.

#         if hostname in ["localhost", "127.0.0.1"]:

#             local_tenant_schema = getattr(
#                 settings,
#                 "LOCAL_TENANT_SCHEMA",
#                 public_schema,
#             )

#             if local_tenant_schema and local_tenant_schema != public_schema:
#                 try:
#                     logger.info(
#                         "Local hostname '%s' using tenant schema '%s'",
#                         hostname,
#                         local_tenant_schema,
#                     )

#                     return TenantModel.objects.get(
#                         schema_name=local_tenant_schema
#                     )

#                 except TenantModel.DoesNotExist:
#                     logger.warning(
#                         "LOCAL_TENANT_SCHEMA '%s' not found; falling back to public",
#                         local_tenant_schema,
#                     )

#             logger.info(
#                 "Public hostname detected: '%s'",
#                 hostname,
#             )

#             return TenantModel.objects.get(
#                 schema_name=public_schema
#             )

#         # ---------------------------------------------------------
#         # DOMAIN TABLE LOOKUP
#         # ---------------------------------------------------------

#         try:

#             tenant = domain_model.objects.select_related(
#                 "tenant"
#             ).get(
#                 domain=hostname
#             ).tenant

#             logger.info(
#                 "Resolved hostname '%s' → schema '%s'",
#                 hostname,
#                 tenant.schema_name,
#             )

#             return tenant

#         except domain_model.DoesNotExist:

#             logger.warning(
#                 "No domain match found for hostname='%s'",
#                 hostname,
#             )

#         # ---------------------------------------------------------
#         # SUBDOMAIN FALLBACK
#         # ---------------------------------------------------------

#         subdomain = hostname.split(".")[0]

#         schema_name = f"{subdomain}"

#         try:

#             tenant = TenantModel.objects.get(
#                 schema_name=schema_name
#             )
#             logger.warning(
#                 "HOST RECEIVED: %s",
#                 hostname,
#             )
#             logger.info(
#                 "Subdomain fallback resolved '%s' → '%s'",
#                 hostname,
#                 schema_name,
#             )

#             return tenant

#         except TenantModel.DoesNotExist:

#             logger.error(
#                 "Tenant not found for hostname='%s'",
#                 hostname,
#             )

#             raise Http404("Tenant not found")

"""This is the new middleware that we will use,
   It was not introduced until now to avoid conflicts with existing tenants and domains during development and testing.
   But as we are creating new db so we can use this.
"""      
import logging

from django.http import Http404

from django_tenants.middleware.main import (
    TenantMainMiddleware,
)

from django_tenants.utils import (
    get_public_schema_name,
    get_tenant_model,
)

from apps.subscriptions.models import (
    Subscription,
)
from django.conf import settings

logger = logging.getLogger(__name__)


class CustomTenantMiddleware(TenantMainMiddleware):

    def get_tenant(self, domain_model, hostname):

        TenantModel = get_tenant_model()

        hostname = hostname.lower().split(":")[0]

        public_schema = get_public_schema_name()

        logger.debug(
            "Resolving tenant for hostname='%s'",
            hostname,
        )

        # ---------------------------------------------------------
        # PUBLIC SCHEMA
        # ---------------------------------------------------------

        if hostname in ["localhost", "127.0.0.1"]:

            local_tenant_schema = getattr(
                settings,
                "LOCAL_TENANT_SCHEMA",
                public_schema,
            )

            if local_tenant_schema and local_tenant_schema != public_schema:
                try:
                    logger.info(
                        "Local hostname '%s' using tenant schema '%s'",
                        hostname,
                        local_tenant_schema,
                    )

                    return TenantModel.objects.get(
                        schema_name=local_tenant_schema
                    )

                except TenantModel.DoesNotExist:
                    logger.warning(
                        "LOCAL_TENANT_SCHEMA '%s' not found; falling back to public",
                        local_tenant_schema,
                    )

            logger.info(
                "Public hostname detected: '%s'",
                hostname,
            )

            return TenantModel.objects.get(
                schema_name=public_schema
            )
        # ---------------------------------------------------------
        # DOMAIN TABLE LOOKUP
        # ---------------------------------------------------------

        try:

            domain = (
                domain_model.objects
                .select_related(
                    "tenant",
                    "tenant__subscription",
                )
                .get(domain=hostname)
            )

            tenant = domain.tenant

            # ---------------------------------------------------------
            # TENANT ACTIVE CHECK
            # ---------------------------------------------------------

            if not tenant.is_active:

                logger.warning(
                    "Blocked suspended tenant '%s'",
                    tenant.schema_name,
                )

                raise Http404(
                    "Tenant account suspended"
                )

            # ---------------------------------------------------------
            # SUBSCRIPTION ACTIVE CHECK
            # ---------------------------------------------------------

            subscription = getattr(
                tenant,
                "subscription",
                None,
            )
            print(subscription)
            if not subscription:

                logger.error(
                    "No subscription found for tenant '%s'",
                    tenant.schema_name,
                )

                raise Http404(
                    "Subscription not found"
                )

            if not subscription.is_active:

                logger.warning(
                    "Inactive subscription for tenant '%s'",
                    tenant.schema_name,
                )

                raise Http404(
                    "Subscription inactive"
                )

            logger.info(
                "Resolved hostname '%s' → schema '%s'",
                hostname,
                tenant.schema_name,
            )

            return tenant

        except domain_model.DoesNotExist:

            logger.warning(
                "No domain match found for hostname='%s'",
                hostname,
            )

        # ---------------------------------------------------------
        # SUBDOMAIN FALLBACK
        # ---------------------------------------------------------

        subdomain = hostname.split(".")[0]

        try:

            tenant = (
                TenantModel.objects
                .select_related("subscription")
                .get(schema_name=subdomain)
            )

            # ---------------------------------------------------------
            # TENANT ACTIVE CHECK
            # ---------------------------------------------------------

            if not tenant.is_active:

                logger.warning(
                    "Blocked suspended fallback tenant '%s'",
                    tenant.schema_name,
                )

                raise Http404(
                    "Tenant account suspended"
                )

            # ---------------------------------------------------------
            # SUBSCRIPTION ACTIVE CHECK
            # ---------------------------------------------------------

            subscription = getattr(
                tenant,
                "subscription",
                None,
            )

            if not subscription:

                logger.error(
                    "No subscription found for fallback tenant '%s'",
                    tenant.schema_name,
                )

                raise Http404(
                    "Subscription not found"
                )

            if not subscription.is_active:

                logger.warning(
                    "Inactive subscription for fallback tenant '%s'",
                    tenant.schema_name,
                )

                raise Http404(
                    "Subscription inactive"
                )

            logger.info(
                "Fallback resolved '%s' → '%s'",
                hostname,
                subdomain,
            )

            return tenant

        except TenantModel.DoesNotExist:

            logger.error(
                "Tenant not found for hostname='%s'",
                hostname,
            )

            raise Http404("Tenant not found")
        
       