#!/usr/bin/env python
import os
import django
from uuid import uuid4
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from django.contrib.auth import get_user_model
from apps.core.models import Tenant
from apps.employees.models import Employee
from apps.employees.models.masters.personal import Gender

User = get_user_model()

DEMO_USERS = [
    {
        'email': 'hr.admin@acme.com',
        'password': 'Password@123',
        'is_staff': True,
        'is_superuser': False,
        'employee_code': 'EMP-ADMIN-001',
        'first_name': 'HR',
        'last_name': 'Admin',
    },
    {
        'email': 'manager@hrms.com',
        'password': 'Manager@123',
        'is_staff': True,
        'is_superuser': False,
        'employee_code': 'EMP-MGR-001',
        'first_name': 'Manager',
        'last_name': 'User',
    },
    {
        'email': 'amit.patel@acme.com',
        'password': 'Password@123',
        'is_staff': False,
        'is_superuser': False,
        'employee_code': 'EMP-001',
        'first_name': 'Amit',
        'last_name': 'Patel',
    },
]

try:
    tenant = Tenant.objects.get(schema_name='acme')
except Tenant.DoesNotExist:
    print("✗ Tenant 'acme' not found. Run setup_tenant.py first.")
    exit(1)

with schema_context('acme'):
    # Get or create company
    from apps.employees.models.masters.organization import Company
    try:
        company = Company.objects.first()
        if not company:
            company = Company.objects.create(
                code='ACME',
                name='ACME Corporation'
            )
            print("✓ Company created: ACME Corporation")
        else:
            print(f"✓ Using existing company: {company.name}")
    except Exception as e:
        print(f"✗ Error creating company: {e}")
        exit(1)

    for user_data in DEMO_USERS:
        email = user_data.get('email')
        password = user_data.get('password')
        employee_code = user_data.get('employee_code')
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')

        # Create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'is_active': True,
                'is_staff': user_data.get('is_staff', False),
                'is_superuser': user_data.get('is_superuser', False),
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            print(f"✓ User created: {email}")
        else:
            print(f"✓ User already exists: {email}")

        # Create employee profile if it doesn't exist
        if not hasattr(user, 'employee_profile') or user.employee_profile is None:
            try:
                # Get or create a default gender
                gender, _ = Gender.objects.get_or_create(
                    code='M',
                    defaults={'label': 'Male', 'is_active': True}
                )
                
                # Set default dates
                today = datetime.now().date()
                dob = today - timedelta(days=365*30)  # Default 30 years old
                
                Employee.objects.create(
                    id=uuid4(),
                    user=user,
                    company=company,
                    employee_code=employee_code,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    date_of_joining=today,
                    date_of_birth=dob,
                    status='ACTIVE',
                    is_active=True,
                )
                print(f"  → Employee profile created: {employee_code}")
            except Exception as e:
                print(f"  ✗ Error creating employee profile: {e}")

print("\n✓ Demo users setup complete!")
print("\nLogin credentials:")
for user_data in DEMO_USERS:
    email = user_data.get('email')
    password = user_data.get('password')
    print(f"  - {email} / {password}")
