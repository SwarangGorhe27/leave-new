from django.core.management import call_command


class TenantTestMixin:
    """Mixin to create a test tenant and run tenant migrations for django-tenants.

    Usage: inherit before `django.test.TestCase` in your test classes.
    """

    @classmethod
    def setUpTestData(cls):
        # Create tenant and run tenant migrations inside the test DB
        from apps.core.models.tenant import Tenant

        # create or reuse a tenant with schema_name 'testtenant'
        cls.tenant, created = Tenant.objects.get_or_create(
            slug='testtenant', defaults={'company_name': 'TestTenant', 'schema_name': 'testtenant'}
        )

        # run tenant migrations for this schema (applies tenant-specific tables)
        # Run tenant migrations once per test DB (best-effort)
        try:
            call_command('migrate_schemas', schema_name=cls.tenant.schema_name, interactive=False, verbosity=0)
        except Exception:
            pass

        # create a domain for the tenant if Domain model is available
        try:
            from django_tenants.models import Domain

            Domain.objects.create(domain=f'{cls.tenant.schema_name}.localhost', tenant=cls.tenant, is_primary=True)
        except Exception:
            pass

        super_methods = [getattr(base, 'setUpTestData', None) for base in cls.__mro__[1:]]
        for m in super_methods:
            if callable(m):
                try:
                    m()
                except Exception:
                    pass
