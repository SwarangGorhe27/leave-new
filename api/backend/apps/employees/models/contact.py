"""
Employee contacts model.

Table: employee_contacts  (labelled employee_Contacts in README)

1-to-1 with employees. Contains official/personal email, phone numbers,
emergency contact info, and social profile links.

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionPIIBaseModel


class EmployeeContacts(TransactionPIIBaseModel):
    """
    Contact details for an employee.

    official_email is the primary login identifier — globally unique.
    mobile_no is validated as 7-20 chars of digits, +, or spaces.
    PII fields inherited from TransactionPIIBaseModel (email/phone are PII).
    is_active inherited from TransactionPIIBaseModel.
    """

    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="contacts",
    )

    # -------------------------------------------------------- email
    official_email = models.CharField(max_length=255, unique=True)
    personal_email = models.CharField(max_length=255, blank=True, null=True)

    # -------------------------------------------------------- phone
    mobile_no = models.CharField(max_length=20)
    alternate_mobile_no = models.CharField(max_length=20, blank=True, null=True)
    work_phone = models.CharField(max_length=20, blank=True, null=True)
    extension_number = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="Desk / PBX extension (profile section).",
    )

    # -------------------------------------------------------- emergency
    emergency_contact_name = models.CharField(max_length=150)
    emergency_contact_relation = models.ForeignKey(
        "employees.Relation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="emergency_contact_relation_id",
        related_name="emp_emergency_contacts",
    )
    emergency_contact_phone = models.CharField(max_length=20)
    emergency_contact_email = models.CharField(max_length=255, blank=True, null=True)

    # -------------------------------------------------------- social
    skype_id = models.CharField(max_length=100, blank=True, null=True)
    linkedin_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "employee_contacts"
        verbose_name = "Employee Contact"
        verbose_name_plural = "Employee Contacts"
        indexes = [
            models.Index(fields=["official_email"], name="idx_emp_contacts_ofemail"),
            models.Index(fields=["employee"], name="idx_emp_contacts_employee"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee"],
                name="uq_emp_contacts_employee",
            ),
            models.UniqueConstraint(
                fields=["official_email"],
                name="uq_emp_contacts_ofemail",
            ),
        ]

    def __str__(self) -> str:
        return f"Contact — {self.official_email}"
