from rest_framework import serializers


class TeamAttendanceMemberSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    employee_code = serializers.CharField(allow_null=True)
    role = serializers.CharField()
    department = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    check_in = serializers.CharField(allow_null=True)
    check_out = serializers.CharField(allow_null=True)
    work_hours = serializers.FloatField()
    avatar_url = serializers.CharField(allow_null=True)


class TeamAttendanceRecordSerializer(serializers.Serializer):
    date = serializers.DateField()
    check_in = serializers.CharField(allow_null=True)
    check_out = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    work_hours = serializers.FloatField(allow_null=True)


class TeamMemberAttendanceSerializer(serializers.Serializer):
    employee_id = serializers.UUIDField()
    total_hours = serializers.FloatField()
    average_hours = serializers.FloatField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    records = TeamAttendanceRecordSerializer(many=True)


class TeamAttendanceOverrideSerializer(serializers.Serializer):
    date = serializers.DateField()
    check_in = serializers.TimeField(required=False, allow_null=True)
    check_out = serializers.TimeField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=["present", "absent", "on_leave", "late"])
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        check_in = attrs.get("check_in")
        check_out = attrs.get("check_out")
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError({"check_out": "check_out must be after check_in."})
        return attrs


class TeamAttendanceOverrideResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    record_id = serializers.UUIDField()
    message = serializers.CharField()


class TeamMemberStatsSerializer(serializers.Serializer):
    avg_work_hours = serializers.FloatField()
    total_hours = serializers.FloatField()
    attendance_score = serializers.FloatField()
    absences = serializers.IntegerField()
    late_count = serializers.IntegerField()
    leave_days = serializers.IntegerField()


class TeamWorkHoursTrendSerializer(serializers.Serializer):
    date = serializers.DateField()
    hours = serializers.FloatField()


class TeamStatusMixSerializer(serializers.Serializer):
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    holiday = serializers.IntegerField()
    on_leave = serializers.IntegerField()
    late = serializers.IntegerField()


class TeamMemberAnalyticsSerializer(serializers.Serializer):
    work_hours_trend = TeamWorkHoursTrendSerializer(many=True)
    status_mix = TeamStatusMixSerializer()


class TeamMemberProfileSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    role = serializers.CharField()
    department = serializers.CharField(allow_null=True)
    avatar_url = serializers.CharField(allow_null=True)
    email = serializers.EmailField(allow_blank=True)
    join_date = serializers.DateField(allow_null=True)
