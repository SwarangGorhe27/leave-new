import api, { unwrap } from "../../../api/client";
import type { ProfileChangeRequest, RequestStatus, SectionKey } from "./types";

export interface ApiChangeRequest {
  id: string;
  module: string;
  status: string;
  request_data: Record<string, unknown>;
  old_data: Record<string, unknown>;
  employee: string;
  employee_name?: string;
  employee_code?: string;
  reviewed_by_name?: string | null;
  reviewed_at?: string | null;
  admin_remarks?: string | null;
  created_at: string;
}

const MODULE_LABELS: Record<string, string> = {
  PERSONAL: "Personal Details",
  ADDRESS: "Address Section",
  FAMILY: "Family Details",
  EDUCATION: "Education Details",
  EMPLOYMENT: "Employment Details",
  BANK: "Bank & Statutory Details",
  NOMINEE: "Nominee Details",
  INSURANCE: "Insurance Details",
  LANGUAGE: "Language Details",
  PASSPORT: "Passport & Visa",
  MEDICAL: "Medical Details",
  SOCIAL: "Social Profile",
};

const MODULE_TO_SECTION: Record<string, SectionKey> = {
  PERSONAL: "personalDetails",
  ADDRESS: "addresses",
  FAMILY: "familyDetails",
  EDUCATION: "educationDetails",
  EMPLOYMENT: "employmentDetails",
  BANK: "bankAndStatutoryDetails",
  NOMINEE: "nomineeDetails",
  INSURANCE: "insuranceDetails",
  LANGUAGE: "languageDetails",
};

function normalizeStatus(status: string): RequestStatus {
  const value = status.toLowerCase();
  if (value === "pending" || value === "approved" || value === "rejected" || value === "draft") {
    return value;
  }
  return "pending";
}

export function mapApiChangeRequest(row: ApiChangeRequest): ProfileChangeRequest {
  const moduleKey = row.module?.toUpperCase() ?? "PERSONAL";
  return {
    id: row.id,
    employee_id: row.employee,
    section: (MODULE_TO_SECTION[moduleKey] ?? "personalDetails") as SectionKey,
    section_label: MODULE_LABELS[moduleKey] ?? moduleKey,
    changes: {
      oldValue: row.old_data ?? {},
      newValue: row.request_data ?? {},
    },
    status: normalizeStatus(row.status),
    created_at: row.created_at,
    reviewed_by: row.reviewed_by_name ?? null,
    reviewed_at: row.reviewed_at ?? null,
    rejection_comment: row.status?.toUpperCase() === "REJECTED" ? row.admin_remarks ?? "" : undefined,
    _source: "api",
    _employeeName: row.employee_name,
    _employeeCode: row.employee_code,
  };
}

export async function fetchAdminChangeRequests(): Promise<ProfileChangeRequest[]> {
  try {
    const response = await api.get("/admin/change-requests/", {
      params: { page_size: 500 },
    });
    const payload = response.data?.data ?? unwrap<ApiChangeRequest[]>(response);
    if (!Array.isArray(payload)) return [];
    return payload.map(mapApiChangeRequest);
  } catch {
    return [];
  }
}

export async function approveApiChangeRequest(
  requestId: string,
  adminRemarks?: string,
): Promise<boolean> {
  try {
    await api.post(`/admin/change-request/${requestId}/approve/`, {
      admin_remarks: adminRemarks ?? "",
    });
    return true;
  } catch {
    return false;
  }
}

export async function rejectApiChangeRequest(
  requestId: string,
  adminRemarks: string,
): Promise<boolean> {
  try {
    await api.post(`/admin/change-request/${requestId}/reject/`, {
      admin_remarks: adminRemarks,
    });
    return true;
  } catch {
    return false;
  }
}

export function isApiRequestId(id: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id);
}
