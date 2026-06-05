"""
HRMS ESS views package.

Employee endpoints: apps.employees.views.employee
Admin endpoints:      apps.employees.views.admin
"""

from .admin import *  # noqa: F403
from .employee import *  # noqa: F403
