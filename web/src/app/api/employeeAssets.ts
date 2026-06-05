import { AssetEntry } from "../components/employees/mockData";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://acme.localhost:8000";

export interface EmployeeAssetApi {
  id: string;
  asset_name: string;
  asset_code: string | null;
  asset_category: string;
  asset_category_label?: string;
  serial_no: string | null;
  assign_date: string;
  return_date: string | null;
  asset_condition: string | null;
  asset_condition_label?: string;
  status: string;
  remarks: string | null;
  assetName?: string;
  assetId?: string;
  assetCategory?: string;
  assetCategoryLabel?: string;
  serialNumber?: string;
  assignDate?: string;
  returnDate?: string | null;
  assetCondition?: string | null;
  assetConditionLabel?: string;
}

export interface EmployeeAssetWritePayload {
  assetName: string;
  assetId?: string | null;
  assetCategory: string;
  serialNumber?: string | null;
  assignDate: string;
  returnDate?: string | null;
  assetCondition?: string | null;
  status: string;
  remarks?: string | null;
}

const STATUS_TO_API: Record<string, string> = {
  Assigned: "ASSIGNED",
  Returned: "RETURNED",
  Lost: "LOST",
  Damaged: "DAMAGED",
  "Under Repair": "DAMAGED",
  ASSIGNED: "ASSIGNED",
  RETURNED: "RETURNED",
  LOST: "LOST",
  DAMAGED: "DAMAGED",
};

const STATUS_FROM_API: Record<string, string> = {
  ASSIGNED: "Assigned",
  RETURNED: "Returned",
  LOST: "Lost",
  DAMAGED: "Damaged",
};

function authHeaders() {
  const token = localStorage.getItem("hrms_access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export function isPersistedAssetId(id: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id);
}

export function extractAssetApiError(error: unknown, fallback: string): string {
  if (error instanceof AssetApiError && error.message.trim()) return error.message;
  if (error instanceof Error && error.message.trim()) return error.message;
  return fallback;
}

export class AssetApiError extends Error {
  fieldErrors: Record<string, string>;

  constructor(message: string, fieldErrors: Record<string, string> = {}) {
    super(message);
    this.name = "AssetApiError";
    this.fieldErrors = fieldErrors;
  }
}

const API_ERROR_FIELDS = [
  "assignDate",
  "returnDate",
  "assetCategory",
  "assetCondition",
  "assetName",
  "assetId",
  "status",
  "serialNumber",
  "remarks",
] as const;

async function parseApiError(response: Response): Promise<never> {
  try {
    const data = (await response.json()) as Record<string, unknown>;
    const fieldErrors: Record<string, string> = {};

    if (typeof data.detail === "string" && data.detail.trim()) {
      throw new AssetApiError(data.detail, fieldErrors);
    }

    for (const key of API_ERROR_FIELDS) {
      const value = data[key];
      if (Array.isArray(value) && typeof value[0] === "string") {
        fieldErrors[key] = value[0];
      } else if (typeof value === "string" && value.trim()) {
        fieldErrors[key] = value;
      }
    }

    if (Object.keys(fieldErrors).length) {
      const first = Object.values(fieldErrors)[0];
      throw new AssetApiError(first, fieldErrors);
    }

    for (const value of Object.values(data)) {
      if (Array.isArray(value) && typeof value[0] === "string") {
        throw new AssetApiError(value[0], fieldErrors);
      }
      if (typeof value === "string" && value.trim()) {
        throw new AssetApiError(value, fieldErrors);
      }
    }

    throw new AssetApiError(JSON.stringify(data), fieldErrors);
  } catch (error) {
    if (error instanceof AssetApiError) throw error;
    throw new AssetApiError(`Request failed with status ${response.status}`);
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
    throw await parseApiError(response);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return (await response.json()) as T;
}

function assetsBaseUrl(employeeId: string) {
  return `${API_BASE_URL}/api/employees/${employeeId}/asset-details`;
}

export async function getEmployeeAssets(employeeId: string): Promise<EmployeeAssetApi[]> {
  return requestJson<EmployeeAssetApi[]>(`${assetsBaseUrl(employeeId)}/`, { method: "GET" });
}

export async function createEmployeeAsset(
  employeeId: string,
  payload: EmployeeAssetWritePayload,
): Promise<EmployeeAssetApi> {
  return requestJson<EmployeeAssetApi>(`${assetsBaseUrl(employeeId)}/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateEmployeeAsset(
  employeeId: string,
  assetId: string,
  payload: Partial<EmployeeAssetWritePayload>,
): Promise<EmployeeAssetApi> {
  return requestJson<EmployeeAssetApi>(`${assetsBaseUrl(employeeId)}/${assetId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteEmployeeAsset(employeeId: string, assetId: string) {
  await requestJson(`${assetsBaseUrl(employeeId)}/${assetId}/`, { method: "DELETE" });
}

export function todayIsoDate(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function minReturnDate(assignDate: string, today: string): string {
  if (!assignDate.trim()) return today;
  return assignDate > today ? assignDate : today;
}

export function assetsToEmployeeEntries(rows: EmployeeAssetApi[]): AssetEntry[] {
  return rows.map((row) => ({
    id: row.id,
    assetName: row.assetName ?? row.asset_name ?? "",
    assetId: row.assetId ?? row.asset_code ?? "",
    assetCategory: row.assetCategory ?? row.asset_category ?? "",
    assetCategoryLabel: row.assetCategoryLabel ?? row.asset_category_label ?? "",
    serialNumber: row.serialNumber ?? row.serial_no ?? "",
    assignedDate: row.assignDate ?? row.assign_date ?? "",
    returnDate: row.returnDate ?? row.return_date ?? "",
    assetCondition: row.assetCondition ?? row.asset_condition ?? "",
    assetConditionLabel: row.assetConditionLabel ?? row.asset_condition_label ?? "",
    status: STATUS_FROM_API[row.status] ?? row.status ?? "Assigned",
    remarks: row.remarks ?? "",
  }));
}

function resolveMasterOptionId(
  value: string,
  options: Array<{ value: string; label: string }>,
): string {
  if (!value.trim()) return "";
  if (isPersistedAssetId(value)) return value;
  const match = options.find(
    (option) => option.value === value || option.label.toLowerCase() === value.toLowerCase(),
  );
  return match?.value ?? value;
}

export function assetEntryToWritePayload(
  asset: AssetEntry,
  options: {
    categoryOptions: Array<{ value: string; label: string }>;
    conditionOptions: Array<{ value: string; label: string }>;
  },
): EmployeeAssetWritePayload {
  const categoryId = resolveMasterOptionId(asset.assetCategory, options.categoryOptions);
  const conditionRaw = asset.assetCondition?.trim();
  const conditionId = conditionRaw
    ? resolveMasterOptionId(conditionRaw, options.conditionOptions)
    : null;

  return {
    assetName: asset.assetName.trim(),
    assetId: asset.assetId.trim() || null,
    assetCategory: categoryId,
    serialNumber: asset.serialNumber.trim() || null,
    assignDate: asset.assignedDate,
    returnDate: asset.returnDate?.trim() || null,
    assetCondition: conditionId,
    status: STATUS_TO_API[asset.status] ?? "ASSIGNED",
    remarks: asset.remarks?.trim() || null,
  };
}

export function assetEntriesEqual(a: AssetEntry, b: AssetEntry): boolean {
  return (
    a.assetName === b.assetName &&
    a.assetId === b.assetId &&
    a.assetCategory === b.assetCategory &&
    a.serialNumber === b.serialNumber &&
    a.assignedDate === b.assignedDate &&
    (a.returnDate ?? "") === (b.returnDate ?? "") &&
    a.assetCondition === b.assetCondition &&
    a.status === b.status &&
    (a.remarks ?? "") === (b.remarks ?? "")
  );
}

const API_FIELD_TO_FORM: Record<string, string> = {
  assetName: "assetName",
  assetId: "assetId",
  assetCategory: "assetCategory",
  serialNumber: "serialNumber",
  assignDate: "assignedDate",
  returnDate: "returnDate",
  assetCondition: "assetCondition",
  status: "status",
  remarks: "remarks",
};

export function mapAssetFieldErrorsToRowErrors(
  fieldErrors: Record<string, string>,
): Record<string, string> {
  const row: Record<string, string> = {};
  for (const [apiKey, message] of Object.entries(fieldErrors)) {
    const formKey = API_FIELD_TO_FORM[apiKey];
    if (formKey && message.trim()) row[formKey] = message;
  }
  return row;
}

export function buildAssetUpdatePayload(
  previous: AssetEntry,
  next: AssetEntry,
  options: {
    categoryOptions: Array<{ value: string; label: string }>;
    conditionOptions: Array<{ value: string; label: string }>;
  },
): Partial<EmployeeAssetWritePayload> {
  const full = assetEntryToWritePayload(next, options);
  const payload: Partial<EmployeeAssetWritePayload> = {};

  if (previous.assetName !== next.assetName) payload.assetName = full.assetName;
  if (previous.assetId !== next.assetId) payload.assetId = full.assetId;
  if (previous.assetCategory !== next.assetCategory) payload.assetCategory = full.assetCategory;
  if (previous.serialNumber !== next.serialNumber) payload.serialNumber = full.serialNumber;
  if (previous.assignedDate !== next.assignedDate) payload.assignDate = full.assignDate;
  if ((previous.returnDate ?? "") !== (next.returnDate ?? "")) {
    payload.returnDate = full.returnDate ?? null;
  }
  if (previous.assetCondition !== next.assetCondition) {
    payload.assetCondition = full.assetCondition ?? null;
  }
  if (previous.status !== next.status) payload.status = full.status;
  if ((previous.remarks ?? "") !== (next.remarks ?? "")) payload.remarks = full.remarks ?? null;

  return payload;
}
