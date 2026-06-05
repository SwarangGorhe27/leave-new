import * as XLSX from "xlsx";
import {
  bulkImportEmployees,
  createEmployee,
  type AddEmployeePayload,
  type AddEmployeeResponse,
  type BulkImportResult,
} from "@/api/addEmployeeApi";
import { normalizeLegacyEmployee, type Employee } from "@/app/components/employees/mockData";

export type BulkPreviewRow = Record<string, unknown> & {
  isValid?: boolean;
  error?: string;
};

export function cellToIsoDate(value: unknown): string {
  if (value == null || value === "") return "";
  if (typeof value === "number") {
    const parsed = XLSX.SSF.parse_date_code(value);
    if (parsed) {
      const m = String(parsed.m).padStart(2, "0");
      const d = String(parsed.d).padStart(2, "0");
      return `${parsed.y}-${m}-${d}`;
    }
  }
  const s = String(value).trim();
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;
  const dmy = s.match(/^(\d{2})[-/](\d{2})[-/](\d{4})$/);
  if (dmy) return `${dmy[3]}-${dmy[2]}-${dmy[1]}`;
  return s;
}

export function mapBulkRowStatus(status: unknown): Employee["status"] {
  const s = String(status ?? "Active")
    .trim()
    .toLowerCase()
    .replace(/[\s-]+/g, "_");
  if (s === "inactive") return "Inactive";
  if (s === "on_leave" || s === "onleave") return "On Leave";
  return "Active";
}

export function findPreviewRow(
  previewData: BulkPreviewRow[],
  employeeCode: string | null | undefined,
): BulkPreviewRow | undefined {
  if (!employeeCode) return undefined;
  const key = employeeCode.trim().toLowerCase();
  return previewData.find(
    (r) => String(r["Employee No"] ?? "").trim().toLowerCase() === key,
  );
}

/** Maps an import-sheet row to the legacy shape consumed by normalizeLegacyEmployee (same as Add Employee form). */
export function mapPreviewRowToLegacyInput(
  row: BulkPreviewRow,
  employeeCode: string,
  employeeId?: string,
): Record<string, unknown> {
  const firstName = String(row["First Name"] ?? "").trim();
  const lastName = String(row["Last Name"] ?? "").trim();
  const name = `${firstName} ${lastName}`.trim() || employeeCode;
  const initials =
    ((firstName[0] ?? "") + (lastName[0] ?? "")).toUpperCase() ||
    employeeCode.slice(0, 2).toUpperCase();

  return {
    id: employeeId ?? employeeCode,
    name,
    firstName,
    lastName,
    employeeId: employeeCode,
    designation: String(row["Designation / Role"] ?? row["Designation"] ?? ""),
    department: String(row["Department"] ?? ""),
    team: "",
    email: String(row["Email"] ?? ""),
    phone: String(row["Mobile Number"] ?? ""),
    joiningDate: cellToIsoDate(row["Date of Joining"]),
    location: String(row["Work Location"] ?? ""),
    status: mapBulkRowStatus(row["Status"]),
    initials,
    avatarColor: "#334155",
    dateOfBirth: cellToIsoDate(row["Date of Birth"]),
    gender: String(row["Gender"] ?? ""),
    maritalStatus: "",
    bloodGroup: "",
    nationality: "",
    bankName: "",
    accountNumber: "",
    ifscCode: "",
    pfNumber: "",
    esiNumber: "",
    family: [],
    passportNumber: "",
    passportExpiry: "",
    visaType: "",
    visaExpiry: "",
    visaCountry: "",
    positionHistory: [],
    basicSalary: 0,
    hra: 0,
    conveyance: 0,
    medicalAllowance: 0,
    specialAllowance: 0,
    grossSalary: 0,
    pf: 0,
    tds: 0,
    netSalary: 0,
    salutation: String(row["Salutation"] ?? ""),
    aadhaarNumber: String(row["Aadhaar Number"] ?? ""),
  };
}

export function employeeFromBulkSuccess(
  previewRow: BulkPreviewRow,
  employeeCode: string,
  employeeId?: string,
): Employee {
  return normalizeLegacyEmployee(
    mapPreviewRowToLegacyInput(previewRow, employeeCode, employeeId),
  );
}

export function mapPreviewRowToCreatePayload(row: BulkPreviewRow): AddEmployeePayload {
  const employeeCode = String(row["Employee No"] ?? "").trim();
  return {
    employee_code: employeeCode,
    employee_number_series: String(row["Employee Number Series"] ?? "").trim() || null,
    first_name: String(row["First Name"] ?? "").trim(),
    last_name: String(row["Last Name"] ?? "").trim(),
    date_of_birth: cellToIsoDate(row["Date of Birth"]) || "",
    joining_date: cellToIsoDate(row["Date of Joining"]) || "",
    official_email: String(row["Email"] ?? "").trim(),
    mobile_number: String(row["Mobile Number"] ?? "").trim(),
    emergency_contact_name: "",
    emergency_contact_number: "",
    gender: String(row["Gender"] ?? "").trim() || null,
    salutation: String(row["Salutation"] ?? "").trim() || null,
    employee_status: String(row["Status"] ?? "Active").trim().toUpperCase().replace(/\s+/g, "_"),
    employment_type: String(row["Employment Type"] ?? "").trim() || null,
    department: String(row["Department"] ?? "").trim() || null,
    designation: String(row["Designation / Role"] ?? row["Designation"] ?? "").trim() || null,
    work_location: String(row["Work Location"] ?? "").trim() || null,
    aadhaar_number: String(row["Aadhaar Number"] ?? "").trim() || null,
    is_draft: false,
    is_active: true,
  };
}

function extractRowErrors(err: unknown): Record<string, string> {
  const data = (err as { response?: { data?: unknown } })?.response?.data;
  if (!data || typeof data !== "object") {
    return { __all__: "Employee could not be imported." };
  }
  const record = data as Record<string, unknown>;
  if (typeof record.detail === "string") return { __all__: record.detail };
  if (record.errors && typeof record.errors === "object") {
    const errors = record.errors as Record<string, unknown>;
    return Object.fromEntries(
      Object.entries(errors).map(([k, v]) => [
        k,
        Array.isArray(v) ? v.map(String).join(" ") : String(v),
      ]),
    );
  }
  return Object.fromEntries(
    Object.entries(record).map(([k, v]) => [
      k,
      Array.isArray(v) ? v.map(String).join(" ") : String(v),
    ]),
  );
}

/** Fallback when bulk-import endpoint is unavailable: one createEmployee() per valid row. */
export async function bulkImportViaCreateEmployee(
  validRows: BulkPreviewRow[],
): Promise<BulkImportResult> {
  const results: BulkImportResult["results"] = [];
  let success_count = 0;
  let failed_count = 0;

  for (let index = 0; index < validRows.length; index++) {
    const row = validRows[index];
    const rowNumber = index + 2;
    const employeeCode = String(row["Employee No"] ?? "").trim() || null;

    try {
      const response: AddEmployeeResponse = await createEmployee(mapPreviewRowToCreatePayload(row));
      results.push({
        row: rowNumber,
        employee_code: response.employee_code,
        status: "success",
        employee_id: response.employee_id,
      } as BulkImportResult["results"][number]);
      success_count += 1;
    } catch (err) {
      results.push({
        row: rowNumber,
        employee_code: employeeCode,
        status: "failed",
        errors: extractRowErrors(err),
      });
      failed_count += 1;
    }
  }

  return {
    total_rows: validRows.length,
    success_count,
    failed_count,
    results,
  };
}

export async function runBulkImport(
  file: File,
  validPreviewRows: BulkPreviewRow[],
): Promise<BulkImportResult> {
  try {
    return await bulkImportEmployees(file);
  } catch (err: unknown) {
    const status = (err as { response?: { status?: number } })?.response?.status;
    if (status === 404 || status === 405) {
      return bulkImportViaCreateEmployee(validPreviewRows);
    }
    throw err;
  }
}

/** Build normalized employees for Redux (same shape as single Add Employee submit). */
export function buildEmployeesFromImportResult(
  result: BulkImportResult,
  previewData: BulkPreviewRow[],
): Employee[] {
  const employees: Employee[] = [];

  for (const rowResult of result.results) {
    if (rowResult.status !== "success" || !rowResult.employee_code) continue;

    const previewRow = findPreviewRow(previewData, rowResult.employee_code);
    if (!previewRow) continue;

    const employeeId = (rowResult as { employee_id?: string }).employee_id;
    employees.push(
      employeeFromBulkSuccess(previewRow, rowResult.employee_code, employeeId),
    );
  }

  return employees;
}
