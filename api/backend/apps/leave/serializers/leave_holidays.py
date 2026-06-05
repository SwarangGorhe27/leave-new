from rest_framework import serializers


class AdminHolidayListRequestSerializer(serializers.Serializer):
    branch_id = serializers.UUIDField(required=False)
    year = serializers.IntegerField(min_value=1900, max_value=2100, required=False)


class AdminHolidayCreateRequestSerializer(serializers.Serializer):
    date = serializers.DateField()
    name = serializers.CharField(max_length=200)
    type = serializers.ChoiceField(
        choices=["NATIONAL", "RESTRICTED", "OPTIONAL", "COMPANY"]
    )
    branch_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )


class AdminHolidayCreateResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()


class AdminHolidayCalendarSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()
    calendar_year = serializers.IntegerField()
    branch_id = serializers.UUIDField(allow_null=True)


class AdminHolidayListItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    holiday_calendar_id = serializers.UUIDField()
    calendar = AdminHolidayCalendarSerializer()
    holiday_date = serializers.DateField()
    name = serializers.CharField()
    holiday_type = serializers.CharField()
    is_active = serializers.BooleanField()


class AdminHolidayListResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    data = AdminHolidayListItemSerializer(many=True)


class HolidayCalendarSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, allow_blank=True)
    date = serializers.DateField()
    name = serializers.CharField()
    holiday_type = serializers.CharField(source='type', required=False, allow_blank=True)
    is_optional = serializers.BooleanField(required=False, default=False)


class HolidayGroupAssignmentSerializer(serializers.Serializer):
    employee_ids = serializers.ListField(child=serializers.UUIDField())
    holiday_group_id = serializers.UUIDField()

    def validate_employee_ids(self, value):
        if not value:
            raise serializers.ValidationError("employee_ids is required.")
        return value


class CarryForwardSerializer(serializers.Serializer):
    leave_policy_id = serializers.UUIDField()
    from_year = serializers.IntegerField()
    to_year = serializers.IntegerField()