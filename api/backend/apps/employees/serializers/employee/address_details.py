"""Address Details serializers - current and permanent address sections."""

from rest_framework import serializers

from apps.employees.constants.address_details import ADDRESS_ROW_EDITABLE
from apps.employees.models.address import EmployeeAddress


class AddressRowSubmitSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False, allow_null=True)
    address_type = serializers.ChoiceField(
        choices=EmployeeAddress.AddressType.choices,
        required=True,
    )
    address_line1 = serializers.CharField(required=True, allow_blank=False, max_length=255)
    address_line2 = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=255)
    landmark = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=150)
    city_id = serializers.IntegerField(required=False, allow_null=True)
    state_id = serializers.IntegerField(required=True)
    country_id = serializers.IntegerField(required=True)
    pincode = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=10)
    start_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    to_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_same_as_permanent = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        unknown = set(attrs.keys()) - ADDRESS_ROW_EDITABLE
        if unknown:
            raise serializers.ValidationError(
                f"Fields not allowed: {', '.join(sorted(unknown))}"
            )
        return attrs


class AddressDetailsSubmitSerializer(serializers.Serializer):
    """Employee PATCH body - full address section for admin approval."""

    current_address = AddressRowSubmitSerializer(required=False)
    permanent_address = AddressRowSubmitSerializer(required=False)
    address_details = AddressRowSubmitSerializer(many=True, required=False)
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")

    def validate(self, attrs):
        remarks = attrs.pop("remarks", "")
        self._remarks = remarks

        rows = list(attrs.get("address_details") or [])
        if attrs.get("current_address"):
            rows.append(attrs["current_address"])
        if attrs.get("permanent_address"):
            rows.append(attrs["permanent_address"])

        if not rows:
            raise serializers.ValidationError(
                {"address_details": "Provide current_address, permanent_address, or address_details."}
            )

        address_types = {row.get("address_type") for row in rows}
        required_types = {
            EmployeeAddress.AddressType.CURRENT,
            EmployeeAddress.AddressType.PERMANENT,
        }
        if not address_types & required_types:
            raise serializers.ValidationError(
                {"address_details": "Provide at least CURRENT or PERMANENT address."}
            )

        attrs["address_details"] = rows
        attrs.pop("current_address", None)
        attrs.pop("permanent_address", None)
        return attrs

    @property
    def employee_remarks(self):
        return getattr(self, "_remarks", "")
