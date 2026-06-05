import api from "@api/client";
import type { Employee } from "../../components/employees/mockData";

/* ------------------------------------------------------------------ */
/*  API response types                                                  */
/* ------------------------------------------------------------------ */

export interface OrgChartNodeDto {
  id: string;
  employee_code: string;
  label: string;
  full_name: string;
  designation: string | null;
  department: string | null;
  team: string | null;
  manager_id: string | null;
  is_top_level?: boolean;
  children?: OrgChartNodeDto[];
}

export interface OrgChartTreeDto {
  company_id: string;
  top_level_manager_id: string | null;
  roots: OrgChartNodeDto[];
  nodes: Array<{ id: string; type: string; data: Record<string, unknown> }>;
  edges: Array<{ id: string; source: string; target: string }>;
}

export interface OrgEmployeeSearchResult {
  id: string;
  employee_code: string;
  full_name: string;
  designation: string | null;
  department: string | null;
  team: string | null;
  manager_id?: string | null;
  manager_name?: string | null;
  status: string;
  profile_picture_url?: string | null;
}

export interface PaginatedResponse<T> {
  success?: boolean;
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/* ------------------------------------------------------------------ */
/*  Mappers                                                             */
/* ------------------------------------------------------------------ */

const AVATAR_COLORS = [
  "#1E293B",
  "#2563EB",
  "#7C3AED",
  "#0891B2",
  "#059669",
  "#D97706",
  "#DC2626",
  "#DB2777",
];

function avatarColorFromId(id: string): string {
  let hash = 0;
  for (let i = 0; i < id.length; i += 1) {
    hash = id.charCodeAt(i) + ((hash << 5) - hash);
  }
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length] ?? "#64748B";
}

function initialsFromName(name: string): string {
  return (
    name
      .split(/[\s._-]+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? "")
      .join("") || "?"
  );
}

export function mapSearchResultToEmployee(
  row: OrgEmployeeSearchResult,
  reportingManagerId?: string | null,
): Employee {
  const resolvedManager =
    reportingManagerId === undefined
      ? row.manager_id ?? undefined
      : reportingManagerId || undefined;

  return {
    id: row.id,
    employeeId: row.employee_code,
    name: row.full_name,
    designation: row.designation ?? "",
    department: row.department ?? "",
    team: row.team ?? "",
    reportingManagerId: resolvedManager,
    email: "",
    phone: "",
    joiningDate: "",
    location: "",
    status: row.status?.toLowerCase() === "inactive" ? "Inactive" : "Active",
    initials: initialsFromName(row.full_name),
    avatarColor: avatarColorFromId(row.id),
    avatar: row.profile_picture_url ?? undefined,
    dateOfBirth: "",
    gender: "",
    maritalStatus: "",
    bloodGroup: "",
    nationality: "",
    bankName: "",
    accountNumber: "",
    ifscCode: "",
    pfNumber: "",
    esiNumber: "",
    family: [],
  } as Employee;
}

export function flattenOrgChartTree(roots: OrgChartNodeDto[]): Employee[] {
  const employees: Employee[] = [];

  const walk = (node: OrgChartNodeDto, managerId: string | null) => {
    employees.push(
      mapSearchResultToEmployee(
        {
          id: node.id,
          employee_code: node.employee_code,
          full_name: node.full_name,
          designation: node.designation,
          department: node.department,
          team: node.team,
          manager_id: node.manager_id,
          status: "Active",
        },
        managerId,
      ),
    );
    node.children?.forEach((child) => walk(child, node.id));
  };

  roots.forEach((root) => walk(root, null));
  return employees;
}

/* ------------------------------------------------------------------ */
/*  API calls                                                           */
/* ------------------------------------------------------------------ */

async function fetchAllPages<T>(
  fetchPage: (page: number) => Promise<PaginatedResponse<T>>,
): Promise<T[]> {
  const items: T[] = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const response = await fetchPage(page);
    items.push(...(response.results ?? []));
    hasMore = Boolean(response.next);
    page += 1;
    if (page > 50) break;
  }

  return items;
}

export async function fetchOrgChartTree(params?: {
  team?: string;
  manager_id?: string;
}): Promise<OrgChartTreeDto> {
  const response = await api.get<OrgChartTreeDto>("/employees/org-chart/tree/", { params });
  return response.data;
}

export async function fetchUnassignedEmployees(query?: string): Promise<Employee[]> {
  const rows = await fetchAllPages<OrgEmployeeSearchResult>((page) =>
    api
      .get<PaginatedResponse<OrgEmployeeSearchResult>>("/employees/org-chart/unassigned/", {
        params: { page, page_size: 100, q: query || undefined },
      })
      .then((res) => res.data),
  );
  return rows.map((row) => mapSearchResultToEmployee(row));
}

/** Direct reportees of a manager (from employee search, filtered by manager_id). */
export async function fetchDirectReportees(managerId: string): Promise<Employee[]> {
  const all = await searchOrgChartEmployees({});
  const managerKey = managerId.toLowerCase();
  return all.filter(
    (employee) => (employee.reportingManagerId ?? "").toLowerCase() === managerKey,
  );
}

export async function searchOrgChartEmployees(params?: {
  q?: string;
  team?: string;
}): Promise<Employee[]> {
  const rows = await fetchAllPages<OrgEmployeeSearchResult>((page) =>
    api
      .get<PaginatedResponse<OrgEmployeeSearchResult>>("/employees/employees/search/", {
        params: {
          page,
          page_size: 100,
          q: params?.q || undefined,
          team: params?.team && params.team !== "All" ? params.team : undefined,
        },
      })
      .then((res) => res.data),
  );
  return rows.map((row) => mapSearchResultToEmployee(row));
}

export async function setTopLevelManager(managerId: string) {
  const response = await api.post("/employees/org-chart/top-level-manager/", {
    manager_id: managerId,
  });
  return response.data;
}

export async function assignManager(employeeId: string, managerId: string | null) {
  const response = await api.post("/employees/org-chart/assign-manager/", {
    employee_id: employeeId,
    manager_id: managerId,
  });
  return response.data;
}

export function extractOrgChartApiError(error: unknown, fallback: string): string {
  const err = error as {
    response?: {
      data?: Record<string, unknown> | string;
    };
    message?: string;
  };
  const data = err.response?.data;
  if (typeof data === "string" && data.trim()) return data;
  if (data && typeof data === "object") {
    if (typeof data.detail === "string") return data.detail;
    for (const value of Object.values(data)) {
      if (typeof value === "string" && value.trim()) return value;
      if (Array.isArray(value) && typeof value[0] === "string") return value[0];
    }
  }
  return err.message?.trim() || fallback;
}

export async function massTransfer(params: {
  from_manager_id: string;
  to_manager_id: string;
  employee_ids: string[];
}) {
  const response = await api.post("/employees/org-chart/mass-transfer/", params);
  return response.data;
}

export async function exportOrgChart(params: {
  format: "png" | "pdf";
  team?: string;
  manager_id?: string;
  image_base64?: string;
}): Promise<{ blob: Blob; filename: string }> {
  const response = await api.post("/employees/org-chart/export/", params, {
    responseType: "blob",
  });

  const disposition = response.headers["content-disposition"] as string | undefined;
  const filenameMatch = disposition?.match(/filename="?([^"]+)"?/);
  const filename = filenameMatch?.[1] ?? `org-chart.${params.format}`;

  return { blob: response.data as Blob, filename };
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
