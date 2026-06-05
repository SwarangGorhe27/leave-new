from django.core.management.base import BaseCommand

from apps.core.services.tenant_provision_service import (
    TenantProvisionService,
)


class Command(BaseCommand):

    help = "Provision a tenant"

    def add_arguments(self, parser):

        parser.add_argument(
            "--company",
            required=True,
            help="Company name",
        )

        parser.add_argument(
            "--slug",
            required=True,
            help="Tenant slug / schema name",
        )

        parser.add_argument(
            "--domain",
            required=False,
            help="Tenant domain. Defaults to <slug>.localhost.",
        )

        parser.add_argument(
            "--plan",
            default="STARTER",
            choices=[
                "STARTER",
                "PROFESSIONAL",
                "ENTERPRISE",
            ],
            help="Subscription plan tier",
        )

    def handle(self, *args, **options):

        tenant = TenantProvisionService.provision_tenant(
            company_name=options["company"],
            slug=options["slug"],
            domain=options["domain"] or f"{options['slug']}.localhost",
            plan_tier=options["plan"],
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Tenant created successfully: {tenant.schema_name}"
            )
        )
