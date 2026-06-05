import uuid

from django.db import models
from django_tenants.models import TenantMixin


class Tenant(TenantMixin):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    company_name = models.CharField(
        max_length=255,
    )

    slug = models.SlugField(
        unique=True,
    )

    schema_name = models.CharField(
        max_length=63,
        unique=True,
    )

    paid_until = models.DateField(
        null=True,
        blank=True,
    )

    on_trial = models.BooleanField(
        default=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    auto_create_schema = True
    auto_drop_schema = True
    class Meta:
        db_table = "tenants"

    def save(self, *args, **kwargs):

        if not self.schema_name:
            self.schema_name = self.slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name