import { Employee } from "../components/employees/mockData";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://acme.localhost:8000";

const MY_MEDICAL_DETAILS_URL = `${API_BASE_URL}/api/employee/my-medical-details/`;
const EMPLOYEE_MEDICAL_DETAILS_URL = `${API_BASE_URL}/api/admin/employees`;

export interface EmployeeMedicalDetailsApi {
  emergency_contact_name?: string | null;
  emergency_contact_number?: string | null;
  emergency_contact_relationship?: string | null;
  medical_conditions?: string | null;
  any_disease?: boolean | null;
  has_disease?: boolean | null;
  disease_description?: string | null;
  pre_existing_diseases?: string | null;
  undergone_major_surgery?: boolean | null;
  any_surgery_operation_done?: boolean | null;
  surgery_details?: string | null;
  surgery_operation_description?: string | null;
  allergies?: string | null;
  doctor_name?: string | null;
}

export interface MedicalDetailsSubmitPayload {
  medical_details: EmployeeMedicalDetailsApi;
  remarks?: string;
}

interface MedicalDetailsResponse {
  medical_details?: EmployeeMedicalDetailsApi;
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

export async function getMyMedicalDetails() {
  const data = await requestJson<MedicalDetailsResponse>(MY_MEDICAL_DETAILS_URL, {
    method: "GET",
  });
  return data.medical_details ?? {};
}

export async function postMyMedicalDetails(payload: MedicalDetailsSubmitPayload) {
  return requestJson(MY_MEDICAL_DETAILS_URL, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function patchMyMedicalDetails(payload: MedicalDetailsSubmitPayload) {
  return requestJson(MY_MEDICAL_DETAILS_URL, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function getEmployeeMedicalDetails(employeeId: string) {
  const data = await requestJson<MedicalDetailsResponse>(
    `${EMPLOYEE_MEDICAL_DETAILS_URL}/${employeeId}/medical-details/`,
    { method: "GET" }
  );
  return data.medical_details ?? {};
}

export async function patchEmployeeMedicalDetails(
  employeeId: string,
  payload: MedicalDetailsSubmitPayload
) {
  const data = await requestJson<MedicalDetailsResponse>(
    `${EMPLOYEE_MEDICAL_DETAILS_URL}/${employeeId}/medical-details/`,
    {
      method: "PATCH",
      body: JSON.stringify(payload),
    }
  );
  return data.medical_details ?? {};
}

export function medicalDetailsToEmployeePatch(details: EmployeeMedicalDetailsApi): Partial<Employee> {
  const diseaseDetails = details.disease_description || details.pre_existing_diseases || "";
  const surgeryDetails = details.surgery_operation_description || details.surgery_details || "";
  const allergyDetails = details.allergies || "";

  return {
    emergencyContact: {
      name: details.emergency_contact_name || "",
      phone: details.emergency_contact_number || "",
      relationship: details.emergency_contact_relationship || "",
    },
    medicalInfo: {
      conditions: details.medical_conditions || "",
      hasDisease: Boolean(details.has_disease ?? details.any_disease ?? diseaseDetails),
      diseaseDetails,
      hasSurgery: Boolean(details.undergone_major_surgery ?? details.any_surgery_operation_done ?? surgeryDetails),
      surgeryDetails,
      hasAllergies: Boolean(allergyDetails),
      allergyDetails,
      allergies: details.allergies || "",
      doctorName: details.doctor_name || "",
      relationship: details.emergency_contact_relationship || "",
    },
  };
}

export function employeeMedicalDetailsToPayload(
  emergency: {
    ec?: Employee["emergencyContact"];
    med?: Employee["medicalInfo"];
  }
): MedicalDetailsSubmitPayload {
  return {
    medical_details: {
      emergency_contact_name: emergency.ec?.name || null,
      emergency_contact_number: emergency.ec?.phone || null,
      emergency_contact_relationship:
        emergency.ec?.relationship || emergency.med?.relationship || null,
      medical_conditions: emergency.med?.conditions || null,
      has_disease: Boolean(emergency.med?.hasDisease),
      any_disease: Boolean(emergency.med?.hasDisease),
      disease_description: emergency.med?.hasDisease ? emergency.med?.diseaseDetails || null : null,
      pre_existing_diseases: emergency.med?.hasDisease ? emergency.med?.diseaseDetails || null : null,
      undergone_major_surgery: Boolean(emergency.med?.hasSurgery),
      any_surgery_operation_done: Boolean(emergency.med?.hasSurgery),
      surgery_details: emergency.med?.hasSurgery ? emergency.med?.surgeryDetails || null : null,
      surgery_operation_description: emergency.med?.hasSurgery ? emergency.med?.surgeryDetails || null : null,
      allergies: emergency.med?.hasAllergies
        ? emergency.med?.allergyDetails || emergency.med?.allergies || null
        : null,
      doctor_name: emergency.med?.doctorName || null,
    },
  };
}

export function hasMedicalDetails(details: EmployeeMedicalDetailsApi) {
  return Boolean(
    details.emergency_contact_name ||
      details.emergency_contact_number ||
      details.emergency_contact_relationship ||
      details.medical_conditions ||
      details.has_disease ||
      details.any_disease ||
      details.disease_description ||
      details.pre_existing_diseases ||
      details.undergone_major_surgery ||
      details.any_surgery_operation_done ||
      details.surgery_details ||
      details.surgery_operation_description ||
      details.allergies ||
      details.doctor_name
  );
}
