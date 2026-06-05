"""
Position history serializers for admin employee details.
"""

from rest_framework import serializers

from apps.employees.models.employee import Employee
from apps.employees.models.employment import EmployeeEmploymentDetails
from apps.employees.models.masters.audit_additions import ReportingManager
from apps.employees.models.masters.hr_setup import Branch
from apps.employees.models.masters.organization import Department, Designation, Grade
from apps.employees.models.position_history import EmployeePositionHistory


class ReportingManagerRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Accept either a ReportingManager UUID or an Employee UUID.

    The UI commonly has employee IDs available for managers. Position history
    stores ReportingManager IDs, so we create/reuse the master row here.
    """

    default_error_messages = {
        "does_not_exist": (
            'Invalid pk "{pk_value}" - no active ReportingManager or Employee exists.'
        ),
        "incorrect_type": "Incorrect type. Expected UUID string.",
    }

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            manager_employee = Employee.objects.filter(id=data, is_active=True).first()
            if manager_employee is None:
                self.fail("does_not_exist", pk_value=data)

            defaults = {"is_active": True}
            employment_details = (
                EmployeeEmploymentDetails.objects.filter(
                    employee=manager_employee,
                    is_active=True,
                )
                .select_related("designation", "department")
                .first()
            )
            if employment_details is not None:
                defaults["designation"] = employment_details.designation
                defaults["department"] = employment_details.department

            reporting_manager, _created = ReportingManager.objects.get_or_create(
                company_id=manager_employee.company_id,
                employee=manager_employee,
                defaults=defaults,
            )
            if not reporting_manager.is_active:
                reporting_manager.is_active = True
                reporting_manager.save(update_fields=["is_active"])
            return reporting_manager


class PositionHistorySerializer(serializers.ModelSerializer):
    designation_title = serializers.CharField(source="designation.title", read_only=True, allow_null=True)
    department_name = serializers.CharField(source="department.name", read_only=True, allow_null=True)
    grade_label = serializers.CharField(source="grade.label", read_only=True, allow_null=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True, allow_null=True)
    reporting_to_id = serializers.SerializerMethodField()
    reporting_to_name = serializers.SerializerMethodField()
    reporting_to_designation = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = EmployeePositionHistory
        fields = [
            "id",
            "employee",
            "designation",
            "designation_title",
            "department",
            "department_name",
            "grade",
            "grade_label",
            "branch",
            "branch_name",
            "reporting_to",
            "reporting_to_id",
            "reporting_to_name",
            "reporting_to_designation",
            "effective_from",
            "effective_to",
            "is_current",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "employee",
            "designation_title",
            "department_name",
            "grade_label",
            "branch_name",
            "reporting_to_id",
            "reporting_to_name",
            "reporting_to_designation",
            "is_current",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_reporting_to_id(self, obj):
        return str(obj.reporting_to.id) if obj.reporting_to else None

    def get_reporting_to_name(self, obj):
        if obj.reporting_to:
            return obj.reporting_to.employee.full_name
        return None

    def get_reporting_to_designation(self, obj):
        if obj.reporting_to and obj.reporting_to.designation:
            return obj.reporting_to.designation.title
        return None

    def get_is_current(self, obj):
        return obj.effective_to is None


class PositionHistoryWriteSerializer(serializers.Serializer):
    designation = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    grade = serializers.PrimaryKeyRelatedField(
        queryset=Grade.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    reporting_to = ReportingManagerRelatedField(
        queryset=ReportingManager.objects.filter(is_active=True),
        required=False,
        allow_null=True,
        help_text="UUID of ReportingManager or manager Employee.",
    )
    effective_from = serializers.DateField(required=False)
    effective_to = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        if not self.partial and "effective_from" not in attrs:
            raise serializers.ValidationError({"effective_from": "This field is required."})

        effective_from = attrs.get("effective_from")
        effective_to = attrs.get("effective_to")
        if self.instance is not None:
            effective_from = effective_from or self.instance.effective_from
            effective_to = effective_to if "effective_to" in attrs else self.instance.effective_to

        if effective_from and effective_to and effective_to < effective_from:
            raise serializers.ValidationError(
                {"effective_to": "Effective to date cannot be before effective from date."}
            )

        employee = self.context.get("employee")
        reporting_to = attrs.get("reporting_to")
        if employee is not None and reporting_to is not None and reporting_to.employee.id == employee.id:
            raise serializers.ValidationError(
                {"reporting_to": "Employee cannot report to themselves."}
            )

        if not self.partial:
            has_position = attrs.get("designation") or attrs.get("department")
            if not has_position:
                raise serializers.ValidationError(
                    "Provide designation, department, or both for the position history row."
                )

        return attrs
