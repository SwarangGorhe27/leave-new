import api from '@/api/client';
import type { MasterListQuery, MasterRecord, PaginatedMasterResponse } from "./types";

const DEMO_STORAGE_PREFIX = "hrms-superadmin-demo-masters";
const ALLOW_DEMO_MASTER_FALLBACK =
  import.meta.env.VITE_ALLOW_DEMO_MASTER_FALLBACK === "true";

// These keys must NEVER be seeded from demo data — always fetched from the real API.
const REAL_API_ONLY_MASTERS = new Set(["ReportingManager"]);
// Clear any stale demo cache for real-API-only masters on every load.
REAL_API_ONLY_MASTERS.forEach((key) =>
  localStorage.removeItem(`${DEMO_STORAGE_PREFIX}:${key}`)
);

const DEMO_MASTERS: Record<string, MasterRecord[]> = {
  Company: [
    { id: "company-1", code: "COOL", label: "Coolor HRMS Pvt Ltd", name: "Coolor HRMS Pvt Ltd", is_active: true },
    { id: "company-2", code: "NOVA", label: "Nova Manufacturing", name: "Nova Manufacturing", is_active: true },
  ],
  Gender: [
    { id: "gender-1", code: "M", label: "Male", name: "Male", is_active: true },
    { id: "gender-2", code: "F", label: "Female", name: "Female", is_active: true },
    { id: "gender-3", code: "O", label: "Other", name: "Other", is_active: true },
  ],
  Salutation: [
    { id: "salutation-1", code: "MR", label: "Mr.", name: "Mr.", is_active: true },
    { id: "salutation-2", code: "MS", label: "Ms.", name: "Ms.", is_active: true },
    { id: "salutation-3", code: "DR", label: "Dr.", name: "Dr.", is_active: true },
  ],
  Department: [
    { id: "department-1", code: "HR", label: "Human Resources", name: "Human Resources", is_active: true, company: "company-1", company_name: "Coolor HRMS Pvt Ltd" },
    { id: "department-2", code: "FIN", label: "Finance", name: "Finance", is_active: true, company: "company-1", company_name: "Coolor HRMS Pvt Ltd" },
    { id: "department-3", code: "OPS", label: "Operations", name: "Operations", is_active: true, company: "company-2", company_name: "Nova Manufacturing" },
  ],
  Designation: [
    { id: "designation-1", code: "HRM", title: "HR Manager", label: "HR Manager", name: "HR Manager", is_active: true, company: "company-1", company_name: "Coolor HRMS Pvt Ltd" },
    { id: "designation-2", code: "SWE", title: "Software Engineer", label: "Software Engineer", name: "Software Engineer", is_active: true, company: "company-1", company_name: "Coolor HRMS Pvt Ltd" },
    { id: "designation-3", code: "SUP", title: "Production Supervisor", label: "Production Supervisor", name: "Production Supervisor", is_active: true, company: "company-2", company_name: "Nova Manufacturing" },
  ],
  Grade: [
    { id: "grade-1", code: "G1", label: "Junior", name: "Junior", is_active: true, company: "company-1", company_name: "Coolor HRMS Pvt Ltd" },
    { id: "grade-2", code: "G2", label: "Senior", name: "Senior", is_active: true, company: "company-1", company_name: "Coolor HRMS Pvt Ltd" },
  ],
  Country: [
    { id: "country-1", code: "IN", iso3_code: "IND", numeric_code: 356, label: "India", name: "India", is_active: true },
    { id: "country-2", code: "US", iso3_code: "USA", numeric_code: 840, label: "United States", name: "United States", is_active: true },
  ],
  State: [
    { id: "state-1", code: "MH", label: "Maharashtra", name: "Maharashtra", country: "country-1", country_name: "India", is_active: true },
    { id: "state-2", code: "KA", label: "Karnataka", name: "Karnataka", country: "country-1", country_name: "India", is_active: true },
  ],
  City: [
    { id: "city-1", code: "MUM", label: "Mumbai", name: "Mumbai", state: "state-1", state_name: "Maharashtra", pincode: "400001", is_active: true },
    { id: "city-2", code: "BLR", label: "Bengaluru", name: "Bengaluru", state: "state-2", state_name: "Karnataka", pincode: "560001", is_active: true },
  ],
};

function storageKey(masterApiName: string) {
  return `${DEMO_STORAGE_PREFIX}:${masterApiName}`;
}

function formatMasterName(masterApiName: string) {
  return masterApiName.replace(/([a-z])([A-Z])/g, "$1 $2").trim();
}

function createGenericSeed(masterApiName: string): MasterRecord[] {
  const label = formatMasterName(masterApiName);
  return [
    {
      id: `${masterApiName.toLowerCase()}-demo-1`,
      code: `${masterApiName.replace(/[^A-Z0-9]/gi, "").slice(0, 4).toUpperCase() || "MST"}01`,
      label: `Default ${label}`,
      name: `Default ${label}`,
      is_active: true,
    },
  ];
}

function readDemoMasters(masterApiName: string): MasterRecord[] {
  const raw = localStorage.getItem(storageKey(masterApiName));
  if (raw) {
    try {
      return JSON.parse(raw) as MasterRecord[];
    } catch {
      // fall through to a fresh seed
    }
  }
  const seeded = DEMO_MASTERS[masterApiName] ?? createGenericSeed(masterApiName);
  localStorage.setItem(storageKey(masterApiName), JSON.stringify(seeded));
  return seeded;
}

function writeDemoMasters(masterApiName: string, records: MasterRecord[]) {
  localStorage.setItem(storageKey(masterApiName), JSON.stringify(records));
}

function matchesSearch(record: MasterRecord, search: string) {
  const haystack = [record.code, record.label, record.name, record.title, record.description]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  return haystack.includes(search.toLowerCase());
}

function applyDemoQuery(records: MasterRecord[], query: MasterListQuery): MasterRecord[] {
  return records.filter((record) => {
    if (query.is_active === "true" && !record.is_active) return false;
    if (query.is_active === "false" && record.is_active) return false;
    if (query.company && String(record.company) !== String(query.company)) return false;
    if (query.search && !matchesSearch(record, query.search)) return false;
    return true;
  });
}

function listDemoMasters(masterApiName: string, query: MasterListQuery): PaginatedMasterResponse<MasterRecord> {
  const results = applyDemoQuery(readDemoMasters(masterApiName), query);
  return { count: results.length, next: null, previous: null, results };
}

function normalizeMasterListResponse(
  data: PaginatedMasterResponse<MasterRecord> | MasterRecord[],
): PaginatedMasterResponse<MasterRecord> {
  if (Array.isArray(data)) {
    return {
      count: data.length,
      next: null,
      previous: null,
      results: data,
    };
  }

  return {
    count: data.count ?? data.results?.length ?? 0,
    next: data.next ?? null,
    previous: data.previous ?? null,
    results: data.results ?? [],
  };
}

function makeDemoRecord(masterApiName: string, payload: Record<string, unknown>): MasterRecord {
  const labelValue = String(payload.label ?? payload.name ?? payload.title ?? `New ${formatMasterName(masterApiName)}`);
  return {
    id: crypto.randomUUID(),
    code: String(payload.code ?? labelValue.replace(/\W+/g, "_").toUpperCase()),
    label: labelValue,
    name: String(payload.name ?? labelValue),
    is_active: payload.is_active === undefined ? true : Boolean(payload.is_active),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...payload,
  };
}

function toQueryString(query: MasterListQuery) {
  const params = new URLSearchParams();
  if (query.search) params.set("search", query.search);
  if (query.company) params.set("company", query.company);
  if (query.is_active) params.set("is_active", query.is_active);
  if (query.page) params.set("page", String(query.page));
  if (query.page_size) params.set("page_size", String(query.page_size));
  const str = params.toString();
  return str ? `?${str}` : "";
}

// Masters that have a dedicated non-generic endpoint returning [{ value, label }]
const DEDICATED_MASTER_ENDPOINTS: Record<string, string> = {
  ReportingManager: '/admin/employees/reporting-managers/',
};

export async function getMasterList(masterApiName: string, query: MasterListQuery) {
  const dedicatedUrl = DEDICATED_MASTER_ENDPOINTS[masterApiName];
  if (dedicatedUrl) {
    const params: Record<string, string> = {};
    if (query.search) params.search = query.search;
    const res = await api.get<{ value: string; label: string }[]>(dedicatedUrl, { params });
    const results: MasterRecord[] = res.data.map((item) => ({
      id: item.value,
      code: item.value,
      label: item.label,
      name: item.label,
      is_active: true,
    }));
    return { count: results.length, next: null, previous: null, results };
  }

  try {
    const res = await api.get<PaginatedMasterResponse<MasterRecord> | MasterRecord[]>(
      `/masters/${masterApiName}/${toQueryString(query)}`,
    );
    return normalizeMasterListResponse(res.data);
  } catch (error) {
    if (!ALLOW_DEMO_MASTER_FALLBACK) {
      console.error(`Failed to load master '${masterApiName}'`, error);
      return { count: 0, next: null, previous: null, results: [] };
    }
    return listDemoMasters(masterApiName, query);
  }
}

export async function createMaster(masterApiName: string, payload: Record<string, unknown>) {
  try {
    const res = await api.post<MasterRecord>(`/masters/${masterApiName}/`, payload);
    return res.data;
  } catch {
    const record = makeDemoRecord(masterApiName, payload);
    writeDemoMasters(masterApiName, [record, ...readDemoMasters(masterApiName)]);
    return record;
  }
}

export async function patchMaster(masterApiName: string, id: string | number, payload: Record<string, unknown>) {
  try {
    const res = await api.patch<MasterRecord>(`/masters/${masterApiName}/${id}/`, payload);
    return res.data;
  } catch {
    const records = readDemoMasters(masterApiName);
    const updated = records.map((record) =>
      String(record.id) === String(id) ? { ...record, ...payload, updated_at: new Date().toISOString() } : record,
    );
    writeDemoMasters(masterApiName, updated);
    return updated.find((record) => String(record.id) === String(id)) ?? records[0];
  }
}

export async function deleteMaster(masterApiName: string, id: string | number) {
  try {
    await api.delete(`/masters/${masterApiName}/${id}/`);
  } catch {
    writeDemoMasters(
      masterApiName,
      readDemoMasters(masterApiName).filter((record) => String(record.id) !== String(id)),
    );
  }
}

