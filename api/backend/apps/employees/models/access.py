"""
Employee access cards model.

Table: employee_access_cards

Physical RFID / smart card / QR access cards per employee.
Self-referential replaced_by_card_id for card replacement chain.
Post-audit additive: card_status field per ADMIN_SIDE.md.

PostgreSQL schema: employee
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionBaseModel


class EmployeeAccessCard(TransactionBaseModel):
    """
    Physical / RFID / smart card access record for an employee.

    card_number is unique across all active cards.
    replaced_by_card_id tracks the replacement chain for lost/expired cards.
    Post-audit additive: card_status field (ADMIN_SIDE.md: ADD status VARCHAR(20)).
    """

    class CardStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        LOST = "LOST", "Lost"
        REVOKED = "REVOKED", "Revoked"
        EXPIRED = "EXPIRED", "Expired"
        REPLACED = "REPLACED", "Replaced"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="access_cards",
    )

    # -------------------------------------------------------- card identity
    card_number = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)

    # -------------------------------------------------------- location
    office_location = models.ForeignKey(
        "employees.OfficeLocation",
        on_delete=models.PROTECT,
        db_column="office_location_id",
        related_name="emp_access_cards",
        null=True,
        blank=True,
    )
    floor = models.ForeignKey(
        "employees.Floor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="floor_id",
        related_name="emp_access_cards",
    )

    # -------------------------------------------------------- status
    card_status = models.CharField(
        max_length=20,
        choices=CardStatus.choices,
        default=CardStatus.ACTIVE,
    )

    # -------------------------------------------------------- dates
    issued_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True, help_text="NULL = no expiry")
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.CharField(max_length=200, blank=True, null=True)

    # -------------------------------------------------------- replacement chain
    replaced_by_card = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="replaced_by_card_id",
        related_name="replaces",
    )

    # -------------------------------------------------------- issued by
    issued_by = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="issued_by",
        related_name="issued_access_cards",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_access_cards"
        verbose_name = "Employee Access Card"
        verbose_name_plural = "Employee Access Cards"
        indexes = [
            models.Index(
                fields=["employee", "card_status"],
                name="idx_emp_acard_emp_status",
            ),
            models.Index(fields=["card_number"], name="idx_emp_acard_number"),
        ]
        constraints = [
            # Unique active card number — partial unique index
            models.UniqueConstraint(
                fields=["card_number"],
                condition=models.Q(card_status="ACTIVE"),
                name="uq_emp_access_card_active_number",
            ),
        ]

    def __str__(self) -> str:
        return f"Card {self.card_number} [{self.card_status}] — {self.employee_id}"
