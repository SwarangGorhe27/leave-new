"""
Employee address model.

Table: employee_addresses

Multiple addresses per employee (CURRENT / PERMANENT / CORRESPONDENCE / TEMPORARY).
Soft-deletable, HR-verifiable.

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionPIIBaseModel


class EmployeeAddress(TransactionPIIBaseModel):
    """
    Postal address record for an employee.

    address_type categorises the address.
    is_same_as_permanent enables UI copy-paste of permanent address.
    is_verified / verified_by / verified_at track HR address verification.
    PII fields inherited from TransactionPIIBaseModel (addresses are PII).
    """

    class AddressType(models.TextChoices):
        CURRENT = "CURRENT", "Current"
        PERMANENT = "PERMANENT", "Permanent"
        CORRESPONDENCE = "CORRESPONDENCE", "Correspondence"
        TEMPORARY = "TEMPORARY", "Temporary"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="addresses",
    )

    # -------------------------------------------------------- type
    address_type = models.CharField(max_length=20, choices=AddressType.choices)

    # -------------------------------------------------------- address lines
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=150, blank=True, null=True)

    # -------------------------------------------------------- location FK
    city = models.ForeignKey(
        "employees.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="city_id",
        related_name="emp_addresses",
    )
    state = models.ForeignKey(
        "employees.State",
        on_delete=models.PROTECT,
        db_column="state_id",
        related_name="emp_addresses",
    )
    country = models.ForeignKey(
        "employees.Country",
        on_delete=models.PROTECT,
        db_column="country_id",
        related_name="emp_addresses",
    )
    pincode = models.CharField(max_length=10, blank=True, null=True)

    # -------------------------------------------------------- effective period
    start_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)

    # -------------------------------------------------------- flags
    is_same_as_permanent = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="verified_by",
        related_name="verified_emp_addresses",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_addresses"
        verbose_name = "Employee Address"
        verbose_name_plural = "Employee Addresses"
        indexes = [
            models.Index(
                fields=["employee", "address_type"],
                name="idx_emp_addr_emp_type",
            ),
            models.Index(fields=["employee"], name="idx_emp_addresses_employee"),
        ]

    def __str__(self) -> str:
        return f"{self.address_type} — {self.employee_id}"
