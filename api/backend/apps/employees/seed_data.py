"""
Comprehensive seed data for the Employee module.

This module provides seed data generation for all master tables and sample employee records.
It includes proper FK relationships and realistic data.

Usage:
    from apps.employees.seed_data import seed_all_data
    seed_all_data()
    
    OR run as management command (tenant-aware):
    python manage.py seed_employees --schema acme

Note: All seed functions follow the pattern:
    1. Check if data already exists (to avoid duplicates)
    2. Create master data first (no FK dependencies)
    3. Create transaction data (depends on masters)
"""

import uuid
from datetime import datetime, timedelta, date
from decimal import Decimal

from django.db import transaction as db_transaction

# Import all models
from apps.employees.models import (
    # Base/Masters - Personal
    Gender, Salutation, MaritalStatus, Religion, Caste, CasteCategory,
    MotherTongue, Nationality, BloodGroup,
    
    # Base/Masters - Education
    EducationLevel, EducationStatus, Specialization, Board, Qualification,
    StudyMode, EducationSpecialization, Institution, University, PassingYear,
    
    # Base/Masters - Employment
    EmployeeType, EmployeeCategory, SourceOfHire, SourceOfHireType,
    PayrollStatus, PayrollMode, PayrollGroup, TransportType,
    WorkExperienceRange, RelevantExperienceRange, EmployeeStatus,
    
    # Base/Masters - Location
    Country, State, City, HeadquarterLocation, OfficeLocation,
    ProductionCell, Floor, LocationType,
    
    # Base/Masters - Organization
    Company, Department, Designation, Grade, Bank, BankStatus,
    AccountType, DepartmentDivision, Extension, Batch, Cab,
    
    # Base/Masters - Insurance
    PolicyType, InsuranceType, CoverType, PremiumFrequency,
    InsuranceCompany,
    
    # Base/Masters - Misc
    Language, LanguageProficiency, ProficiencyLevel,
    NomineePurpose, Relation, Occupation, Profession,
    CommunicationChannel, CommunicationTask, DocumentType,
    DocumentSide, 
    # SystemRole, DefaultRole,
    
    # C.1 Core HR Setup Masters
    Branch, BusinessUnit, CostCenter, ProfitCenter, Band,
    ShiftType, Shift, WorkWeekPolicy, HolidayCalendar,
    Holiday, HolidayGroup,
    
    # C.2 Audit Additions Masters
    SeparationMode, ContractStatus, VerificationStatus,
    ResidentialStatus, PaymentType, AttendanceScheme,
    AttendanceStatus, EmployeeFilter, BulletinCategory,
    PolicyCategory, FormCategory, ImportType,
    LetterApprovalType, ClearanceItemType,
    PositionChangeReason, CounterParty, AuthorizedSignatory,
    
    # C.3 Attendance & Leave Masters
    # AttendancePolicy, RegularizationReason, OvertimePolicy,
    # CompOffPolicy,
    
    # C.4 Payroll & Compliance Masters
    PayComponentGroup, PayComponent, SalaryStructure,
    SalaryStructureComponent, ReimbursementType,
    LoanType, PayrollCycle, TaxRegime,
    TdsSection, ArrearType, StatutoryComponent,
    PfScheme, EsiScheme, PtStateSlab,
    LwfSlab, LabourRegisterType,
    
    # C.5 Recruitment Masters
    JobFunction, JobLevel, InterviewRound,
    CandidateSource, OfferStatus, RejectionReason,
    PipelineStage,
    
    # C.6 Performance, Training & Asset Masters
    AppraisalCycle, RatingScale, GoalCategory,
    KpiLibrary, KraLibrary, CompetencyGroup,
    Competency, TrainingCategory, TrainingMode,
    Course, CertificationBody, AssetCategory,
    AssetCondition, AssetType, Vendor,
    
    # C.7 Workflow, Security & Notification Masters
    WorkflowType, ApprovalAction, EscalationType,
    AuditEventType, Permission, 
    # MenuItem, DataScopeType,
    PasswordPolicy, SessionPolicy,
    NotificationChannel, NotificationTemplate,
    NotificationTrigger,
    
    # Transaction Models
    Employee, EmployeePersonalDetails, EmployeeEmploymentDetails,
    EmployeeAddress, EmployeeContacts, EmployeeFamilyMember,
    EmployeeEducation, EmployeeRoleAssignment, EmployeeLifecycle,
    EmployeeAuth, EmployeeVerificationToken, LoginHistory,
    EmployeeNominee, EmployeeDocument, EmployeeBankAccount,
    EmployeeStatutoryIds, EmployeeInsurancePolicy,
    EmployeeLanguageProficiency, EmployeeProfessionalReference,
    EmployeeCommunicationPreference, EmployeeLocalization,
    EmployeeAccessCard, EmployeeReportingRelationship,
    EmployeeAuditLog, EmployeeDeputationLocation,
    EmployeeCodeSequence,
)


# ═════════════════════════════════════════════════════════════════════════════
# PERSONAL MASTERS
# ═════════════════════════════════════════════════════════════════════════════

def seed_gender():
    """Create gender master data."""
    if Gender.objects.exists():
        print("✓ Gender data already exists, skipping...")
        return
    
    genders = [
        {"code": "M", "label": "Male"},
        {"code": "F", "label": "Female"},
        {"code": "O", "label": "Other"},
        {"code": "NA", "label": "Prefer Not to Say"},
    ]
    
    for gender in genders:
        Gender.objects.create(**gender)
    print(f"✓ Created {len(genders)} gender records")


def seed_salutation():
    """Create salutation master data."""
    if Salutation.objects.exists():
        print("✓ Salutation data already exists, skipping...")
        return
    
    salutations = [
        {"code": "MR", "label": "Mr."},
        {"code": "MRS", "label": "Mrs."},
        {"code": "MS", "label": "Ms."},
        {"code": "DR", "label": "Dr."},
        {"code": "PROF", "label": "Prof."},
    ]
    
    for sal in salutations:
        Salutation.objects.create(**sal)
    print(f"✓ Created {len(salutations)} salutation records")


def seed_marital_status():
    """Create marital status master data."""
    if MaritalStatus.objects.exists():
        print("✓ Marital Status data already exists, skipping...")
        return
    
    statuses = [
        {"code": "SINGLE", "label": "Single"},
        {"code": "MARRIED", "label": "Married"},
        {"code": "DIVORCED", "label": "Divorced"},
        {"code": "WIDOWED", "label": "Widowed"},
        {"code": "SEPARATED", "label": "Separated"},
    ]
    
    for status in statuses:
        MaritalStatus.objects.create(**status)
    print(f"✓ Created {len(statuses)} marital status records")


def seed_religion():
    """Create religion master data."""
    if Religion.objects.exists():
        print("✓ Religion data already exists, skipping...")
        return
    
    religions = [
        {"code": "HINDU", "label": "Hindu"},
        {"code": "MUSLIM", "label": "Muslim"},
        {"code": "CHRISTIAN", "label": "Christian"},
        {"code": "SIKH", "label": "Sikh"},
        {"code": "BUDDHIST", "label": "Buddhist"},
        {"code": "JAIN", "label": "Jain"},
        {"code": "OTHER", "label": "Other"},
    ]
    
    for religion in religions:
        Religion.objects.create(**religion)
    print(f"✓ Created {len(religions)} religion records")


def seed_blood_group():
    """Create blood group master data."""
    if BloodGroup.objects.exists():
        print("✓ Blood Group data already exists, skipping...")
        return
    
    blood_groups = [
        {"code": "A+", "label": "A+"},
        {"code": "A-", "label": "A-"},
        {"code": "B+", "label": "B+"},
        {"code": "B-", "label": "B-"},
        {"code": "AB+", "label": "AB+"},
        {"code": "AB-", "label": "AB-"},
        {"code": "O+", "label": "O+"},
        {"code": "O-", "label": "O-"},
    ]
    
    for bg in blood_groups:
        BloodGroup.objects.create(**bg)
    print(f"✓ Created {len(blood_groups)} blood group records")


def seed_nationality():
    """Create nationality master data."""
    if Nationality.objects.exists():
        print("✓ Nationality data already exists, skipping...")
        return
    
    nationalities = [
        {"code": "IND", "label": "Indian"},
        {"code": "USA", "label": "American"},
        {"code": "GBR", "label": "British"},
        {"code": "AUS", "label": "Australian"},
        {"code": "CAN", "label": "Canadian"},
    ]
    
    for nat in nationalities:
        Nationality.objects.create(**nat)
    print(f"✓ Created {len(nationalities)} nationality records")


def seed_caste_category():
    """Create caste category master data."""
    if CasteCategory.objects.exists():
        print("✓ Caste Category data already exists, skipping...")
        return
    
    categories = [
        {"code": "GEN", "label": "General"},
        {"code": "OBC", "label": "Other Backward Class"},
        {"code": "SC", "label": "Scheduled Caste"},
        {"code": "ST", "label": "Scheduled Tribe"},
    ]
    
    for cat in categories:
        CasteCategory.objects.create(**cat)
    print(f"✓ Created {len(categories)} caste category records")


def seed_relation():
    """Create relation master data."""
    if Relation.objects.exists():
        print("✓ Relation data already exists, skipping...")
        return
    
    relations = [
        {"code": "FATHER", "label": "Father"},
        {"code": "MOTHER", "label": "Mother"},
        {"code": "SPOUSE", "label": "Spouse"},
        {"code": "SON", "label": "Son"},
        {"code": "DAUGHTER", "label": "Daughter"},
        {"code": "BROTHER", "label": "Brother"},
        {"code": "SISTER", "label": "Sister"},
        {"code": "GRANDFATHER", "label": "Grandfather"},
        {"code": "GRANDMOTHER", "label": "Grandmother"},
    ]
    
    for rel in relations:
        Relation.objects.create(**rel)
    print(f"✓ Created {len(relations)} relation records")


def seed_occupation():
    """Create occupation master data."""
    if Occupation.objects.exists():
        print("✓ Occupation data already exists, skipping...")
        return
    
    occupations = [
        {"code": "SALARIED", "label": "Salaried"},
        {"code": "SELF_EMP", "label": "Self Employed"},
        {"code": "STUDENT", "label": "Student"},
        {"code": "RETIRED", "label": "Retired"},
        {"code": "HOMEMAKER", "label": "Homemaker"},
        {"code": "FARMER", "label": "Farmer"},
    ]
    
    for occ in occupations:
        Occupation.objects.create(**occ)
    print(f"✓ Created {len(occupations)} occupation records")


# ═════════════════════════════════════════════════════════════════════════════
# EDUCATION MASTERS
# ═════════════════════════════════════════════════════════════════════════════

def seed_education_level():
    """Create education level master data."""
    if EducationLevel.objects.exists():
        print("✓ Education Level data already exists, skipping...")
        return
    
    levels = [
        {"code": "PRIMARY", "label": "Primary"},
        {"code": "SECONDARY", "label": "Secondary"},
        {"code": "SENIOR_SEC", "label": "Senior Secondary"},
        {"code": "DIPLOMA", "label": "Diploma"},
        {"code": "BACHELOR", "label": "Bachelor"},
        {"code": "MASTER", "label": "Master"},
        {"code": "DOCTORATE", "label": "Doctorate"},
    ]
    
    for level in levels:
        EducationLevel.objects.create(**level)
    print(f"✓ Created {len(levels)} education level records")


def seed_education_status():
    """Create education status master data."""
    if EducationStatus.objects.exists():
        print("✓ Education Status data already exists, skipping...")
        return
    
    statuses = [
        {"code": "PURSUING", "label": "Pursuing"},
        {"code": "COMPLETED", "label": "Completed"},
        {"code": "DROPPED", "label": "Dropped"},
    ]
    
    for status in statuses:
        EducationStatus.objects.create(**status)
    print(f"✓ Created {len(statuses)} education status records")


def seed_study_mode():
    """Create study mode master data."""
    if StudyMode.objects.exists():
        print("✓ Study Mode data already exists, skipping...")
        return
    
    modes = [
        {"code": "FULL_TIME", "label": "Full Time"},
        {"code": "PART_TIME", "label": "Part Time"},
        {"code": "DISTANCE", "label": "Distance"},
        {"code": "ONLINE", "label": "Online"},
    ]
    
    for mode in modes:
        StudyMode.objects.create(**mode)
    print(f"✓ Created {len(modes)} study mode records")


def seed_qualification():
    """Create qualification master data."""
    if Qualification.objects.exists():
        print("✓ Qualification data already exists, skipping...")
        return
    
    qualifications = [
        {"code": "BA", "label": "Bachelor of Arts"},
        {"code": "BSC", "label": "Bachelor of Science"},
        {"code": "BE", "label": "Bachelor of Engineering"},
        {"code": "BTECH", "label": "B.Tech"},
        {"code": "BCA", "label": "Bachelor of Computer Applications"},
        {"code": "MBA", "label": "Master of Business Administration"},
        {"code": "MCA", "label": "Master of Computer Applications"},
        {"code": "MS", "label": "Master of Science"},
        {"code": "PHD", "label": "Doctor of Philosophy"},
    ]
    
    for qual in qualifications:
        Qualification.objects.create(**qual)
    print(f"✓ Created {len(qualifications)} qualification records")


def seed_specialization():
    """Create specialization master data."""
    if Specialization.objects.exists():
        print("✓ Specialization data already exists, skipping...")
        return
    
    specs = [
        {"code": "CSE", "label": "Computer Science"},
        {"code": "ECE", "label": "Electronics & Communication"},
        {"code": "MECH", "label": "Mechanical Engineering"},
        {"code": "CIVIL", "label": "Civil Engineering"},
        {"code": "FINANCE", "label": "Finance"},
        {"code": "MARKETING", "label": "Marketing"},
        {"code": "HR", "label": "Human Resources"},
    ]
    
    for spec in specs:
        Specialization.objects.create(**spec)
    print(f"✓ Created {len(specs)} specialization records")


def seed_institution():
    if Institution.objects.exists():
        print("✓ Institution data already exists, skipping...")
        return

    institutions = [
        {"code": "ABC_IT", "label": "ABC Institute of Technology"},
        {"code": "DELHI_IT", "label": "Delhi Institute of Technology"},
        {"code": "IIT_DELHI", "label": "Indian Institute of Technology"},
        {"code": "MUMBAI_IT", "label": "Mumbai Institute of Technology"},
    ]
    for row in institutions:
        Institution.objects.create(**row)
    print(f"✓ Created {len(institutions)} institution records")


def seed_university():
    if University.objects.exists():
        print("✓ University data already exists, skipping...")
        return

    universities = [
        {"code": "VTU", "label": "VTU"},
        {"code": "DELHI_UNI", "label": "Delhi University"},
        {"code": "IIT_DELHI", "label": "IIT Delhi"},
        {"code": "MUMBAI_UNI", "label": "Mumbai University"},
    ]
    for row in universities:
        University.objects.create(**row)
    print(f"✓ Created {len(universities)} university records")


def seed_passing_year():
    if PassingYear.objects.exists():
        print("✓ Passing Year data already exists, skipping...")
        return

    current_year = date.today().year
    years = range(current_year - 30, current_year + 2)
    for year in years:
        PassingYear.objects.create(code=str(year), label=str(year), year=year)
    print(f"✓ Created {len(list(years))} passing year records")


# ═════════════════════════════════════════════════════════════════════════════
# EMPLOYMENT MASTERS
# ═════════════════════════════════════════════════════════════════════════════

def seed_employee_type():
    """Create employee type master data."""
    if EmployeeType.objects.exists():
        print("✓ Employee Type data already exists, skipping...")
        return
    
    types = [
        {"code": "PERMANENT", "label": "Permanent"},
        {"code": "CONTRACT", "label": "Contract"},
        {"code": "INTERN", "label": "Intern"},
        {"code": "TRAINEE", "label": "Trainee"},
        {"code": "CONSULTANT", "label": "Consultant"},
    ]
    
    for etype in types:
        EmployeeType.objects.create(**etype)
    print(f"✓ Created {len(types)} employee type records")


def seed_employee_category():
    """Create employee category master data."""
    if EmployeeCategory.objects.exists():
        print("✓ Employee Category data already exists, skipping...")
        return
    
    categories = [
        {"code": "STAFF", "label": "Staff"},
        {"code": "WORKER", "label": "Worker"},
        {"code": "MANAGEMENT", "label": "Management"},
        {"code": "TRAINEE", "label": "Trainee"},
    ]
    
    for cat in categories:
        EmployeeCategory.objects.create(**cat)
    print(f"✓ Created {len(categories)} employee category records")


def seed_employee_status():
    """Create employee status master data."""
    if EmployeeStatus.objects.exists():
        print("✓ Employee Status data already exists, skipping...")
        return
    
    statuses = [
        {"code": "ACTIVE", "label": "Active"},
        {"code": "INACTIVE", "label": "Inactive"},
        {"code": "SUSPENDED", "label": "Suspended"},
        {"code": "TERMINATED", "label": "Terminated"},
    ]
    
    for status in statuses:
        EmployeeStatus.objects.create(**status)
    print(f"✓ Created {len(statuses)} employee status records")


def seed_payroll_status():
    """Create payroll status master data."""
    if PayrollStatus.objects.exists():
        print("✓ Payroll Status data already exists, skipping...")
        return
    
    statuses = [
        {"code": "ACTIVE", "label": "Active", "description": "Employee is in active payroll"},
        {"code": "HOLD", "label": "On Hold", "description": "Payroll is on hold"},
        {"code": "EXCLUDED", "label": "Excluded", "description": "Excluded from payroll"},
    ]
    
    for status in statuses:
        PayrollStatus.objects.create(**status)
    print(f"✓ Created {len(statuses)} payroll status records")


def seed_source_of_hire():
    """Create source of hire master data."""
    if SourceOfHire.objects.exists():
        print("✓ Source of Hire data already exists, skipping...")
        return
    
    sources = [
        {"code": "WALK_IN", "label": "Walk-in"},
        {"code": "REFERRAL", "label": "Employee Referral"},
        {"code": "PORTAL", "label": "Job Portal"},
        {"code": "CAMPUS", "label": "Campus Recruitment"},
        {"code": "INTERNAL", "label": "Internal Promotion"},
    ]
    
    for source in sources:
        SourceOfHire.objects.create(**source)
    print(f"✓ Created {len(sources)} source of hire records")


def seed_transport_type():
    """Create transport type master data."""
    if TransportType.objects.exists():
        print("✓ Transport Type data already exists, skipping...")
        return
    
    types = [
        {"code": "OWN", "label": "Own Vehicle"},
        {"code": "COMPANY_BUS", "label": "Company Bus"},
        {"code": "PUBLIC", "label": "Public Transport"},
        {"code": "NONE", "label": "No Transport"},
    ]
    
    for ttype in types:
        TransportType.objects.create(**ttype)
    print(f"✓ Created {len(types)} transport type records")


# ═════════════════════════════════════════════════════════════════════════════
# LOCATION MASTERS
# ═════════════════════════════════════════════════════════════════════════════

def seed_country():
    """Create country master data."""
    if Country.objects.exists():
        print("✓ Country data already exists, skipping...")
        return
    
    countries = [
        {"code": "IN", "iso3_code": "IND", "numeric_code": 356, "label": "India"},
        {"code": "US", "iso3_code": "USA", "numeric_code": 840, "label": "United States"},
        {"code": "GB", "iso3_code": "GBR", "numeric_code": 826, "label": "United Kingdom"},
        {"code": "AU", "iso3_code": "AUS", "numeric_code": 36, "label": "Australia"},
        {"code": "CA", "iso3_code": "CAN", "numeric_code": 124, "label": "Canada"},
    ]
    
    for country in countries:
        Country.objects.create(**country)
    print(f"✓ Created {len(countries)} country records")


def seed_state():
    """Create state master data."""
    if State.objects.exists():
        print("✓ State data already exists, skipping...")
        return
    
    india = Country.objects.get(code="IN")
    
    states = [
        {"country": india, "code": "DL", "label": "Delhi"},
        {"country": india, "code": "MH", "label": "Maharashtra"},
        {"country": india, "code": "KA", "label": "Karnataka"},
        {"country": india, "code": "TG", "label": "Telangana"},
        {"country": india, "code": "GJ", "label": "Gujarat"},
        {"country": india, "code": "TN", "label": "Tamil Nadu"},
        {"country": india, "code": "AP", "label": "Andhra Pradesh"},
        {"country": india, "code": "WB", "label": "West Bengal"},
    ]
    
    for state in states:
        State.objects.create(**state)
    print(f"✓ Created {len(states)} state records")


def seed_city():
    """Create city master data."""
    if City.objects.exists():
        print("✓ City data already exists, skipping...")
        return
    
    delhi = State.objects.get(code="DL")
    maharashtra = State.objects.get(code="MH")
    karnataka = State.objects.get(code="KA")
    
    cities = [
        {"state": delhi, "code": "DEL", "label": "Delhi", "pincode": "110001"},
        {"state": delhi, "code": "NOIDA", "label": "NOIDA", "pincode": "201301"},
        {"state": maharashtra, "code": "MUM", "label": "Mumbai", "pincode": "400001"},
        {"state": maharashtra, "code": "PUN", "label": "Pune", "pincode": "411001"},
        {"state": karnataka, "code": "BLR", "label": "Bangalore", "pincode": "560001"},
    ]
    
    for city in cities:
        City.objects.create(**city)
    print(f"✓ Created {len(cities)} city records")


# ═════════════════════════════════════════════════════════════════════════════
# ORGANIZATION MASTERS
# ═════════════════════════════════════════════════════════════════════════════

def seed_company():
    """Create company master data."""
    if Company.objects.exists():
        print("✓ Company data already exists, skipping...")
        return
    
    companies = [
        {
            "code": "TECH001",
            "name": "Tech Solutions India Pvt Ltd",
            "pan": "AABCS1234C",
            "gstin": "07AABCS1234C1Z0",
            "cin": "U72900MH2010PTC205116",
            "registered_address": "123 Tech Park, Mumbai, MH 400001"
        },
        {
            "code": "TECH002",
            "name": "Digital Innovation Corp",
            "pan": "AABCT1234D",
            "gstin": "07AABCT1234D1Z0",
            "cin": "U72900DL2015PTC284532",
            "registered_address": "456 Innovation Hub, Delhi, DL 110001"
        },
    ]
    
    for company in companies:
        Company.objects.create(**company)
    print(f"✓ Created {len(companies)} company records")


def seed_grade():
    """Create grade master data."""
    if Grade.objects.exists():
        print("✓ Grade data already exists, skipping...")
        return
    
    company = Company.objects.first()
    
    grades = [
        {"company": company, "code": "G1", "label": "Grade 1 - Entry Level"},
        {"company": company, "code": "G2", "label": "Grade 2 - Associate"},
        {"company": company, "code": "G3", "label": "Grade 3 - Senior Associate"},
        {"company": company, "code": "G4", "label": "Grade 4 - Manager"},
        {"company": company, "code": "G5", "label": "Grade 5 - Senior Manager"},
    ]
    
    for grade in grades:
        Grade.objects.create(**grade)
    print(f"✓ Created {len(grades)} grade records")


def seed_department():
    """Create department master data."""
    if Department.objects.exists():
        print("✓ Department data already exists, skipping...")
        return
    
    company = Company.objects.first()
    
    departments = [
        {"company": company, "code": "IT", "name": "Information Technology", "parent_department": None},
        {"company": company, "code": "HR", "name": "Human Resources", "parent_department": None},
        {"company": company, "code": "FIN", "name": "Finance", "parent_department": None},
        {"company": company, "code": "OPS", "name": "Operations", "parent_department": None},
    ]
    
    for dept in departments:
        Department.objects.create(**dept)
    print(f"✓ Created {len(departments)} department records")


def seed_designation():
    """Create designation master data."""
    if Designation.objects.exists():
        print("✓ Designation data already exists, skipping...")
        return
    
    company = Company.objects.first()
    grade = Grade.objects.first()
    
    designations = [
        {"company": company, "code": "SE", "title": "Software Engineer", "grade": grade},
        {"company": company, "code": "SSE", "title": "Senior Software Engineer", "grade": grade},
        {"company": company, "code": "PM", "title": "Project Manager", "grade": grade},
        {"company": company, "code": "HR_EXE", "title": "HR Executive", "grade": grade},
        {"company": company, "code": "FIN_EXE", "title": "Finance Executive", "grade": grade},
    ]
    
    for desig in designations:
        Designation.objects.create(**desig)
    print(f"✓ Created {len(designations)} designation records")


def seed_bank():
    """Create bank master data."""
    if Bank.objects.exists():
        print("✓ Bank data already exists, skipping...")
        return
    
    banks = [
        {"code": "ICICI", "name": "ICICI Bank", "ifsc_prefix": "ICIC"},
        {"code": "HDFC", "name": "HDFC Bank", "ifsc_prefix": "HDFC"},
        {"code": "AXIS", "name": "Axis Bank", "ifsc_prefix": "UTIB"},
        {"code": "SBI", "name": "State Bank of India", "ifsc_prefix": "SBIN"},
        {"code": "KOTK", "name": "Kotak Mahindra Bank", "ifsc_prefix": "KKBK"},
    ]
    
    for bank in banks:
        Bank.objects.create(**bank)
    print(f"✓ Created {len(banks)} bank records")


def seed_bank_status():
    """Create bank status master data."""
    if BankStatus.objects.exists():
        print("✓ Bank Status data already exists, skipping...")
        return
    
    statuses = [
        {"code": "ACTIVE", "label": "Active"},
        {"code": "DORMANT", "label": "Dormant"},
        {"code": "CLOSED", "label": "Closed"},
    ]
    
    for status in statuses:
        BankStatus.objects.create(**status)
    print(f"✓ Created {len(statuses)} bank status records")


def seed_account_type():
    """Create account type master data."""
    if AccountType.objects.exists():
        print("✓ Account Type data already exists, skipping...")
        return
    
    types = [
        {"code": "SAVINGS", "label": "Savings Account"},
        {"code": "CURRENT", "label": "Current Account"},
        {"code": "NRE", "label": "NRE Account"},
        {"code": "NRO", "label": "NRO Account"},
    ]
    
    for atype in types:
        AccountType.objects.create(**atype)
    print(f"✓ Created {len(types)} account type records")


def _bulk_get_or_create(model, rows, lookup_fields=("code",)):
    """Create a batch of master records using safe get_or_create semantics."""
    if model.objects.exists():
        print(f"✓ {model.__name__} data already exists, skipping...")
        return

    created = 0
    for row in rows:
        lookup = {field: row[field] for field in lookup_fields if field in row}
        _, created_flag = model.objects.get_or_create(defaults=row, **lookup)
        if created_flag:
            created += 1
    print(f"✓ Created {created} {model.__name__} records")


# Additional Masters
# ---------------------------------------------------------------------------

def seed_payroll_mode():
    _bulk_get_or_create(
        PayrollMode,
        [
            {"code": "NEFT", "label": "NEFT"},
            {"code": "RTGS", "label": "RTGS"},
            {"code": "CHEQUE", "label": "Cheque"},
            {"code": "CASH", "label": "Cash"},
        ],
    )


def seed_payroll_group():
    _bulk_get_or_create(
        PayrollGroup,
        [
            {"code": "MONTHLY", "label": "Monthly Payroll"},
            {"code": "WEEKLY", "label": "Weekly Payroll"},
        ],
    )


def seed_profession():
    _bulk_get_or_create(
        Profession,
        [
            {"code": "DEVELOPER", "label": "Developer"},
            {"code": "ACCOUNTANT", "label": "Accountant"},
            {"code": "HR", "label": "HR Professional"},
            {"code": "MANAGER", "label": "Manager"},
        ],
    )


def seed_work_experience_range():
    _bulk_get_or_create(
        WorkExperienceRange,
        [
            {"code": "0-1", "label": "0-1 Years", "min_months": 0, "max_months": 12},
            {"code": "1-3", "label": "1-3 Years", "min_months": 12, "max_months": 36},
            {"code": "3-5", "label": "3-5 Years", "min_months": 36, "max_months": 60},
            {"code": "5-10", "label": "5-10 Years", "min_months": 60, "max_months": 120},
        ],
    )


def seed_relevant_experience_range():
    _bulk_get_or_create(
        RelevantExperienceRange,
        [
            {"code": "0-1", "label": "0-1 Years", "min_months": 0, "max_months": 12},
            {"code": "1-3", "label": "1-3 Years", "min_months": 12, "max_months": 36},
            {"code": "3-5", "label": "3-5 Years", "min_months": 36, "max_months": 60},
            {"code": "5-10", "label": "5-10 Years", "min_months": 60, "max_months": 120},
        ],
    )


def seed_location_type():
    _bulk_get_or_create(
        LocationType,
        [
            {"code": "HQ", "label": "Headquarters"},
            {"code": "BRANCH", "label": "Branch"},
            {"code": "REMOTE", "label": "Remote Site"},
            {"code": "CLIENT", "label": "Client Site"},
        ],
    )


def seed_headquarter_location():
    if HeadquarterLocation.objects.exists():
        print("✓ Headquarter Location data already exists, skipping...")
        return

    india = Country.objects.get(code="IN")
    delhi = State.objects.get(code="DL")
    delhi_city = City.objects.get(code="DEL")

    _bulk_get_or_create(
        HeadquarterLocation,
        [
            {
                "code": "HQ_DELHI",
                "label": "Delhi Headquarters",
                "country": india,
                "state": delhi,
                "city": delhi_city,
                "address_line1": "100 Corporate Avenue",
                "address_line2": "Sector 17",
                "pincode": "110001",
            }
        ],
    )


def seed_office_location():
    if OfficeLocation.objects.exists():
        print("✓ Office Location data already exists, skipping...")
        return

    india = Country.objects.get(code="IN")
    delhi = State.objects.get(code="DL")
    delhi_city = City.objects.get(code="DEL")

    _bulk_get_or_create(
        OfficeLocation,
        [
            {
                "code": "OFF_DELHI",
                "label": "Delhi Office",
                "country": india,
                "state": delhi,
                "city": delhi_city,
                "address_line1": "200 Business Park",
                "address_line2": "Block A",
                "pincode": "110002",
                "timezone": "Asia/Kolkata",
                "is_headquarter": True,
            }
        ],
    )


def seed_production_cell():
    office = OfficeLocation.objects.first()
    if not office:
        print("⚠️ OfficeLocation is required for ProductionCell seed")
        return

    _bulk_get_or_create(
        ProductionCell,
        [
            {
                "code": "PC_DELHI_1",
                "label": "Production Cell 1",
                "office_location": office,
                "capacity": 120,
            }
        ],
    )


def seed_floor():
    office = OfficeLocation.objects.first()
    if not office:
        print("⚠️ OfficeLocation is required for Floor seed")
        return

    if Floor.objects.exists():
        print("✓ Floor data already exists, skipping...")
        return

    floors = [
        {"office_location": office, "floor_number": 1, "label": "First Floor"},
        {"office_location": office, "floor_number": 2, "label": "Second Floor"},
    ]

    created = 0
    for floor in floors:
        _, created_flag = Floor.objects.get_or_create(
            office_location=floor["office_location"],
            floor_number=floor["floor_number"],
            defaults=floor,
        )
        if created_flag:
            created += 1

    print(f"✓ Created {created} Floor records")


def seed_branch():
    company = Company.objects.first()
    _bulk_get_or_create(
        Branch,
        [
            {
                "company_id": company.id if company else None,
                "code": "BR_DELHI",
                "name": "Delhi Branch",
                "branch_type": Branch.BranchType.BRANCH,
                "gstin": "07AABBCC1234D1Z0",
                "pt_registration": "DLPT123456",
                "is_payroll_entity": True,
            }
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_business_unit():
    company = Company.objects.first()
    _bulk_get_or_create(
        BusinessUnit,
        [
            {"company_id": company.id if company else None, "code": "BUS_DEV", "name": "Business Development"},
            {"company_id": company.id if company else None, "code": "PRODUCT", "name": "Product"},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_cost_center():
    company = Company.objects.first()
    branch = Branch.objects.first()
    _bulk_get_or_create(
        CostCenter,
        [
            {
                "company_id": company.id if company else None,
                "branch_id": branch.id if branch else None,
                "code": "CC_IT",
                "name": "IT Cost Center",
                "budget_code": "BUD_IT_01",
                "cost_center_type": CostCenter.CostCenterType.DIRECT,
            }
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_profit_center():
    company = Company.objects.first()
    _bulk_get_or_create(
        ProfitCenter,
        [{"company_id": company.id if company else None, "code": "PC_MAIN", "name": "Main Profit Center"}],
        lookup_fields=("company_id", "code"),
    )


def seed_band():
    company = Company.objects.first()
    _bulk_get_or_create(
        Band,
        [
            {
                "company_id": company.id if company else None,
                "code": "B1",
                "name": "Band 1",
                "min_ctc": 300000,
                "max_ctc": 600000,
            }
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_shift_type():
    _bulk_get_or_create(
        ShiftType,
        [
            {"code": "DAY", "name": "Day Shift", "sort_order": 1},
            {"code": "NIGHT", "name": "Night Shift", "sort_order": 2},
        ],
    )


def seed_shift():
    shift_type = ShiftType.objects.filter(code="DAY").first()
    company = Company.objects.first()
    if not shift_type or not company:
        return

    _bulk_get_or_create(
        Shift,
        [
            {
                "company_id": company.id,
                "code": "SHIFT_DAY",
                "name": "Day Shift",
                "shift_type_id": shift_type.id,
                "start_time": "09:00:00",
                "end_time": "18:00:00",
                "grace_in_minutes": 15,
                "grace_out_minutes": 15,
                "break_minutes": 60,
                "weekly_off_days": "SAT,SUN",
                "is_overnight": False,
                "is_flexible": False,
                "ot_applicable": True,
            }
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_work_week_policy():
    company = Company.objects.first()
    _bulk_get_or_create(
        WorkWeekPolicy,
        [
            {"company_id": company.id if company else None, "code": "5DAY", "name": "Five Day Week", "working_days": 5, "week_off_days": "SAT,SUN"},
            {"company_id": company.id if company else None, "code": "6DAY", "name": "Six Day Week", "working_days": 6, "week_off_days": "SUN"},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_holiday_calendar():
    company = Company.objects.first()
    _bulk_get_or_create(
        HolidayCalendar,
        [
            {
                "company_id": company.id if company else None,
                "code": "CAL_2025",
                "name": "2025 Holiday Calendar",
                "calendar_year": date.today().year,
                "branch_id": None,
            }
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_holiday():
    calendar = HolidayCalendar.objects.filter(code="CAL_2025").first()
    if not calendar:
        return
    if Holiday.objects.exists():
        print("✓ Holiday data already exists, skipping...")
        return

    holidays = [
        {"holiday_calendar_id": calendar.id, "holiday_date": date(date.today().year, 1, 26), "name": "Republic Day", "holiday_type": Holiday.HolidayType.NATIONAL},
        {"holiday_calendar_id": calendar.id, "holiday_date": date(date.today().year, 8, 15), "name": "Independence Day", "holiday_type": Holiday.HolidayType.NATIONAL},
    ]

    for holiday in holidays:
        Holiday.objects.create(**holiday)
    print(f"✓ Created {len(holidays)} holiday records")


def seed_holiday_group():
    calendar = HolidayCalendar.objects.filter(code="CAL_2025").first()
    company = Company.objects.first()
    _bulk_get_or_create(
        HolidayGroup,
        [
            {"company_id": company.id if company else None, "code": "HG_DEFAULT", "name": "Default Holiday Group", "holiday_calendar_id": calendar.id if calendar else None},
        ],
        lookup_fields=("company_id", "code"),
    )


# def seed_system_role():
#     _bulk_get_or_create(
#         SystemRole,
#         [
#             {"code": "ADMIN", "label": "Administrator", "description": "System administrator role."},
#             {"code": "HR_MANAGER", "label": "HR Manager", "description": "Human resources manager role."},
#             {"code": "EMPLOYEE", "label": "Employee", "description": "Standard employee role."},
#         ],
#         lookup_fields=("code",),
#     )


# def seed_default_role():
#     if DefaultRole.objects.exists():
#         print("✓ Default Role data already exists, skipping...")
#         return

#     admin_role = SystemRole.objects.filter(code="ADMIN").first()
#     if admin_role:
#         DefaultRole.objects.create(role=admin_role)
#         print("✓ Created Default Role record")


def seed_communication_channel():
    _bulk_get_or_create(
        CommunicationChannel,
        [
            {"code": "EMAIL", "label": "Email"},
            {"code": "SMS", "label": "SMS"},
            {"code": "WHATSAPP", "label": "WhatsApp"},
            {"code": "PUSH", "label": "Push Notification"},
            {"code": "IN_APP", "label": "In-app Notification"},
        ],
        lookup_fields=("code",),
    )


def seed_communication_task():
    _bulk_get_or_create(
        CommunicationTask,
        [
            {"code": "WELCOME_EMAIL", "label": "Welcome Email"},
            {"code": "PAYSLIP_PUBLISHED", "label": "Payslip Published"},
            {"code": "LEAVE_APPROVAL", "label": "Leave Approval"},
        ],
        lookup_fields=("code",),
    )


def seed_document_type():
    _bulk_get_or_create(
        DocumentType,
        [
            {"code": "AADHAAR", "label": "Aadhaar", "is_expiry_required": False},
            {"code": "PAN", "label": "PAN", "is_expiry_required": False},
            {"code": "PASSPORT", "label": "Passport", "is_expiry_required": True},
        ],
        lookup_fields=("code",),
    )


def seed_document_side():
    _bulk_get_or_create(
        DocumentSide,
        [
            {"code": "FRONT", "label": "Front Side"},
            {"code": "BACK", "label": "Back Side"},
            {"code": "FULL", "label": "Full Document"},
        ],
        lookup_fields=("code",),
    )


def seed_separation_mode():
    _bulk_get_or_create(
        SeparationMode,
        [
            {"code": "RESIGNED", "name": "Resigned", "is_voluntary": True},
            {"code": "TERMINATED", "name": "Terminated", "is_terminal": True},
        ],
        lookup_fields=("code",),
    )


def seed_contract_status():
    _bulk_get_or_create(
        ContractStatus,
        [
            {"code": "ACTIVE", "name": "Active", "is_terminal": False},
            {"code": "EXPIRED", "name": "Expired", "is_terminal": True},
        ],
        lookup_fields=("code",),
    )


def seed_verification_status():
    _bulk_get_or_create(
        VerificationStatus,
        [
            {"code": "PENDING", "name": "Pending", "is_positive": False},
            {"code": "VERIFIED", "name": "Verified", "is_positive": True},
            {"code": "REJECTED", "name": "Rejected", "is_positive": False},
        ],
        lookup_fields=("code",),
    )


def seed_residential_status():
    _bulk_get_or_create(
        ResidentialStatus,
        [
            {"code": "RESIDENT", "name": "Resident"},
            {"code": "NRI", "name": "NRI"},
            {"code": "OCI", "name": "OCI"},
        ],
        lookup_fields=("code",),
    )


def seed_payment_type():
    _bulk_get_or_create(
        PaymentType,
        [
            {"code": "NEFT", "name": "NEFT", "requires_bank_account": True, "requires_ifsc": True},
            {"code": "CHEQUE", "name": "Cheque", "requires_bank_account": False, "requires_ifsc": False},
        ],
        lookup_fields=("code",),
    )


def seed_attendance_status():
    _bulk_get_or_create(
        AttendanceStatus,
        [
            {"code": "PRESENT", "name": "Present", "is_paid": True, "is_present_equivalent": True, "sort_order": 1},
            {"code": "ABSENT", "name": "Absent", "is_paid": False, "is_present_equivalent": False, "sort_order": 2},
            {"code": "HALF_DAY", "name": "Half Day", "is_paid": True, "is_present_equivalent": True, "sort_order": 3},
        ],
        lookup_fields=("code",),
    )


def seed_employee_filter():
    company = Company.objects.first()
    _bulk_get_or_create(
        EmployeeFilter,
        [
            {"company_id": company.id if company else None, "code": "ALL_EMPLOYEES", "name": "All Employees", "filter_type": EmployeeFilter.FilterType.STATIC, "description": "All employees in the company", "is_system": True, "member_count": 0},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_bulletin_category():
    company = Company.objects.first()
    _bulk_get_or_create(
        BulletinCategory,
        [
            {"company_id": company.id if company else None, "code": "GENERAL", "name": "General", "context_type": BulletinCategory.ContextType.ALL},
            {"company_id": company.id if company else None, "code": "HR", "name": "HR Bulletin", "context_type": BulletinCategory.ContextType.POLICY},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_policy_category():
    company = Company.objects.first()
    _bulk_get_or_create(
        PolicyCategory,
        [
            {"company_id": company.id if company else None, "code": "HR", "name": "HR Policies", "sort_order": 1},
            {"company_id": company.id if company else None, "code": "COMPLIANCE", "name": "Compliance Policies", "sort_order": 2},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_form_category():
    company = Company.objects.first()
    _bulk_get_or_create(
        FormCategory,
        [
            {"company_id": company.id if company else None, "code": "ONBOARD", "name": "Onboarding Forms"},
            {"company_id": company.id if company else None, "code": "EXIT", "name": "Exit Forms"},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_import_type():
    _bulk_get_or_create(
        ImportType,
        [
            {"code": "EMPLOYEE_UPLOAD", "name": "Employee Upload", "module_category": "EMPLOYEE", "template_schema": {}, "sort_order": 1},
        ],
        lookup_fields=("code",),
    )


def seed_letter_approval_type():
    _bulk_get_or_create(
        LetterApprovalType,
        [
            {"code": "NO_APPROVAL", "name": "No Approval", "requires_digital_signature": False, "requires_approver": False},
            {"code": "APPROVAL_REQUIRED", "name": "Approval Required", "requires_digital_signature": False, "requires_approver": True},
        ],
        lookup_fields=("code",),
    )


def seed_clearance_item_type():
    department = Department.objects.first()
    company = Company.objects.first()
    _bulk_get_or_create(
        ClearanceItemType,
        [
            {"company_id": company.id if company else None, "code": "IT", "name": "IT Clearance", "responsible_department_id": department.id if department else None, "sort_order": 1},
            {"company_id": company.id if company else None, "code": "HR", "name": "HR Clearance", "responsible_department_id": department.id if department else None, "sort_order": 2},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_position_change_reason():
    _bulk_get_or_create(
        PositionChangeReason,
        [
            {"code": "PROMOTION", "name": "Promotion", "change_type": PositionChangeReason.ChangeType.PROMOTION},
            {"code": "TRANSFER", "name": "Transfer", "change_type": PositionChangeReason.ChangeType.TRANSFER},
        ],
        lookup_fields=("code",),
    )


def seed_counter_party():
    company = Company.objects.first()
    _bulk_get_or_create(
        CounterParty,
        [
            {"company_id": company.id if company else None, "code": "CLIENT_A", "name": "Client A", "counter_party_type": CounterParty.CounterPartyType.CLIENT},
            {"company_id": company.id if company else None, "code": "VENDOR_X", "name": "Vendor X", "counter_party_type": CounterParty.CounterPartyType.VENDOR},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_authorized_signatory():
    employee = Employee.objects.first()
    company = Company.objects.first()
    _bulk_get_or_create(
        AuthorizedSignatory,
        [
            {"company_id": company.id if company else None, "signatory_name": "Amit Sharma", "signatory_title": "HR Head", "employee_id": employee.id if employee else None},
        ],
        lookup_fields=("company_id", "signatory_name"),
    )


# def seed_attendance_policy():
#     company = Company.objects.first()
#     if not company:
#         return
#     _bulk_get_or_create(
#         AttendancePolicy,
#         [
#             {
#                 "company": company,
#                 "name": "Standard Attendance Policy",
#                 "version": 1,
#                 "is_current": True,
#                 "late_login_cycle_limit": 3,
#                 "late_login_grace_mins": 15,
#                 "late_login_max_grace_mins": 30,
#                 "early_exit_max_grace_mins": 15,
#                 "short_leave_max_mins": 120,
#                 "monthly_grace_instance_limit": 4,
#                 "half_day_min_work_mins": 240,
#                 "half_day_min_mins": 240,
#                 "half_day_max_mins": 360,
#                 "full_day_min_mins": 480,
#                 "lop_deduction_unit": "0.50",
#                 "ot_enabled": True,
#                 "ot_min_mins": 30,
#                 "max_regularizations_month": 3,
#             }
#         ],
#         lookup_fields=("company", "name", "version"),
#     )


# def seed_regularization_reason():
#     company = Company.objects.first()
#     if not company:
#         return
#     _bulk_get_or_create(
#         RegularizationReason,
#         [
#             {"company_id": company.id, "code": "WFO_ISSUE", "name": "Work From Office Issue"},
#             {"company_id": company.id, "code": "TRANSPORT", "name": "Transport Issue"},
#         ],
#         lookup_fields=("company_id", "code"),
#     )


# def seed_overtime_policy():
#     company = Company.objects.first()
#     _bulk_get_or_create(
#         OvertimePolicy,
#         [
#             {"company_id": company.id if company else None, "code": "STANDARD", "ot_multiplier": "1.50", "min_ot_minutes": 30},
#         ],
#         lookup_fields=("company_id", "code"),
#     )


# def seed_comp_off_policy():
#     company = Company.objects.first()
#     _bulk_get_or_create(
#         CompOffPolicy,
#         [
#             {"company_id": company.id if company else None, "code": "STANDARD", "min_hours_for_full_day": "8.00", "expiry_days": 90},
#         ],
#         lookup_fields=("company_id", "code"),
#     )


def seed_pay_component_group():
    company = Company.objects.first()
    _bulk_get_or_create(
        PayComponentGroup,
        [
            {"company_id": company.id if company else None, "code": "EARNING", "name": "Earning", "is_earning": True},
            {"company_id": company.id if company else None, "code": "DEDUCTION", "name": "Deduction", "is_earning": False},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_pay_component():
    company = Company.objects.first()
    pay_group = PayComponentGroup.objects.filter(code="EARNING").first()
    _bulk_get_or_create(
        PayComponent,
        [
            {
                "company_id": company.id if company else None,
                "component_group_id": pay_group.id if pay_group else None,
                "code": "BASIC",
                "name": "Basic Salary",
                "component_type": PayComponent.ComponentType.FIXED,
                "is_taxable": True,
                "formula_type": PayComponent.FormulaType.FIXED_AMOUNT,
                "formula_value": "30000",
                "sort_order": 1,
            }
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_salary_structure():
    company = Company.objects.first()
    band = Band.objects.filter(code="B1").first()
    grade = Grade.objects.filter(code="G1").first()
    _bulk_get_or_create(
        SalaryStructure,
        [
            {
                "company_id": company.id if company else None,
                "code": "STRUC_STANDARD",
                "name": "Standard Salary Structure",
                "grade_id": grade.id if grade else None,
                "band_id": band.id if band else None,
                "min_ctc": "300000",
                "max_ctc": "600000",
                "effective_from": date(date.today().year, 1, 1),
            }
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_salary_structure_component():
    salary_structure = SalaryStructure.objects.filter(code="STRUC_STANDARD").first()
    pay_component = PayComponent.objects.filter(code="BASIC").first()
    if not salary_structure or not pay_component:
        return
    _bulk_get_or_create(
        SalaryStructureComponent,
        [
            {
                "salary_structure_id": salary_structure.id,
                "pay_component_id": pay_component.id,
                "calculation_order": 1,
                "is_mandatory": True,
            }
        ],
        lookup_fields=("salary_structure_id", "pay_component_id"),
    )


def seed_reimbursement_type():
    company = Company.objects.first()
    _bulk_get_or_create(
        ReimbursementType,
        [
            {"company_id": company.id if company else None, "code": "TRAVEL", "name": "Travel Reimbursement", "taxable": False},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_loan_type():
    company = Company.objects.first()
    _bulk_get_or_create(
        LoanType,
        [
            {"company_id": company.id if company else None, "code": "SALARY_ADVANCE", "name": "Salary Advance", "default_interest_rate": "0.00"},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_payroll_cycle():
    company = Company.objects.first()
    _bulk_get_or_create(
        PayrollCycle,
        [
            {"company_id": company.id if company else None, "code": "MONTHLY", "name": "Monthly", "frequency": PayrollCycle.CycleFrequency.MONTHLY, "pay_date_day": 25, "cut_off_day": 20},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_tax_regime():
    _bulk_get_or_create(
        TaxRegime,
        [
            {"code": "OLD_2025", "name": "Old Regime 2025", "financial_year": "2025-26", "standard_deduction": "50000"},
            {"code": "NEW_2025", "name": "New Regime 2025", "financial_year": "2025-26", "standard_deduction": "50000"},
        ],
        lookup_fields=("code",),
    )


def seed_tds_section():
    _bulk_get_or_create(
        TdsSection,
        [
            {"section_code": "80C", "description": "Section 80C Deductions", "category": "TAX"},
            {"section_code": "80D", "description": "Section 80D Medical Insurance", "category": "TAX"},
        ],
        lookup_fields=("section_code",),
    )


def seed_arrear_type():
    company = Company.objects.first()
    _bulk_get_or_create(
        ArrearType,
        [
            {"company_id": company.id if company else None, "code": "SALARY_REVISION", "name": "Salary Revision"},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_statutory_component():
    _bulk_get_or_create(
        StatutoryComponent,
        [
            {"code": "PF", "name": "Provident Fund", "is_employee_contribution": True, "is_employer_contribution": True},
            {"code": "ESI", "name": "Employee State Insurance", "is_employee_contribution": True, "is_employer_contribution": True},
        ],
        lookup_fields=("code",),
    )


def seed_pf_scheme():
    _bulk_get_or_create(
        PfScheme,
        [
            {"code": "EPF", "name": "EPF", "employee_rate": "12.00", "employer_rate": "12.00", "wage_ceiling": "15000"},
        ],
        lookup_fields=("code",),
    )


def seed_esi_scheme():
    _bulk_get_or_create(
        EsiScheme,
        [
            {"code": "ESI_BASIC", "employee_rate": "0.75", "employer_rate": "3.25", "wage_ceiling": "21000"},
        ],
        lookup_fields=("code",),
    )


def seed_pt_state_slab():
    state = State.objects.filter(code="DL").first()
    _bulk_get_or_create(
        PtStateSlab,
        [
            {"state_id": state.id if state else None, "income_from": "0", "income_to": "250000", "annual_tax": "0", "financial_year": "2025-26"},
        ],
        lookup_fields=("state_id", "financial_year"),
    )


def seed_lwf_slab():
    state = State.objects.filter(code="DL").first()
    _bulk_get_or_create(
        LwfSlab,
        [
            {"state_id": state.id if state else None, "employee_contribution": "10.00", "employer_contribution": "20.00", "frequency": LwfSlab.LwfFrequency.MONTHLY},
        ],
        lookup_fields=("state_id", "frequency"),
    )


def seed_labour_register_type():
    _bulk_get_or_create(
        LabourRegisterType,
        [
            {"code": "MUSTER_ROLL", "name": "Muster Roll", "statutory_form_ref": "Form D"},
            {"code": "WAGE_REGISTER", "name": "Wage Register", "statutory_form_ref": "Form VII"},
        ],
        lookup_fields=("code",),
    )


def seed_job_function():
    _bulk_get_or_create(
        JobFunction,
        [
            {"code": "ENG", "name": "Engineering"},
            {"code": "HR", "name": "Human Resources"},
        ],
        lookup_fields=("code",),
    )


def seed_job_level():
    _bulk_get_or_create(
        JobLevel,
        [
            {"code": "JR", "name": "Junior", "sort_order": 1},
            {"code": "SR", "name": "Senior", "sort_order": 2},
            {"code": "MGR", "name": "Manager", "sort_order": 3},
        ],
        lookup_fields=("code",),
    )


def seed_interview_round():
    _bulk_get_or_create(
        InterviewRound,
        [
            {"code": "SCREENING", "name": "Screening", "sort_order": 1},
            {"code": "TECHNICAL", "name": "Technical", "sort_order": 2},
        ],
        lookup_fields=("code",),
    )


def seed_candidate_source():
    _bulk_get_or_create(
        CandidateSource,
        [
            {"code": "REFERRAL", "name": "Referral", "source_category": CandidateSource.SourceCategory.REFERRAL},
            {"code": "LINKEDIN", "name": "LinkedIn", "source_category": CandidateSource.SourceCategory.ACTIVE},
        ],
        lookup_fields=("code",),
    )


def seed_offer_status():
    _bulk_get_or_create(
        OfferStatus,
        [
            {"code": "DRAFT", "name": "Draft", "is_terminal": False},
            {"code": "ACCEPTED", "name": "Accepted", "is_terminal": True},
        ],
        lookup_fields=("code",),
    )


def seed_rejection_reason():
    company = Company.objects.first()
    _bulk_get_or_create(
        RejectionReason,
        [
            {"company_id": company.id if company else None, "code": "SKILLS", "name": "Lack of Skills", "rejection_stage": "INTERVIEW"},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_pipeline_stage():
    company = Company.objects.first()
    _bulk_get_or_create(
        PipelineStage,
        [
            {"company_id": company.id if company else None, "code": "SCREENING", "name": "Screening", "sort_order": 1, "is_terminal": False},
            {"company_id": company.id if company else None, "code": "OFFER", "name": "Offer", "sort_order": 4, "is_terminal": False},
            {"company_id": company.id if company else None, "code": "JOINED", "name": "Joined", "sort_order": 5, "is_terminal": True},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_appraisal_cycle():
    _bulk_get_or_create(
        AppraisalCycle,
        [
            {"code": "ANNUAL", "name": "Annual"},
            {"code": "QUARTERLY", "name": "Quarterly"},
        ],
        lookup_fields=("code",),
    )


def seed_rating_scale():
    company = Company.objects.first()
    _bulk_get_or_create(
        RatingScale,
        [
            {"company_id": company.id if company else None, "code": "SCALE_5", "min_value": 1, "max_value": 5, "rating_labels": {"1": "Poor", "5": "Excellent"}},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_goal_category():
    _bulk_get_or_create(
        GoalCategory,
        [
            {"code": "BUSINESS", "name": "Business"},
            {"code": "BEHAVIORAL", "name": "Behavioral"},
        ],
        lookup_fields=("code",),
    )


def seed_kpi_library():
    company = Company.objects.first()
    goal_category = GoalCategory.objects.filter(code="BUSINESS").first()
    _bulk_get_or_create(
        KpiLibrary,
        [
            {"company_id": company.id if company else None, "code": "SALES_GROWTH", "name": "Sales Growth", "unit_of_measure": "%", "goal_category_id": goal_category.id if goal_category else None},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_kra_library():
    company = Company.objects.first()
    goal_category = GoalCategory.objects.filter(code="BUSINESS").first()
    _bulk_get_or_create(
        KraLibrary,
        [
            {"company_id": company.id if company else None, "code": "REVENUE", "name": "Revenue Growth", "goal_category_id": goal_category.id if goal_category else None, "weightage": "50.00"},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_competency_group():
    company = Company.objects.first()
    _bulk_get_or_create(
        CompetencyGroup,
        [
            {"company_id": company.id if company else None, "code": "TECH", "name": "Technical Competency", "sort_order": 1},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_competency():
    company = Company.objects.first()
    competency_group = CompetencyGroup.objects.filter(code="TECH").first()
    rating_scale = RatingScale.objects.filter(code="SCALE_5").first()
    _bulk_get_or_create(
        Competency,
        [
            {"company_id": company.id if company else None, "code": "CODE_QUALITY", "name": "Code Quality", "competency_group_id": competency_group.id if competency_group else None, "rating_scale_id": rating_scale.id if rating_scale else None},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_training_category():
    _bulk_get_or_create(
        TrainingCategory,
        [
            {"code": "TECHNICAL", "name": "Technical Training"},
            {"code": "SOFT_SKILLS", "name": "Soft Skills"},
        ],
        lookup_fields=("code",),
    )


def seed_training_mode():
    _bulk_get_or_create(
        TrainingMode,
        [
            {"code": "ONLINE", "name": "Online", "requires_venue": False},
            {"code": "CLASSROOM", "name": "Classroom", "requires_venue": True},
        ],
        lookup_fields=("code",),
    )


def seed_course():
    company = Company.objects.first()
    training_category = TrainingCategory.objects.filter(code="TECHNICAL").first()
    _bulk_get_or_create(
        Course,
        [
            {"company_id": company.id if company else None, "code": "PYTHON101", "name": "Python Basics", "training_category_id": training_category.id if training_category else None, "duration_hours": "24.00", "provider": "Training Institute"},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_certification_body():
    _bulk_get_or_create(
        CertificationBody,
        [
            {"code": "NASSCOM", "name": "NASSCOM"},
        ],
        lookup_fields=("code",),
    )


def seed_asset_category():
    _bulk_get_or_create(
        AssetCategory,
        [
            {"code": "IT", "name": "IT"},
            {"code": "VEHICLE", "name": "Vehicle"},
        ],
        lookup_fields=("code",),
    )


def seed_asset_condition():
    _bulk_get_or_create(
        AssetCondition,
        [
            {"code": "NEW", "name": "New"},
            {"code": "GOOD", "name": "Good"},
        ],
        lookup_fields=("code",),
    )


def seed_asset_type():
    category = AssetCategory.objects.filter(code="IT").first()
    _bulk_get_or_create(
        AssetType,
        [
            {"asset_category_id": category.id if category else None, "code": "LAPTOP", "name": "Laptop", "requires_serial_no": True},
        ],
        lookup_fields=("code",),
    )


def seed_vendor():
    company = Company.objects.first()
    _bulk_get_or_create(
        Vendor,
        [
            {"company_id": company.id if company else None, "code": "VENDOR_IT", "name": "IT Vendor", "vendor_type": Vendor.VendorType.SERVICE},
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_workflow_type():
    _bulk_get_or_create(
        WorkflowType,
        [
            {"code": "LEAVE", "name": "Leave Workflow", "module": "LEAVE"},
            {"code": "PAYROLL", "name": "Payroll Workflow", "module": "PAYROLL"},
        ],
        lookup_fields=("code",),
    )


def seed_approval_action():
    _bulk_get_or_create(
        ApprovalAction,
        [
            {"code": "APPROVE", "name": "Approve", "is_positive": True},
            {"code": "REJECT", "name": "Reject", "is_positive": False},
        ],
        lookup_fields=("code",),
    )


def seed_escalation_type():
    _bulk_get_or_create(
        EscalationType,
        [
            {"code": "TIME_BASED", "name": "Time Based"},
            {"code": "NO_RESPONSE", "name": "No Response"},
        ],
        lookup_fields=("code",),
    )


def seed_audit_event_type():
    _bulk_get_or_create(
        AuditEventType,
        [
            {"code": "LOGIN", "name": "Login", "severity": AuditEventType.Severity.INFO},
            {"code": "UPDATE", "name": "Update", "severity": AuditEventType.Severity.INFO},
        ],
        lookup_fields=("code",),
    )


# def seed_permission():
#     _bulk_get_or_create(
#         Permission,
#         [
#             {"module": "EMPLOYEE", "action": "VIEW", "resource": "EMPLOYEE_RECORD", "permission_code": "EMPLOYEE.VIEW.RECORD", "description": "View employee records."},
#         ],
#         lookup_fields=("permission_code",),
#     )


# def seed_menu_item():
#     _bulk_get_or_create(
#         MenuItem,
#         [
#             {"code": "EMPLOYEE.DASHBOARD", "name": "Employee Dashboard", "module": "EMPLOYEE", "route_path": "/employee/dashboard", "sort_order": 1},
#         ],
#         lookup_fields=("code",),
#     )


# def seed_data_scope_type():
#     _bulk_get_or_create(
#         DataScopeType,
#         [
#             {"code": "ALL", "name": "All Records"},
#             {"code": "SELF", "name": "Self Records"},
#         ],
#         lookup_fields=("code",),
#     )


def seed_password_policy():
    company = Company.objects.first()
    _bulk_get_or_create(
        PasswordPolicy,
        [
            {"company_id": company.id if company else None, "min_length": 8, "max_length": 50, "require_uppercase": True, "require_digits": True, "require_special": True, "expiry_days": 90, "history_count": 5, "max_login_attempts": 5},
        ],
        lookup_fields=("company_id",),
    )


def seed_session_policy():
    company = Company.objects.first()
    _bulk_get_or_create(
        SessionPolicy,
        [
            {"company_id": company.id if company else None, "max_sessions": 3, "idle_timeout_minutes": 30, "absolute_timeout_hours": 8},
        ],
        lookup_fields=("company_id",),
    )


def seed_notification_channel():
    _bulk_get_or_create(
        NotificationChannel,
        [
            {"code": "EMAIL", "name": "Email", "config_keys": {"smtp_server": "string"}},
        ],
        lookup_fields=("code",),
    )


def seed_notification_template():
    channel = NotificationChannel.objects.filter(code="EMAIL").first()
    company = Company.objects.first()
    _bulk_get_or_create(
        NotificationTemplate,
        [
            {
                "company_id": company.id if company else None,
                "code": "LEAVE_APPROVED",
                "name": "Leave Approved Template",
                "channel_id": channel.id if channel else None,
                "subject_template": "Your leave has been approved",
                "body_template": "Hello {{employee_name}}, your leave request is approved.",
            }
        ],
        lookup_fields=("company_id", "code"),
    )


def seed_notification_trigger():
    template = NotificationTemplate.objects.filter(code="LEAVE_APPROVED").first()
    _bulk_get_or_create(
        NotificationTrigger,
        [
            {
                "trigger_event": "LEAVE.APPROVED",
                "notification_template_id": template.id if template else None,
                "recipient_type": NotificationTrigger.RecipientType.EMPLOYEE,
            }
        ],
        lookup_fields=("trigger_event", "notification_template_id", "recipient_type"),
    )


def seed_employee_lifecycle():
    if EmployeeLifecycle.objects.exists():
        print("✓ Employee Lifecycle data already exists, skipping...")
        return

    for employee in Employee.objects.all():
        EmployeeLifecycle.objects.create(
            employee=employee,
            date_of_joining=employee.date_of_joining or date.today(),
            reporting_date=employee.date_of_joining or date.today(),
        )
    print(f"✓ Created {EmployeeLifecycle.objects.count()} employee lifecycle records")


# def seed_employee_role_assignments():
#     if EmployeeRoleAssignment.objects.exists():
#         print("✓ Employee Role Assignment data already exists, skipping...")
#         return

#     employee = Employee.objects.first()
#     role = SystemRole.objects.filter(code="EMPLOYEE").first()
#     if employee and role:
#         EmployeeRoleAssignment.objects.create(
#             employee=employee,
#             role=role,
#             company=employee.company,
#             department=employee.employmentdetails.department if hasattr(employee, "employmentdetails") else None,
#             assigned_by=employee,
#             effective_from=employee.date_of_joining or date.today(),
#         )
#         print("✓ Created 1 Employee Role Assignment record")


def seed_employee_auth():
    if EmployeeAuth.objects.exists():
        print("✓ Employee Auth data already exists, skipping...")
        return

    for employee in Employee.objects.all():
        EmployeeAuth.objects.create(
            employee=employee,
            password_hash="pbkdf2_sha256$260000$placeholder$hash",
            mfa_type=EmployeeAuth.MFAType.NONE,
        )
    print(f"✓ Created {EmployeeAuth.objects.count()} employee auth records")


def seed_employee_verification_tokens():
    if EmployeeVerificationToken.objects.exists():
        print("✓ Employee Verification Token data already exists, skipping...")
        return

    for employee in Employee.objects.all():
        EmployeeVerificationToken.objects.create(
            employee=employee,
            token_hash=uuid.uuid4().hex,
            token_type=EmployeeVerificationToken.TokenType.EMAIL_VERIFY,
            expires_at=datetime.now() + timedelta(days=1),
        )
    print(f"✓ Created {EmployeeVerificationToken.objects.count()} verification token records")


def seed_login_history():
    if LoginHistory.objects.exists():
        print("✓ Login History data already exists, skipping...")
        return

    for employee in Employee.objects.all():
        LoginHistory.objects.create(
            employee=employee,
            session_id=uuid.uuid4(),
            ip_address="127.0.0.1",
            login_status=LoginHistory.LoginStatus.SUCCESS,
            device_type=LoginHistory.DeviceType.WEB,
        )
    print(f"✓ Created {LoginHistory.objects.count()} login history records")


def seed_employee_nominees():
    if EmployeeNominee.objects.exists():
        print("✓ Employee Nominee data already exists, skipping...")
        return

    employee = Employee.objects.first()
    relation = Relation.objects.filter(code="SPOUSE").first()
    nominee_purpose = NomineePurpose.objects.first()
    family_member = EmployeeFamilyMember.objects.filter(employee=employee).first()
    if employee and relation and nominee_purpose:
        EmployeeNominee.objects.create(
            employee=employee,
            nominee_purpose=nominee_purpose,
            family_member=family_member,
            first_name="Anita",
            relation=relation,
            nominee_percentage=100,
        )
        print("✓ Created 1 Employee Nominee record")


def seed_employee_documents():
    if EmployeeDocument.objects.exists():
        print("✓ Employee Document data already exists, skipping...")
        return

    employee = Employee.objects.first()
    doc_type = DocumentType.objects.filter(code="PAN").first()
    doc_side = DocumentSide.objects.filter(code="FULL").first()
    country = Country.objects.filter(code="IN").first()
    if employee and doc_type:
        EmployeeDocument.objects.create(
            employee=employee,
            document_type=doc_type,
            document_side=doc_side,
            document_number="ABCDE1234F",
            document_name="PAN Card",
            issue_date=date(2018, 1, 1),
            expiry_date=date(2028, 1, 1),
            issuing_country=country,
            file_url="https://example.com/pan.pdf",
            file_name="pan.pdf",
            file_size_bytes=1024,
            mime_type="application/pdf",
            is_primary=True,
        )
        print("✓ Created 1 Employee Document record")


def seed_employee_bank_accounts():
    if EmployeeBankAccount.objects.exists():
        print("✓ Employee Bank Account data already exists, skipping...")
        return

    employee = Employee.objects.first()
    bank = Bank.objects.first()
    account_type = AccountType.objects.filter(code="SAVINGS").first()
    bank_status = BankStatus.objects.filter(code="ACTIVE").first()
    if employee and bank and account_type:
        EmployeeBankAccount.objects.create(
            employee=employee,
            bank=bank,
            account_type=account_type,
            account_number="123456789012",
            ifsc_code="ICIC0000001",
            branch_name="Corporate Branch",
            account_holder_name=f"{employee.first_name} {employee.last_name}",
            bank_status=bank_status,
            is_primary=True,
            is_verified=True,
        )
        print("✓ Created 1 Employee Bank Account record")


def seed_employee_statutory_ids():
    if EmployeeStatutoryIds.objects.exists():
        print("✓ Employee Statutory IDs data already exists, skipping...")
        return

    employee = Employee.objects.first()
    if employee:
        EmployeeStatutoryIds.objects.create(
            employee=employee,
            pan="ABCDE1234F",
            pan_verified=True,
            aadhaar_no="123412341234",
            aadhaar_linked=True,
            uan="123456789012",
            pf_account_no="PF1234567890",
            pt_applicable=True,
        )
        print("✓ Created 1 Employee Statutory IDs record")


def seed_insurance_masters():
    """Create insurance master data required by employee insurance policies."""
    policy_types = [
        {
            "code": "HEALTH",
            "label": "Health",
            "description": "Health insurance policy",
        },
        {
            "code": "LIFE",
            "label": "Life",
            "description": "Life insurance policy",
        },
        {
            "code": "GPA",
            "label": "Group Personal Accident",
            "description": "Group personal accident policy",
        },
    ]
    for item in policy_types:
        PolicyType.objects.update_or_create(
            code=item["code"],
            defaults={**item, "is_active": True},
        )

    insurance_types = [
        {
            "code": "GROUP",
            "label": "Group",
            "description": "Employer group policy",
            "is_group_policy": True,
        },
        {
            "code": "INDIVIDUAL",
            "label": "Individual",
            "description": "Individual policy",
            "is_group_policy": False,
        },
    ]
    for item in insurance_types:
        InsuranceType.objects.update_or_create(
            code=item["code"],
            defaults={**item, "is_active": True},
        )

    cover_types = [
        {
            "code": "SELF",
            "label": "Self",
            "description": "Employee only",
            "is_family_based": False,
        },
        {
            "code": "SELF_SPOUSE",
            "label": "Self + Spouse",
            "description": "Employee and spouse",
            "is_family_based": True,
        },
        {
            "code": "FAMILY",
            "label": "Family Floater",
            "description": "Employee and dependent family members",
            "is_family_based": True,
        },
    ]
    for item in cover_types:
        CoverType.objects.update_or_create(
            code=item["code"],
            defaults={**item, "is_active": True},
        )

    premium_frequencies = [
        {"code": "MONTHLY", "label": "Monthly", "months_interval": 1},
        {"code": "QUARTERLY", "label": "Quarterly", "months_interval": 3},
        {"code": "ANNUAL", "label": "Annual", "months_interval": 12},
    ]
    for item in premium_frequencies:
        PremiumFrequency.objects.update_or_create(
            code=item["code"],
            defaults={**item, "is_active": True},
        )

    companies = [
        {
            "code": "STAR_HEALTH",
            "label": "Star Health",
            "description": "Star Health and Allied Insurance",
        },
        {
            "code": "HDFC_ERGO",
            "label": "HDFC ERGO",
            "description": "HDFC ERGO General Insurance",
        },
        {
            "code": "ICICI_LOMBARD",
            "label": "ICICI Lombard",
            "description": "ICICI Lombard General Insurance",
        },
    ]
    for item in companies:
        InsuranceCompany.objects.update_or_create(
            code=item["code"],
            defaults={**item, "is_active": True},
        )

    print("Insurance master data ready")


def seed_employee_insurance_policies():
    if EmployeeInsurancePolicy.objects.exists():
        print("✓ Employee Insurance Policies data already exists, skipping...")
        return

    employee = Employee.objects.first()
    policy_type = PolicyType.objects.first()
    insurance_type = InsuranceType.objects.filter(code="GROUP").first() or InsuranceType.objects.first()
    insurance_company = InsuranceCompany.objects.first()
    premium_frequency = PremiumFrequency.objects.filter(code="MONTHLY").first()
    family_member = EmployeeFamilyMember.objects.filter(employee=employee).first()
    if employee and policy_type and insurance_company:
        EmployeeInsurancePolicy.objects.create(
            employee=employee,
            policy_type=policy_type,
            insurance_type=insurance_type,
            insurance_company=insurance_company,
            cover_type=CoverType.objects.filter(code="SELF").first(),
            policy_number="POLICY12345",
            sum_insured="500000",
            premium_amount="5000",
            premium_frequency=premium_frequency,
            start_date=date.today(),
            end_date=date(date.today().year + 1, date.today().month, date.today().day),
            nominee_family_member=family_member,
            company=employee.company,
        )
        print("✓ Created 1 Employee Insurance Policy record")


def seed_employee_language_proficiencies():
    if EmployeeLanguageProficiency.objects.exists():
        print("✓ Employee Language Proficiency data already exists, skipping...")
        return

    employee = Employee.objects.first()
    language = Language.objects.first()
    proficiency = LanguageProficiency.objects.first()
    if employee and language:
        EmployeeLanguageProficiency.objects.create(
            employee=employee,
            language=language,
            read_proficiency=proficiency,
            write_proficiency=proficiency,
            speak_proficiency=proficiency,
            is_mother_tongue=True,
        )
        print("✓ Created 1 Employee Language Proficiency record")


def seed_employee_communication_preferences():
    if EmployeeCommunicationPreference.objects.exists():
        print("✓ Employee Communication Preferences data already exists, skipping...")
        return

    employee = Employee.objects.first()
    channel = CommunicationChannel.objects.filter(code="EMAIL").first()
    if employee and channel:
        EmployeeCommunicationPreference.objects.create(
            employee=employee,
            task_code="WELCOME_EMAIL",
            channel=channel,
            is_enabled=True,
        )
        print("✓ Created 1 Employee Communication Preference record")


def seed_employee_localization():
    if EmployeeLocalization.objects.exists():
        print("✓ Employee Localization data already exists, skipping...")
        return

    employee = Employee.objects.first()
    language = Language.objects.first()
    if employee and language:
        EmployeeLocalization.objects.create(
            employee=employee,
            language=language,
            timezone="Asia/Kolkata",
            date_format="DD/MM/YYYY",
            time_format=EmployeeLocalization.TimeFormat.H24,
            number_format=EmployeeLocalization.NumberFormat.IN,
            currency_display="INR",
        )
        print("✓ Created 1 Employee Localization record")


def seed_employee_access_cards():
    if EmployeeAccessCard.objects.exists():
        print("✓ Employee Access Cards data already exists, skipping...")
        return

    employee = Employee.objects.first()
    location = OfficeLocation.objects.first()
    floor = Floor.objects.first()
    if employee and location:
        EmployeeAccessCard.objects.create(
            employee=employee,
            card_number="CARD001",
            barcode="BARCODE001",
            office_location=location,
            floor=floor,
            issued_date=date.today(),
            card_status=EmployeeAccessCard.CardStatus.ACTIVE,
        )
        print("✓ Created 1 Employee Access Card record")


def seed_employee_reporting_relationships():
    if EmployeeReportingRelationship.objects.exists():
        print("✓ Employee Reporting Relationships data already exists, skipping...")
        return

    employees = list(Employee.objects.all()[:2])
    department = Department.objects.first()
    if len(employees) >= 2 and department:
        EmployeeReportingRelationship.objects.create(
            employee=employees[1],
            reports_to_employee=employees[0],
            relationship_type=EmployeeReportingRelationship.RelationshipType.PRIMARY,
            effective_from=employees[1].date_of_joining or date.today(),
            department=department,
            company=employees[1].company,
        )
        print("✓ Created 1 Employee Reporting Relationship record")


def seed_employee_audit_logs():
    if EmployeeAuditLog.objects.exists():
        print("✓ Employee Audit Log data already exists, skipping...")
        return

    employee = Employee.objects.first()
    if employee:
        EmployeeAuditLog.objects.create(
            employee=employee,
            table_name="employees_employee",
            record_id=employee.id,
            operation=EmployeeAuditLog.Operation.INSERT,
            changed_by=employee,
            old_values=None,
            new_values={"employee_code": employee.employee_code},
            changed_columns=["employee_code"],
            ip_address="127.0.0.1",
        )
        print("✓ Created 1 Employee Audit Log record")


def seed_employee_deputation_locations():
    if EmployeeDeputationLocation.objects.exists():
        print("✓ Employee Deputation Location data already exists, skipping...")
        return

    employee = Employee.objects.first()
    location = OfficeLocation.objects.first()
    if employee and location:
        EmployeeDeputationLocation.objects.create(
            employee=employee,
            from_location=location,
            to_location=location,
            deputation_type=EmployeeDeputationLocation.DeputationType.TEMPORARY,
            effective_from=date.today(),
            effective_to=date.today() + timedelta(days=90),
            company=employee.company,
            status=EmployeeDeputationLocation.DeputationStatus.ACTIVE,
        )
        print("✓ Created 1 Employee Deputation Location record")


def seed_employee_code_sequences():
    if EmployeeCodeSequence.objects.exists():
        print("✓ Employee Code Sequence data already exists, skipping...")
        return

    employee_type = EmployeeType.objects.filter(code="PERMANENT").first()
    EmployeeCodeSequence.objects.create(
        company=Company.objects.first(),
        employee_type=employee_type,
        prefix="EMP",
        separator="-",
        padding_length=4,
        last_sequence_no=1,
        reset_frequency=EmployeeCodeSequence.ResetFrequency.YEARLY,
        last_reset_at=date.today(),
    )
    print("✓ Created 1 Employee Code Sequence record")


# ═════════════════════════════════════════════════════════════════════════════
# TRANSACTION DATA - EMPLOYEE & RELATED
# ═════════════════════════════════════════════════════════════════════════════

# def seed_employees():
#     """Create sample employee records."""
#     if Employee.objects.exists():
#         print("✓ Employee data already exists, skipping...")
#         return
    
#     company = Company.objects.first()
#     gender_male = Gender.objects.get(code="M")
#     gender_female = Gender.objects.get(code="F")
    
#     employees_data = [
#         {
#             "user": None,
#             "employee_code": "EMP001",
#             "company": company,
#             "first_name": "Rajesh",
#             "last_name": "Kumar",
#             "date_of_joining": date(2020, 1, 15),
#             "date_of_birth": date(1990, 5, 20),
#             "gender": gender_male,
#             "status": Employee.StatusChoices.ACTIVE,
#         },
#         {
#             "user": None,
#             "employee_code": "EMP002",
#             "company": company,
#             "first_name": "Priya",
#             "last_name": "Singh",
#             "date_of_joining": date(2021, 3, 10),
#             "date_of_birth": date(1992, 8, 15),
#             "gender": gender_female,
#             "status": Employee.StatusChoices.ACTIVE,
#         },
#         {
#             "user": None,
#             "employee_code": "EMP003",
#             "company": company,
#             "first_name": "Amit",
#             "last_name": "Patel",
#             "date_of_joining": date(2022, 6, 1),
#             "date_of_birth": date(1995, 11, 30),
#             "gender": gender_male,
#             "status": Employee.StatusChoices.ACTIVE,
#         },
#     ]
    
#     for emp_data in employees_data:
#         Employee.objects.create(**emp_data)
#     print(f"✓ Created {len(employees_data)} employee records")
from datetime import date

from apps.accounts.models import User

from apps.employees.models import (
    Employee,
    Company,
    Gender,
)


def seed_employees():
    """Create sample employee records with users."""

    # if Employee.objects.exists():
    #     print("✓ Employee data already exists, skipping...")
    #     return

    company = Company.objects.first()

    gender_male = Gender.objects.get(code="M")
    gender_female = Gender.objects.get(code="F")

    employees_data = [
        {
            "email": "rajesh.kumar@acme.com",
            "username": "rajesh",
            "password": "Password@123",

            "employee_code": "EMP001",
            "company": company,
            "first_name": "Rajesh",
            "last_name": "Kumar",
            "date_of_joining": date(2020, 1, 15),
            "date_of_birth": date(1990, 5, 20),
            "gender": gender_male,
            "status": Employee.StatusChoices.ACTIVE,
        },
        {
            "email": "priya.singh@acme.com",
            "username": "priya",
            "password": "Password@123",

            "employee_code": "EMP002",
            "company": company,
            "first_name": "Priya",
            "last_name": "Singh",
            "date_of_joining": date(2021, 3, 10),
            "date_of_birth": date(1992, 8, 15),
            "gender": gender_female,
            "status": Employee.StatusChoices.ACTIVE,
        },
        {
            "email": "amit.patel@acme.com",
            "username": "amit",
            "password": "Password@123",
            "employee_code": "EMP003",
            "company": company,
            "first_name": "Amit",
            "last_name": "Patel",
            "date_of_joining": date(2022, 6, 1),
            "date_of_birth": date(1995, 11, 30),
            "gender": gender_male,
            "status": Employee.StatusChoices.ACTIVE,
        },
        {
            "email": "amit.mehta@acme.com",
            "username": "amit.mehta",
            "password": "Password@123",
            "employee_code": "EMP004",
            "company": company,
            "first_name": "Amit",
            "last_name": "Mehta",
            "date_of_joining": date(2022, 6, 1),
            "date_of_birth": date(1995, 11, 30),
            "gender": gender_male,
            "status": Employee.StatusChoices.ACTIVE,
        },
        # -------------------------------------------------------------
        # SUPER ADMIN
        # -------------------------------------------------------------
        {
            "email": "admin@company.com",
            "username": "superadmin",
            "password": "Password@123",

            "employee_code": "EMP005",
            "company": company,
            "first_name": "System",
            "last_name": "Admin",
            "date_of_joining": date(2020, 1, 1),
            "date_of_birth": date(1988, 5, 10),
            "gender": gender_male,
            "status": Employee.StatusChoices.ACTIVE,
        },

        # -------------------------------------------------------------
        # HR ADMIN
        # -------------------------------------------------------------
        {
            "email": "hr.admin@company.com",
            "username": "hradmin",
            "password": "Password@123",

            "employee_code": "EMP006",
            "company": company,
            "first_name": "Priya",
            "last_name": "Sharma",
            "date_of_joining": date(2020, 3, 15),
            "date_of_birth": date(1990, 7, 22),
            "gender": gender_female,
            "status": Employee.StatusChoices.ACTIVE,
        },

        # -------------------------------------------------------------
        # HR MANAGER
        # -------------------------------------------------------------
        {
            "email": "hr.manager@company.com",
            "username": "hrmanager",
            "password": "Password@123",

            "employee_code": "EMP007",
            "company": company,
            "first_name": "Ankit",
            "last_name": "Verma",
            "date_of_joining": date(2021, 6, 10),
            "date_of_birth": date(1991, 2, 18),
            "gender": gender_male,
            "status": Employee.StatusChoices.ACTIVE,
        },

        # -------------------------------------------------------------
        # MANAGER
        # -------------------------------------------------------------
        {
            "email": "john.manager@company.com",
            "username": "johnmanager",
            "password": "Password@123",

            "employee_code": "EMP008",
            "company": company,
            "first_name": "John",
            "last_name": "Mathew",
            "date_of_joining": date(2021, 9, 5),
            "date_of_birth": date(1989, 11, 12),
            "gender": gender_male,
            "status": Employee.StatusChoices.ACTIVE,
        },

        # -------------------------------------------------------------
        # EMPLOYEE
        # -------------------------------------------------------------
        {
            "email": "jane.employee@company.com",
            "username": "janeemployee",
            "password": "Password@123",

            "employee_code": "EMP009",
            "company": company,
            "first_name": "Jane",
            "last_name": "Doe",
            "date_of_joining": date(2022, 1, 20),
            "date_of_birth": date(1995, 4, 8),
            "gender": gender_female,
            "status": Employee.StatusChoices.ACTIVE,
        },
        

        # -------------------------------------------------------------
        # RECRUITER
        # -------------------------------------------------------------
        {
            "email": "recruiter@company.com",
            "username": "recruiter",
            "password": "Password@123",

            "employee_code": "EMP010",
            "company": company,
            "first_name": "Neha",
            "last_name": "Kapoor",
            "date_of_joining": date(2022, 7, 1),
            "date_of_birth": date(1993, 9, 25),
            "gender": gender_female,
            "status": Employee.StatusChoices.ACTIVE,
        },
        
        # -------------------------------------------------------------
        # PAYROLL ADMIN
        # -------------------------------------------------------------
        {
            "email": "payroll@company.com",
            "username": "payrolladmin",
            "password": "Password@123",

            "employee_code": "EMP011",
            "company": company,
            "first_name": "Rahul",
            "last_name": "Mehta",
            "date_of_joining": date(2021, 11, 11),
            "date_of_birth": date(1992, 12, 3),
            "gender": gender_male,
            "status": Employee.StatusChoices.ACTIVE,
        },
    ]

    created_count = 0
    skipped_count = 0

    for emp_data in employees_data:

        email = emp_data["email"]

        # -------------------------------------------------------------
        # Skip if employee/user already exists
        # -------------------------------------------------------------

        if User.objects.filter(email=email).exists():
            print(f"✓ Employee already exists for email: {email}")
            skipped_count += 1
            continue

        # -------------------------------------------------------------
        # Create User
        # -------------------------------------------------------------

        user = User.objects.create_user(
            email=emp_data.pop("email"),
            username=emp_data.pop("username"),
            password=emp_data.pop("password"),
            is_active=True,
        )

        # -------------------------------------------------------------
        # Create Employee linked to User
        # -------------------------------------------------------------

        Employee.objects.create(
            user=user,
            **emp_data,
        )

        created_count += 1
        print(f"✓ Created employee: {user.email}")

    print("\n" + "=" * 50)
    print(f"Created: {created_count}")
    print(f"Skipped: {skipped_count}")
    print("=" * 50)



def seed_employee_personal_details():
    """Create employee personal details."""
    if EmployeePersonalDetails.objects.exists():
        print("✓ Employee Personal Details data already exists, skipping...")
        return
    
    nationality_india = Nationality.objects.get(code="IND")
    marital_single = MaritalStatus.objects.get(code="SINGLE")
    marital_married = MaritalStatus.objects.get(code="MARRIED")
    religion = Religion.objects.first()
    blood_group = BloodGroup.objects.first()
    
    employees = Employee.objects.all()[:3]
    
    details_data = [
        {
            "employee": employees[0],
            "nationality": nationality_india,
            "marital_status": marital_single,
            "residential_status": EmployeePersonalDetails.ResidentialStatus.RESIDENT,
            "father_name": "Hari Kumar",
            "place_of_birth": "Delhi",
            "religion": religion,
            "blood_group": blood_group,
            "dietary_preference": EmployeePersonalDetails.DietaryPreference.VEG,
        },
        {
            "employee": employees[1],
            "nationality": nationality_india,
            "marital_status": marital_married,
            "marriage_date": date(2018, 6, 15),
            "spouse_name": "Vikram Singh",
            "residential_status": EmployeePersonalDetails.ResidentialStatus.RESIDENT,
            "father_name": "Suresh Singh",
            "place_of_birth": "Mumbai",
            "religion": religion,
            "blood_group": blood_group,
            "dietary_preference": EmployeePersonalDetails.DietaryPreference.NON_VEG,
        },
        {
            "employee": employees[2],
            "nationality": nationality_india,
            "marital_status": marital_single,
            "residential_status": EmployeePersonalDetails.ResidentialStatus.RESIDENT,
            "father_name": "Rajesh Patel",
            "place_of_birth": "Gujarat",
            "religion": religion,
            "blood_group": blood_group,
            "dietary_preference": EmployeePersonalDetails.DietaryPreference.JAIN,
        },
    ]
    
    for detail in details_data:
        EmployeePersonalDetails.objects.create(**detail)
    print(f"✓ Created {len(details_data)} employee personal details records")


def seed_employee_employment_details():
    """Create employee employment details."""
    if EmployeeEmploymentDetails.objects.exists():
        print("✓ Employee Employment Details data already exists, skipping...")
        return
    
    employees = Employee.objects.all()[:3]
    company = Company.objects.first()
    employee_type = EmployeeType.objects.get(code="PERMANENT")
    emp_category = EmployeeCategory.objects.get(code="STAFF")
    department = Department.objects.get(code="IT")
    designation = Designation.objects.first()
    payroll_status = PayrollStatus.objects.get(code="ACTIVE")
    
    emp_details = [
        {
            "employee": employees[0],
            "employee_type": employee_type,
            "employee_work_type": EmployeeEmploymentDetails.EmployeeWorkType.OFFICE,
            "category": emp_category,
            "wages_type": EmployeeEmploymentDetails.WagesType.MONTHLY,
            "department": department,
            "designation": designation,
            "payroll_frequency": EmployeeEmploymentDetails.PayrollFrequency.MONTHLY,
            "payment_mode": EmployeeEmploymentDetails.PaymentMode.BANK_TRANSFER,
        },
        {
            "employee": employees[1],
            "employee_type": employee_type,
            "employee_work_type": EmployeeEmploymentDetails.EmployeeWorkType.HYBRID,
            "category": emp_category,
            "wages_type": EmployeeEmploymentDetails.WagesType.MONTHLY,
            "department": department,
            "designation": designation,
            "payroll_frequency": EmployeeEmploymentDetails.PayrollFrequency.MONTHLY,
            "payment_mode": EmployeeEmploymentDetails.PaymentMode.BANK_TRANSFER,
        },
        {
            "employee": employees[2],
            "employee_type": employee_type,
            "employee_work_type": EmployeeEmploymentDetails.EmployeeWorkType.WFH,
            "category": emp_category,
            "wages_type": EmployeeEmploymentDetails.WagesType.MONTHLY,
            "department": department,
            "designation": designation,
            "payroll_frequency": EmployeeEmploymentDetails.PayrollFrequency.MONTHLY,
            "payment_mode": EmployeeEmploymentDetails.PaymentMode.BANK_TRANSFER,
        },
    ]
    
    for detail in emp_details:
        EmployeeEmploymentDetails.objects.create(**detail)
    print(f"✓ Created {len(emp_details)} employee employment details records")


def seed_employee_contacts():
    """Create employee contact details."""
    if EmployeeContacts.objects.exists():
        print("✓ Employee Contacts data already exists, skipping...")
        return
    
    employees = Employee.objects.all()[:3]
    relation = Relation.objects.first()
    
    contacts_data = [
        {
            "employee": employees[0],
            "official_email": "rajesh.kumar@company.com",
            "personal_email": "rajesh.kumar@personal.com",
            "mobile_no": "9876543210",
            "alternate_mobile_no": "9876543211",
            "work_phone": "+91-11-12345678",
            "emergency_contact_name": "Hari Kumar",
            "emergency_contact_relation": relation,
            "emergency_contact_phone": "9876543212",
            "emergency_contact_email": "hari.kumar@email.com",
            "skype_id": "rajesh.kumar.skype",
            "linkedin_url": "https://linkedin.com/in/rajesh-kumar",
        },
        {
            "employee": employees[1],
            "official_email": "priya.singh@company.com",
            "personal_email": "priya.singh@personal.com",
            "mobile_no": "9123456789",
            "alternate_mobile_no": "9123456790",
            "work_phone": "+91-22-87654321",
            "emergency_contact_name": "Suresh Singh",
            "emergency_contact_relation": relation,
            "emergency_contact_phone": "9123456791",
            "emergency_contact_email": "suresh.singh@email.com",
            "skype_id": "priya.singh.skype",
            "linkedin_url": "https://linkedin.com/in/priya-singh",
        },
        {
            "employee": employees[2],
            "official_email": "amit.patel@company.com",
            "personal_email": "amit.patel@personal.com",
            "mobile_no": "8765432109",
            "work_phone": "+91-80-34567890",
            "emergency_contact_name": "Rajesh Patel",
            "emergency_contact_relation": relation,
            "emergency_contact_phone": "8765432108",
            "emergency_contact_email": "rajesh.patel@email.com",
            "linkedin_url": "https://linkedin.com/in/amit-patel",
        },
    ]
    
    for contact in contacts_data:
        EmployeeContacts.objects.create(**contact)
    print(f"✓ Created {len(contacts_data)} employee contact records")


def seed_employee_addresses():
    """Create employee address records."""
    if EmployeeAddress.objects.exists():
        print("✓ Employee Address data already exists, skipping...")
        return
    
    employees = Employee.objects.all()[:3]
    delhi = State.objects.get(code="DL")
    mumbai_state = State.objects.get(code="MH")
    bangalore_state = State.objects.get(code="KA")
    india = Country.objects.get(code="IN")
    delhi_city = City.objects.get(code="DEL")
    mumbai_city = City.objects.get(code="MUM")
    bangalore_city = City.objects.get(code="BLR")
    
    addresses_data = [
        {
            "employee": employees[0],
            "address_type": EmployeeAddress.AddressType.PERMANENT,
            "address_line1": "123 Green Street",
            "address_line2": "Apartment 45",
            "landmark": "Near Central Park",
            "city": delhi_city,
            "state": delhi,
            "country": india,
            "pincode": "110001",
            "is_verified": True,
        },
        {
            "employee": employees[0],
            "address_type": EmployeeAddress.AddressType.CURRENT,
            "address_line1": "456 Business Park",
            "address_line2": "Building A, Floor 5",
            "landmark": "Tech Hub",
            "city": delhi_city,
            "state": delhi,
            "country": india,
            "pincode": "110088",
            "is_same_as_permanent": False,
        },
        {
            "employee": employees[1],
            "address_type": EmployeeAddress.AddressType.PERMANENT,
            "address_line1": "789 Marine Drive",
            "address_line2": "High Rise Tower",
            "landmark": "Sea Facing",
            "city": mumbai_city,
            "state": mumbai_state,
            "country": india,
            "pincode": "400001",
            "is_verified": True,
        },
        {
            "employee": employees[2],
            "address_type": EmployeeAddress.AddressType.PERMANENT,
            "address_line1": "321 IT Hub Lane",
            "address_line2": "Tech City",
            "landmark": "Whitefield Area",
            "city": bangalore_city,
            "state": bangalore_state,
            "country": india,
            "pincode": "560001",
            "is_verified": True,
        },
    ]
    
    for address in addresses_data:
        EmployeeAddress.objects.create(**address)
    print(f"✓ Created {len(addresses_data)} employee address records")


def seed_employee_education():
    """Create employee education records."""
    if EmployeeEducation.objects.exists():
        print("✓ Employee Education data already exists, skipping...")
        return
    
    employees = Employee.objects.all()[:3]
    education_level_bachelor = EducationLevel.objects.get(code="BACHELOR")
    education_level_master = EducationLevel.objects.get(code="MASTER")
    qualification = Qualification.objects.filter(code="BTECH").first() or Qualification.objects.first()
    specialization = Specialization.objects.get(code="CSE")
    institution = Institution.objects.filter(code="ABC_IT").first()
    university = University.objects.filter(code="VTU").first()
    passing_year = PassingYear.objects.filter(year=2014).first()
    study_mode = StudyMode.objects.get(code="FULL_TIME")
    edu_status = EducationStatus.objects.get(code="COMPLETED")
    
    education_data = [
        {
            "employee": employees[0],
            "education_level": education_level_bachelor,
            "qualification": qualification,
            "specialization": specialization,
            "institution": institution,
            "university": university,
            "passing_year": passing_year,
            "institution_name": getattr(institution, "label", "ABC Institute of Technology"),
            "university_name": getattr(university, "label", "VTU"),
            "start_year": 2008,
            "end_year": 2014,
            "percentage": Decimal("82.00"),
            "grade_or_cgpa": "A",
            "start_date": date(2008, 7, 1),
            "end_date": date(2012, 5, 31),
            "study_mode": study_mode,
            "education_status": edu_status,
        },
        {
            "employee": employees[0],
            "education_level": education_level_master,
            "qualification": qualification,
            "specialization": specialization,
            "institution_name": "Indian Institute of Technology",
            "university_name": "IIT Delhi",
            "start_year": 2012,
            "end_year": 2014,
            "study_mode": study_mode,
            "education_status": edu_status,
        },
        {
            "employee": employees[1],
            "education_level": education_level_bachelor,
            "qualification": qualification,
            "specialization": specialization,
            "institution_name": "Mumbai Institute of Technology",
            "university_name": "Mumbai University",
            "start_year": 2010,
            "end_year": 2014,
            "study_mode": study_mode,
            "education_status": edu_status,
        },
        {
            "employee": employees[2],
            "education_level": education_level_bachelor,
            "qualification": qualification,
            "specialization": specialization,
            "institution_name": "Bangalore Institute of Technology",
            "university_name": "Bangalore University",
            "start_year": 2013,
            "end_year": 2017,
            "study_mode": study_mode,
            "education_status": edu_status,
        },
    ]
    
    for edu in education_data:
        EmployeeEducation.objects.create(**edu)
    print(f"✓ Created {len(education_data)} employee education records")


def seed_employee_family_members():
    """Create employee family member records."""
    if EmployeeFamilyMember.objects.exists():
        print("✓ Employee Family Members data already exists, skipping...")
        return
    
    employees = Employee.objects.all()[:3]
    relation_father = Relation.objects.get(code="FATHER")
    relation_mother = Relation.objects.get(code="MOTHER")
    relation_spouse = Relation.objects.get(code="SPOUSE")
    gender_male = Gender.objects.get(code="M")
    gender_female = Gender.objects.get(code="F")
    occupation = Occupation.objects.first()
    nationality = Nationality.objects.get(code="IND")
    blood_group = BloodGroup.objects.first()
    
    family_data = [
        {
            "employee": employees[0],
            "relation": relation_father,
            "first_name": "Hari",
            "last_name": "Kumar",
            "date_of_birth": date(1960, 3, 15),
            "gender": gender_male,
            "occupation": occupation,
            "blood_group": blood_group,
            "nationality": nationality,
            "is_dependent": False,
            "mobile_no": "9876543200",
            "aadhaar_no": "123412341234",
            "pan_no": "ABCPK1234A",
        },
        {
            "employee": employees[0],
            "relation": relation_mother,
            "first_name": "Sunita",
            "last_name": "Kumari",
            "date_of_birth": date(1962, 7, 20),
            "gender": gender_female,
            "occupation": occupation,
            "blood_group": blood_group,
            "nationality": nationality,
            "is_dependent": False,
            "mobile_no": "9876543201",
            "aadhaar_no": "234523452345",
        },
        {
            "employee": employees[1],
            "relation": relation_spouse,
            "first_name": "Vikram",
            "last_name": "Singh",
            "date_of_birth": date(1992, 5, 10),
            "gender": gender_male,
            "occupation": occupation,
            "blood_group": blood_group,
            "nationality": nationality,
            "is_dependent": False,
            "is_nominee": True,
            "mobile_no": "9123456780",
            "email": "vikram.singh@email.com",
            "aadhaar_no": "345634563456",
            "pan_no": "BCSPK5678B",
        },
    ]
    
    for family in family_data:
        EmployeeFamilyMember.objects.create(**family)
    print(f"✓ Created {len(family_data)} employee family member records")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN SEED FUNCTION
# ═════════════════════════════════════════════════════════════════════════════

@db_transaction.atomic
def seed_all_data(masters_only=False):
    """
    Master seed function - seeds all master and transaction data for employees.
    Wraps everything in a database transaction for atomicity.

    Args:
        masters_only (bool): If True, only master tables are seeded and transaction rows are skipped.
    """
    print("\n" + "="*80)
    print("SEEDING EMPLOYEE MODULE DATA")
    print("="*80 + "\n")
    
    try:
        # Personal Masters
        print("📋 Seeding Personal Masters...")
        seed_gender()
        seed_salutation()
        seed_marital_status()
        seed_religion()
        seed_blood_group()
        seed_nationality()
        seed_caste_category()
        seed_relation()
        seed_occupation()
        
        # Education Masters
        print("\n📚 Seeding Education Masters...")
        seed_education_level()
        seed_education_status()
        seed_study_mode()
        seed_qualification()
        seed_specialization()
        seed_institution()
        seed_university()
        seed_passing_year()
        
        # Employment Masters
        print("\n💼 Seeding Employment Masters...")
        seed_employee_type()
        seed_employee_category()
        seed_employee_status()
        seed_payroll_status()
        seed_source_of_hire()
        seed_transport_type()
        seed_payroll_mode()
        seed_payroll_group()
        seed_profession()
        seed_company()
        seed_work_experience_range()
        seed_relevant_experience_range()
        seed_shift_type()
        seed_shift()
        seed_work_week_policy()
        seed_holiday_calendar()
        seed_holiday()
        seed_holiday_group()
        
        # Location Masters
        print("\n📍 Seeding Location Masters...")
        seed_country()
        seed_state()
        seed_city()
        seed_location_type()
        seed_headquarter_location()
        seed_office_location()
        seed_production_cell()
        seed_floor()
        
        # Organization Masters
        print("\n🏢 Seeding Organization Masters...")
        seed_grade()
        seed_department()
        seed_designation()
        seed_bank()
        seed_bank_status()
        seed_account_type()
        seed_insurance_masters()
        seed_branch()
        seed_business_unit()
        seed_cost_center()
        seed_profit_center()
        seed_band()
        
        # System & Workflow Masters
        print("\n⚙️ Seeding System & Workflow Masters...")
        # seed_system_role()
        # seed_default_role()
        seed_communication_channel()
        seed_communication_task()
        seed_document_type()
        seed_document_side()
        seed_separation_mode()
        seed_contract_status()
        seed_verification_status()
        seed_residential_status()
        seed_payment_type()
        seed_attendance_status()
        seed_employee_filter()
        seed_bulletin_category()
        seed_policy_category()
        seed_form_category()
        seed_import_type()
        seed_letter_approval_type()
        seed_clearance_item_type()
        seed_position_change_reason()
        seed_counter_party()
        seed_authorized_signatory()
        # seed_attendance_policy()
        # seed_regularization_reason()
        # seed_overtime_policy()
        # seed_comp_off_policy()
        seed_pay_component_group()
        seed_pay_component()
        seed_salary_structure()
        seed_salary_structure_component()
        seed_reimbursement_type()
        seed_loan_type()
        seed_payroll_cycle()
        seed_tax_regime()
        seed_tds_section()
        seed_arrear_type()
        seed_statutory_component()
        seed_pf_scheme()
        seed_esi_scheme()
        seed_pt_state_slab()
        seed_lwf_slab()
        seed_labour_register_type()
        seed_job_function()
        seed_job_level()
        seed_interview_round()
        seed_candidate_source()
        seed_offer_status()
        seed_rejection_reason()
        seed_pipeline_stage()
        seed_appraisal_cycle()
        seed_rating_scale()
        seed_goal_category()
        seed_kpi_library()
        seed_kra_library()
        seed_competency_group()
        seed_competency()
        seed_training_category()
        seed_training_mode()
        seed_course()
        seed_certification_body()
        seed_asset_category()
        seed_asset_condition()
        seed_asset_type()
        seed_vendor()
        seed_workflow_type()
        seed_approval_action()
        seed_escalation_type()
        seed_audit_event_type()
        # seed_permission()
        # seed_menu_item()
        # seed_data_scope_type()
        seed_password_policy()
        seed_session_policy()
        seed_notification_channel()
        seed_notification_template()
        seed_notification_trigger()
        
        if masters_only:
            print("\n✅ MASTER DATA CREATED SUCCESSFULLY! Transaction data seeding skipped.")
            return

        # Transaction Data
        print("\n👥 Seeding Transaction Data...")
        seed_employees()
        seed_employee_personal_details()
        seed_employee_employment_details()
        seed_employee_contacts()
        seed_employee_addresses()
        seed_employee_education()
        seed_employee_family_members()
        seed_employee_lifecycle()
        # seed_employee_role_assignments()
        seed_employee_auth()
        seed_employee_verification_tokens()
        seed_login_history()
        seed_employee_nominees()
        seed_employee_documents()
        seed_employee_bank_accounts()
        seed_employee_statutory_ids()
        seed_employee_insurance_policies()
        seed_employee_language_proficiencies()
        seed_employee_communication_preferences()
        seed_employee_localization()
        seed_employee_access_cards()
        seed_employee_reporting_relationships()
        seed_employee_audit_logs()
        seed_employee_deputation_locations()
        seed_employee_code_sequences()
        
        print("\n" + "="*80)
        print("✅ ALL SEED DATA CREATED SUCCESSFULLY!")
        print("="*80 + "\n")
        
        # Print summary
        from apps.employees.models import Employee as EmpModel
        print("📊 SUMMARY:")
        print(f"   • Total Employees: {EmpModel.objects.count()}")
        print(f"   • Companies: {Company.objects.count()}")
        print(f"   • Departments: {Department.objects.count()}")
        print(f"   • Designations: {Designation.objects.count()}")
        print(f"   • Genders: {Gender.objects.count()}")
        print(f"   • Countries: {Country.objects.count()}")
        print(f"   • States: {State.objects.count()}")
        print(f"   • Cities: {City.objects.count()}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        raise


# Script entry point
if __name__ == "__main__":
    seed_all_data()
