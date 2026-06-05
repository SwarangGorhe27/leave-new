import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from django.contrib.auth import get_user_model
from apps.core.models import Tenant

User = get_user_model()

print('PUBLIC USERS:')
for u in User.objects.all():
    print('TYPE:', type(u), 'ID:', u.id, 'EMAIL:', repr(getattr(u,'email',None)), 'USERNAME:', repr(getattr(u,'username',None)), 'ACTIVE:', u.is_active, 'STAFF:', u.is_staff, 'SUPERUSER:', u.is_superuser)
print('PUBLIC COUNT', User.objects.count())
print('----')
try:
    tenant = Tenant.objects.get(schema_name='acme')
except Exception as e:
    print('tenant error', e)
else:
    with schema_context('acme'):
        print('ACME USERS:')
        for u in User.objects.all():
            print('TYPE:', type(u), 'ID:', u.id, 'EMAIL:', repr(getattr(u,'email',None)), 'USERNAME:', repr(getattr(u,'username',None)), 'ACTIVE:', u.is_active, 'STAFF:', u.is_staff, 'SUPERUSER:', u.is_superuser)
        print('ACME COUNT', User.objects.count())
