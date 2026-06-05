from rest_framework import serializers
from ..models.masters.calendar_period import CalendarPeriod


class CalendarPeriodCreateRequestSerializer(serializers.Serializer):
    name = serializers.CharField()
    period_type = serializers.ChoiceField(
        choices=CalendarPeriod._meta.get_field("period_type").choices
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, attrs):
        if attrs["end_date"] <= attrs["start_date"]:
            raise serializers.ValidationError(
                {"end_date": "end_date must be after start_date."}
            )
        return attrs
        
    
class CalendarPeriodResponseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()

    class Meta:
        model = CalendarPeriod
        fields = [
            "id",
            "name",
            "period_type",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_name(self, obj):
        return obj.meta_data.get("name") if isinstance(obj.meta_data, dict) else None

    def get_start_date(self, obj):
        return obj.meta_data.get("start_date") if isinstance(obj.meta_data, dict) else None

    def get_end_date(self, obj):
        return obj.meta_data.get("end_date") if isinstance(obj.meta_data, dict) else None