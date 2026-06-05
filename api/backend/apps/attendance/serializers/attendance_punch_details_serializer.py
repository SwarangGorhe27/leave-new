from rest_framework import serializers


class PunchEntrySerializer(serializers.Serializer):
    time = serializers.CharField(allow_null=True)
    location = serializers.CharField(allow_null=True)
    status = serializers.CharField()


class AttendancePunchDetailsSerializer(serializers.Serializer):
    date = serializers.DateField()
    status = serializers.CharField(required=False)
    punch_in = PunchEntrySerializer()
    punch_out = PunchEntrySerializer()
    shift = serializers.CharField(allow_null=True)
    shift_start = serializers.CharField(allow_null=True, required=False)
    shift_end = serializers.CharField(allow_null=True, required=False)
    day_type = serializers.CharField(allow_null=True)
    work_hours = serializers.FloatField()
