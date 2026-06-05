from rest_framework import serializers


class InsightItemSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["POSITIVE", "WARNING", "INFO"])
    title = serializers.CharField()
    description = serializers.CharField()


class AttendanceAIInsightsSerializer(serializers.Serializer):
    insights = InsightItemSerializer(many=True)
    generated_at = serializers.CharField()
