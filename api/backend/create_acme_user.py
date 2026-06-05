import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from apps.accounts.models import User
from apps.core.models import Tenant

try:
    tenant = Tenant.objects.get(schema_name='acme')
except Exception as exc:
    print('tenant lookup failed:', exc)
    raise

with schema_context('acme'):
    if User.objects.filter(email='admin@acme.localhost').exists():
        print('User already exists: admin@acme.localhost')
    else:
        user = User.objects.create_user(
            email='admin@acme.localhost',
            password='Admin@1234',
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        print('Created user:', user.email, user.id)
    print('ACME user count', User.objects.count())
    for u in User.objects.all():
        print('  ', u.email, u.username, u.is_active, u.is_staff, u.is_superuser)
