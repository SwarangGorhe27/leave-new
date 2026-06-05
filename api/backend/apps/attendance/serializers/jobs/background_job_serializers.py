"""Serializers for attendance background job APIs."""

from __future__ import annotations

from rest_framework import serializers

from apps.attendance.models import AttendanceJob, AttendanceJobStatus, AttendanceJobType
from apps.attendance.utils.attendance_job_helpers import (
    get_employee_or_error,
    get_request_employee,
    validate_request_company_access,
    validate_trigger_role,
)


class AttendanceJobListFilterSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    job_type = serializers.ChoiceField(choices=AttendanceJobType.choices, required=False)
    status = serializers.ChoiceField(choices=AttendanceJobStatus.choices, required=False)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

    def validate(self, attrs):
        from_date = attrs.get("from_date")
        to_date = attrs.get("to_date")
        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError({"to_date": "to_date must be on or after from_date."})
        validate_request_company_access(attrs["company_id"], self.context["request"].user)
        return attrs


class TriggerDailyComputeJobSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    job_date = serializers.DateField()
    triggered_by = serializers.UUIDField(required=False, allow_null=True)

    def validate_job_date(self, value):
        return value

    def validate(self, attrs):
        request = self.context["request"]
        validate_request_company_access(attrs["company_id"], request.user)

        actor_employee = get_request_employee(request.user)
        validate_trigger_role(
            actor_employee=actor_employee,
            request_user=request.user,
            job_date=attrs["job_date"],
        )

        if attrs.get("triggered_by"):
            get_employee_or_error(
                company_id=attrs["company_id"],
                employee_id=attrs["triggered_by"],
            )
        elif actor_employee is not None:
            attrs["triggered_by"] = actor_employee.id

        duplicate_running_job = AttendanceJob.objects.filter(
            company_id=attrs["company_id"],
            job_type=AttendanceJobType.DAILY_COMPUTE,
            job_date=attrs["job_date"],
            status=AttendanceJobStatus.RUNNING,
            deleted_at__isnull=True,
        ).exists()
        if duplicate_running_job:
            raise serializers.ValidationError(
                {"job_date": "A DAILY_COMPUTE job is already running for this company and date."}
            )
        return attrs


class RetryAttendanceJobSerializer(serializers.Serializer):
    company_id = serializers.UUIDField()
    triggered_by = serializers.UUIDField(required=False, allow_null=True)
    retry_reason = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, attrs):
        request = self.context["request"]
        validate_request_company_access(attrs["company_id"], request.user)

        actor_employee = get_request_employee(request.user)
        validate_trigger_role(actor_employee=actor_employee, request_user=request.user)

        if attrs.get("triggered_by"):
            get_employee_or_error(
                company_id=attrs["company_id"],
                employee_id=attrs["triggered_by"],
            )
        elif actor_employee is not None:
            attrs["triggered_by"] = actor_employee.id

        job = self.context["job"]
        if str(job.company_id) != str(attrs["company_id"]):
            raise serializers.ValidationError({"company_id": "Job does not belong to the requested company."})
        if job.status != AttendanceJobStatus.FAILED:
            raise serializers.ValidationError({"status": "Only FAILED jobs can be retried."})
        return attrs


class AttendanceJobListItemSerializer(serializers.ModelSerializer):
    queued_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = AttendanceJob
        fields = [
            "id",
            "job_type",
            "job_date",
            "status",
            "attempt_count",
            "queued_at",
            "started_at",
            "completed_at",
            "error_log",
            "meta_data",
        ]


class AttendanceJobDetailSerializer(AttendanceJobListItemSerializer):
    company_id = serializers.UUIDField(source="company_id", read_only=True)
    triggered_by = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta(AttendanceJobListItemSerializer.Meta):
        fields = AttendanceJobListItemSerializer.Meta.fields + [
            "company_id",
            "triggered_by",
            "created_at",
            "updated_at",
        ]

    def get_triggered_by(self, obj):
        employee = obj.created_by
        if employee is None:
            return obj.meta_data.get("triggered_by") if obj.meta_data else None
        return {
            "id": str(employee.id),
            "name": employee.full_name,
            "employee_code": employee.employee_code,
        }
