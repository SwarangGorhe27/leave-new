"""Nominee Details serializers - screenshot fields."""

from rest_framework import serializers

from apps.employees.constants.nominee_details import NOMINEE_ROW_EDITABLE
from apps.employees.services.nominee_details import MAX_NOMINEES_PER_EMPLOYEE


class NomineeRowSubmitSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=201)
    relation_id = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    share_percentage = serializers.DecimalField(
        required=False,
        allow_null=True,
        max_digits=5,
        decimal_places=2,
    )
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=20)
    date_of_birth = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    aadhaar_card_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pan_card_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    identity_proof_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    relationship_proof_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    supporting_documents_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remove = serializers.BooleanField(required=False, default=False)
    delete = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        unknown = set(attrs.keys()) - NOMINEE_ROW_EDITABLE
        if unknown:
            raise serializers.ValidationError(
                f"Fields not allowed: {', '.join(sorted(unknown))}"
            )
        if attrs.get("remove") or attrs.get("delete"):
            return attrs
        if not attrs.get("name") and not attrs.get("id"):
            raise serializers.ValidationError({"name": "Name is required for new nominees."})
        if not attrs.get("relation_id"):
            raise serializers.ValidationError({"relation_id": "Relation is required."})
        if attrs.get("share_percentage") is None:
            raise serializers.ValidationError(
                {"share_percentage": "Share percentage is required."}
            )
        return attrs


class NomineeDetailsSubmitSerializer(serializers.Serializer):
    """Employee PATCH body - nominee details rows for admin approval."""

    nominee_details = NomineeRowSubmitSerializer(many=True)
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")

    def validate(self, attrs):
        remarks = attrs.pop("remarks", "")
        self._remarks = remarks
        rows = attrs.get("nominee_details", [])
        if not rows:
            raise serializers.ValidationError(
                {"nominee_details": "Provide at least one nominee row."}
            )
        active_rows = [
            row for row in rows if not row.get("remove") and not row.get("delete")
        ]
        if len(active_rows) > MAX_NOMINEES_PER_EMPLOYEE:
            raise serializers.ValidationError(
                {
                    "nominee_details": (
                        f"Maximum {MAX_NOMINEES_PER_EMPLOYEE} nominees are allowed."
                    )
                }
            )
        return attrs

    @property
    def employee_remarks(self):
        return getattr(self, "_remarks", "")
