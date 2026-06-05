import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django_tenants.utils import get_tenant_model, tenant_context

from apps.employees.models.masters.organization import Bank


CSV_TO_MODEL_FIELDS = {
    "BANK": "name",
    "BRANCH": "branch",
    "CENTRE": "centre",
    "DISTRICT": "district",
    "STATE": "state",
    "ADDRESS": "address",
    "CONTACT": "contact",
    "CITY": "city",
    "ISO3166": "iso3166",
    "MICR": "micr",
}

DEFAULT_CSV_PATH = (
    Path(__file__).resolve().parents[2] / "banc_csv" / "IFSC.csv"
)


def normalize_csv_value(value):
    value = (value or "").strip()
    return value if value else "NaN"


class Command(BaseCommand):
    help = "Import bank and IFSC branch details from apps/employees/banc_csv/IFSC.csv."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema",
            type=str,
            required=True,
            help="Tenant schema name to import bank data into.",
        )
        parser.add_argument(
            "--csv-path",
            type=str,
            default=str(DEFAULT_CSV_PATH),
            help="CSV file path. Defaults to apps/employees/banc_csv/IFSC.csv.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=2000,
            help="Number of records to insert/update per batch.",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        TenantModel = get_tenant_model()
        try:
            tenant = TenantModel.objects.get(schema_name=options["schema"])
        except TenantModel.DoesNotExist as exc:
            raise CommandError(
                f"Tenant with schema '{options['schema']}' not found"
            ) from exc

        batch_size = options["batch_size"]
        if batch_size <= 0:
            raise CommandError("--batch-size must be greater than 0")

        with tenant_context(tenant):
            imported, created, updated = self.import_csv(csv_path, batch_size)

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {imported} rows into mst_bank "
                f"({created} created, {updated} updated)."
            )
        )

    def import_csv(self, csv_path, batch_size):
        imported = created = updated = 0
        batch = []

        with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)
            missing_headers = {"IFSC", *CSV_TO_MODEL_FIELDS.keys()} - set(
                reader.fieldnames or []
            )
            if missing_headers:
                raise CommandError(
                    "CSV is missing required column(s): "
                    + ", ".join(sorted(missing_headers))
                )

            for row_number, row in enumerate(reader, start=2):
                ifsc = normalize_csv_value(row.get("IFSC"))
                code = ifsc if ifsc != "NaN" else f"NaN-{row_number}"
                bank_data = {
                    "code": code,
                    "ifsc_prefix": ifsc[:4] if ifsc != "NaN" else "NaN",
                }
                for csv_field, model_field in CSV_TO_MODEL_FIELDS.items():
                    bank_data[model_field] = normalize_csv_value(row.get(csv_field))
                batch.append(bank_data)

                if len(batch) >= batch_size:
                    batch_created, batch_updated = self.upsert_batch(batch)
                    created += batch_created
                    updated += batch_updated
                    imported += len(batch)
                    batch = []

            if batch:
                batch_created, batch_updated = self.upsert_batch(batch)
                created += batch_created
                updated += batch_updated
                imported += len(batch)

        return imported, created, updated

    @transaction.atomic
    def upsert_batch(self, rows):
        existing = {
            bank.code: bank
            for bank in Bank.objects.filter(code__in=[row["code"] for row in rows])
        }
        to_create = []
        to_update = []
        update_fields = [
            "name",
            "ifsc_prefix",
            "branch",
            "centre",
            "district",
            "state",
            "address",
            "contact",
            "city",
            "iso3166",
            "micr",
        ]

        for row in rows:
            bank = existing.get(row["code"])
            if bank is None:
                to_create.append(Bank(**row))
                continue
            for field in update_fields:
                setattr(bank, field, row[field])
            to_update.append(bank)

        if to_create:
            Bank.objects.bulk_create(to_create, batch_size=len(to_create))
        if to_update:
            Bank.objects.bulk_update(
                to_update,
                update_fields,
                batch_size=len(to_update),
            )

        return len(to_create), len(to_update)
