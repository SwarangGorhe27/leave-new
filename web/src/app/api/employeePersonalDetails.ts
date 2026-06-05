import { Employee } from "../components/employees/mockData";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://acme.localhost:8000";

const MY_PERSONAL_DETAILS_URL = `${API_BASE_URL}/api/employee/my-personal-details/`;

export interface EmployeePersonalDetailsApi {
  first_name: string | null;
  middle_name: string | null;
  last_name: string | null;
  date_of_birth: string | null;
  actual_dob: string | null;
  actual_date_of_birth: string | null;
  joining_date: string | null;
  gender_id: number | null;
  gender: string | null;
  marital_status_id: number | null;
  marital_status: string | null;
  religion_id: number | null;
  religion: string | null;
  caste_category_id: number | null;
  caste_category: string | null;
  place_of_birth: string | null;
  is_physically_challenged: boolean;
  father_name: string | null;
  spouse_name: string | null;
  blood_group_id: number | null;
  blood_group: string | null;
  nationality_id: number | null;
  nationality: string | null;
  caste_id: number | null;
  caste: string | null;
  identification_mark: string | null;
  height: string | null;
  height_cm: string | null;
  weight: string | null;
  weight_kg: string | null;
  is_international_employee: boolean;
}

export type PersonalDetailsSubmitPayload = Partial<{
  first_name: string | null;
  middle_name: string | null;
  last_name: string | null;
  date_of_birth: string | null;
  actual_dob: string | null;
  actual_date_of_birth: string | null;
  joining_date: string | null;
  gender_id: number | null;
  marital_status_id: number | null;
  religion_id: number | null;
  caste_category_id: number | null;
  place_of_birth: string | null;
  is_physically_challenged: boolean;
  father_name: string | null;
  spouse_name: string | null;
  blood_group_id: number | null;
  nationality_id: number | null;
  caste_id: number | null;
  identification_mark: string | null;
  height_cm: string | null;
  weight_kg: string | null;
  is_international_employee: boolean;
  remarks: string;
}>;

interface PersonalDetailsResponse {
  personal_details?: EmployeePersonalDetailsApi;
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

export async function getMyPersonalDetails() {
  const response = await fetch(MY_PERSONAL_DETAILS_URL, {
    method: "GET",
    headers: authHeaders(),
  });

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  const data = (await response.json()) as PersonalDetailsResponse;
  return data.personal_details;
}

export async function patchMyPersonalDetails(payload: PersonalDetailsSubmitPayload) {
  const response = await fetch(MY_PERSONAL_DETAILS_URL, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  return response.json();
}

export async function postMyPersonalDetails(payload: PersonalDetailsSubmitPayload) {
  const response = await fetch(MY_PERSONAL_DETAILS_URL, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  return response.json();
}

export function personalDetailsToEmployee(
  employee: Employee,
  details: EmployeePersonalDetailsApi
): Employee {
  const firstName = details.first_name ?? "";
  const middleName = details.middle_name ?? "";
  const lastName = details.last_name ?? "";
  const fullName = [firstName, middleName, lastName].filter(Boolean).join(" ");

  return {
    ...employee,
    name: fullName || employee.name,
    firstName,
    middleName,
    lastName,
    dateOfBirth: details.date_of_birth ?? "",
    actualDob: details.actual_dob ?? details.actual_date_of_birth ?? "",
    joiningDate: details.joining_date ?? employee.joiningDate,
    gender: details.gender ?? "",
    maritalStatus: details.marital_status ?? "",
    bloodGroup: details.blood_group ?? "",
    nationality: details.nationality ?? "",
    religion: details.religion ?? "",
    caste: details.caste ?? "",
    casteCategory: details.caste_category ?? "",
    placeOfBirth: details.place_of_birth ?? "",
    identificationMark: details.identification_mark ?? "",
    isPhysicallyChallenged: details.is_physically_challenged,
    isInternationalEmployee: details.is_international_employee,
    fathersName: details.father_name ?? "",
    spouseName: details.spouse_name ?? "",
  };
}

export function employeeToPersonalDetailsPayload(
  employee: Employee,
  source?: EmployeePersonalDetailsApi
): PersonalDetailsSubmitPayload {
  return {
    first_name: employee.firstName ?? "",
    middle_name: employee.middleName ?? "",
    last_name: employee.lastName ?? "",
    father_name: employee.fathersName ?? "",
    spouse_name: employee.spouseName ?? "",
    date_of_birth: employee.dateOfBirth || null,
    actual_dob: employee.actualDob || null,
    joining_date: employee.joiningDate || null,
    place_of_birth: employee.placeOfBirth ?? "",
    identification_mark: employee.identificationMark ?? "",
    is_physically_challenged: !!employee.isPhysicallyChallenged,
    is_international_employee: !!employee.isInternationalEmployee,
    gender_id: source?.gender_id ?? undefined,
    marital_status_id: source?.marital_status_id ?? undefined,
    religion_id: source?.religion_id ?? undefined,
    caste_category_id: source?.caste_category_id ?? undefined,
    blood_group_id: source?.blood_group_id ?? undefined,
    nationality_id: source?.nationality_id ?? undefined,
    caste_id: source?.caste_id ?? undefined,
  };
}
