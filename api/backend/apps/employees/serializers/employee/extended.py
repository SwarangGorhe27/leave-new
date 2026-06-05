"""
HRMS ESS — Extended Serializers

Read + Write serializers for the five new ESS models:
  - EmployeePassportVisa
  - EmployeeWorkExperience
  - EmployeeSkillCertification
  - EmployeeMedicalEmergency
  - EmployeeSocialProfile

Also contains:
  - ChangeRequestSubmitSerializer  (employee submits any module change)
  - ChangeRequestReadSerializer    (employee & admin reads)
  - ProfilePictureUploadSerializer
  - DocumentUploadSerializer
  - PassportDocumentUploadSerializer
"""

from datetime import date

from rest_framework import serializers

from apps.employees.constants import (
    ChangeRequestAction,
    ESSModule,
    MODULE_ALLOWED_FIELDS,
)
from apps.employees.models import EmployeeChangeRequest
from apps.employees.models.ess_extended import (
    EmployeeMedicalEmergency,
    EmployeePassportVisa,
    EmployeeSkillCertification,
    EmployeeSocialProfile,
    EmployeeWorkExperience,
)
from apps.employees.validators import (
    validate_certificate_upload,
    validate_document_upload,
    validate_module_known,
    validate_no_immutable_fields,
    validate_change_request_data_not_empty,
    validate_experience_dates,
    validate_passport_number,
    validate_phone_number,
    validate_profile_picture,
    validate_signature_upload,
    validate_passport_document,
    validate_url_safe,
)


# ─────────────────────────────────────────────────────────────────────────────
# PASSPORT / VISA
# ─────────────────────────────────────────────────────────────────────────────

class PassportVisaReadSerializer(serializers.ModelSerializer):
    issue_country_name      = serializers.CharField(source="issue_country.name",       read_only=True, default="")
    nationality_name        = serializers.CharField(source="nationality.name",         read_only=True, default="")
    visa_issue_country_name = serializers.CharField(source="visa_issue_country.name",  read_only=True, default="")

    class Meta:
        model  = EmployeePassportVisa
        fields = [
            "id", "passport_number", "issue_date", "expiry_date",
            "issue_place", "issue_country", "issue_country_name",
            "nationality", "nationality_name",
            "is_current", "document_url",
            "has_visa", "visa_type", "visa_number",
            "visa_expiry_date", "visa_issue_date",
            "visa_issue_country", "visa_issue_country_name",
            "visa_document_url",
            "created_at", "updated_at",
        ]


class PassportVisaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EmployeePassportVisa
        fields = [
            "passport_number", "issue_date", "expiry_date",
            "issue_place", "issue_country", "nationality",
            "is_current", "document_url",
            "has_visa", "visa_type", "visa_number",
            "visa_expiry_date", "visa_issue_date",
            "visa_issue_country", "visa_document_url",
        ]

    def validate_passport_number(self, value):
        validate_passport_number(value)
        return value.upper()

    def validate(self, attrs):
        # Visa fields required when has_visa=True
        if attrs.get("has_visa"):
            for field in ("visa_type", "visa_number", "visa_expiry_date"):
                if not attrs.get(field):
                    raise serializers.ValidationError(
                        {field: f"{field} is required when has_visa is True."}
                    )
        # Passport expiry must be after issue date
        issue = attrs.get("issue_date")
        expiry = attrs.get("expiry_date")
        if issue and expiry and expiry <= issue:
            raise serializers.ValidationError(
                {"expiry_date": "Passport expiry date must be after issue date."}
            )
        return attrs


# ─────────────────────────────────────────────────────────────────────────────
# WORK EXPERIENCE
# ─────────────────────────────────────────────────────────────────────────────

class WorkExperienceReadSerializer(serializers.ModelSerializer):
    duration_years = serializers.SerializerMethodField()

    class Meta:
        model  = EmployeeWorkExperience
        fields = [
            "id", "company_name", "designation", "department",
            "location", "employment_type",
            "start_date", "end_date", "is_current",
            "responsibilities", "reason_for_leaving", "last_ctc",
            "is_verified", "verified_at",
            "offer_letter_url", "experience_letter_url",
            "duration_years", "created_at", "updated_at",
        ]

    def get_duration_years(self, obj):
        end = obj.end_date or date.today()
        delta = end - obj.start_date
        return round(delta.days / 365.25, 1)


class WorkExperienceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EmployeeWorkExperience
        fields = [
            "company_name", "designation", "department",
            "location", "employment_type",
            "start_date", "end_date", "is_current",
            "responsibilities", "reason_for_leaving", "last_ctc",
            "offer_letter_url", "experience_letter_url",
        ]

    def validate(self, attrs):
        try:
            validate_experience_dates(
                attrs.get("start_date"),
                attrs.get("end_date"),
                attrs.get("is_current", False),
            )
        except Exception as exc:
            raise serializers.ValidationError({"non_field_errors": str(exc)})
        return attrs


# ─────────────────────────────────────────────────────────────────────────────
# SKILLS & CERTIFICATIONS
# ─────────────────────────────────────────────────────────────────────────────

class SkillCertificationReadSerializer(serializers.ModelSerializer):
    is_cert_expired  = serializers.SerializerMethodField()
    days_to_expiry   = serializers.SerializerMethodField()

    class Meta:
        model  = EmployeeSkillCertification
        fields = [
            "id", "skill_name", "skill_type",
            "proficiency_level", "years_of_experience", "last_used_year",
            "is_certified", "certification_name", "certification_body",
            "certification_date", "certification_expiry",
            "credential_id", "credential_url", "certificate_url",
            "is_cert_expired", "days_to_expiry",
            "created_at", "updated_at",
        ]

    def get_is_cert_expired(self, obj):
        if obj.is_certified and obj.certification_expiry:
            return obj.certification_expiry < date.today()
        return False

    def get_days_to_expiry(self, obj):
        if obj.is_certified and obj.certification_expiry:
            delta = (obj.certification_expiry - date.today()).days
            return delta
        return None


class SkillCertificationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EmployeeSkillCertification
        fields = [
            "skill_name", "skill_type", "proficiency_level",
            "years_of_experience", "last_used_year",
            "is_certified", "certification_name", "certification_body",
            "certification_date", "certification_expiry",
            "credential_id", "credential_url", "certificate_url",
        ]

    def validate(self, attrs):
        if attrs.get("is_certified"):
            if not attrs.get("certification_name"):
                raise serializers.ValidationError(
                    {"certification_name": "Required when is_certified is True."}
                )
            cert_date   = attrs.get("certification_date")
            cert_expiry = attrs.get("certification_expiry")
            if cert_date and cert_expiry and cert_expiry <= cert_date:
                raise serializers.ValidationError(
                    {"certification_expiry": "Expiry must be after certification date."}
                )
        if attrs.get("credential_url"):
            validate_url_safe(attrs["credential_url"])
        return attrs


# ─────────────────────────────────────────────────────────────────────────────
# MEDICAL & EMERGENCY
# ─────────────────────────────────────────────────────────────────────────────

class MedicalEmergencyReadSerializer(serializers.ModelSerializer):
    blood_group_name = serializers.CharField(source="blood_group.name", read_only=True, default="")

    class Meta:
        model  = EmployeeMedicalEmergency
        fields = [
            "id",
            "emergency_contact_name", "emergency_contact_number",
            "emergency_contact_relationship", "emergency_contact_alt_number",
            "emergency_contact_email", "emergency_contact_address",
            "blood_group", "blood_group_name",
            "pre_existing_diseases", "ongoing_medications",
            "allergies", "undergone_major_surgery", "surgery_details",
            "is_physically_challenged", "disability_details", "disability_percentage",
            "doctor_name", "doctor_contact",
            "medical_document_url",
            "created_at", "updated_at",
        ]


class MedicalEmergencyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EmployeeMedicalEmergency
        fields = [
            "emergency_contact_name", "emergency_contact_number",
            "emergency_contact_relationship", "emergency_contact_alt_number",
            "emergency_contact_email", "emergency_contact_address",
            "blood_group",
            "pre_existing_diseases", "ongoing_medications",
            "allergies", "undergone_major_surgery", "surgery_details",
            "is_physically_challenged", "disability_details", "disability_percentage",
            "doctor_name", "doctor_contact",
            "medical_document_url",
        ]

    def validate_emergency_contact_number(self, value):
        if value:
            validate_phone_number(value)
        return value

    def validate_emergency_contact_alt_number(self, value):
        if value:
            validate_phone_number(value)
        return value

    def validate(self, attrs):
        if attrs.get("undergone_major_surgery") and not attrs.get("surgery_details"):
            raise serializers.ValidationError(
                {"surgery_details": "surgery_details is required when undergone_major_surgery is True."}
            )
        if attrs.get("is_physically_challenged") and not attrs.get("disability_details"):
            raise serializers.ValidationError(
                {"disability_details": "disability_details is required when is_physically_challenged is True."}
            )
        return attrs


# ─────────────────────────────────────────────────────────────────────────────
# SOCIAL PROFILES
# ─────────────────────────────────────────────────────────────────────────────

class SocialProfileReadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EmployeeSocialProfile
        fields = [
            "id",
            "linkedin_url", "github_url", "stackoverflow_url",
            "portfolio_url", "personal_website",
            "twitter_url", "facebook_url", "instagram_url",
            "created_at", "updated_at",
        ]


class SocialProfileWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EmployeeSocialProfile
        fields = [
            "linkedin_url", "github_url", "stackoverflow_url",
            "portfolio_url", "personal_website",
            "twitter_url", "facebook_url", "instagram_url",
        ]

    def _validate_url(self, value):
        if value:
            validate_url_safe(value)
        return value

    def validate_linkedin_url(self, v):    return self._validate_url(v)
    def validate_github_url(self, v):      return self._validate_url(v)
    def validate_stackoverflow_url(self, v): return self._validate_url(v)
    def validate_portfolio_url(self, v):   return self._validate_url(v)
    def validate_personal_website(self, v): return self._validate_url(v)
    def validate_twitter_url(self, v):     return self._validate_url(v)
    def validate_facebook_url(self, v):    return self._validate_url(v)
    def validate_instagram_url(self, v):   return self._validate_url(v)


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE REQUEST — SUBMIT (Employee)
# ─────────────────────────────────────────────────────────────────────────────

class ChangeRequestSubmitSerializer(serializers.Serializer):
    """
    Used by employees to submit a change request for any module.

    Fields:
        module        — ESSModule constant (e.g. "ADDRESS")
        action        — CREATE | UPDATE | DELETE
        request_data  — arbitrary dict with new values
        record_id     — UUID of the specific record (for multi-record modules)
        remarks       — optional employee note
    """

    module       = serializers.ChoiceField(choices=[(m, m) for m in ESSModule.ALL])
    action       = serializers.ChoiceField(
        choices=[(a, a) for a in [
            ChangeRequestAction.CREATE,
            ChangeRequestAction.UPDATE,
            ChangeRequestAction.DELETE,
        ]],
        default=ChangeRequestAction.UPDATE,
    )
    request_data = serializers.DictField(required=True)
    record_id    = serializers.UUIDField(required=False, allow_null=True, default=None)
    remarks      = serializers.CharField(
        required=False, allow_blank=True, max_length=1000, default=""
    )

    def validate_request_data(self, value):
        validate_change_request_data_not_empty(value)
        validate_no_immutable_fields(value)
        return value

    def validate(self, attrs):
        module  = attrs["module"]
        action  = attrs["action"]
        data    = attrs["request_data"]
        allowed = MODULE_ALLOWED_FIELDS.get(module, set())

        # Asset module is read-only for employees
        if module == ESSModule.ASSET:
            raise serializers.ValidationError(
                {"module": "Asset records are managed by HR only. "
                           "Employees cannot submit asset change requests."}
            )

        # Enforce allowed-field whitelist for known modules
        if allowed:
            disallowed = set(data.keys()) - allowed
            if disallowed:
                raise serializers.ValidationError(
                    {"request_data": f"Fields not permitted for module {module}: "
                                     f"{', '.join(sorted(disallowed))}."}
                )

        # DELETE requires record_id
        if action == ChangeRequestAction.DELETE and not attrs.get("record_id"):
            raise serializers.ValidationError(
                {"record_id": "record_id is required for DELETE action."}
            )

        return attrs


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE REQUEST — READ
# ─────────────────────────────────────────────────────────────────────────────

class ChangeRequestReadSerializer(serializers.ModelSerializer):
    employee_name   = serializers.SerializerMethodField()
    employee_code   = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model  = EmployeeChangeRequest
        fields = [
            "id", "module", "action", "status",
            "request_data", "old_data",
            "employee", "employee_name", "employee_code",
            "reviewed_by", "reviewed_by_name", "reviewed_at",
            "admin_remarks", "employee_remarks",
            "record_id",
            "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        emp = getattr(obj, "employee", None)
        if emp:
            return f"{emp.first_name} {emp.last_name}".strip()
        return ""

    def get_employee_code(self, obj):
        emp = getattr(obj, "employee", None)
        return getattr(emp, "employee_code", "") if emp else ""

    def get_reviewed_by_name(self, obj):
        rb = getattr(obj, "reviewed_by", None)
        if rb:
            return getattr(rb, "get_full_name", lambda: str(rb))()
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN SERIALIZERS
# ─────────────────────────────────────────────────────────────────────────────

class AdminApproveSerializer(serializers.Serializer):
    """Payload for HR/Admin to approve a change request."""
    admin_remarks = serializers.CharField(
        required=False, allow_blank=True, max_length=2000, default=""
    )


class AdminRejectSerializer(serializers.Serializer):
    """Payload for HR/Admin to reject a change request. Remarks mandatory."""
    admin_remarks = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=2000,
        error_messages={"blank": "Rejection reason (admin_remarks) is required."},
    )


class AdminChangeRequestDetailSerializer(ChangeRequestReadSerializer):
    """Identical to read serializer but includes old_data for admin diff view."""
    diff = serializers.SerializerMethodField()

    class Meta(ChangeRequestReadSerializer.Meta):
        fields = ChangeRequestReadSerializer.Meta.fields + ["diff"]

    def get_diff(self, obj):
        """Returns field-by-field diff of old_data vs request_data."""
        old  = obj.old_data or {}
        new  = obj.request_data or {}
        all_keys = set(old.keys()) | set(new.keys())
        result = {}
        for key in sorted(all_keys):
            old_val = old.get(key, "—")
            new_val = new.get(key, "—")
            if old_val != new_val:
                result[key] = {"from": old_val, "to": new_val}
        return result


# ─────────────────────────────────────────────────────────────────────────────
# FILE UPLOAD SERIALIZERS
# ─────────────────────────────────────────────────────────────────────────────

class ProfilePictureUploadSerializer(serializers.Serializer):
    """Validates the profile picture file before passing to service."""
    profile_picture = serializers.ImageField(validators=[validate_profile_picture])


class SignatureUploadSerializer(serializers.Serializer):
    """Validates signature file (PNG/JPEG/WebP/PDF) for profile section."""
    signature_upload = serializers.FileField(validators=[validate_signature_upload])


class DocumentUploadSerializer(serializers.Serializer):
    """Generic ESS document upload."""
    document            = serializers.FileField(validators=[validate_document_upload])
    document_type_label = serializers.CharField(
        required=False, max_length=100, default="", allow_blank=True
    )
    remarks             = serializers.CharField(
        required=False, max_length=500, default="", allow_blank=True
    )


class PassportDocumentUploadSerializer(serializers.Serializer):
    """Passport/visa document upload."""
    document      = serializers.FileField(validators=[validate_passport_document])
    document_kind = serializers.ChoiceField(
        choices=[("passport", "Passport"), ("visa", "Visa")],
        default="passport",
    )
    record_id     = serializers.UUIDField(
        required=False, allow_null=True, default=None,
        help_text="UUID of the EmployeePassportVisa record to attach to.",
    )
