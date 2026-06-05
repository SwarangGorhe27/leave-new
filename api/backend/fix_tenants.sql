-- Create public tenant to fix django-tenants issue
INSERT INTO core_tenant (id, company_name, slug, schema_name, paid_until, on_trial, is_active, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'Public Tenant',
    'public',
    'public',
    NULL,
    true,
    true,
    NOW(),
    NOW()
) ON CONFLICT (schema_name) DO NOTHING;

-- Show all tenants
SELECT schema_name, company_name, is_active FROM core_tenant;