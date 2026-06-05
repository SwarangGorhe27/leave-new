"""Social & Professional Profiles serializers."""

from rest_framework import serializers


class SocialProfileSubmitSerializer(serializers.Serializer):
    """Employee form payload for social profile change request."""

    linkedin_url = serializers.URLField(required=False, allow_blank=True, default="")
    github_url = serializers.URLField(required=False, allow_blank=True, default="")
    portfolio_url = serializers.URLField(required=False, allow_blank=True, default="")
    personal_website = serializers.URLField(required=False, allow_blank=True, default="")
    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
        default="",
    )

    def validate(self, attrs):
        self._remarks = attrs.pop("remarks", "")
        return attrs

    @property
    def employee_remarks(self):
        return getattr(self, "_remarks", "")
