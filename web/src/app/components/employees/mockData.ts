export interface EducationEntry {
  qualification: string;
  specialization: string;
  institutionName: string;
  university: string;
  fromDate?: string;
  toDate?: string;
  percentageCgpa: string;
  grade: string;
}

export interface WorkExperienceEntry {
  id: string;
  companyName: string;
  jobTitle: string;
  employmentType: string;
  department: string;
  responsibilities: string;
  technologiesUsed: string;
  location: string;
  experienceLetterFileName?: string;
  experienceLetterDataUrl?: string;
  reasonForLeaving: string;
  startDate: string;
  endDate: string;
}

export interface NomineeEntry {
  id: string;
  nomineeName: string;
  nomineeEmail?: string;
  relationship: string;
  dateOfBirth: string;
  contactNumber: string;
  address: string;
  // Percentage allocations per nominee type (strings to keep form inputs simple)
  nomineeType?: string;
  epfPercentage?: string;
  epsPercentage?: string;
  gratuityPercentage?: string;
  customPercentage?: string;
  isMinor?: boolean;
  guardian?: {
    guardianName?: string;
    relationshipWithMinor?: string;
    contactNumber?: string;
    address?: string;
    dateOfBirth?: string;
    idProofFileName?: string;
    idProofDataUrl?: string;
  };
  idProofFileName?: string;
  idProofDataUrl?: string;
}

export interface InsuranceEntry {
  id: string;
  insuranceProvider: string;
  policyNumber: string;
  coverageType: string;
  coverageAmount: string;
  validTill: string;
  dependentsCovered: string;
  documentFileName?: string;
  documentDataUrl?: string;
}

export interface AssetEntry {
  id: string;
  assetName: string;
  assetId: string;
  assetCategory: string;
  assetCategoryLabel?: string;
  serialNumber: string;
  assignedDate: string;
  returnDate?: string;
  assetCondition: string;
  assetConditionLabel?: string;
  status: string;
  remarks?: string;
}

export interface PfDetails {
  id?: string;
  pfNumber: string;
  pfType: string;
  monthlyContribution: string;
  employeeShare: string;
  employerShare: string;
  status: string;
}

export interface EsiDetails {
  id?: string;
  esiNumber: string;
  esiType: string;
  employeeContribution: string;
  employerContribution: string;
  dispensary: string;
  status: string;
}

export interface BankAccount {
  id: string;
  accountNumber: string;
  bankName: string;
  ifscCode: string;
  bankId?: string;
  accountType?: string;
  accountTypeId?: string;
  accountHolderName?: string;
  branchName?: string;
  paymentType?: string;
  paymentTypeId?: string;
  /** True when account number came from API masking (XXXX…1234) */
  accountNumberMasked?: boolean;
  isPrimary?: boolean;
}

export interface BackgroundCheckRecord {
  id: string;
  verificationStatus: string;
  verificationStatusLabel?: string;
  completedOn?: string;
  agencyName?: string;
  remarks?: string;
  reportUrl?: string;
  verifiedBy?: string;
  referenceNumber?: string;
}

export interface SalaryRecord {
  id: string;
  effectiveDate?: string;
  basicSalary: number;
  hra: number;
  conveyance: number;
  medicalAllowance: number;
  specialAllowance: number;
  grossSalary: number;
  pf: number;
  tds: number;
  netSalary: number;
}

export interface AccessCardEntry {
  id: string;
  employeeId: string;
  cardNumber: string;
}

export const EMPLOYEE_DOCUMENT_KEYS = [
  "panCard",
  "aadhaarCard",
  "resume",
  "offerLetter",
  "joiningDocuments",
  "educationalCertificates",
  "salarySlips",
  "experienceLetters",
  "passport",
  "visa",
  "taxDocuments",
  "insuranceDocuments",
  "relievingLetter",
  "appraisalLetters",
  "incrementLetters",
] as const;

export type EmployeeDocumentKey = (typeof EMPLOYEE_DOCUMENT_KEYS)[number];

export interface EmployeeDocumentMeta {
  fileName?: string;
  dataUrl?: string;
  uploadedAt?: string;
  sizeBytes?: number;
}

export interface PositionHistoryEntry {
  id: string;
  title: string;
  department: string;
  from: string;
  to: string;
  reportingTo: string;
  isCurrentPosition?: boolean;
}

export interface Employee {
  id: string;
  name: string;
  firstName?: string;
  middleName?: string;
  lastName?: string;
  employeeId: string;
  designation: string;
  designationId?: string;
  department: string;
  departmentId?: string;
  team: string;
  teamId?: string;
  email: string;
  phone: string;
  joiningDate: string;
  location: string;
  status: "Active" | "Inactive" | "On Leave";
  avatar?: string;
  initials: string;
  avatarColor: string;
  reportingManagerId?: string;
  
  // Profile details
  salutation?: string;
  preferredName?: string;
  alternateMobile?: string;
  extensionNumber?: string;
  bio?: string;
  
  // Personal details
  actualDob?: string;
  dateOfBirth: string;
  gender: string;
  maritalStatus: string;
  bloodGroup: string;
  nationality: string;
  religion?: string;
  caste?: string;
  casteCategory?: string;
  residentialStatus?: string;
  placeOfBirth?: string;
  identificationMark?: string;
  isPhysicallyChallenged?: boolean;
  isInternationalEmployee?: boolean;
  fathersName?: string;
  motherName?: string;
  spouseName?: string;
  
  currentAddress?: {
    addressLine1: string;
    addressLine2: string;
    landmark: string;
    city: string;
    state: string;
    country: string;
    pincode: string;
    startDate: string;
    toDate: string;
    isSameAsPermanent: boolean;
  };
  permanentAddress?: {
    addressLine1: string;
    addressLine2: string;
    landmark: string;
    city: string;
    state: string;
    country: string;
    pincode: string;
    startDate: string;
    toDate: string;
  };

  // Bank & Statutory details
  bankName: string;
  accountNumber: string;
  ifscCode: string;
  panNumber?: string;
  aadhaarNumber?: string;
  uanNumber?: string;
  pfNumber: string;
  esiNumber: string;
  taxRegime?: string;
  taxRegimeId?: string;
  isPfCovered?: boolean;
  isEsiCovered?: boolean;
  isLwfCovered?: boolean;
  linNumber?: string;
  /** Earlier member of pension on higher wages */
  isEarlierMemberOfPensionOnHigherWages?: boolean;

  // Family
  family: {
    name: string;
    relationship: string;
    dob: string;
    occupation: string;
    gender: string;
    bloodGroup: string;
    phone: string;
    isDependent: boolean;
    isEmergencyContact: boolean;
    isNominee?: boolean;
  }[];

  nominees?: NomineeEntry[];

  // Passport & Visa
  passportNumber: string;
  passportHolderName?: string;
  passportIssueDate?: string;
  passportPlaceOfIssue?: string;
  passportCountryOfIssue?: string;
  passportCategory?: string;
  passportStatus?: string;
  passportExpiry: string;
  visaType: string;
  visaNumber?: string;
  visaExpiry: string;
  visaCountry: string;
  visaSponsor?: string;
  visaIssueDate?: string;
  visaStatus?: string;

  positionHistory: PositionHistoryEntry[];

  /** Extended PF row for admin editing (separate from salary `pf` number) */
  pfDetails?: PfDetails;
  esiDetails?: EsiDetails;
  accessCards?: AccessCardEntry[];
  employeeDocuments?: Partial<Record<string, EmployeeDocumentMeta>>;
  /** Salary slips keyed by "YYYY-MM" (e.g. "2024-03") */
  salarySlipsByMonth?: Partial<Record<string, EmployeeDocumentMeta>>;

  workExperience: WorkExperienceEntry[];

  // Salary
  basicSalary: number;
  hra: number;
  conveyance: number;
  medicalAllowance: number;
  specialAllowance: number;
  grossSalary: number;
  pf: number;
  tds: number;
  netSalary: number;

  // Work Details
  employeeType?: string;
  employeeCategory?: string;
  shift?: string;
  functionalManager?: string;
  hrPartner?: string;
  confirmationDate?: string;
  employmentStatus?: string;
  probationPeriod?: string;
  noticePeriod?: string;
  noticePeriodDays?: string;
  referredBy?: string;
  reportingTo?: string;

  education?: EducationEntry[];

  insurance?: InsuranceEntry[];

  // Languages
  languages?: {
    language: string;
    proficiency: string;
    canRead: boolean;
    canWrite: boolean;
    canSpeak: boolean;
  }[];

  assets?: AssetEntry[];

  // Medical Information
  medicalInfo?: {
    relationship?: string;
    conditions?: string;
    hasDisease?: boolean;
    diseaseDetails?: string;
    hasSurgery?: boolean;
    surgeryDetails?: string;
    hasAllergies?: boolean;
    allergyDetails?: string;
    allergies?: string;
    bloodGroup?: string;
    doctorName?: string;
    insuranceProvider?: string;
    insurancePolicyNumber?: string;
  };

  // Background Check
  backgroundCheck?: {
    verificationStatus: string;
    completedOn?: string;
    agencyName?: string;
    remarks?: string;
    reportUrl?: string;
    verifiedBy?: string;
    referenceNumber?: string;
  };

  // Multi-record arrays (admin-managed)
  bankAccounts?: BankAccount[];
  pfRecords?: PfDetails[];
  esiRecords?: EsiDetails[];
  backgroundChecks?: BackgroundCheckRecord[];
  salaryHistory?: SalaryRecord[];

  // Emergency Contact (subset of communication)
  emergencyContact?: {
    name: string;
    relationship: string;
    phone: string;
    alternatePhone?: string;
  };

  // Selective Editing for ESS
  editableSections?: string[]; // IDs of sections/subsections employee can edit
  /** When true the profile is locked for direct edits; changes must go through PROFILE_EDIT_REQUEST workflow */
  profileLocked?: boolean;
  editRequestStatus?: 'None' | 'Pending' | 'Updated';
}

const _legacyEmployees: Record<string, unknown>[] = [
  {
    id: "0",
    name: "Vikram Nair",
    employeeId: "EMP-000",
    designation: "Managing Director",
    department: "Executive",
    team: "Management",
    email: "vikram.nair@company.com",
    phone: "+91 99999 00000",
    joiningDate: "2015-01-01",
    location: "Bangalore",
    status: "Active",
    avatar:
      "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=200",
    initials: "VN",
    avatarColor: "#1E293B",
    reportingManagerId: undefined, // Root
    dateOfBirth: "1980-05-15",
    gender: "Male",
    maritalStatus: "Married",
    bloodGroup: "A+",
    nationality: "Indian",
    address: "CEO Residence, Bangalore",
    city: "Bangalore",
    state: "Karnataka",
    pincode: "560001",
    bankName: "HDFC Bank",
    accountNumber: "XXXX XXXX 1111",
    ifscCode: "HDFC0001111",
    pfNumber: "KN/BAN/00000/000",
    esiNumber: "ESI/2015/000000",
    family: [],
    passportNumber: "A1111111",
    passportExpiry: "2035-01-01",
    visaType: "",
    visaExpiry: "",
    visaCountry: "",
    positionHistory: [],
    previousEmployment: [],
    basicSalary: 200000,
    hra: 80000,
    conveyance: 5000,
    medicalAllowance: 2500,
    specialAllowance: 50000,
    grossSalary: 337500,
    pf: 15000,
    tds: 50000,
    netSalary: 272500,
  },
  {
    id: "1",
    name: "Arjun Sharma",
    employeeId: "EMP-001",
    designation: "Senior Developer",
    department: "Engineering",
    team: "Frontend",
    email: "arjun.sharma@company.com",
    phone: "+91 98765 43210",
    joiningDate: "2021-03-15",
    location: "Bangalore",
    status: "Active",
    avatar:
      "https://images.unsplash.com/photo-1651684215020-f7a5b6610f23?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=200",
    initials: "AS",
    avatarColor: "#4F46E5",
    reportingManagerId: "0", // Reports to Vikram Nair
    dateOfBirth: "1992-07-20",
    gender: "Male",
    maritalStatus: "Married",
    bloodGroup: "B+",
    nationality: "Indian",
    address: "42, Koramangala 5th Block",
    city: "Bangalore",
    state: "Karnataka",
    pincode: "560095",
    bankName: "HDFC Bank",
    accountNumber: "XXXX XXXX 4521",
    ifscCode: "HDFC0001234",
    pfNumber: "KN/BAN/12345/001",
    esiNumber: "ESI/2021/001234",
    family: [
      { 
        name: "Priya Sharma", 
        relationship: "Spouse", 
        dob: "1994-03-10", 
        occupation: "Teacher",
        gender: "Female",
        bloodGroup: "O+",
        phone: "+91 98765 00001",
        isDependent: true,
        isEmergencyContact: true
      },
      { 
        name: "Ramesh Sharma", 
        relationship: "Father", 
        dob: "1962-11-05", 
        occupation: "Retired",
        gender: "Male",
        bloodGroup: "B+",
        phone: "+91 98765 00002",
        isDependent: true,
        isEmergencyContact: false
      },
      { 
        name: "Sunita Sharma", 
        relationship: "Mother", 
        dob: "1965-08-14", 
        occupation: "Homemaker",
        gender: "Female",
        bloodGroup: "A+",
        phone: "+91 98765 00003",
        isDependent: true,
        isEmergencyContact: false
      },
    ],
    passportNumber: "J9876543",
    passportExpiry: "2029-05-12",
    visaType: "Business Visa",
    visaExpiry: "2024-12-31",
    visaCountry: "United States",
    positionHistory: [
      {
        title: "Senior Developer",
        department: "Engineering",
        from: "2023-01-01",
        to: "Present",
        reportingTo: "Vikram Nair",
      },
      {
        title: "Developer",
        department: "Engineering",
        from: "2021-03-15",
        to: "2022-12-31",
        reportingTo: "Vikram Nair",
      },
    ],
    previousEmployment: [
      {
        company: "TechSolutions Pvt Ltd",
        designation: "Junior Developer",
        from: "2018-06-01",
        to: "2021-03-10",
        reasonForLeaving: "Better Opportunity",
      },
      {
        company: "StartupXYZ",
        designation: "Intern",
        from: "2017-11-01",
        to: "2018-05-31",
        reasonForLeaving: "Contract End",
      },
    ],
    basicSalary: 75000,
    hra: 30000,
    conveyance: 3000,
    medicalAllowance: 1250,
    specialAllowance: 10750,
    grossSalary: 120000,
    pf: 9000,
    tds: 8500,
    netSalary: 102500,
    employeeType: "Permanent",
    confirmationDate: "2021-09-15",
    employmentStatus: "Confirmed",
    probationPeriod: "6 Months",
    noticePeriod: "60 Days",
    referredBy: "Self",
    reportingTo: "Vikram Nair",
    education: [
      {
        qualification: "Bachelor of Technology",
        specialization: "Computer Science",
        institutionName: "IIT Bombay",
        university: "IIT Bombay",
        startDate: "2014-07-01",
        endDate: "2018-05-31",
        grade: "8.5 CGPA",
        educationLevel: "Bachelor's",
        modeOfStudy: "Full Time",
        country: "India",
        certificateName: "BTech_Degree.pdf"
      },
      {
        qualification: "Higher Secondary",
        specialization: "Science",
        institutionName: "KV No. 1",
        university: "CBSE",
        startDate: "2012-04-01",
        endDate: "2014-03-31",
        grade: "92%",
        educationLevel: "Higher Secondary",
        modeOfStudy: "Full Time",
        country: "India"
      }
    ],
    backgroundCheck: {
      verificationStatus: "Verified",
      completedOn: "2021-04-10",
      agencyName: "TrustVerify Inc.",
      remarks: "All documents and previous employment verified successfully."
    },
    languages: [
      { language: "English", proficiency: "Advanced", canRead: true, canWrite: true, canSpeak: true },
      { language: "Hindi", proficiency: "Native", canRead: true, canWrite: true, canSpeak: true },
    ],
    nominees: [
      {
        id: "nom-1",
        nomineeName: "Priya Sharma",
        relationship: "Spouse",
        dateOfBirth: "1994-03-10",
        contactNumber: "+91 98765 00001",
        address: "42, Koramangala, Bangalore",
        sharePercentage: "100",
      },
    ],
    insurance: [
      {
        id: "ins-1",
        insuranceProvider: "Star Health",
        policyNumber: "POL-H-99231",
        coverageType: "Health",
        coverageAmount: "1000000",
        validTill: "2026-03-31",
        dependentsCovered: "Priya Sharma",
      },
    ],
    assets: [
      {
        id: "ast-1",
        assetName: "MacBook Pro 16",
        assetId: "AST-LAP-001",
        assetCategory: "Laptop",
        serialNumber: "SN-MBP-2021-001",
        assignedDate: "2021-03-20",
        returnDate: "",
        assetCondition: "Good",
        status: "Assigned",
        remarks: "Company issued",
      },
    ],
    accessCards: [
      { id: "acc-1", employeeId: "EMP-001", cardNumber: "AC-BLR-45210" },
    ],
  },
  {
    id: "2",
    name: "Priya Nair",
    employeeId: "EMP-002",
    designation: "HR Manager",
    department: "Human Resources",
    team: "Talent Acquisition",
    email: "priya.nair@company.com",
    phone: "+91 98765 43211",
    joiningDate: "2020-06-01",
    location: "Mumbai",
    status: "Active",
    avatar:
      "https://images.unsplash.com/photo-1706824265660-5ca5effaf122?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=200",
    initials: "PN",
    avatarColor: "#0891B2",
    reportingManagerId: "0", // Reports to Vikram Nair
    dateOfBirth: "1990-04-15",
    gender: "Female",
    maritalStatus: "Single",
    bloodGroup: "A+",
    nationality: "Indian",
    address: "12, Bandra West, Turner Road",
    city: "Mumbai",
    state: "Maharashtra",
    pincode: "400050",
    bankName: "ICICI Bank",
    accountNumber: "XXXX XXXX 7832",
    ifscCode: "ICIC0002345",
    pfNumber: "MH/MUM/23456/002",
    esiNumber: "ESI/2020/002345",
    family: [
      { name: "Mohan Nair", relationship: "Father", dob: "1960-09-20", occupation: "Business" },
      { name: "Latha Nair", relationship: "Mother", dob: "1963-02-28", occupation: "Homemaker" },
    ],
    passportNumber: "K1234567",
    passportExpiry: "2027-08-22",
    visaType: "Tourist Visa",
    visaExpiry: "2024-06-30",
    visaCountry: "United Kingdom",
    positionHistory: [
      {
        title: "HR Manager",
        department: "Human Resources",
        from: "2022-07-01",
        to: "Present",
        reportingTo: "Deepa Menon",
      },
      {
        title: "HR Executive",
        department: "Human Resources",
        from: "2020-06-01",
        to: "2022-06-30",
        reportingTo: "Deepa Menon",
      },
    ],
    previousEmployment: [
      {
        company: "GlobalHR Solutions",
        designation: "HR Coordinator",
        from: "2016-08-01",
        to: "2020-05-28",
        reasonForLeaving: "Career Growth",
      },
    ],
    basicSalary: 65000,
    hra: 26000,
    conveyance: 3000,
    medicalAllowance: 1250,
    specialAllowance: 9750,
    grossSalary: 105000,
    pf: 7800,
    tds: 7200,
    netSalary: 90000,
    nominees: [
      {
        id: "nom-2",
        nomineeName: "Mohan Nair",
        relationship: "Father",
        dateOfBirth: "1960-09-20",
        contactNumber: "+91 98765 10002",
        address: "12, Bandra West, Turner Road, Mumbai",
        sharePercentage: "50",
      },
      {
        id: "nom-3",
        nomineeName: "Latha Nair",
        relationship: "Mother",
        dateOfBirth: "1963-02-28",
        contactNumber: "+91 98765 10003",
        address: "12, Bandra West, Turner Road, Mumbai",
        sharePercentage: "50",
      },
    ],
    accessCards: [
      { id: "acc-2", employeeId: "EMP-002", cardNumber: "AC-MUM-78421" },
    ],
    assets: [
      {
        id: "ast-2",
        assetName: "Dell Latitude 5540",
        assetId: "AST-LAP-002",
        assetCategory: "Laptop",
        serialNumber: "SN-DELL-5540-002",
        assignedDate: "2020-06-15",
        assetCondition: "Good",
        status: "Assigned",
        remarks: "HR department laptop",
      },
    ],
  },
  {
    id: "3",
    name: "Vikram Mehta",
    employeeId: "EMP-003",
    designation: "Product Manager",
    department: "Product",
    team: "Product Strategy",
    email: "vikram.mehta@company.com",
    phone: "+91 98765 43212",
    joiningDate: "2019-09-10",
    location: "Delhi",
    status: "Active",
    avatar:
      "https://images.unsplash.com/photo-1625929664135-197db5f6c857?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=200",
    initials: "VM",
    avatarColor: "#059669",
    reportingManagerId: "1", // Reports to Arjun Sharma
    dateOfBirth: "1988-12-03",
    gender: "Male",
    maritalStatus: "Married",
    bloodGroup: "O+",
    nationality: "Indian",
    address: "78, Vasant Kunj Phase 2",
    city: "New Delhi",
    state: "Delhi",
    pincode: "110070",
    bankName: "SBI",
    accountNumber: "XXXX XXXX 9012",
    ifscCode: "SBIN0003456",
    pfNumber: "DL/DEL/34567/003",
    esiNumber: "ESI/2019/003456",
    family: [
      { name: "Anita Mehta", relationship: "Spouse", dob: "1991-06-25", occupation: "Doctor" },
      { name: "Rahul Mehta", relationship: "Son", dob: "2018-03-15", occupation: "Student" },
    ],
    passportNumber: "L7654321",
    passportExpiry: "2028-11-10",
    visaType: "Work Visa",
    visaExpiry: "2025-03-15",
    visaCountry: "Germany",
    positionHistory: [
      {
        title: "Product Manager",
        department: "Product",
        from: "2021-04-01",
        to: "Present",
        reportingTo: "CEO",
      },
      {
        title: "Senior Business Analyst",
        department: "Product",
        from: "2019-09-10",
        to: "2021-03-31",
        reportingTo: "CTO",
      },
    ],
    previousEmployment: [
      {
        company: "BigTech Corp",
        designation: "Business Analyst",
        from: "2015-01-15",
        to: "2019-09-05",
        reasonForLeaving: "Better Package",
      },
      {
        company: "ConsultingFirm",
        designation: "Analyst Intern",
        from: "2013-06-01",
        to: "2014-12-31",
        reasonForLeaving: "Full Time Opportunity",
      },
    ],
    basicSalary: 90000,
    hra: 36000,
    conveyance: 3000,
    medicalAllowance: 1250,
    specialAllowance: 19750,
    grossSalary: 150000,
    pf: 10800,
    tds: 15000,
    netSalary: 124200,
    nominees: [
      {
        id: "nom-4",
        nomineeName: "Anita Mehta",
        relationship: "Spouse",
        dateOfBirth: "1991-06-25",
        contactNumber: "+91 98765 20001",
        address: "78, Vasant Kunj Phase 2, New Delhi",
        sharePercentage: "70",
      },
      {
        id: "nom-5",
        nomineeName: "Rahul Mehta",
        relationship: "Son",
        dateOfBirth: "2018-03-15",
        contactNumber: "",
        address: "78, Vasant Kunj Phase 2, New Delhi",
        sharePercentage: "30",
      },
    ],
    accessCards: [
      { id: "acc-3", employeeId: "EMP-003", cardNumber: "AC-DEL-99102" },
      { id: "acc-3b", employeeId: "EMP-003", cardNumber: "AC-DEL-PARK-12" },
    ],
    assets: [
      {
        id: "ast-3",
        assetName: "iPhone 15 Pro",
        assetId: "AST-MOB-003",
        assetCategory: "Mobile",
        serialNumber: "SN-IPH15-003",
        assignedDate: "2023-01-10",
        assetCondition: "New",
        status: "Assigned",
        remarks: "Official mobile",
      },
    ],
  },
  {
    id: "4",
    name: "Sneha Krishnan",
    employeeId: "EMP-004",
    designation: "UI/UX Designer",
    department: "Design",
    team: "User Experience",
    email: "sneha.krishnan@company.com",
    phone: "+91 98765 43213",
    joiningDate: "2022-01-05",
    location: "Chennai",
    status: "On Leave",
    avatar:
      "https://images.unsplash.com/photo-1670852077053-6f9a8b3b0d75?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=200",
    initials: "SK",
    avatarColor: "#DC2626",
    reportingManagerId: "2", // Reports to Priya Nair
    dateOfBirth: "1995-08-30",
    gender: "Female",
    maritalStatus: "Single",
    bloodGroup: "AB+",
    nationality: "Indian",
    address: "5, Anna Nagar East",
    city: "Chennai",
    state: "Tamil Nadu",
    pincode: "600102",
    bankName: "Axis Bank",
    accountNumber: "XXXX XXXX 3456",
    ifscCode: "UTIB0004567",
    pfNumber: "TN/CHE/45678/004",
    esiNumber: "ESI/2022/004567",
    family: [
      { name: "Ravi Krishnan", relationship: "Father", dob: "1965-03-22", occupation: "Engineer" },
      { name: "Meena Krishnan", relationship: "Mother", dob: "1968-10-01", occupation: "Nurse" },
    ],
    passportNumber: "M3456789",
    passportExpiry: "2030-02-18",
    visaType: "Student Visa",
    visaExpiry: "2023-09-30",
    visaCountry: "Singapore",
    positionHistory: [
      {
        title: "UI/UX Designer",
        department: "Design",
        from: "2022-01-05",
        to: "Present",
        reportingTo: "Anand Shenoy",
      },
    ],
    previousEmployment: [
      {
        company: "CreativeStudio",
        designation: "Junior Designer",
        from: "2020-07-01",
        to: "2021-12-31",
        reasonForLeaving: "Relocation",
      },
    ],
    basicSalary: 55000,
    hra: 22000,
    conveyance: 3000,
    medicalAllowance: 1250,
    specialAllowance: 8750,
    grossSalary: 90000,
    pf: 6600,
    tds: 5000,
    netSalary: 78400,
    nominees: [
      {
        id: "nom-6",
        nomineeName: "Kavitha Krishnan",
        relationship: "Mother",
        dateOfBirth: "1968-11-05",
        contactNumber: "+91 98765 40001",
        address: "15, Anna Nagar, Chennai",
        sharePercentage: "100",
      },
    ],
    accessCards: [{ id: "acc-4", employeeId: "EMP-004", cardNumber: "AC-CHN-33018" }],
  },
  {
    id: "5",
    name: "Rajesh Kumar",
    employeeId: "EMP-005",
    designation: "DevOps Engineer",
    department: "Engineering",
    team: "Infrastructure",
    email: "rajesh.kumar@company.com",
    phone: "+91 98765 43214",
    joiningDate: "2021-11-20",
    location: "Hyderabad",
    status: "Active",
    avatar:
      "https://images.unsplash.com/photo-1680515837641-bb4b6cbebe8a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=200",
    initials: "RK",
    avatarColor: "#7C3AED",
    reportingManagerId: "1", // Reports to Arjun Sharma
    dateOfBirth: "1993-01-12",
    gender: "Male",
    maritalStatus: "Married",
    bloodGroup: "O-",
    nationality: "Indian",
    address: "22, Jubilee Hills Road No. 36",
    city: "Hyderabad",
    state: "Telangana",
    pincode: "500033",
    bankName: "Kotak Mahindra Bank",
    accountNumber: "XXXX XXXX 8901",
    ifscCode: "KKBK0005678",
    pfNumber: "TS/HYD/56789/005",
    esiNumber: "ESI/2021/005678",
    family: [
      {
        name: "Kavitha Kumar",
        relationship: "Spouse",
        dob: "1995-05-18",
        occupation: "Software Engineer",
      },
      { name: "Aryan Kumar", relationship: "Son", dob: "2021-08-10", occupation: "Infant" },
    ],
    passportNumber: "N8765432",
    passportExpiry: "2031-07-05",
    visaType: "Business Visa",
    visaExpiry: "2025-01-15",
    visaCountry: "Australia",
    positionHistory: [
      {
        title: "DevOps Engineer",
        department: "Engineering",
        from: "2021-11-20",
        to: "Present",
        reportingTo: "Kiran Bose",
      },
    ],
    previousEmployment: [
      {
        company: "CloudTech Solutions",
        designation: "Systems Engineer",
        from: "2018-03-01",
        to: "2021-11-15",
        reasonForLeaving: "Better Growth",
      },
    ],
    basicSalary: 70000,
    hra: 28000,
    conveyance: 3000,
    medicalAllowance: 1250,
    specialAllowance: 12750,
    grossSalary: 115000,
    pf: 8400,
    tds: 9000,
    netSalary: 97600,
  },
  {
    id: "6",
    name: "Ananya Iyer",
    employeeId: "EMP-006",
    designation: "Marketing Specialist",
    department: "Marketing",
    team: "Digital Marketing",
    email: "ananya.iyer@company.com",
    phone: "+91 98765 43215",
    joiningDate: "2023-02-14",
    location: "Pune",
    status: "Active",
    avatar:
      "https://images.unsplash.com/photo-1758599543146-f263d3b3321e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&w=200",
    initials: "AI",
    avatarColor: "#D97706",
    dateOfBirth: "1997-11-25",
    gender: "Female",
    maritalStatus: "Single",
    bloodGroup: "A-",
    nationality: "Indian",
    address: "8, Koregaon Park Lane 5",
    city: "Pune",
    state: "Maharashtra",
    pincode: "411001",
    bankName: "Yes Bank",
    accountNumber: "XXXX XXXX 6789",
    ifscCode: "YESB0006789",
    pfNumber: "MH/PUN/67890/006",
    esiNumber: "ESI/2023/006789",
    family: [
      { name: "Suresh Iyer", relationship: "Father", dob: "1968-07-15", occupation: "Professor" },
      { name: "Geetha Iyer", relationship: "Mother", dob: "1971-04-30", occupation: "Doctor" },
    ],
    passportNumber: "P2345678",
    passportExpiry: "2032-09-20",
    visaType: "Tourist Visa",
    visaExpiry: "2024-04-10",
    visaCountry: "France",
    positionHistory: [
      {
        title: "Marketing Specialist",
        department: "Marketing",
        from: "2023-02-14",
        to: "Present",
        reportingTo: "Neeraj Shah",
      },
    ],
    previousEmployment: [
      {
        company: "AdAgency Pro",
        designation: "Content Writer",
        from: "2021-01-01",
        to: "2023-02-05",
        reasonForLeaving: "Higher Studies",
      },
    ],
    basicSalary: 45000,
    hra: 18000,
    conveyance: 3000,
    medicalAllowance: 1250,
    specialAllowance: 7750,
    grossSalary: 75000,
    pf: 5400,
    tds: 3000,
    netSalary: 66600,
  },
  {
    id: "7",
    name: "Karthik Reddy",
    employeeId: "EMP-007",
    designation: "Data Analyst",
    department: "Analytics",
    team: "Business Intelligence",
    email: "karthik.reddy@company.com",
    phone: "+91 98765 43216",
    joiningDate: "2022-08-01",
    location: "Bangalore",
    status: "Inactive",
    initials: "KR",
    avatarColor: "#0F766E",
    dateOfBirth: "1994-05-08",
    gender: "Male",
    maritalStatus: "Single",
    bloodGroup: "B-",
    nationality: "Indian",
    address: "15, HSR Layout Sector 4",
    city: "Bangalore",
    state: "Karnataka",
    pincode: "560102",
    bankName: "Punjab National Bank",
    accountNumber: "XXXX XXXX 1234",
    ifscCode: "PUNB0007890",
    pfNumber: "KN/BAN/78901/007",
    esiNumber: "ESI/2022/007890",
    family: [
      { name: "Narayan Reddy", relationship: "Father", dob: "1963-12-18", occupation: "Farmer" },
      { name: "Vimala Reddy", relationship: "Mother", dob: "1966-06-22", occupation: "Homemaker" },
    ],
    passportNumber: "Q9876543",
    passportExpiry: "2028-04-14",
    visaType: "",
    visaExpiry: "",
    visaCountry: "",
    positionHistory: [
      {
        title: "Data Analyst",
        department: "Analytics",
        from: "2022-08-01",
        to: "2024-12-31",
        reportingTo: "Sanjay Patel",
      },
    ],
    previousEmployment: [
      {
        company: "DataFirst Inc",
        designation: "Junior Analyst",
        from: "2019-05-01",
        to: "2022-07-25",
        reasonForLeaving: "Better Opportunity",
      },
    ],
    basicSalary: 58000,
    hra: 23200,
    conveyance: 3000,
    medicalAllowance: 1250,
    specialAllowance: 9550,
    grossSalary: 95000,
    pf: 6960,
    tds: 6000,
    netSalary: 82040,
  },
  {
    id: "8",
    name: "Divya Pillai",
    employeeId: "EMP-008",
    designation: "Finance Executive",
    department: "Finance",
    team: "Accounts",
    email: "divya.pillai@company.com",
    phone: "+91 98765 43217",
    joiningDate: "2020-11-30",
    location: "Kochi",
    status: "Active",
    initials: "DP",
    avatarColor: "#BE185D",
    dateOfBirth: "1993-09-14",
    gender: "Female",
    maritalStatus: "Married",
    bloodGroup: "O+",
    nationality: "Indian",
    address: "34, Edapally Junction",
    city: "Kochi",
    state: "Kerala",
    pincode: "682024",
    bankName: "Federal Bank",
    accountNumber: "XXXX XXXX 5678",
    ifscCode: "FDRL0008901",
    pfNumber: "KL/KOC/89012/008",
    esiNumber: "ESI/2020/008901",
    family: [
      { name: "Sunil Pillai", relationship: "Spouse", dob: "1990-02-14", occupation: "Architect" },
      { name: "George Pillai", relationship: "Father", dob: "1960-07-07", occupation: "Retired" },
    ],
    passportNumber: "R1234567",
    passportExpiry: "2026-12-03",
    visaType: "Tourist Visa",
    visaExpiry: "2024-08-20",
    visaCountry: "UAE",
    positionHistory: [
      {
        title: "Finance Executive",
        department: "Finance",
        from: "2020-11-30",
        to: "Present",
        reportingTo: "CFO",
      },
    ],
    previousEmployment: [
      {
        company: "CA Firm Nair & Associates",
        designation: "Accounts Assistant",
        from: "2017-07-01",
        to: "2020-11-20",
        reasonForLeaving: "Corporate Job",
      },
    ],
    basicSalary: 48000,
    hra: 19200,
    conveyance: 3000,
    medicalAllowance: 1250,
    specialAllowance: 8550,
    grossSalary: 80000,
    pf: 5760,
    tds: 4200,
    netSalary: 70040,
  },
];

function yearFromDate(iso?: string): string {
  if (!iso) return "";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "" : String(d.getFullYear());
}

/** Normalizes persisted or legacy seed rows into the current Employee shape. */
export function normalizeLegacyEmployee(raw: Record<string, unknown>): Employee {
  const e = { ...raw } as Record<string, unknown> & { id: string };
  const prev = (e.previousEmployment ?? e.workExperience ?? []) as Record<string, unknown>[];
  const workExperience: WorkExperienceEntry[] = prev.map((p, i) => {
    if (p.companyName != null) {
      return {
        id: String(p.id ?? `we-${e.id}-${i}`),
        companyName: String(p.companyName ?? ""),
        jobTitle: String(p.jobTitle ?? ""),
        employmentType: String(p.employmentType ?? ""),
        department: String(p.department ?? ""),
        responsibilities: String(p.responsibilities ?? ""),
        technologiesUsed: String(p.technologiesUsed ?? ""),
        location: String(p.location ?? ""),
        experienceLetterFileName: p.experienceLetterFileName as string | undefined,
        reasonForLeaving: String(p.reasonForLeaving ?? ""),
        startDate: String(p.startDate ?? ""),
        endDate: String(p.endDate ?? ""),
      };
    }
    return {
      id: String(p.id ?? `we-${e.id}-${i}`),
      companyName: String(p.company ?? ""),
      jobTitle: String(p.designation ?? ""),
      employmentType: String(p.employmentType ?? ""),
      department: String(p.department ?? ""),
      responsibilities: String(p.responsibilities ?? ""),
      technologiesUsed: String(p.technologiesUsed ?? ""),
      location: String(p.location ?? ""),
      experienceLetterFileName: p.experienceLetterFileName as string | undefined,
      reasonForLeaving: String(p.reasonForLeaving ?? ""),
      startDate: String(p.startDate ?? p.from ?? ""),
      endDate: String(p.endDate ?? p.to ?? ""),
    };
  });

  const eduRaw = (e.education ?? []) as Record<string, unknown>[];
  const education: EducationEntry[] | undefined = eduRaw.length
    ? eduRaw.map((ed) => {
        const rawGrade = String(ed.grade ?? "");
        const hasScoreInGrade = /%|CGPA|GPA/i.test(rawGrade);
        const percentageCgpa = String(ed.percentageCgpa ?? (hasScoreInGrade ? rawGrade : ""));
        const grade = hasScoreInGrade ? "" : rawGrade;
        return {
          qualification: String(ed.qualification ?? ""),
          specialization: String(ed.specialization ?? ""),
          institutionName: String(ed.institutionName ?? ""),
          university: String(ed.university ?? ""),
          fromDate: String(ed.fromDate ?? ed.startDate ?? ""),
          toDate: String(ed.toDate ?? ed.endDate ?? (ed.yearOfPassing ? `${ed.yearOfPassing}-12-31` : "")),
          percentageCgpa,
          grade,
        };
      })
    : undefined;

  const nomRaw = (e.nominees ?? []) as Record<string, unknown>[];
  const nominees: NomineeEntry[] | undefined = nomRaw.length
    ? nomRaw.map((n, i) => ({
        id: String(n.id ?? `nom-${e.id}-${i}`),
        nomineeName: String(n.nomineeName ?? n.name ?? ""),
        nomineeEmail: String(n.nomineeEmail ?? n.email ?? ""),
        relationship: String(n.relationship ?? ""),
        dateOfBirth: String(n.dateOfBirth ?? n.dob ?? ""),
        contactNumber: String(n.contactNumber ?? n.phone ?? ""),
        address: String(n.address ?? ""),
        nomineeType: String(n.nomineeType ?? 'EPF'),
        epfPercentage: String(n.epfPercentage ?? n.sharePercentage ?? ""),
        epsPercentage: String(n.epsPercentage ?? ""),
        gratuityPercentage: String(n.gratuityPercentage ?? ""),
        customPercentage: String(n.customPercentage ?? ""),
        isMinor: Boolean(n.isMinor ?? false),
        guardian: n.guardian as any,
        idProofFileName: n.idProofFileName as string | undefined,
        idProofDataUrl: n.idProofDataUrl as string | undefined,
      }))
    : undefined;

  const insRaw = (e.insurance ?? []) as Record<string, unknown>[];
  const insurance: InsuranceEntry[] | undefined = insRaw.length
    ? insRaw.map((n, i) => {
        if (n.insuranceProvider != null) {
          return {
            id: String(n.id ?? `ins-${e.id}-${i}`),
            insuranceProvider: String(n.insuranceProvider ?? ""),
            policyNumber: String(n.policyNumber ?? ""),
            coverageType: String(n.coverageType ?? ""),
            coverageAmount: String(n.coverageAmount ?? ""),
            validTill: String(n.validTill ?? ""),
            dependentsCovered: String(n.dependentsCovered ?? ""),
            documentFileName: n.documentFileName as string | undefined,
          };
        }
        return {
          id: String(n.id ?? `ins-${e.id}-${i}`),
          insuranceProvider: String(n.provider ?? ""),
          policyNumber: String(n.policyNumber ?? ""),
          coverageType: String(n.policyType ?? ""),
          coverageAmount: String(n.coverageAmount ?? ""),
          validTill: String(n.validTill ?? n.endDate ?? ""),
          dependentsCovered: String(n.dependentsCovered ?? n.nomineeName ?? ""),
          documentFileName: n.documentFileName as string | undefined,
        };
      })
    : undefined;

  const astRaw = (e.assets ?? []) as Record<string, unknown>[];
  const assets: AssetEntry[] | undefined = astRaw.length
    ? astRaw.map((a, i) => {
        if (a.assetName != null) {
          return {
            id: String(a.id ?? `ast-${e.id}-${i}`),
            assetName: String(a.assetName ?? ""),
            assetId: String(a.assetId ?? ""),
            assetCategory: String(a.assetCategory ?? ""),
            serialNumber: String(a.serialNumber ?? ""),
            assignedDate: String(a.assignedDate ?? ""),
            returnDate: a.returnDate as string | undefined,
            assetCondition: String(a.assetCondition ?? ""),
            status: String(a.status ?? ""),
            remarks: a.remarks as string | undefined,
          };
        }
        return {
          id: String(a.id ?? `ast-${e.id}-${i}`),
          assetName: String(a.name ?? ""),
          assetId: String(a.code ?? ""),
          assetCategory: String(a.type ?? ""),
          serialNumber: String(a.serialNumber ?? ""),
          assignedDate: String(a.assignedDate ?? ""),
          returnDate: a.returnDate as string | undefined,
          assetCondition: String(a.condition ?? ""),
          status: String(a.status ?? "Assigned"),
          remarks: a.remarks as string | undefined,
        };
      })
    : undefined;

  const posRaw = (e.positionHistory ?? []) as Record<string, unknown>[];
  const positionHistory: PositionHistoryEntry[] = posRaw.map((p, i) => ({
    id: String(p.id ?? `pos-${e.id}-${i}`),
    title: String(p.title ?? ""),
    department: String(p.department ?? ""),
    from: String(p.from ?? ""),
    to: String(p.to ?? ""),
    reportingTo: String(p.reportingTo ?? ""),
    isCurrentPosition: Boolean(p.isCurrentPosition ?? String(p.to) === "Present"),
  }));

  const pfNum = String(e.pfNumber ?? "");
  const pfAmt = typeof e.pf === "number" ? e.pf : 0;
  const pfDetails: PfDetails =
    (e.pfDetails as PfDetails) ||
    ({
      pfNumber: pfNum,
      pfType: "EPF (Employee Provident Fund)",
      monthlyContribution: pfAmt ? `₹${pfAmt.toLocaleString("en-IN")}` : "",
      employeeShare: "12% of Basic",
      employerShare: "12% of Basic",
      status: "Active",
    } as PfDetails);

  const esiNum = String(e.esiNumber ?? "");
  const esiDetails: EsiDetails =
    (e.esiDetails as EsiDetails) ||
    ({
      esiNumber: esiNum,
      esiType: "Employee State Insurance",
      employeeContribution: "0.75%",
      employerContribution: "3.25%",
      dispensary: "ESI Hospital",
      status: "Active",
    } as EsiDetails);

  const acRaw = (e.accessCards ?? []) as Record<string, unknown>[];
  const accessCards: AccessCardEntry[] = acRaw.map((c, i) => ({
    id: String(c.id ?? `acc-${e.id}-${i}`),
    employeeId: String(c.employeeId ?? e.employeeId ?? ""),
    cardNumber: String(c.cardNumber ?? ""),
  }));

  const employeeDocuments =
    (e.employeeDocuments as Partial<Record<EmployeeDocumentKey, EmployeeDocumentMeta>>) || {};

  const { previousEmployment: _pe, ...rest } = e as Record<string, unknown> & {
    previousEmployment?: unknown;
  };

  // Seed bankAccounts array from existing scalar bank fields if not yet set
  const bankAccounts: BankAccount[] = (e.bankAccounts as BankAccount[]) ||
    (String(e.accountNumber ?? "") || String(e.bankName ?? "") ? [{
      id: `bank-${e.id}-0`,
      accountNumber: String(e.accountNumber ?? ""),
      bankName: String(e.bankName ?? ""),
      ifscCode: String(e.ifscCode ?? ""),
      isPrimary: true,
    }] : []);

  // Seed pfRecords from pfDetails
  const pfRecords: PfDetails[] = (e.pfRecords as PfDetails[]) ||
    [{ id: `pf-${e.id}-0`, ...pfDetails }];

  // Seed esiRecords from esiDetails
  const esiRecords: EsiDetails[] = (e.esiRecords as EsiDetails[]) ||
    [{ id: `esi-${e.id}-0`, ...esiDetails }];

  // Seed backgroundChecks from single backgroundCheck object
  const bgRaw = e.backgroundCheck as BackgroundCheckRecord | undefined;
  const backgroundChecks: BackgroundCheckRecord[] = (e.backgroundChecks as BackgroundCheckRecord[]) ||
    (bgRaw ? [{ id: `bg-${e.id}-0`, ...bgRaw }] : []);

  // Seed salaryHistory from existing flat salary fields
  const salaryHistory: SalaryRecord[] = (e.salaryHistory as SalaryRecord[]) ||
    (typeof e.grossSalary === "number" && (e.grossSalary as number) > 0 ? [{
      id: `sal-${e.id}-0`,
      effectiveDate: "",
      basicSalary: typeof e.basicSalary === "number" ? e.basicSalary as number : 0,
      hra: typeof e.hra === "number" ? e.hra as number : 0,
      conveyance: typeof e.conveyance === "number" ? e.conveyance as number : 0,
      medicalAllowance: typeof e.medicalAllowance === "number" ? e.medicalAllowance as number : 0,
      specialAllowance: typeof e.specialAllowance === "number" ? e.specialAllowance as number : 0,
      grossSalary: typeof e.grossSalary === "number" ? e.grossSalary as number : 0,
      pf: typeof e.pf === "number" ? e.pf as number : 0,
      tds: typeof e.tds === "number" ? e.tds as number : 0,
      netSalary: typeof e.netSalary === "number" ? e.netSalary as number : 0,
    }] : []);

  return {
    ...(rest as Omit<
      Employee,
      | "workExperience"
      | "education"
      | "nominees"
      | "insurance"
      | "assets"
      | "positionHistory"
      | "pfDetails"
      | "esiDetails"
      | "accessCards"
      | "employeeDocuments"
      | "bankAccounts"
      | "pfRecords"
      | "esiRecords"
      | "backgroundChecks"
      | "salaryHistory"
    >),
    workExperience,
    education,
    nominees,
    insurance,
    assets,
    positionHistory,
    pfDetails,
    esiDetails,
    accessCards,
    employeeDocuments,
    bankAccounts,
    pfRecords,
    esiRecords,
    backgroundChecks,
    salaryHistory,
  } as Employee;
}

export const employees: Employee[] = _legacyEmployees.map(normalizeLegacyEmployee);

export const departments = [
  "All Departments",
  "Engineering",
  "Human Resources",
  "Product",
  "Design",
  "Marketing",
  "Analytics",
  "Finance",
];
export const teams = [
  "All Teams",
  "Frontend",
  "Infrastructure",
  "Talent Acquisition",
  "Product Strategy",
  "User Experience",
  "Digital Marketing",
  "Business Intelligence",
  "Accounts",
];
export const designations = [
  "All Designations",
  "Senior Developer",
  "HR Manager",
  "Product Manager",
  "UI/UX Designer",
  "DevOps Engineer",
  "Marketing Specialist",
  "Data Analyst",
  "Finance Executive",
];
