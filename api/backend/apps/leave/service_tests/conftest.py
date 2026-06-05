import pytest
from datetime import date

@pytest.fixture
def create_test_employee():
    from apps.employees.models import Employee

    def _create_employee(name='Test Employee'):
        parts = name.split()
        first = parts[0]
        last = parts[1] if len(parts) > 1 else 'Test'
        return Employee.objects.create(first_name=first, last_name=last, email=f'{first.lower()}.{last.lower()}@example.com')

    return _create_employee


@pytest.fixture
def create_test_leave_type():
    from apps.leave.models.masters.leave_types import LeaveType

    def _create_leave_type(code='SL', name='Sick Leave', days=10):
        return LeaveType.objects.create(code=code, name=name, max_days_per_year=days, is_active=True)

    return _create_leave_type


@pytest.fixture
def create_test_leave_policy():
    from apps.leave.models.masters.leave_policy import LeavePolicy

    def _create_policy(name='Standard Policy'):
        return LeavePolicy.objects.create(name=name, effective_from=date.today(), is_active=True)

    return _create_policy
