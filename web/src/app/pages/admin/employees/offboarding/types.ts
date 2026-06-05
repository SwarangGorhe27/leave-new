// Complete Offboarding Data Types

export interface ApprovalWorkflow {
  reportingManagerApproval: "Pending" | "Approved" | "Rejected";
  reportingManagerApprovedAt?: string;
  reportingManagerRemarks?: string;
  hrApproval: "Pending" | "Approved" | "Rejected";
  hrApprovedAt?: string;
  hrRemarks?: string;
  itClearanceApproval: "Pending" | "Approved" | "Rejected";
  itApprovedAt?: string;
  itRemarks?: string;
  finalApprovalRemarks?: string;
}

export interface NoticePeriod {
  noticeStartDate: string;
  noticeEndDate: string;
  noticeDays: number;
  buyoutRequired: boolean;
  buyoutAmount?: number;
  earlyReleaseApproved: boolean;
  earlyReleaseDate?: string;
}

export interface ClearanceChecklist {
  laptopReturned: boolean;
  laptopReturnedDate?: string;
  idCardReturned: boolean;
  idCardReturnedDate?: string;
  knowledgeTransferDone: boolean;
  knowledgeTransferDate?: string;
  emailAccessDisabled: boolean;
  emailDisabledDate?: string;
  assetsCleared: boolean;
  assetsReturnedDate?: string;
  clearanceRemarks?: string;
  clearanceProgress: number; // 0-100
}

export interface FinancialSettlement {
  leaveEncashment: number;
  deductions: number;
  finalSettlementAmount: number;
  paymentStatus: "Pending" | "Processed" | "Completed";
  paymentDate?: string;
  paymentMethod?: string;
  bankDetails?: string;
}

export interface ExitInterview {
  exitInterviewDate: string;
  exitReason: string;
  employeeFeedback: string;
  wouldRejoin: boolean;
  interviewerName?: string;
  interviewNotes?: string;
}

export interface DocumentFile {
  name: string;
  fileName: string;
  fileSize: number;
  uploadedAt: string;
  file?: File;
  url?: string;
  uploadStatus: "Pending" | "Uploading" | "Uploaded Successfully" | "Failed";
}

export interface OffboardingData {
  // Basic Info
  offboardingId: string;
  employeeId: string;
  name: string;
  initials: string;
  avatarColor: string;
  department: string;
  designation: string;
  reportingManager: string;
  reportingTo?: string;
  
  // Resignation Info
  resignationDate: string;
  lastWorkingDay: string;
  noticePeriod: number;
  type: "Voluntary" | "Involuntary" | "Contractual";
  reason: string;
  
  // Step 3: Approval Workflow
  approvalWorkflow: ApprovalWorkflow;
  
  // Step 4: Notice Period
  noticeDetails: NoticePeriod;
  
  // Step 5: Clearance Checklist
  clearanceChecklist: ClearanceChecklist;
  
  // Step 6: Financial Settlement
  financialSettlement: FinancialSettlement;
  
  // Step 7: Exit Interview
  exitInterview: ExitInterview;
  
  // Step 8: Documents
  documents: Record<string, DocumentFile>;
  
  // Metadata
  createdAt: string;
  updatedAt: string;
  createdBy?: string;
  status: "Draft" | "In Progress" | "Completed" | "Archived";
  
  // Tracking
  completedSteps: number[]; // Array of completed step IDs
}

export interface OffboardingRecord {
  id: string;
  employeeId: string;
  name: string;
  avatar?: string;
  avatarColor?: string;
  initials: string;
  department: string;
  designation: string;
  reportingManager: string;
  resignationDate: string;
  lastWorkingDay: string;
  noticeStatus: "In Notice" | "Completed" | "Waived";
  exitStatus: "Active" | "Pending" | "Approved" | "In Notice Period" | "Clearance Pending" | "Completed" | "Archived";
  clearanceStatus: "Pending" | "Partially Completed" | "Completed";
}
