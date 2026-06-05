import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("hrms")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


class TenantAwareTask(app.Task):
    """Base task that wraps execution in tenant context."""

    def apply_async(self, args=None, kwargs=None, **options):
        from django_tenants.utils import get_tenant_model
        from django.db import connection

        kwargs = kwargs or {}
        if "tenant_schema" not in kwargs:
            tenant = getattr(connection, "tenant", None)
            if tenant:
                kwargs["tenant_schema"] = tenant.schema_name
        return super().apply_async(args, kwargs, **options)

    def __call__(self, *args, **kwargs):
        from django_tenants.utils import get_tenant_model, tenant_context

        tenant_schema = kwargs.pop("tenant_schema", None)
        if tenant_schema:
            TenantModel = get_tenant_model()
            try:
                tenant = TenantModel.objects.get(schema_name=tenant_schema)
                with tenant_context(tenant):
                    return self.run(*args, **kwargs)
            except TenantModel.DoesNotExist:
                raise ValueError(f"Tenant with schema '{tenant_schema}' not found")
        return self.run(*args, **kwargs)


app.Task = TenantAwareTask
