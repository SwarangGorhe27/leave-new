from rest_framework import serializers


class AttendanceTimingSerializer(serializers.Serializer):
    in_ = serializers.CharField(source="in", allow_null=True)
    out = serializers.CharField(allow_null=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["in"] = data.pop("in_", None)
        return data


class AttendanceActionsSerializer(serializers.Serializer):
    can_regularize = serializers.BooleanField()
    can_share = serializers.BooleanField()


class ShiftDetailsSerializer(serializers.Serializer):
    id = serializers.CharField(allow_null=True, required=False)
    code = serializers.CharField(allow_null=True, required=False)
    name = serializers.CharField(allow_null=True, required=False)
    start_time = serializers.CharField(allow_null=True, required=False)
    end_time = serializers.CharField(allow_null=True, required=False)


class AttendanceListRecordSerializer(serializers.Serializer):
    id = serializers.CharField()
    employee_id = serializers.CharField(required=False, allow_null=True)
    employee_name = serializers.CharField(required=False, allow_null=True)
    date = serializers.DateField()
    attendance_date = serializers.CharField(required=False, allow_null=True)
    day_name = serializers.CharField()
    timing = AttendanceTimingSerializer()
    punch_in_time = serializers.CharField(required=False, allow_null=True)
    punch_out_time = serializers.CharField(required=False, allow_null=True)
    work_mode = serializers.CharField(allow_null=True)
    work_hours = serializers.FloatField()
    working_hours = serializers.FloatField(required=False)
    status = serializers.CharField()
    status_label = serializers.CharField(required=False, allow_null=True)
    shift_id = serializers.CharField(required=False, allow_null=True)
    shift_code = serializers.CharField(required=False, allow_null=True)
    shift_name = serializers.CharField(allow_null=True, required=False)
    shift_details = ShiftDetailsSerializer(required=False)
    late_mins = serializers.IntegerField(required=False)
    early_exit_mins = serializers.IntegerField(required=False)
    ot_mins = serializers.IntegerField(required=False)
    is_locked = serializers.BooleanField(required=False)
    actions = AttendanceActionsSerializer()


class AttendanceListSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    page = serializers.IntegerField()
    per_page = serializers.IntegerField()
    records = AttendanceListRecordSerializer(many=True)
