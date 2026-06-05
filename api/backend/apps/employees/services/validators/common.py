"""
HRMS ESS — Validators

Production-grade validators for:
  1. File uploads (size, type, extension)
  2. Per-module request_data field validation
  3. Cross-field business rules (date ranges, percentage totals, etc.)

All validators raise serializers.ValidationError with structured messages.
"""

import os
import re
import logging
from datetime import date, timedelta
from decimal import Decimal

from rest_framework import serializers

from apps.employees.constants import (
    IMMUTABLE_EMPLOYEE_FIELDS,
    MODULE_ALLOWED_FIELDS,
    FileUpload,
    ESSModule,
)

logger = logging.getLogger(__name__)


# =============================================================================
# FILE UPLOAD VALIDATORS
# =============================================================================

def validate_file_extension(file, allowed_extensions=None):
    """Validate file extension against allowed set."""
    if allowed_extensions is None:
        allowed_extensions = FileUpload.ALLOWED_EXTENSIONS
    ext = os.path.splitext(file.name)[-1].lower()
    if ext not in allowed_extensions:
        raise serializers.ValidationError(
            f"File type '{ext}' is not allowed. "
            f"Allowed: {', '.join(sorted(allowed_extensions))}"
        )


def validate_file_content_type(file, allowed_types=None):
    """Validate MIME content type."""
    if allowed_types is None:
        allowed_types = FileUpload.ALLOWED_DOCUMENT_TYPES
    ct = getattr(file, "content_type", "")
    if ct not in allowed_types:
        raise serializers.ValidationError(
            f"Content type '{ct}' is not allowed. "
            f"Allowed: {', '.join(sorted(allowed_types))}"
        )


def validate_file_size(file, max_bytes=None):
    """Validate file does not exceed max_bytes."""
    if max_bytes is None:
        max_bytes = FileUpload.DOCUMENT_MAX_BYTES
    if file.size > max_bytes:
        mb = max_bytes / (1024 * 1024)
        actual_mb = file.size / (1024 * 1024)
        raise serializers.ValidationError(
            f"File size {actual_mb:.1f} MB exceeds the {mb:.0f} MB limit."
        )


def validate_profile_picture(file):
    """Full validation for profile picture uploads."""
    validate_file_content_type(file, FileUpload.ALLOWED_IMAGE_TYPES)
    validate_file_extension(file, {".jpg", ".jpeg", ".png", ".webp"})
    validate_file_size(file, FileUpload.PROFILE_PICTURE_MAX_BYTES)


def validate_signature_upload(file):
    """Full validation for signature image/PDF uploads."""
    validate_file_content_type(file, FileUpload.ALLOWED_SIGNATURE_TYPES)
    validate_file_extension(file, FileUpload.ALLOWED_SIGNATURE_EXTENSIONS)
    validate_file_size(file, FileUpload.SIGNATURE_MAX_BYTES)


def validate_document_upload(file):
    """Full validation for general document uploads."""
    validate_file_content_type(file, FileUpload.ALLOWED_DOCUMENT_TYPES)
    validate_file_extension(file, FileUpload.ALLOWED_EXTENSIONS)
    validate_file_size(file, FileUpload.DOCUMENT_MAX_BYTES)


def validate_passport_upload(file):
    """Full validation for passport document uploads."""
    validate_file_content_type(file, FileUpload.ALLOWED_DOCUMENT_TYPES)
    validate_file_extension(file, FileUpload.ALLOWED_EXTENSIONS)
    validate_file_size(file, FileUpload.PASSPORT_MAX_BYTES)


# =============================================================================
# FIELD-LEVEL VALIDATORS
# =============================================================================

def validate_mobile_number(value: str) -> str:
    """Validates Indian/international mobile number."""
    if not value:
        return value
    # Strip spaces, dashes
    cleaned = re.sub(r"[\s\-]", "", value)
    # Accept +91XXXXXXXXXX or 10-digit or international E.164
    pattern = r"^(\+\d{1,3})?\d{7,15}$"
    if not re.match(pattern, cleaned):
        raise serializers.ValidationError(
            "Enter a valid mobile number (e.g. +919876543210 or 9876543210)."
        )
    return cleaned


def validate_ifsc_code(value: str) -> str:
    """Validates Indian IFSC code format: 4 alpha + 0 + 6 alphanumeric."""
    if not value:
        return value
    pattern = r"^[A-Z]{4}0[A-Z0-9]{6}$"
    if not re.match(pattern, value.upper()):
        raise serializers.ValidationError(
            "Invalid IFSC code. Format: 4 letters + 0 + 6 alphanumeric (e.g. SBIN0001234)."
        )
    return value.upper()


def validate_pan_number(value: str) -> str:
    """Validates Indian PAN number format."""
    if not value:
        return value
    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
    if not re.match(pattern, value.upper()):
        raise serializers.ValidationError(
            "Invalid PAN number. Format: ABCDE1234F"
        )
    return value.upper()


def validate_aadhaar_number(value: str) -> str:
    """Validates Indian Aadhaar number (12 digits)."""
    if not value:
        return value
    cleaned = re.sub(r"\s", "", str(value))
    if not re.match(r"^\d{12}$", cleaned):
        raise serializers.ValidationError(
            "Aadhaar number must be exactly 12 digits."
        )
    return cleaned


def validate_passport_number(value: str) -> str:
    """Validates passport number — letters + digits, 6-20 chars."""
    if not value:
        return value
    if not re.match(r"^[A-Z0-9]{6,20}$", value.upper()):
        raise serializers.ValidationError(
            "Invalid passport number. Must be 6-20 alphanumeric characters."
        )
    return value.upper()


def validate_percentage_or_cgpa(value) -> Decimal:
    """Validates education percentage (0-100) or CGPA (0-10)."""
    if isinstance(value, str):
        match = re.search(r"\d+(\.\d+)?", value)
        if not match:
            raise serializers.ValidationError("Enter a valid percentage or CGPA.")
        value = match.group(0)
    try:
        val = Decimal(str(value))
    except Exception:
        raise serializers.ValidationError("Enter a valid number.")
    if val < 0 or val > 100:
        raise serializers.ValidationError(
            "Percentage/CGPA must be between 0 and 100."
        )
    return val


def validate_future_date(value: date) -> date:
    """Ensures date is in the future (for visa/passport expiry)."""
    if value and value <= date.today():
        raise serializers.ValidationError(
            "Date must be in the future."
        )
    return value


def validate_past_date(value: date) -> date:
    """Ensures date is in the past (for DOB, joining date, etc.)."""
    if value and value >= date.today():
        raise serializers.ValidationError(
            "Date must be in the past."
        )
    return value


def validate_date_of_birth(value: date) -> date:
    """DOB must be in the past and not more than 100 years ago."""
    if not value:
        return value
    today = date.today()
    min_dob = today - timedelta(days=365 * 100)
    if value >= today:
        raise serializers.ValidationError("Date of birth must be in the past.")
    if value < min_dob:
        raise serializers.ValidationError("Date of birth is too far in the past.")
    return value


def validate_nominee_percentage_total(employee, new_percentage: Decimal,
                                       exclude_record_id=None) -> None:
    """
    Ensures total nominee percentage across all nominees does not exceed 100%.
    Called when creating or updating a nominee record.
    """
    from apps.employees.models import EmployeeNominee
    qs = EmployeeNominee.objects.filter(employee=employee)
    if exclude_record_id:
        qs = qs.exclude(pk=exclude_record_id)
    existing_total = sum(
        (n.nominee_percentage or Decimal("0")) for n in qs
    )
    if existing_total + new_percentage > Decimal("100"):
        raise serializers.ValidationError(
            f"Total nominee percentage would exceed 100%. "
            f"Currently allocated: {existing_total}%. "
            f"Available: {100 - existing_total}%."
        )


def validate_url(value: str) -> str:
    """Basic URL validation."""
    if not value:
        return value
    pattern = r"^https?://.{3,}"
    if not re.match(pattern, value):
        raise serializers.ValidationError(
            "Enter a valid URL starting with http:// or https://"
        )
    return value


# =============================================================================
# MODULE-LEVEL REQUEST_DATA VALIDATORS
# =============================================================================

class ModuleValidator:
    """
    Validates request_data payload for each module.
    Called from ChangeRequestSubmitSerializer.validate()
    and from the service layer before applying approved changes.
    """

    @staticmethod
    def validate(module: str, request_data: dict, action: str,
                 employee=None, record_id=None) -> dict:
        """
        Dispatch to per-module validator.
        Returns cleaned data or raises serializers.ValidationError.
        """
        # Strip immutable fields regardless of module, except the approved
        # Employment Details flow where those HR fields are explicitly editable
        # only after admin approval.
        if module == ESSModule.EMPLOYMENT:
            cleaned = dict(request_data)
        else:
            cleaned = {k: v for k, v in request_data.items()
                       if k not in IMMUTABLE_EMPLOYEE_FIELDS}

        # For DELETE, only record_id is needed
        if action == "DELETE":
            if not record_id:
                raise serializers.ValidationError(
                    {"record_id": "record_id is required for DELETE action."}
                )
            return cleaned

        # Restrict to allowed fields for the module
        allowed = MODULE_ALLOWED_FIELDS.get(module, set())
        unknown = set(cleaned.keys()) - allowed
        if unknown:
            raise serializers.ValidationError({
                "request_data": (
                    f"Fields not allowed for module {module}: "
                    f"{', '.join(sorted(unknown))}"
                )
            })

        # Per-module deep validation
        validator_fn = _MODULE_VALIDATORS.get(module)
        if validator_fn:
            cleaned = validator_fn(cleaned, action, employee, record_id)

        return cleaned

    @staticmethod
    def validate_profile(data: dict, action, employee, record_id) -> dict:
        if "personal_mobile" in data and data["personal_mobile"]:
            data["personal_mobile"] = validate_mobile_number(data["personal_mobile"])
        if "alternate_mobile" in data and data["alternate_mobile"]:
            data["alternate_mobile"] = validate_mobile_number(data["alternate_mobile"])
        if "alternate_mobile_number" in data and data["alternate_mobile_number"]:
            data["alternate_mobile_number"] = validate_mobile_number(
                data["alternate_mobile_number"]
            )
        if "work_mobile" in data and data["work_mobile"]:
            data["work_mobile"] = validate_mobile_number(data["work_mobile"])
        if "extension_number" in data and data["extension_number"] is not None:
            ext = str(data["extension_number"]).strip()
            if len(ext) > 30:
                raise serializers.ValidationError(
                    {"extension_number": "Extension must be at most 30 characters."}
                )
            data["extension_number"] = ext or None
        return data

    @staticmethod
    def validate_personal(data: dict, action, employee, record_id) -> dict:
        from apps.employees.services.personal_details import parse_date_value

        if "actual_dob" in data:
            actual_dob = data.pop("actual_dob")
            data.setdefault("actual_date_of_birth", actual_dob)
        if "height" in data:
            height = data.pop("height")
            data.setdefault("height_cm", height)
        if "weight" in data:
            weight = data.pop("weight")
            data.setdefault("weight_kg", weight)

        master_fields = {
            "gender_id": ("apps.employees.models.masters.personal", "Gender"),
            "marital_status_id": (
                "apps.employees.models.masters.personal",
                "MaritalStatus",
            ),
            "religion_id": ("apps.employees.models.masters.personal", "Religion"),
            "caste_id": ("apps.employees.models.masters.personal", "Caste"),
            "caste_category_id": (
                "apps.employees.models.masters.personal",
                "CasteCategory",
            ),
            "nationality_id": (
                "apps.employees.models.masters.personal",
                "Nationality",
            ),
            "blood_group_id": (
                "apps.employees.models.masters.personal",
                "BloodGroup",
            ),
        }
        master_errors = {}
        for field, (module_path, class_name) in master_fields.items():
            value = data.get(field)
            if value is None:
                continue
            module = __import__(module_path, fromlist=[class_name])
            model = getattr(module, class_name)
            if not model.objects.filter(id=value, is_active=True).exists():
                master_errors[field] = f"Invalid {field}."
        if master_errors:
            raise serializers.ValidationError(master_errors)

        for field in ("date_of_birth", "actual_date_of_birth", "joining_date"):
            if field in data and data[field]:
                try:
                    parsed = parse_date_value(data[field])
                except Exception as exc:
                    raise serializers.ValidationError({field: str(exc)})
                if field == "date_of_birth":
                    validate_date_of_birth(parsed)
                data[field] = parsed.isoformat() if parsed else None
        return data

    @staticmethod
    def validate_address(data: dict, action, employee, record_id) -> dict:
        if "address_details" in data or "current_address" in data or "permanent_address" in data:
            from apps.employees.services.address_details import validate_address_details

            return validate_address_details(data)

        required = {"address_line1", "state_id", "country_id"}
        if action == "CREATE":
            missing = required - set(data.keys())
            if missing:
                raise serializers.ValidationError({
                    "request_data": f"Required fields missing: {', '.join(missing)}"
                })
        return data

    @staticmethod
    def validate_employment(data: dict, action, employee, record_id) -> dict:
        from apps.employees.services.employment_details import validate_employment_details

        try:
            return validate_employment_details(data)
        except ValueError as exc:
            raise serializers.ValidationError({"employment_details": str(exc)})

    @staticmethod
    def validate_family(data: dict, action, employee, record_id) -> dict:
        from apps.employees.constants.family_details import FAMILY_MEMBER_EDITABLE
        from apps.employees.services.personal_details import parse_date_value

        items = data.get("family_details")
        if items is None:
            raise serializers.ValidationError(
                {"family_details": "family_details list is required."}
            )
        if not isinstance(items, list):
            raise serializers.ValidationError(
                {"family_details": "family_details must be a list."}
            )
        if not items:
            raise serializers.ValidationError(
                {"family_details": "Provide at least one family member row."}
            )

        cleaned_rows = []
        for index, item in enumerate(items):
            row = dict(item)
            unknown = set(row.keys()) - FAMILY_MEMBER_EDITABLE
            if unknown:
                raise serializers.ValidationError(
                    {
                        "family_details": (
                            f"Row {index + 1}: fields not allowed: "
                            f"{', '.join(sorted(unknown))}"
                        )
                    }
                )
            if row.get("remove") or row.get("delete"):
                cleaned_rows.append(row)
                continue
            if not row.get("name") and not row.get("id"):
                raise serializers.ValidationError(
                    {
                        "family_details": (
                            f"Row {index + 1}: name is required for new members."
                        )
                    }
                )
            if not row.get("relation_id"):
                raise serializers.ValidationError(
                    {
                        "family_details": (
                            f"Row {index + 1}: relation_id is required."
                        )
                    }
                )
            if row.get("phone"):
                row["phone"] = validate_mobile_number(row["phone"])
            if row.get("date_of_birth"):
                try:
                    parsed = parse_date_value(row["date_of_birth"])
                except Exception as exc:
                    raise serializers.ValidationError(
                        {f"family_details[{index}].date_of_birth": str(exc)}
                    )
                row["date_of_birth"] = parsed.isoformat() if parsed else None
            cleaned_rows.append(row)

        return {"family_details": cleaned_rows}

    @staticmethod
    def validate_education(data: dict, action, employee, record_id) -> dict:
        from apps.employees.constants.education_details import EDUCATION_ROW_EDITABLE
        from apps.employees.services.education_details import _parse_date_value

        items = data.get("education_details")
        if items is None:
            raise serializers.ValidationError(
                {"education_details": "education_details list is required."}
            )
        if not isinstance(items, list):
            raise serializers.ValidationError(
                {"education_details": "education_details must be a list."}
            )
        if not items:
            raise serializers.ValidationError(
                {"education_details": "Provide at least one education row."}
            )

        cleaned_rows = []
        for index, item in enumerate(items):
            row = dict(item)
            unknown = set(row.keys()) - EDUCATION_ROW_EDITABLE
            if unknown:
                raise serializers.ValidationError(
                    {
                        "education_details": (
                            f"Row {index + 1}: fields not allowed: "
                            f"{', '.join(sorted(unknown))}"
                        )
                    }
                )
            if row.get("remove") or row.get("delete"):
                cleaned_rows.append(row)
                continue
            if not row.get("qualification_id") and not row.get("qualification"):
                raise serializers.ValidationError(
                    {
                        "education_details": (
                            f"Row {index + 1}: qualification is required."
                        )
                    }
                )
            if not row.get("institution_id") and not row.get("institution") and not row.get("institution_name"):
                raise serializers.ValidationError(
                    {
                        "education_details": (
                            f"Row {index + 1}: institution is required."
                        )
                    }
                )
            year = row.get("year_of_passing")
            if year is None:
                year = row.get("yearOfPassing")
            if row.get("year_of_passing_id") and year is None:
                from apps.employees.models.masters.education import PassingYear

                passing = PassingYear.objects.filter(pk=row["year_of_passing_id"]).first()
                if passing:
                    year = passing.year
                    row["year_of_passing"] = passing.year
            if year is None:
                raise serializers.ValidationError(
                    {
                        "education_details": (
                            f"Row {index + 1}: year_of_passing or year_of_passing_id required."
                        )
                    }
                )
            year = int(year)
            if year < 1950 or year > date.today().year + 5:
                raise serializers.ValidationError(
                    {
                        "education_details": (
                            f"Row {index + 1}: enter a valid year of passing."
                        )
                    }
                )
            row["year_of_passing"] = year
            row["yearOfPassing"] = year
            if row.get("percentage_or_cgpa") is not None:
                validate_percentage_or_cgpa(row["percentage_or_cgpa"])
            if "from_date" in row and "start_date" not in row:
                row["start_date"] = row["from_date"]
            if "to_date" in row and "end_date" not in row:
                row["end_date"] = row["to_date"]
            for date_field in ("start_date", "end_date"):
                if row.get(date_field):
                    row[date_field] = _parse_date_value(row[date_field]).isoformat()
            if row.get("start_date") and row.get("end_date") and row["end_date"] < row["start_date"]:
                raise serializers.ValidationError(
                    {
                        "education_details": (
                            f"Row {index + 1}: to_date must be on or after from_date."
                        )
                    }
                )
            cleaned_rows.append(row)

        return {"education_details": cleaned_rows}

    @staticmethod
    def validate_bank(data: dict, action, employee, record_id) -> dict:
        if action == "CREATE":
            required = {"bank_id", "account_number", "ifsc_code"}
            missing = required - set(data.keys())
            if missing:
                raise serializers.ValidationError({
                    "request_data": f"Required fields: {', '.join(missing)}"
                })
        if "ifsc_code" in data and data["ifsc_code"]:
            data["ifsc_code"] = validate_ifsc_code(data["ifsc_code"])
        return data

    @staticmethod
    def validate_insurance(data: dict, action, employee, record_id) -> dict:
        if "insurance_details" in data:
            from apps.employees.services.insurance_details import validate_insurance_details

            return validate_insurance_details(data)
        if action == "CREATE" and not data.get("policy_number"):
            raise serializers.ValidationError(
                {"request_data": "Policy number is required."}
            )
        return data

    @staticmethod
    def validate_nominee(data: dict, action, employee, record_id) -> dict:
        if "nominee_details" in data:
            from apps.employees.services.nominee_details import validate_nominee_details

            return validate_nominee_details(data)

        if action == "CREATE" and not data.get("name"):
            raise serializers.ValidationError(
                {"request_data": "Nominee name is required."}
            )
        if "nominee_percentage" in data and data["nominee_percentage"] is not None:
            pct = Decimal(str(data["nominee_percentage"]))
            if pct <= 0 or pct > 100:
                raise serializers.ValidationError(
                    {"nominee_percentage": "Nominee percentage must be between 1 and 100."}
                )
            if employee:
                validate_nominee_percentage_total(employee, pct, exclude_record_id=record_id)
        return data

    @staticmethod
    def validate_language(data: dict, action, employee, record_id) -> dict:
        from apps.employees.constants.language_details import LANGUAGE_PROFICIENCY_EDITABLE
        from apps.employees.models.masters.misc import Language, LanguageProficiency

        items = data.get("language_details")
        if items is None:
            raise serializers.ValidationError(
                {"language_details": "language_details list is required."}
            )
        if not isinstance(items, list):
            raise serializers.ValidationError(
                {"language_details": "language_details must be a list."}
            )
        if not items:
            raise serializers.ValidationError(
                {"language_details": "Provide at least one language proficiency row."}
            )

        cleaned_rows = []
        seen_languages = set()
        for index, item in enumerate(items):
            row = dict(item)
            unknown = set(row.keys()) - LANGUAGE_PROFICIENCY_EDITABLE
            if unknown:
                raise serializers.ValidationError(
                    {
                        "language_details": (
                            f"Row {index + 1}: fields not allowed: "
                            f"{', '.join(sorted(unknown))}"
                        )
                    }
                )
            if row.get("remove") or row.get("delete"):
                cleaned_rows.append(row)
                continue

            language_id = row.get("language_id")
            language_name = (row.get("language") or "").strip()
            if not language_id and language_name:
                language = (
                    Language.objects.filter(label__iexact=language_name, is_active=True)
                    .first()
                    or Language.objects.filter(
                        code__iexact=language_name,
                        is_active=True,
                    ).first()
                )
                if not language:
                    raise serializers.ValidationError(
                        {
                            "language_details": (
                                f"Row {index + 1}: language must match an active "
                                "language master."
                            )
                        }
                    )
                language_id = language.id
                row["language_id"] = language_id
            if not language_id:
                raise serializers.ValidationError(
                    {"language_details": f"Row {index + 1}: language_id is required."}
                )
            if not Language.objects.filter(id=language_id, is_active=True).exists():
                raise serializers.ValidationError(
                    {"language_details": f"Row {index + 1}: invalid language_id."}
                )
            if language_id in seen_languages:
                raise serializers.ValidationError(
                    {"language_details": f"Row {index + 1}: duplicate language."}
                )
            seen_languages.add(language_id)

            proficiency_level_id = row.get("proficiency_level_id")
            proficiency_level_name = (row.get("proficiency_level") or "").strip()
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
                            "language_details": (
                                f"Row {index + 1}: proficiency_level must match an "
                                "active language proficiency master."
                            )
                        }
                    )
                proficiency_level_id = proficiency_level.id
                row["proficiency_level_id"] = proficiency_level_id

            if proficiency_level_id:
                if not LanguageProficiency.objects.filter(
                    id=proficiency_level_id,
                    is_active=True,
                ).exists():
                    raise serializers.ValidationError(
                        {
                            "language_details": (
                                f"Row {index + 1}: invalid proficiency_level_id."
                            )
                        }
                    )
                for proficiency_field in (
                    "read_proficiency_id",
                    "write_proficiency_id",
                    "speak_proficiency_id",
                ):
                    if not row.get(proficiency_field):
                        row[proficiency_field] = proficiency_level_id

            for checkbox_field, proficiency_field in (
                ("can_read", "read_proficiency_id"),
                ("can_write", "write_proficiency_id"),
                ("can_speak", "speak_proficiency_id"),
            ):
                proficiency_id = row.get(proficiency_field)
                if row.get(checkbox_field) and not proficiency_id:
                    raise serializers.ValidationError(
                        {
                            "language_details": (
                                f"Row {index + 1}: {proficiency_field} or "
                                "proficiency_level_id is required."
                            )
                        }
                    )
                if proficiency_id and not LanguageProficiency.objects.filter(
                    id=proficiency_id,
                    is_active=True,
                ).exists():
                    raise serializers.ValidationError(
                        {
                            "language_details": (
                                f"Row {index + 1}: invalid {proficiency_field}."
                            )
                        }
                    )

            cleaned_rows.append(row)

        return {"language_details": cleaned_rows}

    @staticmethod
    def validate_passport(data: dict, action, employee, record_id) -> dict:
        rows = data.get("passport_visa_records")
        if rows is not None:
            if not rows:
                raise serializers.ValidationError(
                    {"passport_visa_records": "Provide at least one passport/visa record."}
                )
            cleaned_rows = []
            for index, row in enumerate(rows):
                row = dict(row)
                if row.get("remove") or row.get("delete"):
                    cleaned_rows.append(row)
                    continue
                if not row.get("passport_number") and action == "CREATE":
                    raise serializers.ValidationError(
                        {"passport_visa_records": f"Row {index + 1}: passport number is required."}
                    )
                if row.get("passport_number"):
                    row["passport_number"] = validate_passport_number(row["passport_number"])
                if row.get("issue_date") and row.get("expiry_date"):
                    issue = row["issue_date"] if isinstance(row["issue_date"], date) \
                        else datetime.strptime(str(row["issue_date"]), "%Y-%m-%d").date()
                    expiry = row["expiry_date"] if isinstance(row["expiry_date"], date) \
                        else datetime.strptime(str(row["expiry_date"]), "%Y-%m-%d").date()
                    if expiry <= issue:
                        raise serializers.ValidationError(
                            {"passport_visa_records": f"Row {index + 1}: expiry must be after issue date."}
                        )
                cleaned_rows.append(row)
            return {"passport_visa_records": cleaned_rows}

        if action == "CREATE" and not data.get("passport_number"):
            raise serializers.ValidationError(
                {"request_data": "Passport number is required."}
            )
        if "passport_number" in data and data["passport_number"]:
            data["passport_number"] = validate_passport_number(data["passport_number"])
        if data.get("issue_date") and data.get("expiry_date"):
            from datetime import datetime
            issue = data["issue_date"] if isinstance(data["issue_date"], date) \
                else datetime.strptime(data["issue_date"], "%Y-%m-%d").date()
            expiry = data["expiry_date"] if isinstance(data["expiry_date"], date) \
                else datetime.strptime(data["expiry_date"], "%Y-%m-%d").date()
            if expiry <= issue:
                raise serializers.ValidationError(
                    {"expiry_date": "Passport expiry date must be after issue date."}
                )
        return data

    @staticmethod
    def validate_experience(data: dict, action, employee, record_id) -> dict:
        if action == "CREATE" and not data.get("company_name"):
            raise serializers.ValidationError(
                {"request_data": "Company name is required."}
            )
        if not data.get("is_current") and not data.get("end_date"):
            if action == "CREATE" and data.get("start_date"):
                raise serializers.ValidationError(
                    {"end_date": "End date is required for past employment."}
                )
        if data.get("start_date") and data.get("end_date"):
            from datetime import datetime
            start = data["start_date"] if isinstance(data["start_date"], date) \
                else datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            end = data["end_date"] if isinstance(data["end_date"], date) \
                else datetime.strptime(data["end_date"], "%Y-%m-%d").date()
            if end <= start:
                raise serializers.ValidationError(
                    {"end_date": "End date must be after start date."}
                )
        return data

    @staticmethod
    def validate_skill(data: dict, action, employee, record_id) -> dict:
        if action == "CREATE" and not data.get("skill_name"):
            raise serializers.ValidationError(
                {"request_data": "Skill name is required."}
            )
        if data.get("certification_date") and data.get("certification_expiry"):
            from datetime import datetime
            cert_date = data["certification_date"] if isinstance(data["certification_date"], date) \
                else datetime.strptime(data["certification_date"], "%Y-%m-%d").date()
            cert_exp = data["certification_expiry"] if isinstance(data["certification_expiry"], date) \
                else datetime.strptime(data["certification_expiry"], "%Y-%m-%d").date()
            if cert_exp <= cert_date:
                raise serializers.ValidationError(
                    {"certification_expiry": "Certification expiry must be after issue date."}
                )
        return data

    @staticmethod
    def validate_medical(data: dict, action, employee, record_id) -> dict:
        if "medical_details" in data:
            from apps.employees.services.medical_details import validate_medical_details

            data = validate_medical_details(data)
            details = data["medical_details"]
            if details.get("emergency_contact_number"):
                details["emergency_contact_number"] = validate_mobile_number(
                    details["emergency_contact_number"]
                )
            return data

        if data.get("emergency_contact_number"):
            data["emergency_contact_number"] = validate_mobile_number(
                data["emergency_contact_number"]
            )
        if data.get("emergency_contact_alt_number"):
            data["emergency_contact_alt_number"] = validate_mobile_number(
                data["emergency_contact_alt_number"]
            )
        return data

    @staticmethod
    def validate_social(data: dict, action, employee, record_id) -> dict:
        if "social_profile" in data:
            profile_data = dict(data["social_profile"] or {})
            data["social_profile"] = ModuleValidator.validate_social(
                profile_data,
                action,
                employee,
                record_id,
            )
            return data

        url_fields = [
            "linkedin_url", "github_url", "twitter_url",
            "facebook_url", "instagram_url", "personal_website",
            "personal_website_url", "portfolio_url", "stackoverflow_url",
        ]
        for field in url_fields:
            if data.get(field):
                data[field] = validate_url(data[field])
        if data.get("personal_website_url") and not data.get("personal_website"):
            data["personal_website"] = data.pop("personal_website_url")
        return data

    @staticmethod
    def validate_document(data: dict, action, employee, record_id) -> dict:
        if action == "CREATE" and not data.get("document_name"):
            raise serializers.ValidationError(
                {"request_data": "Document name is required."}
            )
        return data


# ─────────────────────────────────────────────────────────────────────────────
# Module validator dispatch table
# ─────────────────────────────────────────────────────────────────────────────

_MODULE_VALIDATORS = {
    ESSModule.PROFILE:    ModuleValidator.validate_profile,
    ESSModule.PERSONAL:   ModuleValidator.validate_personal,
    ESSModule.EMPLOYMENT: ModuleValidator.validate_employment,
    ESSModule.ADDRESS:    ModuleValidator.validate_address,
    ESSModule.FAMILY:     ModuleValidator.validate_family,
    ESSModule.EDUCATION:  ModuleValidator.validate_education,
    ESSModule.BANK:       ModuleValidator.validate_bank,
    ESSModule.INSURANCE:  ModuleValidator.validate_insurance,
    ESSModule.NOMINEE:    ModuleValidator.validate_nominee,
    ESSModule.LANGUAGE:   ModuleValidator.validate_language,
    ESSModule.PASSPORT:   ModuleValidator.validate_passport,
    ESSModule.EXPERIENCE: ModuleValidator.validate_experience,
    ESSModule.SKILL:      ModuleValidator.validate_skill,
    ESSModule.MEDICAL:    ModuleValidator.validate_medical,
    ESSModule.SOCIAL:     ModuleValidator.validate_social,
    ESSModule.DOCUMENT:   ModuleValidator.validate_document,
}
