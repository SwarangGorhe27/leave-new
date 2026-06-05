from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.core.models import Tenant, Domain
from apps.subscriptions.models import (
    Subscription,
    PLAN_MODULES,
)

from apps.core.services.migration_service import (
    MigrationService,
)


class TenantProvisionService:

    @classmethod
    @transaction.atomic
    def provision_tenant(
        cls,
        company_name,
        slug,
        domain,
        plan_tier="STARTER",
    ):

        schema_name = slug

        # Create Tenant
        tenant = Tenant.objects.create(
            company_name=company_name,
            slug=slug,
            schema_name=schema_name,
        )

        # Create Schema
        # tenant.create_schema(check_if_exists=True)

        # Create Domain
        Domain.objects.create(
            domain=domain,
            tenant=tenant,
            is_primary=True,
        )

        # Resolve modules from plan
        enabled_modules = PLAN_MODULES.get(
            plan_tier,
            [],
        )

        today = timezone.now().date()

        # Create Subscription
        Subscription.objects.create(
            client=tenant,
            plan_tier=plan_tier,
            enabled_modules=enabled_modules,
            current_period_start=today,
            current_period_end=today + timedelta(days=30),
            is_trial=True,
        )

        # Run module migrations
        # MigrationService.migrate_tenant_apps(
        #     schema_name=schema_name,
        #     purchased_modules=enabled_modules,
        # )

        return tenant