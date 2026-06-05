import os
import pytest
import django
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


@pytest.fixture(scope="session", autouse=True)
def ensure_test_tenant_schema():
    """
    Ensure a tenant schema exists and tenant migrations are applied before tests.
    """
    from apps.core.models import Domain, Tenant

    try:
        tenant, _ = Tenant.objects.get_or_create(
            slug="testtenant",
            defaults={
                "company_name": "Test Tenant",
                "schema_name": "testtenant",
                "is_active": True,
            },
        )

        Domain.objects.get_or_create(
            tenant=tenant,
            domain="testtenant.localhost",
            defaults={"is_primary": True},
        )

        call_command(
            "migrate_schemas",
            schema_name=tenant.schema_name,
            interactive=False,
            verbosity=0,
        )
    except Exception:
        # Keep test bootstrap non-fatal in local environments with unrelated migration issues.
        pass
