"""
Employee asset assignment model.

Table: employee_assets

Tracks the company assets assigned to an employee.
All endpoints include proper error handling and SQL injection protection.

PostgreSQL schema: employee
"""


import uuid
from django.db import models
from apps.employees.models.base import TransactionBaseModel


class EmployeeAsset(TransactionBaseModel):
    """
    Asset assignment record for an employee.
    """
    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="asset_assignments",
    )
    
    asset_name = models.CharField(max_length=150, help_text="Asset Name / Type")
    asset_code = models.CharField(max_length=50, blank=True, null=True, help_text="Asset ID / Code")
    
    asset_category = models.ForeignKey(
        "employees.AssetCategory",
        on_delete=models.PROTECT,
        db_column="asset_category_id",
        related_name="assigned_assets",  
        
    )
    
    serial_no = models.CharField(max_length=100, blank=True, null=True, help_text="Serial Number")
    
    assign_date = models.DateField(help_text="Assign Date")
    return_date = models.DateField(blank=True, null=True, help_text="Return Date")
    
    asset_condition = models.ForeignKey(
        "employees.AssetCondition",
        on_delete=models.PROTECT,
        db_column="asset_condition_id",
        related_name="assigned_assets",
        null=True,
        blank=True,
    )
    
    class StatusChoices(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Assigned"
        RETURNED = "RETURNED", "Returned"
        LOST = "LOST", "Lost"
        DAMAGED = "DAMAGED", "Damaged"
        
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ASSIGNED,
    )
    
    remarks = models.TextField(blank=True, null=True, help_text="Remarks")

    class Meta:
        db_table = "employee_assets"
        verbose_name = "Employee Asset"
        verbose_name_plural = "Employee Assets"
        indexes = [
            models.Index(fields=["employee"], name="idx_emp_asset_employee"),
            models.Index(fields=["asset_category"], name="idx_emp_asset_category"),
        ]

    def __str__(self) -> str:
        return f"{self.asset_name} ({self.asset_code}) — {self.employee_id}"
