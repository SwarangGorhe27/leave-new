import { Employee } from "../components/employees/mockData";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://acme.localhost:8000";

const MY_LANGUAGE_URL = `${API_BASE_URL}/api/employee/my-language/`;
const MY_LANGUAGE_DETAILS_URL = `${API_BASE_URL}/api/employee/my-language-details/`;
const ADMIN_EMPLOYEE_URL = `${API_BASE_URL}/api/admin/employees`;
const LANGUAGE_MASTER_URL = `${API_BASE_URL}/api/masters/misc/languages/`;
const LANGUAGE_PROFICIENCY_MASTER_URL = `${API_BASE_URL}/api/masters/misc/language-proficiencies/`;

export interface LanguageMasterOption {
  id: number;
  code?: string | null;
  label: string;
  is_active?: boolean;
}

export interface LanguageProficiencyMasterOption {
  id: number;
  code?: string | null;
  label: string;
  level_order?: number;
  is_active?: boolean;
}

export interface EmployeeLanguageDetailApi {
  id?: string | null;
  language_id?: number | null;
  language?: string | null;
  proficiency_level_id?: number | null;
  proficiency_level?: string | null;
  read_proficiency_id?: number | null;
  read_proficiency?: string | null;
  write_proficiency_id?: number | null;
  write_proficiency?: string | null;
  speak_proficiency_id?: number | null;
  speak_proficiency?: string | null;
  can_read?: boolean;
  can_write?: boolean;
  can_speak?: boolean;
  is_mother_tongue?: boolean;
}

export type EmployeeLanguageRow = NonNullable<Employee["languages"]>[number] & {
  id?: string | null;
  apiId?: string | null;
  languageId?: number | null;
  proficiencyLevelId?: number | null;
  readProficiencyId?: number | null;
  writeProficiencyId?: number | null;
  speakProficiencyId?: number | null;
  isMotherTongue?: boolean;
};

export interface LanguageDetailsSubmitPayload {
  language_details: Array<{
    id?: string | null;
    language_id?: number | null;
    language?: string | null;
    proficiency_level_id?: number | null;
    proficiency_level?: string | null;
    read_proficiency_id?: number | null;
    write_proficiency_id?: number | null;
    speak_proficiency_id?: number | null;
    can_read: boolean;
    can_write: boolean;
    can_speak: boolean;
    is_mother_tongue?: boolean;
  }>;
  remarks?: string;
}

interface LanguageDetailsResponse {
  language_details?: EmployeeLanguageDetailApi[];
}

interface MasterListResponse<T> {
  results?: T[];
  data?: T[] | { results?: T[] };
}

type MasterListApiResponse<T> = MasterListResponse<T> | T[];

function authHeaders() {
  const token = localStorage.getItem("hrms_access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function parseApiError(response: Response) {
  try {
    const data = await response.json();
    return data?.detail || data?.non_field_errors || JSON.stringify(data);
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

  return (await response.json()) as T;
}

function labelFromMaster(value: unknown) {
  if (!value || typeof value !== "object") return value == null ? "" : String(value);
  const record = value as { label?: unknown; name?: unknown; code?: unknown };
  return String(record.label ?? record.name ?? record.code ?? "");
}

function idFromMaster(value: unknown) {
  if (!value || typeof value !== "object") return null;
  const record = value as { id?: unknown };
  return typeof record.id === "number" ? record.id : null;
}

function languageLabel(row: EmployeeLanguageDetailApi) {
  return labelFromMaster(row.language) || "";
}

function proficiencyLabel(row: EmployeeLanguageDetailApi) {
  return (
    labelFromMaster(row.proficiency_level) ||
    labelFromMaster(row.read_proficiency) ||
    labelFromMaster(row.write_proficiency) ||
    labelFromMaster(row.speak_proficiency) ||
    ""
  );
}

function proficiencyId(row: EmployeeLanguageDetailApi) {
  return (
    row.proficiency_level_id ??
    row.read_proficiency_id ??
    row.write_proficiency_id ??
    row.speak_proficiency_id ??
    idFromMaster(row.proficiency_level) ??
    idFromMaster(row.read_proficiency) ??
    idFromMaster(row.write_proficiency) ??
    idFromMaster(row.speak_proficiency)
  );
}

export async function getMyLanguage() {
  return requestJson<EmployeeLanguageDetailApi[]>(MY_LANGUAGE_URL, { method: "GET" });
}

export async function getMyLanguageDetails() {
  const data = await requestJson<LanguageDetailsResponse>(MY_LANGUAGE_DETAILS_URL, {
    method: "GET",
  });
  return data.language_details ?? [];
}

export async function postMyLanguageDetails(payload: LanguageDetailsSubmitPayload) {
  return requestJson(MY_LANGUAGE_DETAILS_URL, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function patchMyLanguageDetails(payload: LanguageDetailsSubmitPayload) {
  return requestJson(MY_LANGUAGE_DETAILS_URL, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function getEmployeeLanguageDetails(employeeId: string) {
  const data = await requestJson<LanguageDetailsResponse>(
    `${ADMIN_EMPLOYEE_URL}/${employeeId}/language-details/`,
    { method: "GET" }
  );
  return data.language_details ?? [];
}

export async function patchEmployeeLanguageDetails(
  employeeId: string,
  payload: LanguageDetailsSubmitPayload
) {
  const data = await requestJson<LanguageDetailsResponse>(
    `${ADMIN_EMPLOYEE_URL}/${employeeId}/language-details/`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    }
  );
  return data.language_details ?? [];
}

export async function getLanguageChoices() {
  const data = await requestJson<MasterListApiResponse<LanguageMasterOption>>(
    `${LANGUAGE_MASTER_URL}?is_active=true&page=1`,
    { method: "GET" }
  );
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.data)) return data.data;
  return data.results ?? data.data?.results ?? [];
}

export async function getLanguageProficiencyChoices() {
  const data = await requestJson<MasterListApiResponse<LanguageProficiencyMasterOption>>(
    `${LANGUAGE_PROFICIENCY_MASTER_URL}?is_active=true&page=1`,
    { method: "GET" }
  );
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.data)) return data.data;
  return data.results ?? data.data?.results ?? [];
}

export function languageDetailsToEmployeeRows(rows: EmployeeLanguageDetailApi[]): EmployeeLanguageRow[] {
  return rows.map((row) => ({
    id: row.id ?? undefined,
    apiId: row.id ?? undefined,
    language: languageLabel(row),
    proficiency: proficiencyLabel(row),
    canRead: Boolean(row.can_read),
    canWrite: Boolean(row.can_write),
    canSpeak: Boolean(row.can_speak),
    languageId: row.language_id ?? idFromMaster(row.language),
    proficiencyLevelId: proficiencyId(row),
    readProficiencyId: row.read_proficiency_id ?? null,
    writeProficiencyId: row.write_proficiency_id ?? null,
    speakProficiencyId: row.speak_proficiency_id ?? null,
    isMotherTongue: Boolean(row.is_mother_tongue),
  }));
}

function resolveMasterId<T extends { id: number; label: string; code?: string | null }>(
  value: string,
  records: T[],
  current?: number | null
) {
  const normalizedValue = value.trim().toLowerCase();
  const selected = records.find(
    (record) =>
      record.label.trim().toLowerCase() === normalizedValue ||
      String(record.code ?? "").trim().toLowerCase() === normalizedValue
  );
  return selected?.id ?? current ?? null;
}

export function employeeLanguageRowsToPayload(
  rows: EmployeeLanguageRow[],
  masters: {
    languages: LanguageMasterOption[];
    proficiencies: LanguageProficiencyMasterOption[];
  }
): LanguageDetailsSubmitPayload {
  return {
    language_details: rows.map((row) => {
      const languageId = resolveMasterId(row.language, masters.languages, row.languageId);
      const proficiencyLevelId = resolveMasterId(
        row.proficiency,
        masters.proficiencies,
        row.proficiencyLevelId
      );
      const readProficiencyId = row.canRead ? proficiencyLevelId ?? row.readProficiencyId ?? null : null;
      const writeProficiencyId = row.canWrite ? proficiencyLevelId ?? row.writeProficiencyId ?? null : null;
      const speakProficiencyId = row.canSpeak ? proficiencyLevelId ?? row.speakProficiencyId ?? null : null;

      return {
        id: row.apiId ?? row.id ?? undefined,
        language_id: languageId,
        language: row.language || null,
        proficiency_level_id: proficiencyLevelId,
        proficiency_level: row.proficiency || null,
        read_proficiency_id: readProficiencyId,
        write_proficiency_id: writeProficiencyId,
        speak_proficiency_id: speakProficiencyId,
        can_read: Boolean(row.canRead),
        can_write: Boolean(row.canWrite),
        can_speak: Boolean(row.canSpeak),
        is_mother_tongue: Boolean(row.isMotherTongue),
      };
    }),
  };
}
