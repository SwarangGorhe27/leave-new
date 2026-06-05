import { EMPLOYEE_DOCUMENT_KEYS } from "../../../components/employees/mockData";
import type { DocumentTypeConfig } from "./types";
import { inferDocumentSection } from "./types";

const LABELS: Record<string, string> = {
  panCard: "PAN Card",
  aadhaarCard: "Aadhaar Card",
  resume: "Resume",
  offerLetter: "Offer Letter",
  joiningDocuments: "Joining Documents",
  educationalCertificates: "Educational Certificates",
  salarySlips: "Salary Slips",
  experienceLetters: "Experience Letters",
  passport: "Passport",
  visa: "Visa",
  taxDocuments: "Tax Documents",
  insuranceDocuments: "Insurance Documents",
  relievingLetter: "Relieving Letter",
  appraisalLetters: "Appraisal Letters",
  incrementLetters: "Increment Letters",
  form16: "Form 16",
};

const CATEGORIES: Record<string, string> = {
  panCard: "KYC",
  aadhaarCard: "KYC",
  resume: "Onboarding",
  offerLetter: "Onboarding",
  joiningDocuments: "Onboarding",
  educationalCertificates: "Education",
  salarySlips: "Payroll",
  experienceLetters: "Employment",
  passport: "Travel",
  visa: "Travel",
  taxDocuments: "Tax",
  insuranceDocuments: "Insurance",
  relievingLetter: "Employment",
  appraisalLetters: "HR",
  incrementLetters: "HR",
  form16: "Tax",
};

const FRONT_BACK = new Set(["panCard", "aadhaarCard", "passport", "visa"]);
const MULTIPLE = new Set(["joiningDocuments", "educationalCertificates", "salarySlips", "experienceLetters", "insuranceDocuments"]);

/** Form 16 is an official tax document shown as a dummy entry */
const FORM16_ENTRY: DocumentTypeConfig = {
  id: "form16",
  documentName: "Form 16",
  documentSection: "Official",
  category: "Tax",
  uploadType: "single",
  allowedFileTypes: ["pdf"],
  mandatory: false,
  allowEmployeeEdit: false,
  displayOrder: 100,
  status: "Active",
  isSystem: true,
};

export function buildDefaultDocumentTypes(): DocumentTypeConfig[] {
  const base = EMPLOYEE_DOCUMENT_KEYS.map((id, index) => ({
    id,
    documentName: LABELS[id] || id,
    documentSection: inferDocumentSection(CATEGORIES[id] || "General"),
    category: CATEGORIES[id] || "General",
    uploadType: FRONT_BACK.has(id) ? "frontBack" : MULTIPLE.has(id) ? "multiple" : "single",
    allowedFileTypes: ["pdf", "jpg", "png", "doc", "docx"],
    mandatory: ["panCard", "aadhaarCard", "resume"].includes(id),
    allowEmployeeEdit: !["offerLetter", "relievingLetter"].includes(id),
    displayOrder: index + 1,
    status: "Active" as const,
    isSystem: true,
  }));
  // Add Form 16 only if not already present
  if (!base.find((d) => d.id === "form16")) {
    base.push(FORM16_ENTRY);
  }
  return base;
}

