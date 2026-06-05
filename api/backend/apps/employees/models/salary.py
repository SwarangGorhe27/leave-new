"""Employee salary assignment and component values."""

from django.db import models

from apps.employees.models.base import TransactionBaseModel


class EmployeeSalaryAssignment(TransactionBaseModel):
    """Current or historical salary structure assigned to an employee."""

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="salary_assignments",
    )
    salary_structure = models.ForeignKey(
        "employees.SalaryStructure",
        on_delete=models.PROTECT,
        db_column="salary_structure_id",
        related_name="employee_assignments",
    )
    ctc_annual = models.DecimalField(max_digits=14, decimal_places=2)
    currency_code = models.CharField(max_length=3, default="INR")
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "emp_salary_assignment"
        verbose_name = "Employee Salary Assignment"
        verbose_name_plural = "Employee Salary Assignments"
        indexes = [
            models.Index(fields=["employee"], name="idx_emp_sal_assign_emp"),
            models.Index(fields=["salary_structure"], name="idx_emp_sal_assign_struct"),
            models.Index(fields=["employee", "is_current"], name="idx_emp_sal_assign_current"),
            models.Index(fields=["effective_from", "effective_to"], name="idx_emp_sal_assign_dates"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(ctc_annual__gt=0),
                name="chk_emp_sal_assign_ctc_gt0",
            ),
            models.CheckConstraint(
                check=(
                    models.Q(effective_to__isnull=True)
                    | models.Q(effective_to__gte=models.F("effective_from"))
                ),
                name="chk_emp_sal_assign_to_gte_from",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.employee_id} - {self.currency_code} {self.ctc_annual}"


class EmployeeSalaryComponentValue(TransactionBaseModel):
    """Monthly and annual value for one component in an employee salary assignment."""

    salary_assignment = models.ForeignKey(
        "employees.EmployeeSalaryAssignment",
        on_delete=models.CASCADE,
        db_column="salary_assignment_id",
        related_name="component_values",
    )
    pay_component = models.ForeignKey(
        "employees.PayComponent",
        on_delete=models.PROTECT,
        db_column="pay_component_id",
        related_name="employee_salary_values",
    )
    amount_monthly = models.DecimalField(max_digits=14, decimal_places=2)
    amount_annual = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    calculation_order = models.SmallIntegerField(default=0)

    class Meta:
        db_table = "emp_salary_component_value"
        verbose_name = "Employee Salary Component Value"
        verbose_name_plural = "Employee Salary Component Values"
        ordering = ["calculation_order", "pay_component__sort_order", "pay_component__name"]
        indexes = [
            models.Index(fields=["salary_assignment"], name="idx_emp_sal_comp_assign"),
            models.Index(fields=["pay_component"], name="idx_emp_sal_comp_component"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["salary_assignment", "pay_component"],
                name="uq_emp_sal_comp_assign_component",
            ),
            models.CheckConstraint(
                check=models.Q(amount_monthly__gte=0),
                name="chk_emp_sal_comp_monthly_gte0",
            ),
            models.CheckConstraint(
                check=models.Q(amount_annual__gte=0) | models.Q(amount_annual__isnull=True),
                name="chk_emp_sal_comp_annual_gte0",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.salary_assignment_id} - {self.pay_component_id}: {self.amount_monthly}"
"""
Employee salary summary model.

Stores the admin-managed compensation card values for an employee.
Net salary is calculated by the API from gross salary minus deductions.
"""

import uuid

from django.db import models

from apps.employees.models.base import TransactionBaseModel


class EmployeeSalary(TransactionBaseModel):
    class PayFrequency(models.TextChoices):
        MONTHLY = "MONTHLY", "Monthly"
        YEARLY = "YEARLY", "Yearly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.OneToOneField(
        "employees.Employee",
        on_delete=models.CASCADE,
        db_column="employee_id",
        related_name="salary_summary",
    )
    currency = models.CharField(max_length=3, default="INR")
    pay_frequency = models.CharField(
        max_length=20,
        choices=PayFrequency.choices,
        default=PayFrequency.MONTHLY,
    )
    basic_salary = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    house_rent_allowance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    conveyance_allowance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    provident_fund = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_deducted_at_source = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    annual_ctc = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    deduction_label = models.CharField(max_length=100, default="PF + TDS", blank=True)
    net_salary_label = models.CharField(max_length=100, default="Take Home", blank=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "employee_salary"
        verbose_name = "Employee Salary"
        verbose_name_plural = "Employee Salaries"
        indexes = [
            models.Index(fields=["employee"], name="idx_emp_salary_employee"),
            models.Index(fields=["currency"], name="idx_emp_salary_currency"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["employee"], name="uq_emp_salary_employee"),
            models.CheckConstraint(
                check=models.Q(gross_salary__gte=0),
                name="chk_emp_salary_gross_gte0",
            ),
            models.CheckConstraint(
                check=models.Q(annual_ctc__gte=0),
                name="chk_emp_salary_ctc_gte0",
            ),
            models.CheckConstraint(
                check=models.Q(total_deductions__gte=0),
                name="chk_emp_salary_deductions_gte0",
            ),
            models.CheckConstraint(
                check=models.Q(net_salary__gte=0),
                name="chk_emp_salary_net_gte0",
            ),
        ]

    def __str__(self) -> str:
        return f"Salary - {self.employee_id}"
