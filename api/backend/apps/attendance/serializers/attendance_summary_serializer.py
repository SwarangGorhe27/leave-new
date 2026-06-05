from rest_framework import serializers


class AttendanceSummarySerializer(serializers.Serializer):
    avg_work_hours = serializers.FloatField()
    avg_actual_work = serializers.FloatField()
    present_days = serializers.FloatField()
    absent_days = serializers.IntegerField()
    leave_taken = serializers.IntegerField()
    late_in = serializers.IntegerField()
    deltas = serializers.DictField(child=serializers.DictField())
    month = serializers.CharField()
