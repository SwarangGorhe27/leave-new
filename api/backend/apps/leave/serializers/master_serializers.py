from rest_framework import serializers

from ..models.masters.reason import Reason
#ALL MASTERS SERIALIZERS TO BE ADDED HERE.

class ReasonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reason
        fields = [
            "id",
            "module",
            "code",
            "label",
        ]