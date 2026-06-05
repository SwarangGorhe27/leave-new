"""
Repair django_migrations when 0005_employee_position_history is recorded but 0004_team is not.

This happens after the old 0003_team migration was renamed to 0004_team while the DB
already had 0005+ applied via the previous graph.

Usage:
    python manage.py fix_employees_0004_team
    python manage.py fix_employees_0004_team --schema=acme
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from django_tenants.utils import get_tenant_model, schema_context


MIGRATION_APP = "employees"
MIGRATION_NAME = "0004_team"
DEPENDENCY_CHECK = "0005_employee_position_history"


class Command(BaseCommand):
    help = "Insert employees.0004_team into django_migrations when it is missing but 0005 is applied."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            type=str,
            help="Only fix this schema (e.g. public, acme). Default: public + all tenants.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be fixed without writing.",
        )

    def handle(self, *args, **options):
        schema_arg = options.get("schema")
        dry_run = options["dry_run"]

        schemas = []
        if schema_arg:
            schemas.append(schema_arg)
        else:
            schemas.append("public")
            for tenant in get_tenant_model().objects.all():
                schemas.append(tenant.schema_name)

        fixed = 0
        for schema in schemas:
            if self._fix_schema(schema, dry_run=dry_run):
                fixed += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f"Dry run: would fix {fixed} schema(s)."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Fixed {fixed} schema(s)."))
            self.stdout.write("Run: python manage.py migrate_schemas")

    def _fix_schema(self, schema: str, *, dry_run: bool) -> bool:
        with schema_context(schema):
            has_0004 = self._migration_applied(MIGRATION_NAME)
            has_0005 = self._migration_applied(DEPENDENCY_CHECK)

            if has_0004:
                self.stdout.write(f"[{schema}] OK — {MIGRATION_NAME} already applied.")
                return False

            if not has_0005:
                self.stdout.write(
                    f"[{schema}] Skip — {DEPENDENCY_CHECK} not applied (no inconsistency)."
                )
                return False

            if dry_run:
                self.stdout.write(
                    f"[{schema}] Would insert {MIGRATION_APP}.{MIGRATION_NAME} (fake)."
                )
                return True

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO django_migrations (app, name, applied)
                    VALUES (%s, %s, %s)
                    """,
                    [MIGRATION_APP, MIGRATION_NAME, timezone.now()],
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"[{schema}] Recorded {MIGRATION_APP}.{MIGRATION_NAME} as applied (fake)."
                )
            )
            return True

    @staticmethod
    def _migration_applied(name: str) -> bool:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1 FROM django_migrations
                WHERE app = %s AND name = %s
                LIMIT 1
                """,
                [MIGRATION_APP, name],
            )
            return cursor.fetchone() is not None
