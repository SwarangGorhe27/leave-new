"""Personal Details serializers — screenshot fields."""

from rest_framework import serializers

from apps.employees.constants.personal_details import PERSONAL_DETAILS_EMPLOYEE_EDITABLE


class PersonalDetailsSubmitSerializer(serializers.Serializer):
    """Employee PATCH body — fields sent for admin approval."""

    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    middle_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date_of_birth = serializers.CharField(required=False, allow_null=True)
    actual_dob = serializers.CharField(required=False, allow_null=True)
    actual_date_of_birth = serializers.CharField(required=False, allow_null=True)
    joining_date = serializers.CharField(required=False, allow_null=True)
    gender_id = serializers.IntegerField(required=False, allow_null=True)
    marital_status_id = serializers.IntegerField(required=False, allow_null=True)
    religion_id = serializers.IntegerField(required=False, allow_null=True)
    caste_category_id = serializers.IntegerField(required=False, allow_null=True)
    place_of_birth = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_physically_challenged = serializers.BooleanField(required=False)
    father_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    spouse_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    blood_group_id = serializers.IntegerField(required=False, allow_null=True)
    nationality_id = serializers.IntegerField(required=False, allow_null=True)
    caste_id = serializers.IntegerField(required=False, allow_null=True)
    identification_mark = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    height = serializers.DecimalField(required=False, max_digits=5, decimal_places=1, allow_null=True)
    height_cm = serializers.DecimalField(required=False, max_digits=5, decimal_places=1, allow_null=True)
    weight = serializers.DecimalField(required=False, max_digits=5, decimal_places=1, allow_null=True)
    weight_kg = serializers.DecimalField(required=False, max_digits=5, decimal_places=1, allow_null=True)
    is_international_employee = serializers.BooleanField(required=False)
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")

    def validate_height_cm(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Height must be greater than 0.")
        return value

    def validate_weight_kg(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Weight must be greater than 0.")
        return value

    def validate(self, attrs):
        remarks = attrs.pop("remarks", "")
        self._remarks = remarks
        if "actual_dob" in attrs:
            actual_dob = attrs.pop("actual_dob")
            attrs.setdefault("actual_date_of_birth", actual_dob)
        if "height" in attrs:
            height = attrs.pop("height")
            attrs.setdefault("height_cm", height)
        if "weight" in attrs:
            weight = attrs.pop("weight")
            attrs.setdefault("weight_kg", weight)
        for required_name in ("first_name", "last_name"):
            if required_name in attrs and not (attrs[required_name] or "").strip():
                raise serializers.ValidationError(
                    {required_name: "This field may not be blank."}
                )
        unknown = set(attrs.keys()) - PERSONAL_DETAILS_EMPLOYEE_EDITABLE
        if unknown:
            raise serializers.ValidationError(
                {"non_field_errors": f"Fields not allowed: {', '.join(sorted(unknown))}"}
            )
        if not attrs:
            raise serializers.ValidationError(
                {"non_field_errors": "Provide at least one field to update."}
            )
        return attrs

    @property
    def employee_remarks(self):
        return getattr(self, "_remarks", "")
