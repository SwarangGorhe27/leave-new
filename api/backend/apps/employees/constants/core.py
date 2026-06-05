"""
HRMS ESS — Constants & Enums

Central file for all string constants, choice sets, and configuration values
used across the ESS module. Import from here; never hardcode strings in views/services.
"""

# ─────────────────────────────────────────────────────────────────────────────
# MODULE CODES  (mirrors EmployeeChangeRequest.Module TextChoices)
# ─────────────────────────────────────────────────────────────────────────────

class ESSModule:
    PROFILE    = "PROFILE"
    EMPLOYMENT = "EMPLOYMENT"
    PERSONAL   = "PERSONAL"
    ADDRESS    = "ADDRESS"
    FAMILY     = "FAMILY"
    EDUCATION  = "EDUCATION"
    BANK       = "BANK"
    NOMINEE    = "NOMINEE"
    INSURANCE  = "INSURANCE"
    LANGUAGE   = "LANGUAGE"
    PASSPORT   = "PASSPORT"
    EXPERIENCE = "EXPERIENCE"
    SKILL      = "SKILL"
    DOCUMENT   = "DOCUMENT"
    MEDICAL    = "MEDICAL"
    SOCIAL     = "SOCIAL"
    ASSET      = "ASSET"

    ALL = [
        PROFILE, EMPLOYMENT, PERSONAL, ADDRESS, FAMILY, EDUCATION,
        BANK, NOMINEE, INSURANCE, LANGUAGE, PASSPORT,
        EXPERIENCE, SKILL, DOCUMENT, MEDICAL, SOCIAL, ASSET,
    ]


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE REQUEST STATUS
# ─────────────────────────────────────────────────────────────────────────────

class ChangeRequestStatus:
    PENDING   = "PENDING"
    APPROVED  = "APPROVED"
    REJECTED  = "REJECTED"
    CANCELLED = "CANCELLED"


class ChangeRequestAction:
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


# ─────────────────────────────────────────────────────────────────────────────
# SECURITY: FIELDS EMPLOYEES CAN NEVER CHANGE
# ─────────────────────────────────────────────────────────────────────────────

IMMUTABLE_EMPLOYEE_FIELDS = frozenset({
    "employee_code",
    "official_email",
    "work_email",
    "basic_salary",
    "gross_salary",
    "net_salary",
    "ctc",
    "department",
    "department_id",
    "designation",
    "designation_id",
    "grade",
    "grade_id",
    "date_of_joining",
    "reporting_manager",
    "reporting_manager_id",
    "employment_status",
    "status",
    "shift",
    "shift_id",
    "payroll_group",
    "payroll_group_id",
    "company",
    "company_id",
    "role",
    "is_active",
})

# ─────────────────────────────────────────────────────────────────────────────
# FILE UPLOAD SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

class FileUpload:
    # Max sizes in bytes
    PROFILE_PICTURE_MAX_BYTES = 5 * 1024 * 1024      # 5 MB
    SIGNATURE_MAX_BYTES       = 2 * 1024 * 1024      # 2 MB
    DOCUMENT_MAX_BYTES        = 10 * 1024 * 1024     # 10 MB
    PASSPORT_MAX_BYTES        = 5 * 1024 * 1024      # 5 MB
    CERTIFICATE_MAX_BYTES     = 5 * 1024 * 1024      # 5 MB

    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
    ALLOWED_SIGNATURE_TYPES = ALLOWED_IMAGE_TYPES | {"application/pdf"}
    ALLOWED_SIGNATURE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
    ALLOWED_DOCUMENT_TYPES = {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".docx", ".doc", ".webp"}

    UPLOAD_PATHS = {
        "profile_picture":  "employees/{code}/profile/",
        "signature":        "employees/{code}/signature/",
        "passport":         "employees/{code}/passport/",
        "visa":             "employees/{code}/visa/",
        "certificate":      "employees/{code}/certificates/",
        "education":        "employees/{code}/education/",
        "medical":          "employees/{code}/medical/",
        "resume":           "employees/{code}/resume/",
        "document":         "employees/{code}/documents/",
    }


# ─────────────────────────────────────────────────────────────────────────────
# PAGINATION
# ─────────────────────────────────────────────────────────────────────────────

class Pagination:
    DEFAULT_PAGE_SIZE  = 20
    MAX_PAGE_SIZE      = 100
    ADMIN_PAGE_SIZE    = 50


# ─────────────────────────────────────────────────────────────────────────────
# RESPONSE KEYS
# ─────────────────────────────────────────────────────────────────────────────

class ResponseKey:
    DETAIL  = "detail"
    COUNT   = "count"
    RESULTS = "results"
    NEXT    = "next"
    PREV    = "previous"
    ERRORS  = "errors"


# ─────────────────────────────────────────────────────────────────────────────
# ALLOWED FIELDS PER MODULE (employee editable)
# ─────────────────────────────────────────────────────────────────────────────

MODULE_ALLOWED_FIELDS = {
    ESSModule.PROFILE: {
        "salutation",
        "middle_name",
        "preferred_name",
        "personal_email",
        "personal_mobile",
        "extension_number",
        "bio_about",
        "profile_photo",
        "first_name",
        "last_name",
        "work_mobile",
        "alternate_mobile_number",
        "username",
        "signature_upload",
    },
    ESSModule.EMPLOYMENT: {
        "department_id",
        "sub_department_id",
        "team_id",
        "designation_id",
        "employee_type_id",
        "employment_type_id",
        "employee_category_id",
        "grade_band_id",
        "work_location_id",
        "shift_id",
        "joining_date",
        "confirmation_date",
        "employment_status",
        "probation_status",
        "probation_period_days",
        "notice_period_days",
        "employee_status",
        "referred_by_id",
        "referred_by_employee_id",
        "referred_by",
        "source_of_hire_id",
        "reporting_to_id",
        "reporting_manager_id",
        "functional_manager_id",
        "hr_partner_id",
    },
    ESSModule.PERSONAL: {
        "first_name",
        "middle_name",
        "last_name",
        "date_of_birth",
        "actual_dob",
        "actual_date_of_birth",
        "joining_date",
        "gender_id",
        "marital_status_id",
        "religion_id",
        "caste_id",
        "caste_category_id",
        "nationality_id",
        "blood_group_id",
        "place_of_birth",
        "identification_mark",
        "height",
        "height_cm",
        "weight",
        "weight_kg",
        "father_name",
        "spouse_name",
        "is_physically_challenged",
        "is_international_employee",
    },
    ESSModule.ADDRESS: {
        "address_type", "address_line1", "address_line2", "landmark",
        "city_id", "state_id", "country_id", "pincode",
        "start_date", "to_date", "is_same_as_permanent",
        "current_address", "permanent_address", "address_details",
    },
    ESSModule.FAMILY: {
        "family_details",
    },
    ESSModule.EDUCATION: {
        "education_details",
        "from_date",
        "to_date",
        "start_date",
        "end_date",
    },
    ESSModule.BANK: {
        "bank_id", "account_number", "account_type_id",
        "ifsc_code", "branch_name", "branch_city", "is_primary",
        "account_holder_name", "bank_accounts", "statutory_details",
        "bank", "account_no", "ifsc", "type", "primary",
        "pan_number", "aadhaar_number", "uan_number", "pf_number",
        "esic_number", "professional_tax_no", "tax_regime", "tax_regime_id",
    },
    ESSModule.NOMINEE: {
        "name", "relationship_id",
        "nominee_percentage", "date_of_birth", "contact_number",
        "aadhaar_number", "address", "nominee_details", "relation_id",
        "share_percentage", "phone",
        "mobile_no", "aadhaar_card_url", "pan_card_url",
        "identity_proof_url", "relationship_proof_url",
        "supporting_documents_url", "remove", "delete",
    },
    ESSModule.INSURANCE: {
        "policy_type_id", "policy_number", "provider_name",
        "sum_insured", "start_date", "end_date",
        "premium_amount", "dependent_name", "dependent_relationship",
        "insurance_details", "insurance_provider_id", "insurance_provider",
        "coverage_type_id", "coverage_type", "coverage_amount",
        "valid_till", "dependents_covered_id", "dependents_covered",
        "insurance_document_url", "insurance_document_upload",
        "delete_policy",
    },
    ESSModule.LANGUAGE: {
        "language_details",
        "id",
        "language",
        "language_id", "read_proficiency_id", "write_proficiency_id",
        "speak_proficiency_id", "proficiency_level_id", "proficiency_level",
        "can_read", "can_write", "can_speak", "is_mother_tongue",
        "remove", "delete",
    },
    ESSModule.PASSPORT: {
        "passport_visa_records",
        "passport_number", "issue_date", "expiry_date",
        "issue_place", "issue_country_id", "nationality_id",
        "passport_category", "passport_status",
        "has_visa", "visa_type", "visa_number", "visa_expiry_date",
        "visa_issue_country_id", "visa_country_id", "visa_issue_date",
        "visa_sponsor", "visa_status",
        "passport_front_url", "passport_back_url", "visa_copy_url",
        "document_url", "id", "remove", "delete",
    },
    ESSModule.EXPERIENCE: {
        "company_name", "designation", "department",
        "start_date", "end_date", "is_current",
        "employment_type", "location", "responsibilities",
        "reason_for_leaving", "last_ctc", "offer_letter_url",
        "experience_letter_url",
    },
    ESSModule.SKILL: {
        "skill_name", "proficiency_level", "years_of_experience",
        "last_used_year", "certification_name", "certification_body",
        "certification_date", "certification_expiry", "certificate_url",
        "credential_id", "credential_url",
    },
    ESSModule.DOCUMENT: {
        "document_type_id", "document_name", "document_number",
        "issue_date", "expiry_date", "issuing_authority",
        "document_url", "remarks",
    },
    ESSModule.MEDICAL: {
        "allergies", "emergency_contact_name",
        "emergency_contact_number", "emergency_contact_relationship",
        "relationship", "doctor_name", "medical_details",
        "medical_conditions", "any_disease", "has_disease",
        "disease_description", "pre_existing_diseases",
        "undergone_major_surgery", "any_surgery_operation_done",
        "surgery_details", "surgery_operation_description",
    },
    ESSModule.SOCIAL: {
        "linkedin_url", "github_url", "twitter_url",
        "facebook_url", "instagram_url", "personal_website",
        "personal_website_url", "portfolio_url", "stackoverflow_url",
        "social_profile",
    },
    ESSModule.ASSET: {},  # Read-only for employees; HR assigns assets
}
