"""
Django management command to seed employee module data.

Usage:
    python manage.py seed_employees
    python manage.py seed_employees --clear  (to delete all employee data first)
"""

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import get_tenant_model, tenant_context
from apps.employees.seed_data import seed_all_data
from apps.employees.models import (
    Employee, EmployeePersonalDetails, EmployeeEmploymentDetails,
    EmployeeAddress, EmployeeContacts, EmployeeFamilyMember, EmployeeEducation,
    EmployeeRoleAssignment
)


class Command(BaseCommand):
    help = "Seed comprehensive employee data into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all employee data before seeding',
        )
        parser.add_argument(
            '--masters-only',
            action='store_true',
            help='Seed only master data without transaction records',
        )
        parser.add_argument(
            '--schema',
            type=str,
            help='Tenant schema name to use for seeding, for example acme',
        )

    def handle(self, *args, **options):
        if options['clear']:
            schema_name = options.get("schema")
        if not schema_name:
            self.stdout.write(self.style.ERROR("\n  Please pass --schema <tenant_schema> to seed tenant data."))
            self.stdout.write(self.style.ERROR("  Example: python manage.py seed_employees --schema acme"))
            return

        TenantModel = get_tenant_model()
        try:
            tenant = TenantModel.objects.get(schema_name=schema_name)
        except TenantModel.DoesNotExist:
            raise CommandError(f"Tenant with schema '{schema_name}' not found")

        with tenant_context(tenant):
            if options['clear']:
                self.stdout.write(self.style.WARNING("\n  Clearing all employee data in tenant schema '%s'..." % schema_name))
                self._clear_employee_data()
                self.stdout.write(self.style.SUCCESS("✓ Employee data cleared!\n"))

            try:
                self.stdout.write(self.style.SUCCESS("\n Starting employee data seeding..."))
                seed_all_data(masters_only=options['masters_only'])
                self.stdout.write(self.style.SUCCESS("\n Employee data seeding completed successfully!"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\nError during seeding: {str(e)}"))
                raise

    def _clear_employee_data(self):
        """Clear all employee-related data in correct dependency order."""
        # Transaction models (no dependencies on other transactions)
        EmployeeRoleAssignment.objects.all().delete()
        EmployeeFamilyMember.objects.all().delete()
        EmployeeEducation.objects.all().delete()
        EmployeeAddress.objects.all().delete()
        EmployeeContacts.objects.all().delete()
        EmployeeEmploymentDetails.objects.all().delete()
        EmployeePersonalDetails.objects.all().delete()
        Employee.objects.all().delete()
