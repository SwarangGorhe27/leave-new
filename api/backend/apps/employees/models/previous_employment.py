"""
Previous Employment History model — tracks employee work history before joining.

Table: emp_previous_employment

This tracks the employee's work experience in organizations prior to joining
this company. Used for employee profile, recruitment verification, and
administrative purposes.

PostgreSQL schema: employee
"""

import uuid

from django.db import models
from django.core.exceptions import ValidationError

from apps.employees.models.base import TransactionBaseModel


class EmployeePreviousEmployment(TransactionBaseModel):
    """
    Previous Employment History for an employee.

    Stores work experience before joining current company.
    Multiple records per employee (1-to-many relationship).
    
    SQL Injection Prevention:
    - All user inputs are parameterized via Django ORM
    - No raw SQL queries used
    - Field validations ensure data integrity
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="previous_employments",
    )

    # ----------------------------------------------------------- organization details
    organization_name = models.CharField(
        max_length=255,
        help_text="Name of the previous employer organization"
    )
    organization_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Type of organization (e.g., IT, Manufacturing, Services)"
    )

    # ----------------------------------------------------------- job details
    job_position = models.CharField(
        max_length=200,
        help_text="Position/Designation held in previous organization"
    )
    job_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Alternative job title"
    )
    department_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Department name in previous organization"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Work location in previous organization"
    )

    # ----------------------------------------------------------- employment duration
    date_from = models.DateField(
        help_text="Start date of employment in previous organization"
    )
    date_to = models.DateField(
        help_text="End date of employment in previous organization"
    )
    total_duration_years = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Computed duration in years (auto-calculated)"
    )
    total_duration_months = models.SmallIntegerField(
        blank=True,
        null=True,
        help_text="Computed duration in months (auto-calculated)"
    )

    # ----------------------------------------------------------- employment terms
    employment_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ("PERMANENT", "Permanent"),
            ("CONTRACT", "Contract"),
            ("TEMPORARY", "Temporary"),
            ("INTERNSHIP", "Internship"),
            ("PART_TIME", "Part Time"),
            ("FREELANCE", "Freelance"),
            ("CONSULTANT", "Consultant"),
            ("OTHER", "Other"),
        ],
        help_text="Type of employment"
    )
    reporting_to = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Name of direct supervisor/reporting manager"
    )

    # ----------------------------------------------------------- compensation
    salary_ctc = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Annual CTC/Salary (if applicable)"
    )
    salary_currency = models.CharField(
        max_length=3,
        default="INR",
        help_text="Currency code (ISO 4217)"
    )

    # ----------------------------------------------------------- reason for leaving
    reason_for_leaving = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Reason for leaving the organization"
    )
    reason_category = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ("CAREER_GROWTH", "Career Growth"),
            ("BETTER_OPPORTUNITY", "Better Opportunity"),
            ("SALARY", "Salary/Compensation"),
            ("RELOCATION", "Relocation"),
            ("HIGHER_STUDIES", "Higher Studies"),
            ("PERSONAL_REASONS", "Personal Reasons"),
            ("FAMILY_REASONS", "Family Reasons"),
            ("HEALTH_REASONS", "Health Reasons"),
            ("COMPANY_CLOSURE", "Company Closure"),
            ("RETRENCHMENT", "Retrenchment"),
            ("LAYOFF", "Layoff"),
            ("CONTRACT_END", "Contract End"),
            ("SABBATICAL", "Sabbatical"),
            ("OTHER", "Other"),
        ],
        help_text="Category of reason for leaving"
    )

    # ----------------------------------------------------------- achievements & skills
    key_responsibilities = models.TextField(
        blank=True,
        null=True,
        help_text="Key responsibilities in the previous role"
    )
    achievements = models.TextField(
        blank=True,
        null=True,
        help_text="Notable achievements or projects"
    )
    skills_acquired = models.TextField(
        blank=True,
        null=True,
        help_text="Skills acquired/developed (comma-separated or JSON)"
    )
    technologies_used = models.TextField(
        blank=True,
        null=True,
        help_text="Technologies or tools used in the previous role"
    )

    # ----------------------------------------------------------- verification & documents
    notice_period_served = models.SmallIntegerField(
        blank=True,
        null=True,
        help_text="Notice period served in days"
    )
    experience_certificate_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to experience certificate if available"
    )
    experience_letter_file_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Uploaded experience letter file name"
    )
    experience_letter_data_url = models.TextField(
        blank=True,
        null=True,
        help_text="Uploaded experience letter data URL"
    )
    reference_contact_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Contact person for reference verification"
    )
    reference_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Reference contact phone number"
    )
    reference_contact_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Reference contact email address"
    )

    # ----------------------------------------------------------- internal tracking
    is_verified = models.BooleanField(
        default=False,
        help_text="Has this work history been verified?"
    )
    verified_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_previous_employments",
        db_column="verified_by_id",
        help_text="Employee who verified this record"
    )
    verified_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp of verification"
    )

    remarks = models.TextField(
        blank=True,
        null=True,
        help_text="Additional remarks or notes"
    )

    class Meta:
        db_table = "emp_previous_employment"
        verbose_name = "Previous Employment"
        verbose_name_plural = "Previous Employments"
        ordering = ["-date_to", "-date_from"]
        unique_together = [
            ("employee", "organization_name", "date_from", "date_to"),
        ]
        indexes = [
            models.Index(fields=["employee", "date_to"]),
            models.Index(fields=["employee", "-date_from"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_verified"]),
        ]

    def clean(self):
        """Validate dates and other constraints."""
        if self.date_to and self.date_from:
            if self.date_from > self.date_to:
                raise ValidationError({
                    "date_to": "End date must be after start date."
                })
        
        if self.salary_ctc and self.salary_ctc < 0:
            raise ValidationError({
                "salary_ctc": "Salary cannot be negative."
            })
        
        if self.notice_period_served and self.notice_period_served < 0:
            raise ValidationError({
                "notice_period_served": "Notice period cannot be negative."
            })

    def save(self, *args, **kwargs):
        """Auto-compute duration fields before saving."""
        self.clean()
        
        # Auto-compute duration if both dates are present
        if self.date_to and self.date_from:
            from dateutil.relativedelta import relativedelta
            
            delta = relativedelta(self.date_to, self.date_from)
            total_months = delta.years * 12 + delta.months
            
            self.total_duration_months = total_months
            self.total_duration_years = round(total_months / 12, 2)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.first_name} - {self.organization_name} ({self.date_from} to {self.date_to})"
