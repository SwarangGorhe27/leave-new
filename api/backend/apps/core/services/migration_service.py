from django.core.management import call_command

from apps.core.constants.module_apps import MODULE_APP_MAP


class MigrationService:

    @classmethod
    def migrate_tenant_apps(
        cls,
        schema_name,
        purchased_modules,
    ):

        for module in purchased_modules:

            app_name = MODULE_APP_MAP.get(module)

            if not app_name:
                continue

            app_label = app_name.split(".")[-1]

            print(f"Applying migrations for " f"{app_label} on schema {schema_name}")

            call_command(
                "migrate_schemas",
                schema_name=schema_name,
                app_label=app_label,
                interactive=False,
                verbosity=1,
            )
