from rest_framework import serializers


class CalendarDaySerializer(serializers.Serializer):
    date = serializers.DateField()
    day_of_week = serializers.CharField()
    status = serializers.CharField()
    punch_in = serializers.CharField(allow_null=True)
    punch_out = serializers.CharField(allow_null=True)
    work_hours = serializers.FloatField()
    shift = serializers.CharField(allow_null=True)
    wfh = serializers.BooleanField()
    is_today = serializers.BooleanField()
    is_holiday = serializers.BooleanField()
    is_weekend = serializers.BooleanField()


class AttendanceCalendarSerializer(serializers.Serializer):
    month = serializers.CharField()
    days = CalendarDaySerializer(many=True)
    legend = serializers.ListField()
