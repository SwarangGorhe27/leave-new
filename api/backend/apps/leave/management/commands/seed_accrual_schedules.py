from django.core.management.base import BaseCommand

from apps.leave.seed_accrual_schedules import seed_accrual_schedules


class Command(BaseCommand):
    help = "Seed leave accrual schedule master data for a tenant schema."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            default="acme",
            help="Tenant schema name. Defaults to acme.",
        )

    def handle(self, *args, **options):
        schema_name = options["schema"]
        schedules = seed_accrual_schedules(schema_name)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(schedules)} accrual schedules in schema '{schema_name}'."
            )
        )

        for schedule in schedules:
            self.stdout.write(
                f"{schedule['id']} | {schedule['leave_type_code']} | "
                f"{schedule['frequency']} | day {schedule['run_day_of_month']}"
            )
