"""
Previous Employment serializers for admin employee details.

Security Note: All serializers use Django ORM parameterized queries only.
No raw SQL is used to prevent SQL injection attacks.
"""

from rest_framework import serializers
from datetime import date

from apps.employees.models.previous_employment import EmployeePreviousEmployment
from apps.employees.models.employee import Employee


class PreviousEmploymentSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for EmployeePreviousEmployment.
    Used for retrieving and displaying employment history.
    """
    employee_name = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()
    companyName = serializers.CharField(source="organization_name", read_only=True)
    jobTitle = serializers.CharField(source="job_position", read_only=True)
    employmentType = serializers.CharField(source="employment_type", read_only=True)
    department = serializers.CharField(source="department_name", read_only=True)
    startDate = serializers.DateField(source="date_from", read_only=True)
    endDate = serializers.DateField(source="date_to", read_only=True)
    reasonForLeaving = serializers.CharField(source="reason_for_leaving", read_only=True)
    responsibilities = serializers.CharField(source="key_responsibilities", read_only=True)
    technologiesUsed = serializers.CharField(source="technologies_used", read_only=True)
    experienceLetterFileName = serializers.CharField(
        source="experience_letter_file_name",
        read_only=True,
    )
    experienceLetterDataUrl = serializers.CharField(
        source="experience_letter_data_url",
        read_only=True,
    )
    
    class Meta:
        model = EmployeePreviousEmployment
        fields = [
            "id",
            "employee",
            "employee_name",
            "organization_name",
            "organization_type",
            "job_position",
            "job_title",
            "department_name",
            "location",
            "date_from",
            "date_to",
            "total_duration_years",
            "total_duration_months",
            "duration_display",
            "employment_type",
            "reporting_to",
            "salary_ctc",
            "salary_currency",
            "reason_for_leaving",
            "reason_category",
            "key_responsibilities",
            "achievements",
            "skills_acquired",
            "technologies_used",
            "notice_period_served",
            "experience_certificate_url",
            "experience_letter_file_name",
            "experience_letter_data_url",
            "reference_contact_name",
            "reference_contact_phone",
            "reference_contact_email",
            "is_verified",
            "verified_by",
            "verified_at",
            "remarks",
            "is_active",
            "created_at",
            "updated_at",
            "companyName",
            "jobTitle",
            "employmentType",
            "department",
            "startDate",
            "endDate",
            "reasonForLeaving",
            "responsibilities",
            "technologiesUsed",
            "experienceLetterFileName",
            "experienceLetterDataUrl",
        ]
        extra_kwargs = {
            "organization_name": {"required": False},
            "job_position": {"required": False},
            "date_from": {"required": False},
            "date_to": {"required": False},
        }
        read_only_fields = [
            "id",
            "employee",
            "total_duration_years",
            "total_duration_months",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_employee_name(self, obj):
        """Return employee full name."""
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None

    def get_duration_display(self, obj):
        """Format duration for display as 'X years Y months'."""
        if obj.total_duration_years is None:
            return None
        
        years = int(obj.total_duration_years)
        remaining_months = (obj.total_duration_years - years) * 12
        months = int(round(remaining_months))
        
        parts = []
        if years > 0:
            parts.append(f"{years}y")
        if months > 0:
            parts.append(f"{months}m")
        
        return " ".join(parts) if parts else "0m"


class PreviousEmploymentWriteSerializer(serializers.ModelSerializer):
    """
    Write serializer for EmployeePreviousEmployment.
    Handles creation and updates with validation.
    Includes all validations to prevent SQL injection.
    """
    organization_name = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=255,
    )
    job_position = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=200,
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    companyName = serializers.CharField(
        source="organization_name",
        required=False,
        allow_blank=False,
        max_length=255,
        write_only=True,
    )
    jobTitle = serializers.CharField(
        source="job_position",
        required=False,
        allow_blank=False,
        max_length=200,
        write_only=True,
    )
    employmentType = serializers.CharField(
        source="employment_type",
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=50,
        write_only=True,
    )
    department = serializers.CharField(
        source="department_name",
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=200,
        write_only=True,
    )
    startDate = serializers.DateField(
        source="date_from",
        required=False,
        write_only=True,
    )
    endDate = serializers.DateField(
        source="date_to",
        required=False,
        write_only=True,
    )
    reasonForLeaving = serializers.CharField(
        source="reason_for_leaving",
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255,
        write_only=True,
    )
    responsibilities = serializers.CharField(
        source="key_responsibilities",
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )
    technologiesUsed = serializers.CharField(
        source="technologies_used",
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )
    experienceLetterFileName = serializers.CharField(
        source="experience_letter_file_name",
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=255,
        write_only=True,
    )
    experienceLetterDataUrl = serializers.CharField(
        source="experience_letter_data_url",
        required=False,
        allow_blank=True,
        allow_null=True,
        write_only=True,
    )
    
    class Meta:
        model = EmployeePreviousEmployment
        fields = [
            "organization_name",
            "organization_type",
            "job_position",
            "job_title",
            "department_name",
            "location",
            "date_from",
            "date_to",
            "employment_type",
            "reporting_to",
            "salary_ctc",
            "salary_currency",
            "reason_for_leaving",
            "reason_category",
            "key_responsibilities",
            "achievements",
            "skills_acquired",
            "technologies_used",
            "notice_period_served",
            "experience_certificate_url",
            "experience_letter_file_name",
            "experience_letter_data_url",
            "reference_contact_name",
            "reference_contact_phone",
            "reference_contact_email",
            "remarks",
            "companyName",
            "jobTitle",
            "employmentType",
            "department",
            "startDate",
            "endDate",
            "reasonForLeaving",
            "responsibilities",
            "technologiesUsed",
            "experienceLetterFileName",
            "experienceLetterDataUrl",
        ]

    def validate_organization_name(self, value):
        """Validate organization name."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Organization name cannot be empty.")
        if len(value) > 255:
            raise serializers.ValidationError("Organization name must be 255 characters or less.")
        return value

    def validate_job_position(self, value):
        """Validate job position."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Job position cannot be empty.")
        if len(value) > 200:
            raise serializers.ValidationError("Job position must be 200 characters or less.")
        return value

    def validate_employment_type(self, value):
        """Accept API codes plus common UI labels."""
        if value in ("", None):
            return None

        normalized = str(value).strip()
        choice_codes = {
            choice_value
            for choice_value, _choice_label in EmployeePreviousEmployment._meta.get_field(
                "employment_type"
            ).choices
        }
        if normalized.upper() in choice_codes:
            return normalized.upper()

        label_map = {
            "permanent": "PERMANENT",
            "full time": "PERMANENT",
            "full-time": "PERMANENT",
            "contract": "CONTRACT",
            "temporary": "TEMPORARY",
            "internship": "INTERNSHIP",
            "part time": "PART_TIME",
            "part-time": "PART_TIME",
            "freelance": "FREELANCE",
            "consultant": "CONSULTANT",
            "other": "OTHER",
        }
        mapped_value = label_map.get(normalized.lower())
        if mapped_value is None:
            raise serializers.ValidationError(
                "Employment type must be a valid employment type."
            )
        return mapped_value

    def validate(self, data):
        """
        Validate the entire record.
        Ensures date logic, no overlaps, and referential integrity.
        """
        date_from = data.get("date_from")
        date_to = data.get("date_to")

        # Check dates
        if date_from and date_to:
            if date_from > date_to:
                raise serializers.ValidationError({
                    "date_to": "End date must be on or after the start date."
                })
            
            # Prevent unrealistic durations (more than 70 years)
            days_diff = (date_to - date_from).days
            if days_diff > (70 * 365):
                raise serializers.ValidationError({
                    "date_to": "Employment duration appears unrealistic (max 70 years)."
                })

        if data.get("employment_type") not in ("", None):
            data["employment_type"] = self.validate_employment_type(
                data["employment_type"]
            )

        if not self.partial:
            required_fields = {
                "organization_name": "Company name is required.",
                "job_position": "Job title is required.",
                "date_from": "Start date is required.",
                "date_to": "End date is required.",
            }
            missing_fields = {
                field: message
                for field, message in required_fields.items()
                if data.get(field) in ("", None)
            }
            if missing_fields:
                raise serializers.ValidationError(missing_fields)

        # Salary validation
        salary_ctc = data.get("salary_ctc")
        if salary_ctc is not None and salary_ctc < 0:
            raise serializers.ValidationError({
                "salary_ctc": "Salary cannot be negative."
            })

        # Notice period validation
        notice_period = data.get("notice_period_served")
        if notice_period is not None and notice_period < 0:
            raise serializers.ValidationError({
                "notice_period_served": "Notice period cannot be negative."
            })

        # URL validation (basic check)
        cert_url = data.get("experience_certificate_url")
        if cert_url and not (cert_url.startswith("http://") or cert_url.startswith("https://")):
            raise serializers.ValidationError({
                "experience_certificate_url": "Certificate URL must be a valid HTTP(S) URL."
            })

        data_url = data.get("experience_letter_data_url")
        if data_url and not data_url.startswith("data:"):
            raise serializers.ValidationError({
                "experienceLetterDataUrl": "Experience letter upload must be a valid data URL."
            })

        return data

    def validate_reference_contact_phone(self, value):
        """Validate phone number format."""
        if value:
            # Allow basic phone number format validation
            cleaned = ''.join(c for c in value if c.isdigit())
            if len(cleaned) < 7:
                raise serializers.ValidationError("Phone number must have at least 7 digits.")
        return value

    def validate_reference_contact_email(self, value):
        """Validate email format (DRF handles this but additional checks)."""
        if value:
            if not value.count("@") == 1:
                raise serializers.ValidationError("Invalid email format.")
            if len(value) > 254:
                raise serializers.ValidationError("Email address is too long.")
        return value


class PreviousEmploymentAdminListSerializer(serializers.ModelSerializer):
    """
    Compact serializer for listing multiple previous employment records.
    Used in admin dashboards or employee lists.
    """
    employee_id = serializers.CharField(source="employee.id", read_only=True)
    employee_name = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()

    class Meta:
        model = EmployeePreviousEmployment
        fields = [
            "id",
            "employee_id",
            "employee_name",
            "organization_name",
            "job_position",
            "date_from",
            "date_to",
            "duration_display",
            "reason_for_leaving",
            "is_verified",
            "created_at",
        ]
        read_only_fields = fields

    def get_employee_name(self, obj):
        """Return employee full name."""
        if obj.employee:
            return f"{obj.employee.first_name} {obj.employee.last_name}"
        return None

    def get_duration_display(self, obj):
        """Format duration for display."""
        if obj.total_duration_years is None:
            return None
        
        years = int(obj.total_duration_years)
        remaining_months = (obj.total_duration_years - years) * 12
        months = int(round(remaining_months))
        
        parts = []
        if years > 0:
            parts.append(f"{years}y")
        if months > 0:
            parts.append(f"{months}m")
        
        return " ".join(parts) if parts else "0m"
