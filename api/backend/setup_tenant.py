#!/usr/bin/env python
import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from apps.core.models import Tenant, Domain
from apps.subscriptions.models import Subscription

TODAY = timezone.now().date()
NEXT_MONTH = TODAY + timedelta(days=30)

# Create tenant if it doesn't exist
tenant, created = Tenant.objects.get_or_create(
    schema_name='acme',
    defaults={
        'company_name': 'ACME Corp',
        'slug': 'acme',
        'is_active': True,
    }
)

if created:
    print(f"✓ Tenant 'acme' created successfully")
else:
    print(f"✓ Tenant 'acme' already exists")

# Create domain if it doesn't exist
domain, created = Domain.objects.get_or_create(
    domain='acme.localhost',
    defaults={
        'tenant': tenant,
        'is_primary': True,
    }
)

if created:
    print(f"✓ Domain 'acme.localhost' created successfully")
else:
    print(f"✓ Domain 'acme.localhost' already exists")

# Create subscription if it doesn't exist
subscription, created = Subscription.objects.get_or_create(
    client=tenant,
    defaults={
        'plan_tier': Subscription.PlanTier.STARTER,
        'billing_cycle': Subscription.BillingCycle.MONTHLY,
        'status': Subscription.Status.ACTIVE,
        'enabled_modules': ['employees', 'attendance', 'leave'],
        'current_period_start': TODAY,
        'current_period_end': NEXT_MONTH,
        'is_trial': False,
        'max_employees': 50,
        'max_storage_gb': 5,
    },
)

if created:
    print(f"✓ Subscription created for tenant 'acme'")
else:
    print(f"✓ Subscription already exists for tenant 'acme'")

# Create a default tenant user so tenant login is possible.
User = get_user_model()
with schema_context('acme'):
    tenant_admin_email = 'admin@acme.localhost'
    tenant_admin_password = 'Admin@1234'
    if User.objects.filter(email=tenant_admin_email).exists():
        print(f"✓ Tenant admin user already exists: {tenant_admin_email}")
    else:
        User.objects.create_user(
            email=tenant_admin_email,
            password=tenant_admin_password,
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        print(
            f"✓ Tenant admin user created: {tenant_admin_email} / {tenant_admin_password}"
        )

print("\n✓ Setup complete! You can now start the server.")
print("  - Frontend: http://localhost:5173")
print("  - Backend: http://acme.localhost:8000")
