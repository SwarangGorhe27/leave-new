import { Employee } from "../components/employees/mockData";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://acme.localhost:8000";

const MY_FAMILY_DETAILS_URL = `${API_BASE_URL}/api/employee/my-family-details/`;
const MY_FAMILY_URL = `${API_BASE_URL}/api/employee/my-family/`;
const FAMILY_RELATIONS_URL = `${API_BASE_URL}/api/employee/family/choices/relations/`;
const FAMILY_OCCUPATIONS_URL = `${API_BASE_URL}/api/employee/family/choices/occupations/`;

export interface EmployeeFamilyMemberApi {
  id?: string | null;
  name?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  relation_id?: number | null;
  relation?: string | null;
  relationship_id?: number | null;
  relationship?: string | null;
  date_of_birth?: string | null;
  age?: string | null;
  age_years?: number | null;
  gender_id?: number | null;
  gender?: string | null;
  blood_group_id?: number | null;
  blood_group?: string | null;
  phone?: string | null;
  mobile_no?: string | null;
  occupation_id?: number | null;
  occupation?: string | null;
  is_dependent?: boolean;
  isDependent?: boolean;
  is_emergency_contact?: boolean;
  emergency_contact?: boolean;
}

export interface FamilyChoiceApi {
  id: number;
  label: string;
}

export type FamilyMemberSubmitPayload = Partial<{
  id: string | null;
  name: string | null;
  first_name: string | null;
  last_name: string | null;
  relation_id: number | null;
  relationship_id: number | null;
  date_of_birth: string | null;
  gender_id: number | null;
  blood_group_id: number | null;
  phone: string | null;
  mobile_no: string | null;
  occupation_id: number | null;
  is_dependent: boolean;
  isDependent: boolean;
  is_emergency_contact: boolean;
  emergency_contact: boolean;
  remove: boolean;
  delete: boolean;
}>;

export interface FamilyDetailsSubmitPayload {
  family_details: FamilyMemberSubmitPayload[];
  remarks?: string;
}

interface FamilyDetailsResponse {
  family_details?: EmployeeFamilyMemberApi[];
}

interface ChoicesResponse {
  results?: FamilyChoiceApi[];
}

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

export async function getMyFamilyDetails() {
  const data = await requestJson<FamilyDetailsResponse>(MY_FAMILY_DETAILS_URL, {
    method: "GET",
  });
  return data.family_details ?? [];
}

export async function getMyFamilyRecords() {
  return requestJson<unknown>(MY_FAMILY_URL, { method: "GET" });
}

export async function getFamilyRelationChoices() {
  const data = await requestJson<ChoicesResponse>(FAMILY_RELATIONS_URL, {
    method: "GET",
  });
  return data.results ?? [];
}

export async function getFamilyOccupationChoices() {
  const data = await requestJson<ChoicesResponse>(FAMILY_OCCUPATIONS_URL, {
    method: "GET",
  });
  return data.results ?? [];
}

export async function patchMyFamilyDetails(payload: FamilyDetailsSubmitPayload) {
  return requestJson(MY_FAMILY_DETAILS_URL, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function postMyFamilyDetails(payload: FamilyDetailsSubmitPayload) {
  return requestJson(MY_FAMILY_DETAILS_URL, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export type EmployeeFamilyMember = Employee["family"][number] & {
  id?: string | null;
  apiId?: string | null;
  relationId?: number | null;
  genderId?: number | null;
  bloodGroupId?: number | null;
  occupationId?: number | null;
  age?: string | null;
  ageYears?: number | null;
};

function splitName(name: string) {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  return {
    firstName: parts[0] ?? "",
    lastName: parts.slice(1).join(" ") || "",
  };
}

export function familyDetailsToEmployeeFamily(
  rows: EmployeeFamilyMemberApi[]
): EmployeeFamilyMember[] {
  return rows.map((row) => ({
    id: row.id ?? undefined,
    apiId: row.id ?? undefined,
    name:
      row.name ??
      [row.first_name, row.last_name].filter(Boolean).join(" ") ??
      "",
    relationship: row.relationship ?? row.relation ?? "",
    dob: row.date_of_birth ?? "",
    occupation: row.occupation ?? "",
    gender: row.gender ?? "",
    bloodGroup: row.blood_group ?? "",
    phone: row.phone ?? row.mobile_no ?? "",
    isDependent: Boolean(row.isDependent ?? row.is_dependent),
    isEmergencyContact: Boolean(row.emergency_contact ?? row.is_emergency_contact),
    relationId: row.relationship_id ?? row.relation_id ?? null,
    genderId: row.gender_id ?? null,
    bloodGroupId: row.blood_group_id ?? null,
    occupationId: row.occupation_id ?? null,
    age: row.age ?? null,
    ageYears: row.age_years ?? null,
  }));
}

export function employeeFamilyToSubmitRows(
  family: EmployeeFamilyMember[],
  resolveIds: {
    relationId: (label: string, current?: number | null) => number | null | undefined;
    genderId: (label: string, current?: number | null) => number | null | undefined;
    bloodGroupId: (label: string, current?: number | null) => number | null | undefined;
    occupationId: (label: string, current?: number | null) => number | null | undefined;
  }
): FamilyMemberSubmitPayload[] {
  return family.map((member) => {
    const { firstName, lastName } = splitName(member.name);

    return {
      id: member.apiId ?? member.id ?? undefined,
      name: member.name || null,
      first_name: firstName || null,
      last_name: lastName || null,
      relation_id: resolveIds.relationId(member.relationship, member.relationId),
      relationship_id: resolveIds.relationId(member.relationship, member.relationId),
      date_of_birth: member.dob || null,
      gender_id: resolveIds.genderId(member.gender, member.genderId),
      blood_group_id: resolveIds.bloodGroupId(member.bloodGroup, member.bloodGroupId),
      phone: member.phone || null,
      mobile_no: member.phone || null,
      occupation_id: resolveIds.occupationId(member.occupation, member.occupationId),
      is_dependent: Boolean(member.isDependent),
      isDependent: Boolean(member.isDependent),
      is_emergency_contact: Boolean(member.isEmergencyContact),
      emergency_contact: Boolean(member.isEmergencyContact),
    };
  });
}
