from datetime import date

from rest_framework import serializers

from ..models.transactions.leave_approvals import LeaveApproval
from ..models.transactions.leave_requests import LeaveRequest, LeaveSessionChoices, LeaveRequestDay
from ..models.masters.leave_types import LeaveType
from ..models.transactions.leave_documents import LeaveDocument

def _validate_leave_sessions(attrs):
    from_date = attrs.get("from_date")
    to_date = attrs.get("to_date")
    from_session = attrs.get("from_session")
    to_session = attrs.get("to_session")

    if from_date and to_date and from_date > to_date:
        raise serializers.ValidationError(
            "from_date cannot be greater than to_date."
        )

    if from_date and to_date and from_session and to_session:
        if (
            from_date == to_date
            and from_session == LeaveSessionChoices.SECOND_HALF
            and to_session == LeaveSessionChoices.FIRST_HALF
        ):
            raise serializers.ValidationError(
                "Invalid same-day session range: cannot start in the second half and end in the first half."
            )


class LeaveApplicationUpdateSerializer(serializers.Serializer):
    leave_type_id = serializers.UUIDField(required=False)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
    from_session = serializers.ChoiceField(
        choices=LeaveSessionChoices.choices,
        required=False,
    )
    to_session = serializers.ChoiceField(
        choices=LeaveSessionChoices.choices,
        required=False,
    )
    reason = serializers.CharField(required=False, allow_blank=True)
    contact_number = serializers.CharField(required=False, allow_blank=True)
    mode_of_work = serializers.CharField(required=False, allow_blank=True)
    notify_team = serializers.BooleanField(required=False)
    backup_employee_id = serializers.UUIDField(required=False)
    remove_document_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
    )
    attachments = serializers.ListField(
        child=serializers.FileField(),
        required=False,
    )

    def validate(self, attrs):
        _validate_leave_sessions(attrs)
        return attrs


class LeaveApplicationResubmitSerializer(serializers.Serializer):
    leave_type_id = serializers.UUIDField(required=False)
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
    from_session = serializers.ChoiceField(
        choices=LeaveSessionChoices.choices,
        required=False,
    )
    to_session = serializers.ChoiceField(
        choices=LeaveSessionChoices.choices,
        required=False,
    )
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        _validate_leave_sessions(attrs)
        return attrs


class LeaveApplicationCommentSerializer(serializers.Serializer):
    comment = serializers.CharField(required=True)
from datetime import date

from rest_framework import serializers

class LeaveApplicationCreateSerializer(serializers.Serializer):
    leave_type_id = serializers.UUIDField()

    from_date = serializers.DateField()
    to_date = serializers.DateField()

    from_session = serializers.ChoiceField(
        choices=LeaveSessionChoices.choices
    )

    to_session = serializers.ChoiceField(
        choices=LeaveSessionChoices.choices
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    contact_during_leave = serializers.CharField(
        required=True,
        allow_blank=True,
    )
    attachment = serializers.FileField(
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        from_date = attrs["from_date"]
        to_date = attrs["to_date"]

        from_session = attrs["from_session"]
        to_session = attrs["to_session"]

        if from_date > to_date:
            raise serializers.ValidationError(
                "from_date must be before or equal to to_date."
            )

        if from_date == to_date:

            if (
                from_session == LeaveSessionChoices.SECOND_HALF
                and to_session == LeaveSessionChoices.FIRST_HALF
            ):
                raise serializers.ValidationError(
                    "Invalid same-day session range."
                )

        if from_date < date.today():
            raise serializers.ValidationError(
                "Cannot apply for leave in the past."
            )
        if contact_during_leave := attrs.get("contact_during_leave"):
            if not contact_during_leave.strip():
                raise serializers.ValidationError(
                    "contact_during_leave cannot be blank."
                )
            if len(contact_during_leave) > 10 or len(contact_during_leave) < 10:
                raise serializers.ValidationError(
                    "contact_during_leave must be exactly 10 numbers."
                )
        if not LeaveType.objects.filter(
            id=attrs["leave_type_id"],
            is_active=True,
            ).exists():
            raise serializers.ValidationError(
                {
                    "leave_type_id":
                    "Leave type not found or inactive."
                }
            )

        return attrs


class LeaveApplicationSummarySerializer(serializers.ModelSerializer):
    leave_type_id = serializers.UUIDField(source="leave_type.id", read_only=True)
    leave_type = serializers.CharField(source="leave_type.name", read_only=True)
    leave_type_code = serializers.CharField(source="leave_type.code", read_only=True)
    leave_status = serializers.CharField(source="status", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "leave_type_id",
            "leave_type",
            "leave_type_code",
            "from_date",
            "to_date",
            "from_session",
            "to_session",
            "total_days",
            "reason",
            "leave_status",
            "applied_at",
        ]

class ManagerLeaveApplicationSummarySerializer(
    LeaveApplicationSummarySerializer
):
    employee_id = serializers.UUIDField(
        source="employee.id",
        read_only=True,
    )

    employee_code = serializers.CharField(
        source="employee.employee_code",
        read_only=True,
    )

    employee_name = serializers.SerializerMethodField()

    class Meta(LeaveApplicationSummarySerializer.Meta):
        fields = LeaveApplicationSummarySerializer.Meta.fields + [
            "employee_id",
            "employee_code",
            "employee_name",
        ]

    def get_employee_name(self, obj):
        return getattr(obj.employee, "full_name", None)

class LeaveApprovalSerializer(serializers.ModelSerializer):
    approver_id = serializers.UUIDField(source="approver.id", read_only=True)
    approver_name = serializers.StringRelatedField(source="approver", read_only=True)

    class Meta:
        model = LeaveApproval
        fields = [
            "id",
            "approval_level",
            "status",
            "remarks",
            "approver_id",
            "approver_name",
            "actioned_at",
            "created_at",
        ]

class LeaveDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveDocument

        fields = [
            "id",
            "file_name",
            "file_url",
            "file_type",
            "file_size_kb",
            "uploaded_by",
            "uploaded_at",
        ]


class LeaveRequestDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequestDay
        fields = [
            "id",
            "leave_date",
            "session",
            "day_value",
            "is_weekend",
            "is_holiday",
            "is_counted",
        ]


class EmployeeLeaveApplicationDetailSerializer(serializers.ModelSerializer):
    leave_type = serializers.CharField(
        source="leave_type.leave_name",
        read_only=True,
    )
    leave_type_code = serializers.CharField(source="leave_type.code", read_only=True)
    documents = LeaveDocumentSerializer(many=True, read_only=True)
    leave_days = LeaveRequestDaySerializer(many=True, read_only=True)
    is_half_day = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "leave_type_id",
            "leave_type",
            "leave_type_code",
            "from_date",
            "to_date",
            "from_session",
            "to_session",
            "is_half_day",          # derived — for UI convenience
            "total_days",
            "reason",
            "contact_number",
            "mode_of_work",
            "notify_team",
            "status",
            "applied_at",
            "documents",
            "leave_days",
        ]

    def get_is_half_day(self, obj):
        """
        Half day = same date, one session only.
        Avoids needing a duration_type field on the model.
        """
        return obj.from_date == obj.to_date and obj.from_session == obj.to_session
class LeaveApplicationCancelSerializer(serializers.Serializer):
    reason = serializers.CharField()


class LeaveApplicationActionSerializer(serializers.Serializer):
    remarks = serializers.CharField(allow_blank=True, required=False)
