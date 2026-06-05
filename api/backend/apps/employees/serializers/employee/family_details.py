"""Family Details serializers — screenshot fields."""

from rest_framework import serializers

from apps.employees.constants.family_details import FAMILY_MEMBER_EDITABLE

class FamilyMemberRowSubmitSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    relation_id = serializers.IntegerField(required=False, allow_null=True)
    relationship_id = serializers.IntegerField(required=False, allow_null=True)
    date_of_birth = serializers.CharField(required=False, allow_null=True)
    gender_id = serializers.IntegerField(required=False, allow_null=True)
    blood_group_id = serializers.IntegerField(required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mobile_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    occupation_id = serializers.IntegerField(required=False, allow_null=True)
    is_dependent = serializers.BooleanField(required=False)
    isDependent = serializers.BooleanField(required=False)
    is_emergency_contact = serializers.BooleanField(required=False)
    emergency_contact = serializers.BooleanField(required=False)
    remove = serializers.BooleanField(required=False, default=False)
    delete = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        if attrs.get("remove") or attrs.get("delete"):
            return attrs
        if "relationship_id" in attrs and "relation_id" not in attrs:
            attrs["relation_id"] = attrs.pop("relationship_id")
        if "mobile_no" in attrs and "phone" not in attrs:
            attrs["phone"] = attrs["mobile_no"]
        if not attrs.get("name") and attrs.get("first_name"):
            attrs["name"] = " ".join(
                part for part in [attrs.get("first_name"), attrs.get("last_name")] if part
            )
        if not attrs.get("name") and not attrs.get("id"):
            raise serializers.ValidationError(
                {"name": "Name is required for new family members."}
            )
        if not attrs.get("relation_id"):
            raise serializers.ValidationError(
                {"relation_id": "Relation is required."}
            )
        return attrs


class FamilyDetailsSubmitSerializer(serializers.Serializer):
    """Employee PATCH body — full family_details table for admin approval."""

    family_details = FamilyMemberRowSubmitSerializer(many=True)
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")

    def validate(self, attrs):
        remarks = attrs.pop("remarks", "")
        self._remarks = remarks
        rows = attrs.get("family_details", [])
        if not rows:
            raise serializers.ValidationError(
                {"family_details": "Provide at least one family member row."}
            )
        for row in rows:
            unknown = set(row.keys()) - FAMILY_MEMBER_EDITABLE
            if unknown:
                raise serializers.ValidationError(
                    {
                        "family_details": (
                            f"Fields not allowed: {', '.join(sorted(unknown))}"
                        )
                    }
                )
        return attrs

    @property
    def employee_remarks(self):
        return getattr(self, "_remarks", "")
