from rest_framework import serializers


class WorkHoursTrendSerializer(serializers.Serializer):
    date = serializers.CharField()
    hours = serializers.FloatField()


class StatusMixSerializer(serializers.Serializer):
    total_working_days = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    work_off = serializers.IntegerField()
    half_day = serializers.IntegerField()
    leave = serializers.IntegerField()
    holiday = serializers.IntegerField()
    work_from_home = serializers.IntegerField()
    late_in = serializers.IntegerField()
    early_out = serializers.IntegerField()


class AttendanceAnalyticsSerializer(serializers.Serializer):
    work_hours_trend = WorkHoursTrendSerializer(many=True)
    status_mix = StatusMixSerializer()
