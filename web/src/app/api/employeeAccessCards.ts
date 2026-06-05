import { AccessCardEntry } from "../components/employees/mockData";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://acme.localhost:8000";

export interface AccessCardApi {
  id: string;
  employee: string;
  employee_id_display: string;
  employee_name: string;
  access_card_number: string;
  from_date: string;
  to_date: string | null;
  is_active: boolean;
}

export interface AccessCardCreatePayload {
  access_card_number: string;
  from_date: string;
  to_date?: string | null;
}

export interface AccessCardUpdatePayload {
  access_card_number?: string;
  from_date?: string;
  to_date?: string | null;
}

interface AccessCardListResponse {
  status?: string;
  count?: number;
  data?: AccessCardApi[];
}

interface AccessCardMutationResponse {
  status?: string;
  detail?: string;
  data?: AccessCardApi;
  errors?: Record<string, string[] | string>;
}

function authHeaders() {
  const token = localStorage.getItem("hrms_access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export function extractAccessCardApiError(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message.trim()) return error.message;
  return fallback;
}

async function parseApiError(response: Response) {
  try {
    const data = (await response.json()) as AccessCardMutationResponse;
    if (typeof data.detail === "string" && data.detail.trim()) return data.detail;
    if (data.errors && typeof data.errors === "object") {
      for (const value of Object.values(data.errors)) {
        if (Array.isArray(value) && typeof value[0] === "string") return value[0];
        if (typeof value === "string" && value.trim()) return value;
      }
    }
    return JSON.stringify(data);
  } catch {
    return `Request failed with status ${response.status}`;
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

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  if (response.status === 204) {
    return {} as T;
  }

  return (await response.json()) as T;
}

function accessCardsBaseUrl(employeeId: string) {
  return `${API_BASE_URL}/api/employees/${employeeId}/access-cards`;
}

export async function getEmployeeAccessCards(employeeId: string): Promise<AccessCardApi[]> {
  const data = await requestJson<AccessCardListResponse>(accessCardsBaseUrl(employeeId), {
    method: "GET",
  });
  return data.data ?? [];
}

export async function createEmployeeAccessCard(
  employeeId: string,
  payload: AccessCardCreatePayload,
): Promise<AccessCardApi> {
  const data = await requestJson<AccessCardMutationResponse>(accessCardsBaseUrl(employeeId), {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!data.data) {
    throw new Error("Access card was created but no data was returned.");
  }
  return data.data;
}

export async function updateEmployeeAccessCard(
  employeeId: string,
  cardId: string,
  payload: AccessCardUpdatePayload,
): Promise<AccessCardApi> {
  const data = await requestJson<AccessCardMutationResponse>(
    `${accessCardsBaseUrl(employeeId)}/${cardId}`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    },
  );
  if (!data.data) {
    throw new Error("Access card was updated but no data was returned.");
  }
  return data.data;
}

export async function deleteEmployeeAccessCard(employeeId: string, cardId: string) {
  await requestJson<{ status?: string; detail?: string }>(
    `${accessCardsBaseUrl(employeeId)}/${cardId}`,
    { method: "DELETE" },
  );
}

export function accessCardsToEmployeeEntries(
  rows: AccessCardApi[],
  employeeCode: string,
): AccessCardEntry[] {
  return rows.map((row) => ({
    id: row.id,
    employeeId: employeeCode,
    cardNumber: row.access_card_number,
  }));
}

export function isPersistedAccessCardId(id: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id);
}

export function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10);
}
