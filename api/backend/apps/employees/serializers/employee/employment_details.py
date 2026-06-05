"""Employment Details serializers - screenshot fields."""

from rest_framework import serializers

from apps.employees.constants.employment_details import (
    EMPLOYMENT_DETAILS_EMPLOYEE_EDITABLE,
)


class EmploymentDetailsSubmitSerializer(serializers.Serializer):
    department_id = serializers.UUIDField(required=False, allow_null=True)
    sub_department_id = serializers.UUIDField(required=False, allow_null=True)
    team_id = serializers.UUIDField(required=False, allow_null=True)
    designation_id = serializers.UUIDField(required=False, allow_null=True)
    employee_type_id = serializers.IntegerField(required=False, allow_null=True)
    employment_type_id = serializers.IntegerField(required=False, allow_null=True)
    employee_category_id = serializers.IntegerField(required=False, allow_null=True)
    grade_band_id = serializers.UUIDField(required=False, allow_null=True)
    work_location_id = serializers.IntegerField(required=False, allow_null=True)
    shift_id = serializers.UUIDField(required=False, allow_null=True)
    joining_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    confirmation_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    employment_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    probation_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    probation_period_days = serializers.IntegerField(required=False, allow_null=True)
    notice_period_days = serializers.IntegerField(required=False, allow_null=True)
    employee_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    referred_by_id = serializers.IntegerField(required=False, allow_null=True)
    referred_by_employee_id = serializers.UUIDField(required=False, allow_null=True)
    referred_by = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_of_hire_id = serializers.IntegerField(required=False, allow_null=True)
    reporting_to_id = serializers.UUIDField(required=False, allow_null=True)
    reporting_manager_id = serializers.UUIDField(required=False, allow_null=True)
    functional_manager_id = serializers.UUIDField(required=False, allow_null=True)
    hr_partner_id = serializers.UUIDField(required=False, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")

    def validate(self, attrs):
        remarks = attrs.pop("remarks", "")
        self._remarks = remarks
        unknown = set(attrs.keys()) - EMPLOYMENT_DETAILS_EMPLOYEE_EDITABLE
        if unknown:
            raise serializers.ValidationError(
                {"non_field_errors": f"Fields not allowed: {', '.join(sorted(unknown))}"}
            )
        if not attrs:
            raise serializers.ValidationError(
                {"non_field_errors": "Provide at least one field to update."}
            )
        return attrs

    @property
    def employee_remarks(self):
        return getattr(self, "_remarks", "")
