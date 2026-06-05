#!/usr/bin/env python3
"""
Create tenant data for django-tenants setup
"""

import sys
import os
import django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.core.models.tenant import Tenant
from django.db import transaction

def create_tenants():
    """Create public and acme tenants."""
    
    print("Creating tenants...")
    
    with transaction.atomic():
        # Create public tenant (required by django-tenants)
        public_tenant, created = Tenant.objects.get_or_create(
            schema_name='public',
            defaults={
                'name': 'Public Tenant',
                'is_active': True,
            }
        )
        if created:
            print(f"✓ Created public tenant: {public_tenant.schema_name}")
        else:
            print(f"✓ Public tenant already exists: {public_tenant.schema_name}")
        
        # Create acme tenant (our test tenant)
        acme_tenant, created = Tenant.objects.get_or_create(
            schema_name='acme',
            defaults={
                'name': 'ACME Corporation',
                'is_active': True,
            }
        )
        if created:
            print(f"✓ Created ACME tenant: {acme_tenant.schema_name}")
        else:
            print(f"✓ ACME tenant already exists: {acme_tenant.schema_name}")
        
        print("\n" + "="*50)
        print("TENANTS CREATED SUCCESSFULLY!")
        print("="*50)
        print(f"Public Tenant ID: {public_tenant.id}")
        print(f"ACME Tenant ID: {acme_tenant.id}")
        print("\nYou can now access:")
        print("- Public: http://public.localhost:8000/")
        print("- ACME: http://acme.localhost:8000/")

if __name__ == "__main__":
    create_tenants()