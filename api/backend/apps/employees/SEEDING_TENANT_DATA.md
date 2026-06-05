# Tenant Seed Data Instructions

This file documents how to run the employee seed data for a tenant schema, such as `acme`.

## What changed

- `backend/apps/employees/seed_employees.py` now requires `--schema` so tenant seeding is explicit.
- `backend/apps/employees/seed_data.py` now supports `masters_only` mode.
- The command uses tenant context from `django-tenants`, so data is inserted into the requested tenant schema instead of the public schema.

## Recommended usage

1. Activate the project virtual environment and move to the backend directory:

```bash
cd "HRMS---ESS/backend"
. .venv/Scripts/activate
```

2. Ensure migrations have run for all tenant schemas and public schema.

```bash
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
```

3. Run seeding for a specific tenant schema, for example `acme`:

```bash
python manage.py seed_employees --schema acme
```

4. If you only want to seed master lookup data and skip transaction records:

```bash
python manage.py seed_employees --schema acme --masters-only
```

5. If you want to clear existing employee transaction rows in the tenant schema before seeding:

```bash
python manage.py seed_employees --schema acme --clear
```

## Notes

- The `--clear` flag only removes employee transaction records inside the selected tenant schema.
- The command will not run unless `--schema` is provided, so it will not accidentally seed the wrong schema.
- Use `acme` only if that tenant schema exists in your `tenants` table.

## Troubleshooting

- If you get `Tenant with schema 'acme' not found`, confirm the tenant exists in the `core_tenant`/`tenants` table.
- If you need to provision the tenant first, run the existing provisioning command for your project.
