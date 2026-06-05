"""Education Details serializers — screenshot fields."""

from rest_framework import serializers

from apps.employees.constants.education_details import EDUCATION_ROW_EDITABLE


class EducationRowSubmitSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False, allow_null=True)
    qualification_id = serializers.IntegerField(required=False, allow_null=True)
    qualification = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    specialization_id = serializers.IntegerField(required=False, allow_null=True)
    specialization = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    institution_id = serializers.IntegerField(required=False, allow_null=True)
    institution = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    institution_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    university_id = serializers.IntegerField(required=False, allow_null=True)
    university = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    year_of_passing_id = serializers.IntegerField(required=False, allow_null=True)
    year_of_passing = serializers.IntegerField(required=False, allow_null=True)
    yearOfPassing = serializers.IntegerField(required=False, allow_null=True)
    from_date = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"],
    )
    to_date = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"],
    )
    start_date = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"],
    )
    end_date = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"],
    )
    percentage_or_cgpa = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    degree_certificate_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    marksheet_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    leaving_certificate_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remove = serializers.BooleanField(required=False, default=False)
    delete = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        if attrs.get("remove") or attrs.get("delete"):
            return attrs
        if "from_date" in attrs and "start_date" not in attrs:
            attrs["start_date"] = attrs["from_date"]
        if "to_date" in attrs and "end_date" not in attrs:
            attrs["end_date"] = attrs["to_date"]
        if attrs.get("start_date") and attrs.get("end_date") and attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError(
                {"to_date": "To date must be on or after from date."}
            )
        if not attrs.get("qualification_id") and not attrs.get("qualification"):
            raise serializers.ValidationError(
                {"qualification_id": "Qualification is required."}
            )
        if not attrs.get("institution_id") and not attrs.get("institution") and not attrs.get("institution_name"):
            raise serializers.ValidationError(
                {"institution_id": "Institution is required."}
            )
        if (
            not attrs.get("year_of_passing_id")
            and attrs.get("year_of_passing") is None
            and attrs.get("yearOfPassing") is None
        ):
            raise serializers.ValidationError(
                {"year_of_passing": "Year of passing is required."}
            )
        return attrs


class EducationDetailsSubmitSerializer(serializers.Serializer):
    education_details = EducationRowSubmitSerializer(many=True)
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")

    def validate(self, attrs):
        remarks = attrs.pop("remarks", "")
        self._remarks = remarks
        rows = attrs.get("education_details", [])
        if not rows:
            raise serializers.ValidationError(
                {"education_details": "Provide at least one education row."}
            )
        for row in rows:
            unknown = set(row.keys()) - EDUCATION_ROW_EDITABLE
            if unknown:
                raise serializers.ValidationError(
                    {
                        "education_details": (
                            f"Fields not allowed: {', '.join(sorted(unknown))}"
                        )
                    }
                )
        return attrs

    @property
    def employee_remarks(self):
        return getattr(self, "_remarks", "")
