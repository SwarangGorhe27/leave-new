import uuid

from django.conf import settings
from django.db import models

from apps.employees.constants import ChangeRequestAction, ChangeRequestStatus, ESSModule
from apps.employees.models.base import TransactionBaseModel, TransactionPIIBaseModel


class EmployeePassportVisa(TransactionPIIBaseModel):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="passport_visa_records",
    )
    # -------------------------------------------------------- passport details
    passport_number = models.CharField(max_length=30, blank=True, null=True)
    passport_holder_name = models.CharField(max_length=255, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    issue_place = models.CharField(max_length=100, blank=True, null=True)
    issue_country = models.ForeignKey(
        "employees.Country",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="passport_issue_records",
    )
    passport_category = models.ForeignKey(
        "employees.PassportCategory",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="passport_records",
    )
    passport_status = models.ForeignKey(
        "employees.PassportStatus",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="passport_records",
    )
    nationality = models.ForeignKey(
        "employees.Nationality",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="passport_visa_records",
    )
    is_current = models.BooleanField(default=True)
    
    # -------------------------------------------------------- passport documents
    passport_front_url = models.TextField(blank=True, null=True)
    passport_back_url = models.TextField(blank=True, null=True)
    document_url = models.TextField(blank=True, null=True)
    
    # -------------------------------------------------------- visa details
    has_visa = models.BooleanField(default=False)
    visa_type = models.ForeignKey(
        "employees.VisaType",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="visa_records",
    )
    visa_number = models.CharField(max_length=50, blank=True, null=True)
    visa_expiry_date = models.DateField(blank=True, null=True)
    visa_issue_date = models.DateField(blank=True, null=True)
    visa_issue_country = models.ForeignKey(
        "employees.Country",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="visa_issue_records",
    )
    visa_country = models.ForeignKey(
        "employees.Country",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column="visa_country_id",
        related_name="visa_country_records",
    )
    visa_sponsor = models.CharField(max_length=255, blank=True, null=True)
    visa_status = models.ForeignKey(
        "employees.VisaStatus",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="visa_records",
    )
    
    # -------------------------------------------------------- visa documents
    visa_document_url = models.TextField(blank=True, null=True)
    visa_copy_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "employee_passport_visa"


class EmployeeWorkExperience(TransactionBaseModel):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="work_experience_records",
    )
    company_name = models.CharField(max_length=200)
    designation = models.CharField(max_length=150, blank=True, null=True)
    department = models.CharField(max_length=150, blank=True, null=True)
    location = models.CharField(max_length=150, blank=True, null=True)
    employment_type = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    responsibilities = models.TextField(blank=True, null=True)
    reason_for_leaving = models.TextField(blank=True, null=True)
    last_ctc = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(blank=True, null=True)
    offer_letter_url = models.TextField(blank=True, null=True)
    experience_letter_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "employee_work_experience"


class EmployeeSkillCertification(TransactionBaseModel):
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="skill_certifications",
    )
    skill_name = models.CharField(max_length=150)
    skill_type = models.CharField(max_length=80, blank=True, null=True)
    proficiency_level = models.CharField(max_length=50, blank=True, null=True)
    years_of_experience = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    last_used_year = models.PositiveSmallIntegerField(blank=True, null=True)
    is_certified = models.BooleanField(default=False)
    certification_name = models.CharField(max_length=200, blank=True, null=True)
    certification_body = models.CharField(max_length=200, blank=True, null=True)
    certification_date = models.DateField(blank=True, null=True)
    certification_expiry = models.DateField(blank=True, null=True)
    credential_id = models.CharField(max_length=120, blank=True, null=True)
    credential_url = models.TextField(blank=True, null=True)
    certificate_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "employee_skill_certifications"


class EmployeeMedicalEmergency(TransactionPIIBaseModel):
    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="medical_emergency",
    )
    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=80, blank=True, null=True)
    emergency_contact_alt_number = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_email = models.EmailField(blank=True, null=True)
    emergency_contact_address = models.TextField(blank=True, null=True)
    blood_group = models.ForeignKey(
        "employees.BloodGroup",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medical_emergency_records",
    )
    pre_existing_diseases = models.TextField(blank=True, null=True)
    ongoing_medications = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    undergone_major_surgery = models.BooleanField(default=False)
    surgery_details = models.TextField(blank=True, null=True)
    is_physically_challenged = models.BooleanField(default=False)
    disability_details = models.TextField(blank=True, null=True)
    disability_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    doctor_name = models.CharField(max_length=150, blank=True, null=True)
    doctor_contact = models.CharField(max_length=20, blank=True, null=True)
    medical_document_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "employee_medical_emergency"


class EmployeeSocialProfile(TransactionBaseModel):
    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="social_profile",
    )
    linkedin_url = models.TextField(blank=True, null=True)
    github_url = models.TextField(blank=True, null=True)
    stackoverflow_url = models.TextField(blank=True, null=True)
    portfolio_url = models.TextField(blank=True, null=True)
    personal_website = models.TextField(blank=True, null=True)
    twitter_url = models.TextField(blank=True, null=True)
    facebook_url = models.TextField(blank=True, null=True)
    instagram_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "employee_social_profiles"


class EmployeeChangeRequest(TransactionBaseModel):
    class Module(models.TextChoices):
        PROFILE = ESSModule.PROFILE, "Profile"
        EMPLOYMENT = ESSModule.EMPLOYMENT, "Employment"
        PERSONAL = ESSModule.PERSONAL, "Personal"
        ADDRESS = ESSModule.ADDRESS, "Address"
        FAMILY = ESSModule.FAMILY, "Family"
        EDUCATION = ESSModule.EDUCATION, "Education"
        BANK = ESSModule.BANK, "Bank"
        NOMINEE = ESSModule.NOMINEE, "Nominee"
        INSURANCE = ESSModule.INSURANCE, "Insurance"
        LANGUAGE = ESSModule.LANGUAGE, "Language"
        PASSPORT = ESSModule.PASSPORT, "Passport"
        EXPERIENCE = ESSModule.EXPERIENCE, "Experience"
        SKILL = ESSModule.SKILL, "Skill"
        DOCUMENT = ESSModule.DOCUMENT, "Document"
        MEDICAL = ESSModule.MEDICAL, "Medical"
        SOCIAL = ESSModule.SOCIAL, "Social"
        ASSET = ESSModule.ASSET, "Asset"

    class Action(models.TextChoices):
        CREATE = ChangeRequestAction.CREATE, "Create"
        UPDATE = ChangeRequestAction.UPDATE, "Update"
        DELETE = ChangeRequestAction.DELETE, "Delete"

    class Status(models.TextChoices):
        PENDING = ChangeRequestStatus.PENDING, "Pending"
        APPROVED = ChangeRequestStatus.APPROVED, "Approved"
        REJECTED = ChangeRequestStatus.REJECTED, "Rejected"
        CANCELLED = ChangeRequestStatus.CANCELLED, "Cancelled"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        related_name="change_requests",
    )
    module = models.CharField(max_length=30, choices=Module.choices)
    action = models.CharField(max_length=20, choices=Action.choices, default=Action.UPDATE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    request_data = models.JSONField(default=dict)
    old_data = models.JSONField(default=dict, blank=True)
    record_id = models.UUIDField(default=uuid.uuid4, blank=True, null=True)
    employee_remarks = models.TextField(blank=True, null=True)
    admin_remarks = models.TextField(blank=True, null=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="employee_change_requests",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reviewed_employee_change_requests",
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "employee_change_requests"
        indexes = [
            models.Index(fields=["employee", "status"], name="idx_emp_cr_emp_status"),
            models.Index(fields=["status", "created_at"], name="idx_emp_cr_status_created"),
        ]
