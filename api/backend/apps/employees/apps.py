"""
HRMS ESS — Django AppConfig

Wire this into INSTALLED_APPS:
    "apps.employees.apps.EmployeesConfig"
"""

from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.employees"
    label = "employees"
    verbose_name = "Employees (ESS)"

    def ready(self):
        try:
            from apps.employees.swagger_schema import register_ess_extensions

            register_ess_extensions()
        except Exception:
            pass

        try:
            import apps.employees.signals  # noqa: F401
        except ImportError:
            pass
