
from django.db import models

from apps.employees.models.base import MasterBaseModel


# ---------------------------------------------------------------------------
# mst_employee_type
# ---------------------------------------------------------------------------


class EmployeeType(MasterBaseModel):
    

    class Meta:
        db_table = "mst_employee_type"
        verbose_name = "Employee Type"
        verbose_name_plural = "Employee Types"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_employee_type_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_employee_type_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_employee_category
# ---------------------------------------------------------------------------


class EmployeeCategory(MasterBaseModel):
   

    class Meta:
        db_table = "mst_employee_category"
        verbose_name = "Employee Category"
        verbose_name_plural = "Employee Categories"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_employee_category_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_employee_category_code"
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_source_of_hire
# ---------------------------------------------------------------------------


class SourceOfHire(MasterBaseModel):
    

    class Meta:
        db_table = "mst_source_of_hire"
        verbose_name = "Source of Hire"
        verbose_name_plural = "Sources of Hire"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_source_of_hire_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_source_of_hire_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_source_of_hire_type
# ---------------------------------------------------------------------------


class SourceOfHireType(MasterBaseModel):
   

    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=150)
    is_internal = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_source_of_hire_type"
        verbose_name = "Source of Hire Type"
        verbose_name_plural = "Sources of Hire Types"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_soh_type_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_soh_type_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_payroll_status
# ---------------------------------------------------------------------------


class PayrollStatus(MasterBaseModel):

    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "mst_payroll_status"
        verbose_name = "Payroll Status"
        verbose_name_plural = "Payroll Statuses"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_payroll_status_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_payroll_status_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_payroll_mode
# ---------------------------------------------------------------------------


class PayrollMode(MasterBaseModel):
    

    class Meta:
        db_table = "mst_payroll_mode"
        verbose_name = "Payroll Mode"
        verbose_name_plural = "Payroll Modes"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_payroll_mode_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_payroll_mode_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_payroll_group
# ---------------------------------------------------------------------------


class PayrollGroup(MasterBaseModel):
   

    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=150)

    class Meta:
        db_table = "mst_payroll_group"
        verbose_name = "Payroll Group"
        verbose_name_plural = "Payroll Groups"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_payroll_group_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_payroll_group_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_transport_type
# ---------------------------------------------------------------------------


class TransportType(MasterBaseModel):
  

    class Meta:
        db_table = "mst_transport_type"
        verbose_name = "Transport Type"
        verbose_name_plural = "Transport Types"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_transport_type_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_mst_transport_type_code"),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_employee_status
# ---------------------------------------------------------------------------


class EmployeeStatus(MasterBaseModel):
  

    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=150)
    is_terminal = models.BooleanField(default=False)

    class Meta:
        db_table = "mst_employee_status"
        verbose_name = "Employee Status"
        verbose_name_plural = "Employee Statuses"
        indexes = [
            models.Index(fields=["code"], name="idx_mst_employee_status_code"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"], name="uq_mst_employee_status_code"
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_work_experience_range
# ---------------------------------------------------------------------------


class WorkExperienceRange(MasterBaseModel):
   

    id = models.SmallAutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    label = models.CharField(max_length=50)
    min_months = models.SmallIntegerField()
    max_months = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "mst_work_experience_range"
        verbose_name = "Work Experience Range"
        verbose_name_plural = "Work Experience Ranges"
        constraints = [
            models.CheckConstraint(
                check=models.Q(min_months__gte=0),
                name="chk_work_exp_range_min_months_positive",
            ),
            models.CheckConstraint(
                check=models.Q(max_months__isnull=True)
                | models.Q(max_months__gt=models.F("min_months")),
                name="chk_work_exp_range_max_gt_min",
            ),
        ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# mst_relevant_experience_range
# ---------------------------------------------------------------------------


class RelevantExperienceRange(MasterBaseModel):
   

    id = models.SmallAutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    label = models.CharField(max_length=50)
    min_months = models.SmallIntegerField()
    max_months = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "mst_relevant_experience_range"
        verbose_name = "Relevant Experience Range"
        verbose_name_plural = "Relevant Experience Ranges"
        constraints = [
            models.CheckConstraint(
                check=models.Q(min_months__gte=0),
                name="chk_rel_exp_range_min_months_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.label
