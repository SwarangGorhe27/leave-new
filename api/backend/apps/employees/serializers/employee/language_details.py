"""Language Details serializers — screenshot fields."""

from rest_framework import serializers

from apps.employees.constants.language_details import LANGUAGE_PROFICIENCY_EDITABLE
from apps.employees.models.masters.misc import Language, LanguageProficiency


class LanguageProficiencyRowSubmitSerializer(serializers.Serializer):
    """Individual language proficiency row for edit form."""

    id = serializers.UUIDField(required=False, allow_null=True)
    language_id = serializers.IntegerField(required=False, allow_null=True)
    language = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    proficiency_level_id = serializers.IntegerField(required=False, allow_null=True)
    proficiency_level = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # Proficiency levels for read, write, speak
    read_proficiency_id = serializers.IntegerField(required=False, allow_null=True)
    read_proficiency = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    write_proficiency_id = serializers.IntegerField(required=False, allow_null=True)
    write_proficiency = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    speak_proficiency_id = serializers.IntegerField(required=False, allow_null=True)
    speak_proficiency = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # Checkboxes for can read, write, speak
    can_read = serializers.BooleanField(required=False, default=False)
    can_write = serializers.BooleanField(required=False, default=False)
    can_speak = serializers.BooleanField(required=False, default=False)
    
    # Flags
    is_mother_tongue = serializers.BooleanField(required=False, default=False)
    
    # Delete/remove flags
    remove = serializers.BooleanField(required=False, default=False)
    delete = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        """Validate language row."""
        if attrs.get("remove") or attrs.get("delete"):
            return attrs
        
        language_name = (attrs.get("language") or "").strip()
        if not attrs.get("language_id") and language_name:
            language = (
                Language.objects.filter(label__iexact=language_name, is_active=True)
                .first()
                or Language.objects.filter(code__iexact=language_name, is_active=True)
                .first()
            )
            if not language:
                raise serializers.ValidationError(
                    {"language": "Language must match an active language master."}
                )
            attrs["language_id"] = language.id

        # Language is required for new entries
        if not attrs.get("language_id") and not attrs.get("language"):
            raise serializers.ValidationError(
                {"language_id": "Language is required."}
            )

        language_id = attrs.get("language_id")
        if language_id and not Language.objects.filter(
            id=language_id,
            is_active=True,
        ).exists():
            raise serializers.ValidationError({"language_id": "Invalid language_id."})

        proficiency_level_id = attrs.get("proficiency_level_id")
        proficiency_level_name = (attrs.get("proficiency_level") or "").strip()
        if not proficiency_level_id and proficiency_level_name:
            proficiency_level = (
                LanguageProficiency.objects.filter(
                    label__iexact=proficiency_level_name,
                    is_active=True,
                ).first()
                or LanguageProficiency.objects.filter(
                    code__iexact=proficiency_level_name,
                    is_active=True,
                ).first()
            )
            if not proficiency_level:
                raise serializers.ValidationError(
                    {
                        "proficiency_level": (
                            "Proficiency level must match an active language "
                            "proficiency master."
                        )
                    }
                )
            proficiency_level_id = proficiency_level.id
            attrs["proficiency_level_id"] = proficiency_level_id

        if proficiency_level_id:
            if not LanguageProficiency.objects.filter(
                id=proficiency_level_id,
                is_active=True,
            ).exists():
                raise serializers.ValidationError(
                    {"proficiency_level_id": "Invalid proficiency_level_id."}
                )
            for field in (
                "read_proficiency_id",
                "write_proficiency_id",
                "speak_proficiency_id",
            ):
                if not attrs.get(field):
                    attrs[field] = proficiency_level_id

        checked_capabilities = (
            ("can_read", "read_proficiency_id"),
            ("can_write", "write_proficiency_id"),
            ("can_speak", "speak_proficiency_id"),
        )
        for checkbox_field, proficiency_field in checked_capabilities:
            if attrs.get(checkbox_field) and not attrs.get(proficiency_field):
                raise serializers.ValidationError(
                    {
                        proficiency_field: (
                            "This field or proficiency_level_id is required when "
                            f"{checkbox_field} is true."
                        )
                    }
                )
            proficiency_id = attrs.get(proficiency_field)
            if proficiency_id and not LanguageProficiency.objects.filter(
                id=proficiency_id,
                is_active=True,
            ).exists():
                raise serializers.ValidationError(
                    {proficiency_field: f"Invalid {proficiency_field}."}
                )
        
        return attrs


class LanguageDetailsSubmitSerializer(serializers.Serializer):
    """Employee PATCH body — full language_details table for admin approval."""

    language_details = LanguageProficiencyRowSubmitSerializer(many=True)
    remarks = serializers.CharField(required=False, allow_blank=True, max_length=1000, default="")

    def validate(self, attrs):
        """Validate language details form."""
        remarks = attrs.pop("remarks", "")
        self._remarks = remarks
        rows = attrs.get("language_details", [])
        
        if not rows:
            raise serializers.ValidationError(
                {"language_details": "Provide at least one language proficiency row."}
            )
        
        for row in rows:
            unknown = set(row.keys()) - LANGUAGE_PROFICIENCY_EDITABLE
            if unknown:
                raise serializers.ValidationError(
                    {
                        "language_details": (
                            f"Fields not allowed: {', '.join(sorted(unknown))}"
                        )
                    }
                )
        
        return attrs

    @property
    def employee_remarks(self):
        """Return employee remarks."""
        return getattr(self, "_remarks", "")
