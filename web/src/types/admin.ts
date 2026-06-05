/* ================================================================== */
/* Admin Module Types                                                  */
/* ================================================================== */

export interface LetterRecord {
  id: string;
  letterTemplate: string;
  employee: string;
  employeeId: string;
  preparedOn: string;
  preparedBy: string;
  authorisedSignatory: string;
  approvalStatus: 'Pending' | 'Approved' | 'Rejected';
  serialNo: string;
  remarks: string;
  signatoryRemarks?: string;
  employeeStatus?: string;
  employeeRemarks?: string;
}

export interface ImportHistory {
  id: string;
  importerType: string;
  fileName: string;
  uploadedBy: string;
  uploadedOn: string;
  status: 'Success' | 'Failed' | 'Processing';
  recordsProcessed: number;
  recordsFailed: number;
  file?: File;
  errors?: string[];
}

export interface MappingField {
  id: string;
  excelField: string;
  mappedTo: string;
  previewData: string;
}

export interface ImporterTypeGroup {
  groupName: string;
  items: ImporterType[];
}

export interface ImporterType {
  id: string;
  name: string;
  description?: string;
}

export interface MasterField {
  id: string;
  fieldName: string;
  category: string;
  required: boolean;
  dataType: 'text' | 'email' | 'number' | 'date' | 'select';
  description?: string;
}

export interface ValidationError {
  row: number;
  field: string;
  message: string;
  value: string;
}

export interface ImportValidationResult {
  isValid: boolean;
  successCount: number;
  errorCount: number;
  errors: ValidationError[];
  warnings?: string[];
}

export interface QuickAddEmployee {
  employeeName: string;
  employeeNumber: string;
  dateOfJoining: string;
  location: string;
  emailId: string;
}

export interface AdminMenuItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  route: string;
  disabled?: boolean;
  description?: string;
}
