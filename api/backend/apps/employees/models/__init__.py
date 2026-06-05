"""
Employee module — all models exported for Django auto-discovery.

Import order preserves FK dependency resolution:
  1. Base abstract models
  2. Master tables (no FK deps on transaction tables)
  3. Core Employee
  4. All transaction tables (depend on Employee + masters)
"""

# ---------------------------------------------------------------------------
# Base models
# ---------------------------------------------------------------------------
from apps.employees.models.base import (
    AuditMixin,
    BaseModel,
    CompanyMasterModel,
    FullAuditMasterModel,
    MasterBaseModel,
    MetadataMixin,
    PIIBaseModel,
    SoftDeleteMixin,
    UUIDMasterBaseModel,
)

# ---------------------------------------------------------------------------
# Original Master tables (personal, education, employment, location, org, ins, misc)
# ---------------------------------------------------------------------------
from apps.employees.models.masters import (
    # Personal
    Gender,
    Salutation,
    MaritalStatus,
    Religion,
    Caste,
    CasteCategory,
    MotherTongue,
    Nationality,
    BloodGroup,
    # Education
    EducationLevel,
    EducationSpecialization,
    EducationStatus,
    Specialization,
    Board,
    Qualification,
    StudyMode,
    Institution,
    PassingYear,
    University,
    # Employment
    EmployeeType,
    EmployeeCategory,
    SourceOfHire,
    SourceOfHireType,
    PayrollStatus,
    PayrollMode,
    PayrollGroup,
    TransportType,
    EmployeeStatus,
    WorkExperienceRange,
    RelevantExperienceRange,
    # Location
    Country,
    State,
    City,
    HeadquarterLocation,
    OfficeLocation,
    ProductionCell,
    Floor,
    LocationType,
    # Organization
    Company,
    Department,
    Designation,
    Grade,
    Bank,
    BankStatus,
    AccountType,
    DepartmentDivision,
    Extension,
    Batch,
    Cab,
    Team,
    # Insurance
    PolicyType,
    InsuranceType,
    CoverType,
    PremiumFrequency,
    InsuranceCompany,
    # Misc
    Language,
    LanguageProficiency,
    ProficiencyLevel,
    NomineePurpose,
    Relation,
    Occupation,
    Profession,
    CommunicationChannel,
    CommunicationTask,
    DocumentType,
    DocumentSide,
    # SystemRole,
    # DefaultRole,
    # Passport & Visa
    PassportCategory,
    PassportStatus,
    VisaType,
    VisaStatus,
    # C.1 Core HR Setup
    Branch,
    BusinessUnit,
    CostCenter,
    ProfitCenter,
    Band,
    ShiftType,
    Shift,
    WorkWeekPolicy,
    HolidayCalendar,
    Holiday,
    HolidayGroup,
    # C.2 Audit Additions
    SeparationMode,
    ContractStatus,
    VerificationStatus,
    ResidentialStatus,
    PaymentType,
    AttendanceScheme,
    AttendanceStatus,
    EmployeeFilter,
    BulletinCategory,
    PolicyCategory,
    FormCategory,
    ImportType,
    LetterApprovalType,
    ClearanceItemType,
    PositionChangeReason,
    CounterParty,
    AuthorizedSignatory,
    ReportingManager,
    # C.3 Attendance & Leave
    AttendancePolicy,
    RegularizationReason,
    # LeaveType,
    # LeavePolicy,
    # LeaveApprovalMatrix,
    # C.4 Payroll
    PayComponentGroup,
    PayComponent,
    SalaryStructure,
    SalaryStructureComponent,
    ReimbursementType,
    LoanType,
    PayrollCycle,
    TaxRegime,
    TdsSection,
    ArrearType,
    StatutoryComponent,
    PfScheme,
    EsiScheme,
    PtStateSlab,
    LwfSlab,
    LabourRegisterType,
    # C.5 Recruitment
    JobFunction,
    JobLevel,
    InterviewRound,
    CandidateSource,
    OfferStatus,
    RejectionReason,
    PipelineStage,
    # C.6 Performance, Training & Asset
    AppraisalCycle,
    RatingScale,
    GoalCategory,
    KpiLibrary,
    KraLibrary,
    CompetencyGroup,
    Competency,
    TrainingCategory,
    TrainingMode,
    Course,
    CertificationBody,
    AssetCategory,
    AssetCondition,
    AssetType,
    Vendor,
    # C.7 Workflow, Security & Notification
    WorkflowType,
    ApprovalAction,
    EscalationType,
    AuditEventType,
    Permission,
    MenuItem,
    # DataScopeType,
    PasswordPolicy,
    SessionPolicy,
    NotificationChannel,
    NotificationTemplate,
    NotificationTrigger,
)
from apps.security.models import Role, EmployeeRoleAssignment, Permission, MenuItem, DataScopeRule
# ---------------------------------------------------------------------------
# Core Employee
# ---------------------------------------------------------------------------
from apps.employees.models.employee import Employee
from apps.employees.models.org_chart import OrgChartSettings

# ---------------------------------------------------------------------------
# Transaction tables
# ---------------------------------------------------------------------------
from apps.employees.models.personal import EmployeePersonalDetails
from apps.employees.models.employment import (
    EmployeeEmploymentDetails,
    EmployeeLifecycle,
)
from apps.employees.models.contact import EmployeeContacts
from apps.employees.models.address import EmployeeAddress
from apps.employees.models.auth import (
    EmployeeAuth,
    EmployeeVerificationToken,
    LoginHistory,
)
from apps.employees.models.family import EmployeeFamilyMember
from apps.employees.models.nominees import EmployeeNominee
from apps.employees.models.education import EmployeeEducation
from apps.employees.models.documents import EmployeeDocument
from apps.employees.models.policies_forms import CompanyPolicyFormDocument
from apps.employees.models.segments import EmployeeSegment, EmployeeSegmentMember
from apps.employees.models.bank import EmployeeBankAccount
from apps.employees.models.statutory import EmployeeStatutoryIds
from apps.employees.models.insurance import EmployeeInsurancePolicy
from apps.employees.models.language import EmployeeLanguageProficiency
from apps.employees.models.skills import EmployeeProfessionalReference
from apps.employees.models.preferences import (
    EmployeeCommunicationPreference,
    EmployeeLocalization,
)
from apps.employees.models.access import EmployeeAccessCard
# from apps.employees.models.roles import EmployeeRoleAssignment
from apps.employees.models.reporting import EmployeeReportingRelationship
from apps.employees.models.position_history import EmployeePositionHistory
from apps.employees.models.previous_employment import EmployeePreviousEmployment
from apps.employees.models.audit import EmployeeAuditLog
from apps.employees.models.deputation import EmployeeDeputationLocation
from apps.employees.models.sequences import EmployeeCodeSequence
from apps.employees.models.salary import EmployeeSalary
from apps.employees.models.background_verification import EmployeeBackgroundVerification
from apps.employees.models.assets import EmployeeAsset
from apps.employees.models.fines_damages import EmployeeFine, EmployeePropertyDamage
from apps.employees.models.employee_filter import EmployeeCustomFilter, EmployeeFilterAuditLog
from apps.employees.models.salary import (
    EmployeeSalaryAssignment,
    EmployeeSalaryComponentValue,
)
from apps.employees.models.ess_extended import (
    EmployeeChangeRequest,
    EmployeeMedicalEmergency,
    EmployeePassportVisa,
    EmployeeSkillCertification,
    EmployeeSocialProfile,
    EmployeeWorkExperience,
)

__all__ = [
    # ── Base ──────────────────────────────────────────────────────────────
    "MetadataMixin",
    "MasterBaseModel",
    "UUIDMasterBaseModel",
    "BaseModel",
    "PIIBaseModel",
    "SoftDeleteMixin",
    "AuditMixin",
    "FullAuditMasterModel",
    "CompanyMasterModel",
    # ── Personal masters ──────────────────────────────────────────────────
    "Gender",
    "Salutation",
    "MaritalStatus",
    "Religion",
    "Caste",
    "CasteCategory",
    "MotherTongue",
    "Nationality",
    "BloodGroup",
    # ── Education masters ─────────────────────────────────────────────────
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
    # ── Employment masters ────────────────────────────────────────────────
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
    # ── Location masters ──────────────────────────────────────────────────
    "Country",
    "State",
    "City",
    "HeadquarterLocation",
    "OfficeLocation",
    "ProductionCell",
    "Floor",
    "LocationType",
    # ── Organization masters ──────────────────────────────────────────────
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
    # ── Insurance masters ─────────────────────────────────────────────────
    "PolicyType",
    "InsuranceType",
    "CoverType",
    "PremiumFrequency",
    "InsuranceCompany",
    # ── Misc masters ──────────────────────────────────────────────────────
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
    # ── Passport & Visa masters ───────────────────────────────────────────
    "PassportCategory",
    "PassportStatus",
    "VisaType",
    "VisaStatus",
    # ── C.1 Core HR Setup ─────────────────────────────────────────────────
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
    # ── C.2 Audit Additions ───────────────────────────────────────────────
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
    # ── C.3 Attendance & Leave ────────────────────────────────────────────
    "AttendancePolicy",
    "RegularizationReason",
    # ── C.4 Payroll ───────────────────────────────────────────────────────
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
    # ── C.5 Recruitment ───────────────────────────────────────────────────
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
    # ── C.7 Workflow, Security & Notification ─────────────────────────────
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
    # ── Core Employee ─────────────────────────────────────────────────────
    "Employee",
    # ── Transaction tables ────────────────────────────────────────────────
    "EmployeePersonalDetails",
    "EmployeeEmploymentDetails",
    "EmployeeLifecycle",
    "EmployeeContacts",
    "EmployeeAddress",
    "EmployeeAuth",
    "EmployeeVerificationToken",
    "LoginHistory",
    "EmployeeFamilyMember",
    "EmployeeNominee",
    "EmployeeEducation",
    "EmployeeDocument",
    "CompanyPolicyFormDocument",
    "EmployeeSegment",
    "EmployeeSegmentMember",
    "EmployeeBankAccount",
    "EmployeeStatutoryIds",
    "EmployeeInsurancePolicy",
    "EmployeeLanguageProficiency",
    "EmployeeProfessionalReference",
    "EmployeeCommunicationPreference",
    "EmployeeLocalization",
    "EmployeeAccessCard",
    "EmployeeRoleAssignment",
    "EmployeeReportingRelationship",
    "EmployeePositionHistory",
    "EmployeePreviousEmployment",
    "EmployeeAuditLog",
    "EmployeeDeputationLocation",
    "EmployeeCodeSequence",
    "EmployeeSalary",
    "EmployeeBackgroundVerification",
    "EmployeeAsset",
    "EmployeeSalaryAssignment",
    "EmployeeSalaryComponentValue",
    "EmployeeChangeRequest",
    "EmployeeMedicalEmergency",
    "EmployeePassportVisa",
    "EmployeeSkillCertification",
    "EmployeeSocialProfile",
    "EmployeeWorkExperience",
    # ── Fines & Damages ───────────────────────────────────────────────────
    "EmployeeFine",
    "EmployeePropertyDamage",
    # ── Employee Filter ───────────────────────────────────────────────────
    "EmployeeCustomFilter",
    "EmployeeFilterAuditLog",
]
