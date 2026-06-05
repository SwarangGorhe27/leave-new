#!/usr/bin/env python3
"""
Fix missing public tenant
"""

import sys
import os
import django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.core.models.tenant import Tenant
from django.db import transaction

def fix_tenants():
    """Create missing public tenant."""
    
    print("Fixing tenant configuration...")
    
    with transaction.atomic():
        # Create public tenant (required by django-tenants)
        public_tenant, created = Tenant.objects.get_or_create(
            schema_name='public',
            defaults={
                'company_name': 'Public Tenant',
                'slug': 'public',
                'is_active': True,
            }
        )
        
        if created:
            print(f"Created public tenant: {public_tenant.schema_name}")
        else:
            print(f"Public tenant already exists: {public_tenant.schema_name}")
        
        print("\nAll tenants:")
        for tenant in Tenant.objects.all():
            print(f"- {tenant.schema_name}: {tenant.company_name} ({'active' if tenant.is_active else 'inactive'})")
        
        print("\n" + "="*50)
        print("TENANT SETUP COMPLETE!")
        print("="*50)
        print("You can now access:")
        print("- ACME Tenant: http://acme.localhost:8000/api/")
        print("- Or use 127.0.0.1:8000 (will use public tenant)")

if __name__ == "__main__":
    fix_tenants()