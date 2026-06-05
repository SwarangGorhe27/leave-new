import { BackgroundCheckRecord } from "../components/employees/mockData";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://acme.localhost:8000";

export interface BackgroundVerificationApi {
  id: string;
  employee: string;
  verificationStatusId?: string;
  verificationStatus?: string;
  verificationStatusCode?: string;
  agencyName?: string | null;
  verifiedBy?: string | null;
  referenceNumber?: string | null;
  completionDate?: string | null;
  agencyRemarks?: string | null;
}

export interface BackgroundVerificationWritePayload {
  verificationStatus?: string;
  verificationStatusId?: string;
  agencyName?: string | null;
  verifiedBy?: string | null;
  referenceNumber?: string | null;
  completionDate?: string | null;
  agencyRemarks?: string | null;
}

function authHeaders() {
  const token = localStorage.getItem("hrms_access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export function isPersistedBackgroundCheckId(id: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id);
}

export class BackgroundVerificationApiError extends Error {
  fieldErrors: Record<string, string>;

  constructor(message: string, fieldErrors: Record<string, string> = {}) {
    super(message);
    this.name = "BackgroundVerificationApiError";
    this.fieldErrors = fieldErrors;
  }
}

const API_FIELD_TO_FORM: Record<string, string> = {
  verificationStatus: "verificationStatus",
  agencyName: "agencyName",
  verifiedBy: "verifiedBy",
  referenceNumber: "referenceNumber",
  completionDate: "completedOn",
  agencyRemarks: "remarks",
};

export function mapBackgroundFieldErrors(
  fieldErrors: Record<string, string>,
): Record<string, string> {
  const row: Record<string, string> = {};
  for (const [apiKey, message] of Object.entries(fieldErrors)) {
    const formKey = API_FIELD_TO_FORM[apiKey];
    if (formKey && message.trim()) row[formKey] = message;
  }
  return row;
}

async function parseApiError(response: Response): Promise<never> {
  try {
    const data = (await response.json()) as Record<string, unknown>;
    const fieldErrors: Record<string, string> = {};

    if (typeof data.detail === "string" && data.detail.trim()) {
      throw new BackgroundVerificationApiError(data.detail, fieldErrors);
    }

    for (const key of Object.keys(API_FIELD_TO_FORM)) {
      const value = data[key];
      if (Array.isArray(value) && typeof value[0] === "string") {
        fieldErrors[key] = value[0];
      } else if (typeof value === "string" && value.trim()) {
        fieldErrors[key] = value;
      }
    }

    if (Object.keys(fieldErrors).length) {
      throw new BackgroundVerificationApiError(Object.values(fieldErrors)[0], fieldErrors);
    }

    throw new BackgroundVerificationApiError(JSON.stringify(data), fieldErrors);
  } catch (error) {
    if (error instanceof BackgroundVerificationApiError) throw error;
    throw new BackgroundVerificationApiError(`Request failed with status ${response.status}`);
  }
}

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      ...authHeaders(),
      ...(init?.headers ?? {}),
    },
  });

  if (response.status === 404) {
    throw new BackgroundVerificationApiError("Background verification not found.");
  }

  if (!response.ok) {
    throw await parseApiError(response);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return (await response.json()) as T;
}

function backgroundBaseUrl(employeeId: string) {
  return `${API_BASE_URL}/api/employees/${employeeId}/background-verification`;
}

export function extractBackgroundVerificationApiError(error: unknown, fallback: string): string {
  if (error instanceof BackgroundVerificationApiError && error.message.trim()) {
    return error.message;
  }
  if (error instanceof Error && error.message.trim()) return error.message;
  return fallback;
}

export async function getEmployeeBackgroundVerification(
  employeeId: string,
): Promise<BackgroundVerificationApi | null> {
  const response = await fetch(`${backgroundBaseUrl(employeeId)}/`, {
    method: "GET",
    headers: authHeaders(),
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw await parseApiError(response);
  }

  return (await response.json()) as BackgroundVerificationApi;
}

export async function createEmployeeBackgroundVerification(
  employeeId: string,
  payload: BackgroundVerificationWritePayload,
): Promise<BackgroundVerificationApi> {
  return requestJson<BackgroundVerificationApi>(`${backgroundBaseUrl(employeeId)}/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateEmployeeBackgroundVerification(
  employeeId: string,
  payload: Partial<BackgroundVerificationWritePayload>,
): Promise<BackgroundVerificationApi> {
  return requestJson<BackgroundVerificationApi>(`${backgroundBaseUrl(employeeId)}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function apiToBackgroundCheckRecord(row: BackgroundVerificationApi): BackgroundCheckRecord {
  return {
    id: row.id,
    verificationStatus: row.verificationStatusId ?? "",
    verificationStatusLabel: row.verificationStatus ?? "",
    agencyName: row.agencyName ?? "",
    verifiedBy: row.verifiedBy ?? "",
    referenceNumber: row.referenceNumber ?? "",
    completedOn: row.completionDate ?? "",
    remarks: row.agencyRemarks ?? "",
  };
}

export function emptyBackgroundCheckRecord(): BackgroundCheckRecord {
  return {
    id: "bg-new",
    verificationStatus: "",
    verificationStatusLabel: "",
    agencyName: "",
    verifiedBy: "",
    referenceNumber: "",
    completedOn: "",
    remarks: "",
  };
}

function resolveStatusId(
  value: string,
  options: Array<{ value: string; label: string }>,
): string {
  if (!value.trim()) return "";
  if (isPersistedBackgroundCheckId(value)) return value;
  const match = options.find(
    (option) =>
      option.value === value ||
      option.label.toLowerCase() === value.toLowerCase(),
  );
  return match?.value ?? value;
}

export function backgroundCheckToWritePayload(
  record: BackgroundCheckRecord,
  statusOptions: Array<{ value: string; label: string }>,
): BackgroundVerificationWritePayload {
  const statusId = resolveStatusId(record.verificationStatus, statusOptions);
  return {
    verificationStatus: statusId,
    agencyName: record.agencyName?.trim() || null,
    verifiedBy: record.verifiedBy?.trim() || null,
    referenceNumber: record.referenceNumber?.trim() || null,
    completionDate: record.completedOn?.trim() || null,
    agencyRemarks: record.remarks?.trim() || null,
  };
}

export function resolveStatusDisplay(
  record: BackgroundCheckRecord,
  options: Array<{ value: string; label: string }>,
): string {
  if (record.verificationStatusLabel?.trim()) return record.verificationStatusLabel;
  const match = options.find((o) => o.value === record.verificationStatus);
  return match?.label ?? record.verificationStatus;
}
