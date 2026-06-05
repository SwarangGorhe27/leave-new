"""
Manual Punch Validators - Business rule validation.
"""

from rest_framework import serializers
from django.utils import timezone
from apps.attendance.models.punch_and_daily import PunchLog
from apps.employees.models import Employee

class ManualPunchValidator:
    """
    Validation logic for manual punch operations.
    """

    @staticmethod
    def validate_creation(data: dict):
        """Validate creation of a manual punch."""
        employee_id = data.get('employee_id')
        punch_time = data.get('punch_time')
        punch_type = data.get('punch_type')
        company_id = data.get('company_id')

        # 1. Employee status
        try:
            employee = Employee.objects.get(id=employee_id, company_id=company_id)
            if not employee.is_active:
                raise serializers.ValidationError("Cannot create manual punch for an inactive employee.")
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee not found.")

        # 2. Future time check
        if punch_time > timezone.now():
            raise serializers.ValidationError("Punch time cannot be in the future.")

        # 3. Duplicate manual punch check (Same emp, same type, same minute)
        duplicate_exists = PunchLog.objects.filter(
            employee_id=employee_id,
            punch_time__year=punch_time.year,
            punch_time__month=punch_time.month,
            punch_time__day=punch_time.day,
            punch_time__hour=punch_time.hour,
            punch_time__minute=punch_time.minute,
            punch_type=punch_type,
        ).exclude(meta_data__is_deleted=True).exists()

        if duplicate_exists:
            raise serializers.ValidationError("A manual punch with this type and time already exists for this employee.")

        return True
