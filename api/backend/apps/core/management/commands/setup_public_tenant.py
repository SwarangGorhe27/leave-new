from django.core.management.base import BaseCommand
from django_tenants.utils import get_public_schema_name

from apps.core.models import Tenant, Domain


class Command(BaseCommand):

    help = "Create public tenant and localhost domains"

    def handle(self, *args, **options):

        public_schema = get_public_schema_name()

        # ---------------------------------------------------
        # CREATE PUBLIC TENANT
        # ---------------------------------------------------

        public_tenant, created = Tenant.objects.get_or_create(
            schema_name=public_schema,
            defaults={
                "company_name": "Public",
                "slug": "public",
                "paid_until": None,
                "on_trial": False,
                "is_active": True,
                # "purchased_modules": [],
            },
        )

        if created:

            self.stdout.write(
                self.style.SUCCESS(
                    f"Public tenant created ({public_schema})"
                )
            )

        else:

            self.stdout.write(
                self.style.WARNING(
                    f"Public tenant already exists ({public_schema})"
                )
            )

        # ---------------------------------------------------
        # LOCALHOST DOMAIN
        # ---------------------------------------------------

        localhost_domain, created = Domain.objects.get_or_create(
            domain="localhost",
            defaults={
                "tenant": public_tenant,
                "is_primary": True,
            },
        )

        if created:

            self.stdout.write(
                self.style.SUCCESS(
                    "localhost domain created"
                )
            )

        # ---------------------------------------------------
        # 127.0.0.1 DOMAIN
        # ---------------------------------------------------

        ip_domain, created = Domain.objects.get_or_create(
            domain="127.0.0.1",
            defaults={
                "tenant": public_tenant,
                "is_primary": False,
            },
        )

        if created:

            self.stdout.write(
                self.style.SUCCESS(
                    "127.0.0.1 domain created"
                )
            )

        # ---------------------------------------------------
        # DONE
        # ---------------------------------------------------

        self.stdout.write(
            self.style.SUCCESS(
                "Public tenant setup completed"
            )
        )