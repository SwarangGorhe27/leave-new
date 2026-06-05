import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from django.contrib.auth import get_user_model
from apps.core.models import Tenant

User = get_user_model()

print('PUBLIC USERS:')
for u in User.objects.all()[:20]:
    print('  ', u.id, u.email, u.is_active, u.is_staff, u.is_superuser)
print('----')

try:
    tenant = Tenant.objects.get(schema_name='acme')
except Exception as e:
    print('tenant error', e)
else:
    with schema_context('acme'):
        print('ACME USERS:')
        for u in User.objects.all()[:20]:
            print('  ', u.id, u.email, u.is_active, u.is_staff, u.is_superuser)
        print('ACME USER COUNT', User.objects.count())
