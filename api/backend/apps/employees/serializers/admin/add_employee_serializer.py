"""
Add Employee Serializer — Admin Side
Flat structure matching the 8-section frontend form exactly.
"""

import logging
import re
from datetime import date, datetime
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import serializers

from apps.employees.models.contact import EmployeeContacts
from apps.employees.models.employee import Employee
from apps.employees.models.masters.employment import EmployeeType
from apps.employees.models.masters.hr_setup import BusinessUnit, Shift
from apps.employees.models.masters.location import OfficeLocation
from apps.employees.models.masters.misc import Relation
from apps.employees.models.masters.organization import Company, Department, Designation, Grade, Team
from apps.employees.models.masters.payroll import SalaryStructure
from apps.employees.models.masters.performance_training import AssetCategory, AssetCondition
from apps.employees.models.masters.personal import BloodGroup, Gender, MaritalStatus
from apps.employees.serializers.admin.bank_statutory_serializer import BankAccountUpdateSerializer

logger = logging.getLogger(__name__)

try:
    from drf_spectacular.utils import extend_schema_field
except ImportError:
    def extend_schema_field(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


# ---------------------------------------------------------------------------
# Compiled validation patterns
# ---------------------------------------------------------------------------

_PHONE_RE = re.compile(r"^\+?[0-9][0-9\s\-]{6,19}$")
_AADHAAR_RE = re.compile(r"^\d{12}$")
_PAN_RE = re.compile(r"^[A-Z]{5}\d{4}[A-Z]$")
_UAN_RE = re.compile(r"^\d{12}$")
_IFSC_RE = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")

_MIN_EMPLOYEE_AGE = 18


# ---------------------------------------------------------------------------
# Custom field
# ---------------------------------------------------------------------------

class MasterOrUUIDField(serializers.Field):
    """Accept a master-model PK or a raw UUID string.

    Returns the model instance if found, otherwise returns the raw value
    so the service layer can handle deferred resolution.
    """

    def __init__(self, queryset=None, **kwargs):
        self.queryset = queryset
        super().__init__(**kwargs)

    def to_internal_value(self, data: Any) -> Any:
        if not data and data != 0:
            return None
        if hasattr(data, "_meta"):
            return data
        if self.queryset is not None:
            try:
                return self.queryset.get(pk=data)
            except (ObjectDoesNotExist, ValueError, TypeError):
                model_name = self.queryset.model._meta.verbose_name.title()
                raise serializers.ValidationError(
                    f"Select a valid {model_name}."
                )
        return data

    def to_representation(self, value: Any) -> Any:
        if value is None:
            return None
        return str(value.pk) if hasattr(value, "pk") else str(value)


# ---------------------------------------------------------------------------
# Private validation helpers
# ---------------------------------------------------------------------------

def _validate_phone(value: str, message: str) -> str:
    value = value.strip()
    if not _PHONE_RE.fullmatch(value):
        raise serializers.ValidationError(message)
    return value


def _validate_company_scoped_master(master: Any, company: Any, field_name: str) -> None:
    if getattr(master, "company_id", None) != company.id:
        label = field_name.replace("_", " ").title()
        raise serializers.ValidationError(
            {field_name: f"{label} does not belong to the selected company."}
        )


def _parse_asset_date(value: Any, field_label: str) -> date:
    if isinstance(value, date):
        return value
    try:
        return datetime.fromisoformat(str(value)).date()
    except (ValueError, TypeError):
        raise serializers.ValidationError(f"Invalid date format for {field_label}.")


# ---------------------------------------------------------------------------
# Main serializer
# ---------------------------------------------------------------------------

class AdminAddEmployeeSerializer(serializers.Serializer):
    """Deserialize and validate the full add-employee payload.

    Sections mirror the 8-section frontend form.
    """

    # --- Section 01: Basic Information ----------------------------------

    employee_code = serializers.CharField(max_length=30)
    salutation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    first_name = serializers.CharField(max_length=100)
    middle_name = serializers.CharField(
        required=False, max_length=100, allow_blank=True, allow_null=True
    )
    last_name = serializers.CharField(max_length=100)
    profile_photo = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    gender = MasterOrUUIDField(queryset=Gender.objects.filter(is_active=True))
    date_of_birth = serializers.DateField()
    marital_status = MasterOrUUIDField(
        queryset=MaritalStatus.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    blood_group = MasterOrUUIDField(
        queryset=BloodGroup.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    official_email = serializers.EmailField(max_length=255)
    personal_email = serializers.EmailField(
        required=False, max_length=255, allow_blank=True, allow_null=True
    )
    mobile_number = serializers.CharField(max_length=20)
    alternate_mobile_number = serializers.CharField(
        required=False, max_length=20, allow_blank=True, allow_null=True
    )
    joining_date = serializers.DateField()
    date_of_confirmation = serializers.DateField(required=False, allow_null=True)
    employee_status = serializers.ChoiceField(
        choices=Employee.StatusChoices.choices,
        required=False,
        default=Employee.StatusChoices.ACTIVE,
    )
    referred_by = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    onboarding_policy = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    allow_employee_to_fill_information = serializers.BooleanField(
        required=False, default=False
    )
    probation_period = serializers.IntegerField(
        required=False, min_value=0, allow_null=True
    )
    employee_number_series = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    father_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    spouse_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    emergency_contact_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True, allow_null=True
    )
    emergency_contact_number = serializers.CharField(
        max_length=20, required=False, allow_blank=True, allow_null=True
    )
    emergency_contact_relationship = MasterOrUUIDField(
        queryset=Relation.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    # --- Section 02: Job Details ----------------------------------------

    employment_type = MasterOrUUIDField(
        queryset=EmployeeType.objects.filter(is_active=True)
    )
    department = MasterOrUUIDField(
        queryset=Department.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    designation = MasterOrUUIDField(
        queryset=Designation.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    work_location = MasterOrUUIDField(
        queryset=OfficeLocation.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    company = MasterOrUUIDField(
        queryset=Company.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    system_role = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    business_unit = serializers.UUIDField(required=False, allow_null=True)
    grade = MasterOrUUIDField(
        queryset=Grade.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    shift = MasterOrUUIDField(
        queryset=Shift.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    reporting_manager = MasterOrUUIDField(
        queryset=Employee.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    # --- Section 03: Attendance Settings --------------------------------

    weekly_off = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    working_hours_start = serializers.TimeField(required=False, allow_null=True)
    working_hours_end = serializers.TimeField(required=False, allow_null=True)
    weekly_off_days = serializers.ListField(
        child=serializers.CharField(), required=False, allow_null=True
    )
    attendance_tracking_mode = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    # --- Section 04: Payroll Information --------------------------------

    salary_structure = MasterOrUUIDField(
        queryset=SalaryStructure.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    basic_salary = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True, min_value=0
    )
    bank_account = BankAccountUpdateSerializer(required=False, allow_null=True)
    pan_number = serializers.CharField(
        required=False, max_length=10, allow_blank=True, allow_null=True
    )

    # --- Section 05: Leave Configuration --------------------------------

    leave_policy = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    annual_leave_balance = serializers.IntegerField(
        required=False, allow_null=True, min_value=0
    )
    sick_leave_balance = serializers.IntegerField(
        required=False, allow_null=True, min_value=0
    )

    # --- Section 06: Background Check -----------------------------------

    verification_status = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    agency_name = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    verified_by = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=150
    )
    reference_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    background_remarks = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    # --- Section 07: Asset Management -----------------------------------

    assets = serializers.ListField(
        child=serializers.DictField(), required=False, allow_null=True
    )

    # --- Section 08: Account Access -------------------------------------

    username = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    temporary_password = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    system_role = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    # --- Metadata -------------------------------------------------------

    aadhaar_number = serializers.CharField(
        required=False, max_length=12, allow_blank=True, allow_null=True
    )
    uan_number = serializers.CharField(
        required=False, max_length=12, allow_blank=True, allow_null=True
    )
    esi_number = serializers.CharField(
        required=False, max_length=17, allow_blank=True, allow_null=True
    )
    passport_number = serializers.CharField(
        required=False, max_length=20, allow_blank=True, allow_null=True
    )
    is_draft = serializers.BooleanField(required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)

    # -----------------------------------------------------------------------
    # Field-level validators
    # -----------------------------------------------------------------------

    def validate_first_name(self, value: str) -> str:
        return value.strip() if value else value

    def validate_last_name(self, value: str) -> str:
        return value.strip() if value else value

    def validate_emergency_contact_name(self, value: str) -> str:
        return value.strip() if value else value

    def validate_employee_code(self, value: str) -> str:
        value = value.strip()
        if Employee.objects.filter(employee_code__iexact=value).exists():
            raise serializers.ValidationError("Employee code already exists.")
        return value

    def validate_official_email(self, value: str) -> str:
        value = value.strip().lower()
        if EmployeeContacts.objects.filter(official_email__iexact=value).exists():
            raise serializers.ValidationError("Official email already exists.")
        return value

    def validate_personal_email(self, value: str) -> str:
        return value.strip().lower() if value else value

    def validate_mobile_number(self, value: str) -> str:
        return _validate_phone(value, "Enter a valid mobile number.")

    def validate_alternate_mobile_number(self, value: str) -> str:
        if not value:
            return value
        return _validate_phone(value, "Enter a valid alternate mobile number.")

    def validate_emergency_contact_number(self, value: str) -> str:
        if not value:
            return value
        return _validate_phone(value, "Enter a valid emergency contact number.")

    def validate_date_of_birth(self, value: date) -> date:
        today = date.today()
        if value >= today:
            raise serializers.ValidationError("Date of birth must be in the past.")
        age = (
            today.year
            - value.year
            - ((today.month, today.day) < (value.month, value.day))
        )
        if age < _MIN_EMPLOYEE_AGE:
            raise serializers.ValidationError(
                f"Employee must be at least {_MIN_EMPLOYEE_AGE} years old."
            )
        return value

    def validate_aadhaar_number(self, value: str) -> str:
        if not value:
            return value
        value = value.strip()
        if not _AADHAAR_RE.fullmatch(value):
            raise serializers.ValidationError(
                "Enter a valid 12-digit Aadhaar number."
            )
        return value

    def validate_pan_number(self, value: str) -> str:
        if not value:
            return value
        value = value.strip().upper()
        if not _PAN_RE.fullmatch(value):
            raise serializers.ValidationError(
                "Enter a valid PAN number (e.g. ABCDE1234F)."
            )
        return value

    def validate_uan_number(self, value: str) -> str:
        if not value:
            return value
        value = value.strip()
        if not _UAN_RE.fullmatch(value):
            raise serializers.ValidationError(
                "Enter a valid 12-digit UAN number."
            )
        return value

    def validate_username(self, value: str) -> str:
        if not value:
            return value
        User = get_user_model()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already in use.")
        return value

    def validate_joining_date(self, value: date) -> date:
        today = date.today()
        if value > today:
            raise serializers.ValidationError(
                "Joining date cannot be in the future."
            )
        return value

    def validate_esi_number(self, value: str) -> str:
        if not value:
            return value
        value = value.strip()
        if len(value) < 6 or len(value) > 17:
            raise serializers.ValidationError(
                "Enter a valid ESI number (6-17 characters)."
            )
        return value

    def validate_bank_account(self, value: dict) -> dict:
        if not value:
            return value
        ifsc_code = value.get("ifsc_code")
        if ifsc_code:
            ifsc_code = ifsc_code.strip().upper()
            if not _IFSC_RE.fullmatch(ifsc_code):
                raise serializers.ValidationError(
                    {"ifsc_code": "IFSC code must be 11 characters (e.g., HDFC0001234)."}
                )
            value["ifsc_code"] = ifsc_code
        return value

    def validate_basic_salary(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Basic salary must be greater than 0.")
        return value

    def validate(self, attrs: dict) -> dict:
        self._validate_account_access_pairing(attrs)
        self._validate_confirmation_date(attrs)
        self._validate_mobile_uniqueness(attrs)
        self._validate_company_scoped_masters(attrs)
        self._validate_working_hours(attrs)
        self._validate_assets(attrs)
        return attrs

    # -----------------------------------------------------------------------
    # Private cross-field helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _validate_account_access_pairing(attrs: dict) -> None:
        if attrs.get("username") and not attrs.get("temporary_password"):
            raise serializers.ValidationError(
                {
                    "temporary_password": "Temporary password is required when creating an account."
                }
            )

    @staticmethod
    def _validate_confirmation_date(attrs: dict) -> None:
        confirmation_date = attrs.get("date_of_confirmation")
        joining_date = attrs.get("joining_date")
        if confirmation_date and joining_date and confirmation_date < joining_date:
            raise serializers.ValidationError(
                {
                    "date_of_confirmation": "Confirmation date cannot be before joining date."
                }
            )

    @staticmethod
    def _validate_mobile_uniqueness(attrs: dict) -> None:
        mobile = attrs.get("mobile_number")
        alternate = attrs.get("alternate_mobile_number")
        if mobile and alternate and mobile == alternate:
            raise serializers.ValidationError(
                {
                    "alternate_mobile_number": "Alternate mobile number must differ from primary mobile number."
                }
            )

    @staticmethod
    def _validate_company_scoped_masters(attrs: dict) -> None:
        company = attrs.get("company")
        if not company or not hasattr(company, "id"):
            return
        for field in ("department", "designation", "grade"):
            master = attrs.get(field)
            if master and hasattr(master, "company_id"):
                _validate_company_scoped_master(master, company, field)
        shift = attrs.get("shift")
        if shift and hasattr(shift, "company_id") and shift.company_id != company.id:
            raise serializers.ValidationError(
                {"shift": "Shift does not belong to the selected company."}
            )
        business_unit = attrs.get("business_unit")
        if business_unit and not BusinessUnit.objects.filter(
            id=business_unit, company_id=company.id, is_active=True
        ).exists():
            raise serializers.ValidationError(
                {"business_unit": "Business unit does not belong to the selected company."}
            )
        reporting_manager = attrs.get("reporting_manager")
        if (
            reporting_manager
            and hasattr(reporting_manager, "company_id")
            and reporting_manager.company_id != company.id
        ):
            raise serializers.ValidationError(
                {"reporting_manager": "Reporting manager does not belong to the selected company."}
            )

    @staticmethod
    def _validate_working_hours(attrs: dict) -> None:
        start_time = attrs.get("working_hours_start")
        end_time = attrs.get("working_hours_end")
        if start_time and end_time:
            if start_time >= end_time:
                raise serializers.ValidationError(
                    {"working_hours_end": "End time must be after start time."}
                )
        elif start_time and not end_time:
            raise serializers.ValidationError(
                {"working_hours_end": "End time is required when start time is provided."}
            )
        elif end_time and not start_time:
            raise serializers.ValidationError(
                {"working_hours_start": "Start time is required when end time is provided."}
            )

    @staticmethod
    def _validate_assets(attrs: dict) -> None:
        for index, asset in enumerate(attrs.get("assets") or []):
            asset_name = asset.get("asset_name")
            asset_code = asset.get("asset_id") or asset.get("asset_code")
            assign_date_raw = asset.get("asset_assign_date")
            if not asset_name or not asset_code or not assign_date_raw:
                raise serializers.ValidationError(
                    {
                        f"assets[{index}]": "Each asset must include asset_name, asset_code (or asset_id), and asset_assign_date."
                    }
                )
            assign_date = _parse_asset_date(
                assign_date_raw, f"assets[{index}].asset_assign_date"
            )
            return_date_raw = asset.get("asset_return_date")
            if return_date_raw:
                return_date = _parse_asset_date(
                    return_date_raw, f"assets[{index}].asset_return_date"
                )
                if return_date < assign_date:
                    raise serializers.ValidationError(
                        {
                            f"assets[{index}]": "asset_return_date cannot be before asset_assign_date."
                        }
                    )
            if assign_date > date.today():
                raise serializers.ValidationError(
                    {
                        f"assets[{index}]": "Asset assignment date cannot be in the future."
                    }
                )


# ---------------------------------------------------------------------------
# Response serializer
# ---------------------------------------------------------------------------

class AdminAddEmployeeResponseSerializer(serializers.Serializer):
    """Read-only serializer for the add-employee API response payload."""

    employee_id = serializers.UUIDField(read_only=True)
    employee_code = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    official_email = serializers.EmailField(read_only=True)
    mobile_number = serializers.CharField(read_only=True)
    employee_status = serializers.CharField(read_only=True)
    company = serializers.DictField(read_only=True)
    department = serializers.DictField(read_only=True, allow_null=True)
    designation = serializers.DictField(read_only=True, allow_null=True)
    is_draft = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)


class AdminEmployeeDirectorySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    employee_code = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    work_email = serializers.CharField(source="contacts.official_email", read_only=True, allow_null=True)
    phone = serializers.CharField(source="contacts.mobile_no", read_only=True, allow_null=True)
    department_id = serializers.UUIDField(source="employment_details.department_id", read_only=True, allow_null=True)
    department = serializers.CharField(source="employment_details.department.name", read_only=True, allow_null=True)
    designation_id = serializers.UUIDField(source="employment_details.designation_id", read_only=True, allow_null=True)
    designation = serializers.CharField(source="employment_details.designation.title", read_only=True, allow_null=True)
    team_id = serializers.SerializerMethodField()
    team = serializers.CharField(source="employment_details.team", read_only=True, allow_null=True)
    location = serializers.SerializerMethodField()
    profile_photo = serializers.CharField(source="profile_picture_url", read_only=True, allow_null=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_code",
            "first_name",
            "middle_name",
            "last_name",
            "full_name",
            "profile_photo",
            "status",
            "status_display",
            "department_id",
            "department",
            "designation_id",
            "designation",
            "team_id",
            "team",
            "date_of_joining",
            "work_email",
            "phone",
            "location",
        ]
        read_only_fields = fields

    @staticmethod
    def _employment_details(obj):
        try:
            return obj.employment_details
        except ObjectDoesNotExist:
            return None

    def get_location(self, obj):
        employment = self._employment_details(obj)
        office_location = getattr(employment, "office_location", None)
        return (
            getattr(office_location, "name", None)
            or getattr(office_location, "label", None)
            or getattr(office_location, "code", None)
        )

    def get_team_id(self, obj):
        employment = self._employment_details(obj)
        team = getattr(employment, "team", None)
        if not team:
            return None
        if isinstance(team, Team):
            return team.id

        teams = Team.objects.filter(
            company_id=obj.company_id,
            is_active=True,
        ).filter(Q(name__iexact=team) | Q(code__iexact=team))
        department_id = getattr(employment, "department_id", None)
        if department_id:
            department_team = teams.filter(department_id=department_id).first()
            if department_team:
                return department_team.id
        team = teams.first()
        return team.id if team else None


# ---------------------------------------------------------------------------
# Rehire serializer
# ---------------------------------------------------------------------------

class RehireEmployeeSerializer(serializers.Serializer):
    """Payload for rehiring a former (inactive) employee."""

    former_employee_id   = serializers.UUIDField()
    rehire_date          = serializers.DateField()
    new_employee_code    = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=30)
    rehire_remarks       = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    restore_salary       = serializers.BooleanField(default=False)
    restore_assets       = serializers.BooleanField(default=False)
    restore_leaves       = serializers.BooleanField(default=False)

    # Optional overrides for the new employment period
    employment_type      = MasterOrUUIDField(queryset=EmployeeType.objects.filter(is_active=True), required=False, allow_null=True)
    department           = MasterOrUUIDField(queryset=Department.objects.filter(is_active=True), required=False, allow_null=True)
    designation          = MasterOrUUIDField(queryset=Designation.objects.filter(is_active=True), required=False, allow_null=True)
    reporting_manager    = MasterOrUUIDField(queryset=Employee.objects.filter(is_active=True), required=False, allow_null=True)
    work_location        = MasterOrUUIDField(queryset=OfficeLocation.objects.filter(is_active=True), required=False, allow_null=True)
    shift                = MasterOrUUIDField(queryset=Shift.objects.filter(is_active=True), required=False, allow_null=True)
    username             = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    temporary_password   = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_rehire_date(self, value: date) -> date:
        if value > date.today():
            raise serializers.ValidationError("Rehire date cannot be in the future.")
        return value


# ---------------------------------------------------------------------------
# Former employee search serializer (response)
# ---------------------------------------------------------------------------

class FormerEmployeeSerializer(serializers.Serializer):
    employee_id         = serializers.UUIDField()
    employee_code       = serializers.CharField()
    full_name           = serializers.CharField()
    department          = serializers.CharField(allow_null=True)
    designation         = serializers.CharField(allow_null=True)
    last_working_date   = serializers.DateField(allow_null=True)
    separation_reason   = serializers.CharField(allow_null=True)
    status              = serializers.CharField()
    profile_picture_url = serializers.CharField(allow_null=True)


# ---------------------------------------------------------------------------
# Bulk import serializers
# ---------------------------------------------------------------------------

class BulkImportSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        ext = value.name.rsplit(".", 1)[-1].lower()
        if ext not in ("xlsx", "xls", "csv"):
            raise serializers.ValidationError("Only .xlsx, .xls, .csv files are allowed.")
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size must not exceed 10 MB.")
        return value


class BulkImportRowResultSerializer(serializers.Serializer):
    row          = serializers.IntegerField()
    employee_code = serializers.CharField(allow_null=True, required=False)
    status       = serializers.ChoiceField(choices=["success", "failed"])
    errors       = serializers.DictField(child=serializers.CharField(), required=False)


class BulkImportResultSerializer(serializers.Serializer):
    total_rows = serializers.IntegerField()
    success_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    results = BulkImportRowResultSerializer(many=True)


# ---------------------------------------------------------------------------
# Draft serializers
# ---------------------------------------------------------------------------

class SaveDraftSerializer(serializers.Serializer):
    draft_data = serializers.JSONField()
    draft_type = serializers.ChoiceField(choices=["new", "rehire"], default="new")
    draft_id   = serializers.UUIDField(required=False, allow_null=True)


class DraftResponseSerializer(serializers.Serializer):
    draft_id   = serializers.CharField()
    draft_type = serializers.CharField()
    saved_at   = serializers.CharField()
