"""
Employee module — master table models.

All master tables (mst_*) are defined in sub-modules and re-exported here
to support Django's auto-discovery and clean import paths.

Original masters (62 tables):
  personal, education, employment, location, organization, insurance, misc

New masters added (62 tables across 6 new files):
  hr_setup, audit_additions, attendance_leave, payroll, recruitment,
  performance_training, workflow_security
"""

# ── Original masters ──────────────────────────────────────────────────────

from apps.employees.models.masters.personal import (
    BloodGroup,
    Caste,
    CasteCategory,
    Gender,
    MaritalStatus,
    MotherTongue,
    Nationality,
    Religion,
    Salutation,
)

from apps.employees.models.masters.education import (
    Board,
    EducationLevel,
    EducationSpecialization,
    EducationStatus,
    Institution,
    PassingYear,
    Qualification,
    Specialization,
    StudyMode,
    University,
)

from apps.employees.models.masters.employment import (
    EmployeeCategory,
    EmployeeStatus,
    EmployeeType,
    PayrollGroup,
    PayrollMode,
    PayrollStatus,
    RelevantExperienceRange,
    SourceOfHire,
    SourceOfHireType,
    TransportType,
    WorkExperienceRange,
)

from apps.employees.models.masters.location import (
    City,
    Country,
    Floor,
    HeadquarterLocation,
    LocationType,
    OfficeLocation,
    ProductionCell,
    State,
)

from apps.employees.models.masters.organization import (
    AccountType,
    Bank,
    BankStatus,
    Batch,
    Cab,
    Company,
    Department,
    DepartmentDivision,
    Designation,
    Extension,
    Grade,
    Team,
)

from apps.employees.models.masters.insurance import (
    CoverType,
    InsuranceCompany,
    InsuranceType,
    PolicyType,
    PremiumFrequency,
)

from apps.employees.models.masters.misc import (
    CommunicationChannel,
    CommunicationTask,
    # DefaultRole,
    DocumentSide,
    DocumentType,
    Language,
    LanguageProficiency,
    NomineePurpose,
    Occupation,
    Profession,
    ProficiencyLevel,
    Relation,
    # SystemRole,
)
from apps.employees.models.masters.weekly_off_days import WeeklyOffDays
from apps.security.models.role import Role, EmployeeRoleAssignment
from apps.employees.models.masters.passport_visa import (
    PassportCategory,
    PassportStatus,
    VisaStatus,
    VisaType,
)

# ── C.1 Core HR Setup Masters ─────────────────────────────────────────────

from apps.employees.models.masters.hr_setup import (
    Band,
    Branch,
    BusinessUnit,
    CostCenter,
    Holiday,
    HolidayCalendar,
    HolidayGroup,
    ProfitCenter,
    Shift,
    ShiftType,
    WorkWeekPolicy,
)

# ── C.2 New Masters from Audit Findings ───────────────────────────────────

from apps.employees.models.masters.audit_additions import (
    AuthorizedSignatory,
    BulletinCategory,
    ClearanceItemType,
    ContractStatus,
    CounterParty,
    EmployeeFilter,
    FormCategory,
    ImportType,
    LetterApprovalType,
    PaymentType,
    PolicyCategory,
    PositionChangeReason,
    ResidentialStatus,
    SeparationMode,
    VerificationStatus,
    ReportingManager,
)

# ── C.3 Attendance & Leave Masters ────────────────────────────────────────

from apps.attendance.models.masters.policy_masters import (
    AttendancePolicy,
    RegularizationReason,
)
from apps.attendance.models.masters.scheme_status import (
    AttendanceScheme,
    AttendanceStatus,
)

# from apps.employees.models.masters.attendance_leave import (
#     CompOffPolicy,
#     # LeaveApprovalMatrix,
#     # LeavePolicy,
#     # LeaveType,
#     OvertimePolicy,
# )

# ── C.4 Payroll & Compliance Masters ─────────────────────────────────────

from apps.employees.models.masters.payroll import (
    ArrearType,
    EsiScheme,
    LabourRegisterType,
    LoanType,
    LwfSlab,
    PayComponentGroup,
    PayComponent,
    PayrollCycle,
    PfScheme,
    PtStateSlab,
    ReimbursementType,
    SalaryStructure,
    SalaryStructureComponent,
    StatutoryComponent,
    TaxRegime,
    TdsSection,
)

# ── C.5 Recruitment Masters ───────────────────────────────────────────────

from apps.employees.models.masters.recruitment import (
    CandidateSource,
    InterviewRound,
    JobFunction,
    JobLevel,
    OfferStatus,
    PipelineStage,
    RejectionReason,
)

# ── C.6 Performance, Training & Asset Masters ─────────────────────────────

from apps.employees.models.masters.performance_training import (
    AppraisalCycle,
    AssetCategory,
    AssetCondition,
    AssetType,
    CertificationBody,
    Competency,
    CompetencyGroup,
    Course,
    GoalCategory,
    KpiLibrary,
    KraLibrary,
    RatingScale,
    TrainingCategory,
    TrainingMode,
    Vendor,
)

# ── C.7 Workflow, Security & Notification Masters ─────────────────────────

from apps.employees.models.masters.workflow_security import (
    ApprovalAction,
    AuditEventType,
    # DataScopeType,
    EscalationType,
    # MenuItem,
    NotificationChannel,
    NotificationTemplate,
    NotificationTrigger,
    PasswordPolicy,
    # Permission,
    SessionPolicy,
    WorkflowType,
)
from apps.security.models import Permission, MenuItem, DataScopeRule
__all__ = [
    # ── Personal ────────────────────────────────────────────────────────
    "Gender",
    "Salutation",
    "MaritalStatus",
    "Religion",
    "Caste",
    "CasteCategory",
    "MotherTongue",
    "Nationality",
    "BloodGroup",
    # ── Education ───────────────────────────────────────────────────────
    "EducationLevel",
    "EducationSpecialization",
    "EducationStatus",
    "Specialization",
    "Board",
    "Qualification",
    "StudyMode",
    "Institution",
    "PassingYear",
    "University",
    # ── Employment ──────────────────────────────────────────────────────
    "EmployeeType",
    "EmployeeCategory",
    "SourceOfHire",
    "SourceOfHireType",
    "PayrollStatus",
    "PayrollMode",
    "PayrollGroup",
    "TransportType",
    "EmployeeStatus",
    "WorkExperienceRange",
    "RelevantExperienceRange",
    # ── Location ────────────────────────────────────────────────────────
    "Country",
    "State",
    "City",
    "HeadquarterLocation",
    "OfficeLocation",
    "ProductionCell",
    "Floor",
    "LocationType",
    # ── Organization ────────────────────────────────────────────────────
    "Company",
    "Department",
    "Designation",
    "Grade",
    "Bank",
    "BankStatus",
    "AccountType",
    "DepartmentDivision",
    "Extension",
    "Batch",
    "Cab",
    "Team",
    # ── Insurance ───────────────────────────────────────────────────────
    "PolicyType",
    "InsuranceType",
    "CoverType",
    "PremiumFrequency",
    "InsuranceCompany",
    # ── Misc ────────────────────────────────────────────────────────────
    "Language",
    "LanguageProficiency",
    "ProficiencyLevel",
    "NomineePurpose",
    "Relation",
    "Occupation",
    "Profession",
    "CommunicationChannel",
    "CommunicationTask",
    "DocumentType",
    "DocumentSide",
    "SystemRole",
    "DefaultRole",
    "WeeklyOffDays",
    # ── Passport & Visa ─────────────────────────────────────────────────
    "PassportCategory",
    "PassportStatus",
    "VisaType",
    "VisaStatus",
    # ── C.1 Core HR Setup ────────────────────────────────────────────────
    "Branch",
    "BusinessUnit",
    "CostCenter",
    "ProfitCenter",
    "Band",
    "ShiftType",
    "Shift",
    "WorkWeekPolicy",
    "HolidayCalendar",
    "Holiday",
    "HolidayGroup",
    # ── C.2 Audit Additions ──────────────────────────────────────────────
    "SeparationMode",
    "ContractStatus",
    "VerificationStatus",
    "ResidentialStatus",
    "PaymentType",
    "AttendanceScheme",
    "AttendanceStatus",
    "EmployeeFilter",
    "BulletinCategory",
    "PolicyCategory",
    "FormCategory",
    "ImportType",
    "LetterApprovalType",
    "ClearanceItemType",
    "PositionChangeReason",
    "CounterParty",
    "AuthorizedSignatory",
    # ── C.3 Attendance & Leave ───────────────────────────────────────────
    "AttendancePolicy",
    "RegularizationReason",
    # ── C.4 Payroll ──────────────────────────────────────────────────────
    "PayComponentGroup",
    "PayComponent",
    "SalaryStructure",
    "SalaryStructureComponent",
    "ReimbursementType",
    "LoanType",
    "PayrollCycle",
    "TaxRegime",
    "TdsSection",
    "ArrearType",
    "StatutoryComponent",
    "PfScheme",
    "EsiScheme",
    "PtStateSlab",
    "LwfSlab",
    "LabourRegisterType",
    # ── C.5 Recruitment ──────────────────────────────────────────────────
    "JobFunction",
    "JobLevel",
    "InterviewRound",
    "CandidateSource",
    "OfferStatus",
    "RejectionReason",
    "PipelineStage",
    # ── C.6 Performance, Training & Asset ────────────────────────────────
    "AppraisalCycle",
    "RatingScale",
    "GoalCategory",
    "KpiLibrary",
    "KraLibrary",
    "CompetencyGroup",
    "Competency",
    "TrainingCategory",
    "TrainingMode",
    "Course",
    "CertificationBody",
    "AssetCategory",
    "AssetCondition",
    "AssetType",
    "Vendor",
    # ── C.7 Workflow, Security & Notification ────────────────────────────
    "WorkflowType",
    "ApprovalAction",
    "EscalationType",
    "AuditEventType",
    "Permission",
    "MenuItem",
    "DataScopeType",
    "PasswordPolicy",
    "SessionPolicy",
    "NotificationChannel",
    "NotificationTemplate",
    "NotificationTrigger",
]
