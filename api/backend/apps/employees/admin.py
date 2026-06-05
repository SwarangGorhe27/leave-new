from django.contrib import admin

# Register your models here.
from apps.employees.models.employee import Employee
from apps.employees.models.reporting import EmployeeReportingRelationship
from apps.employees.models.masters.organization import *
# from apps.employees.models.roles import EmployeeRoleAssignment
# from apps.employees.models.masters.misc import SystemRole
from apps.security.models.role import Role, EmployeeRoleAssignment

admin.site.register(Employee)
admin.site.register(EmployeeReportingRelationship)
admin.site.register(Department)
admin.site.register(Designation)
# admin.site.register(Role)
admin.site.register(EmployeeRoleAssignment)