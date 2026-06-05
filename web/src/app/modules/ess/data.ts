import { EmployeeProfile } from "./types";
import { attendanceEmployees } from "../attendance/mockData";

export const ESS_SECTIONS = [
  { key: "profile", label: "Profile Section", editable: true },
  { key: "personalDetails", label: "Personal Details", editable: true },
  { key: "employmentDetails", label: "Employment Details", editable: true },
  { key: "addresses", label: "Address Section", editable: true },
  { key: "familyDetails", label: "Family Details", editable: true },
  { key: "educationDetails", label: "Education Details", editable: true },
  { key: "bankAndStatutoryDetails", label: "Bank & Statutory Details", editable: true },
  { key: "nomineeDetails", label: "Nominee Details", editable: true },
  { key: "insuranceDetails", label: "Insurance Details", editable: true },
  { key: "languageDetails", label: "Language Details", editable: true },
  { key: "assets", label: "Assets", editable: false },
] as const;

export const getSeedProfile = (employeeId: string): EmployeeProfile => {
  const emp = attendanceEmployees.find(e => e.id === employeeId);
  const firstName = emp ? emp.name.split(" ")[0] : "Arjun";
  const lastName = emp ? emp.name.split(" ").slice(1).join(" ") : "Sharma";
  const email = emp ? emp.email : "arjun.sharma@company.com";
  const mobile = emp ? emp.contact : "+91 9988776655";
  const dept = emp ? emp.dept : "Engineering";
  const desig = emp ? emp.desig : "Senior Developer";
  const manager = emp ? emp.manager : "Vikram Nair";

  return {
    profileLocked: false,
    employeeId,
    profile: {
      firstName,
      middleName: "",
      lastName,
      personalMobile: "+91 9876543210",
      personalEmail: "arjun.sharma@gmail.com",
      workMobile: mobile,
      officialEmail: email,
    alternateMobileNumber: "",
    extensionNumber: "",
    emergencyContactName: "Priya Sharma",
    emergencyContactNumber: "+91 9123456780",
  },
  personalDetails: {
    dateOfBirth: "1992-07-20",
    actualDateOfBirth: "1992-07-20",
    gender: "Male",
    bloodGroup: "B+",
    maritalStatus: "Married",
    spouseName: "Priya Sharma",
    fatherName: "Ramesh Sharma",
    placeOfBirth: "Jaipur",
    nationality: "Indian",
    religion: "Hindu",
    residentialStatus: "Resident",
    identificationMark: "Small scar on left wrist",
    panNumber: "ABCDE1234F",
    aadhaarNumber: "2345 6789 1122",
    passportNumber: "J7654321",
    uanNumber: "100200300400",
    physicallyChallenged: false,
    internationalEmployee: false,
  },
  employmentDetails: {
    department: dept,
    designation: desig,
    employmentType: "Full Time",
    workLocation: "Bangalore",
    employeeCategory: "Permanent",
    shift: "General",
    noticePeriod: "60",
    reportingManager: manager,
    functionalManager: "Karthik Menon",
    hrPartner: "Priya Nair",
    employeeStatus: "Active",
  },
  addresses: {
    current: {
      addressLine1: "42 Koramangala 5th Block",
      addressLine2: "Near Sony Signal",
      landmark: "Forum Mall",
      city: "Bangalore",
      state: "Karnataka",
      country: "India",
      pincode: "560095",
    },
    permanent: {
      addressLine1: "House 108, Jawahar Nagar",
      addressLine2: "Ward No. 6",
      landmark: "Hanuman Mandir",
      city: "Jaipur",
      state: "Rajasthan",
      country: "India",
      pincode: "302004",
    },
    temporary: {
      addressLine1: "",
      addressLine2: "",
      landmark: "",
      city: "",
      state: "",
      country: "",
      pincode: "",
    },
  },
  familyDetails: [
    {
      id: "fam-1",
      name: "Priya Sharma",
      relation: "Spouse",
      dateOfBirth: "1994-03-10",
      gender: "Female",
      bloodGroup: "O+",
      phone: "+91 9876001111",
      occupation: "Teacher",
      isDependent: true,
      emergencyContact: true,
    },
  ],
  educationDetails: [
    {
      id: "edu-1",
      qualification: "B.Tech",
      specialization: "Computer Science",
      institutionName: "ABC Institute of Technology",
      university: "VTU",
      fromDate: "2010-07-01",
      toDate: "2014-06-30",
      percentageCgpa: "8.2",
      grade: "A",
    },
  ],
  bankAndStatutoryDetails: {
    bankAccounts: [
      {
        id: "bank-1",
        bankName: "HDFC Bank",
        accountNumber: "00901012345678",
        ifscCode: "HDFC0001234",
        accountHolderName: "Arjun Sharma",
        branchName: "Koramangala",
        accountType: "Savings",
        isPrimary: true,
      },
    ],
    panNumber: "ABCDE1234F",
    aadhaarNumber: "2345 6789 1122",
    uanNumber: "100200300400",
    passportNumber: "J7654321",
  },
  nomineeDetails: [
    {
      id: "nom-1",
      name: "Priya Sharma",
      relation: "Spouse",
      dateOfBirth: "1994-03-10",
      epfPercentage: "100",
      phone: "+91 9876001111",
      address: "",
    },
  ],
  insuranceDetails: {
    policyNumber: "PLCY-2026-8821",
    provider: "Care Health",
    startDate: "2026-01-01",
    endDate: "2026-12-31",
    coverageAmount: "500000",
    nomineeName: "Priya Sharma",
  },
  languageDetails: [
    { id: "lng-1", language: "English", proficiencyLevel: "Advanced", canRead: true, canWrite: true, canSpeak: true },
    { id: "lng-2", language: "Hindi", proficiencyLevel: "Native", canRead: true, canWrite: true, canSpeak: true },
  ],
  emergencyAndMedical: {
    emergencyContactName: "Priya Sharma",
    emergencyContactNumber: "+91 9123456780",
    relationship: "Spouse",
    medicalConditions: "",
    allergies: "",
    bloodGroup: "",
    doctorName: "",
    insuranceProvider: "",
    insurancePolicyNumber: "",
  },
  assets: [
    {
      id: "asset-1",
      assetName: "MacBook Pro 14",
      assetCode: "IT-LPT-1023",
      assetType: "Laptop",
      assignedDate: "2025-07-10",
      returnDate: "",
      condition: "Good",
      remarks: "Issued by IT",
    },
  ],
  employeeDocuments: {},
  };
};
