export type DocumentUploadType = "single" | "frontBack" | "multiple";

export type AllowedFileType = "pdf" | "jpg" | "png" | "doc" | "docx";

export type DocumentTypeStatus = "Active" | "Inactive";

export type DocumentSection = "Personal" | "Official" | "Company";

export interface DocumentTypeConfig {
  id: string;
  documentName: string;
  documentSection: DocumentSection;
  category: string;
  uploadType: DocumentUploadType;
  allowedFileTypes: AllowedFileType[];
  mandatory: boolean;
  allowEmployeeEdit: boolean;
  displayOrder: number;
  status: DocumentTypeStatus;
  /** Built-in HRMS types — cannot be deleted */
  isSystem?: boolean;
  needsVerification?: boolean;
}

export const ALLOWED_FILE_TYPE_OPTIONS: { value: AllowedFileType; label: string }[] = [
  { value: "pdf", label: "PDF" },
  { value: "jpg", label: "JPG" },
  { value: "png", label: "PNG" },
  { value: "doc", label: "DOC" },
  { value: "docx", label: "DOCX" },
];

export const UPLOAD_TYPE_OPTIONS: { value: DocumentUploadType; label: string }[] = [
  { value: "single", label: "Single Side" },
  { value: "frontBack", label: "Front & Back Side" },
  { value: "multiple", label: "Multiple Files" },
];

export const DOCUMENT_SECTION_OPTIONS: { value: DocumentSection; label: string }[] = [
  { value: "Personal", label: "Personal" },
  { value: "Official", label: "Official" },
  { value: "Company", label: "Company" },
];

export function inferDocumentSection(category: string): DocumentSection {
  if (["KYC", "Travel", "Education"].includes(category)) return "Personal";
  if (["Payroll", "Tax", "Insurance", "HR"].includes(category)) return "Official";
  return "Company";
}

export function fileTypesToAccept(types: AllowedFileType[]): string {
  const map: Record<AllowedFileType, string> = {
    pdf: ".pdf",
    jpg: ".jpg,.jpeg",
    png: ".png",
    doc: ".doc",
    docx: ".docx",
  };
  return types.map((t) => map[t]).join(",");
}

export function validateFileAgainstTypes(file: File, types: AllowedFileType[], maxBytes = 8 * 1024 * 1024): string | null {
  const ext = file.name.split(".").pop()?.toLowerCase() || "";
  const allowed = new Set<string>();
  types.forEach((t) => {
    if (t === "jpg") {
      allowed.add("jpg");
      allowed.add("jpeg");
    } else allowed.add(t);
  });
  if (!allowed.has(ext)) {
    return `Allowed types: ${types.map((t) => t.toUpperCase()).join(", ")}`;
  }
  if (file.size > maxBytes) return "File must be 8 MB or smaller.";
  return null;
}

/** Storage keys for a document type instance */
export function getStorageKeys(type: DocumentTypeConfig): string[] {
  if (type.uploadType === "frontBack") return [`${type.id}_front`, `${type.id}_back`];
  if (type.uploadType === "multiple") return [`${type.id}_0`, `${type.id}_1`, `${type.id}_2`];
  return [type.id];
}

export function slugifyDocumentId(name: string): string {
  return name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_|_$/g, "")
    .slice(0, 48);
}
