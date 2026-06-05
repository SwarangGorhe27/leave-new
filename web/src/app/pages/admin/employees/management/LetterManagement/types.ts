export type LetterType = 
  | "Offer Letter"
  | "Appointment Letter"
  | "Confirmation Letter"
  | "Promotion Letter"
  | "Salary Revision Letter"
  | "Increment Letter"
  | "Transfer Letter"
  | "Experience Letter"
  | "Relieving Letter"
  | "Warning Letter"
  | "Appreciation Letter"
  | "Custom Template";

export type ApprovalWorkflow = 
  | "No Approval Required"
  | "Reporting Manager"
  | "HR Manager"
  | "Department Head"
  | "Custom Approval Chain";

export type LetterStatus = 
  | "Draft"
  | "Pending Approval"
  | "Approved"
  | "Rejected"
  | "Published"
  | "Cancelled";

export interface LetterBatch {
  id: string;
  letterType: LetterType;
  templateId: string;
  approvalWorkflow: ApprovalWorkflow;
  subject: string;
  remarks: string;
  effectiveDate: string;
  publishDate: string;
  attachmentUrls: string[];
  selectedEmployeeIds: string[];
  authorisedSignatory?: string;
  purpose?: string;
  generationMode?: "Single" | "Multiple";
  employeeType?: "All Employees" | "Current Employees" | "Resigned Employees";
  status: LetterStatus;
  createdBy: string;
  createdAt: string;
  approvedBy?: string;
  approvedAt?: string;
  publishedAt?: string;
  zipFileUrl?: string;
  pdfUrl?: string;
  templateName?: string;
  updatedAt?: string;
  currentStep?: number;
  activityLog?: { id: string; time: string; message: string }[];
  approvalHistory?: { id: string; time: string; by: string; action: string; remarks?: string }[];
}

export interface GeneratedLetter {
  id: string;
  batchId: string;
  employeeId: string;
  pdfUrl: string;
  status: "Generated" | "Sent" | "Failed";
  generatedAt: string;
}

export interface LetterTemplate {
  id: string;
  name: string;
  type: LetterType;
  content: string; // HTML or Markdown with {{merge_fields}}
}
