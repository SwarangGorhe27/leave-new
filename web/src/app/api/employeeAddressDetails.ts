import { Employee } from "../components/employees/mockData";

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://acme.localhost:8000";

const MY_ADDRESS_DETAILS_URL = `${API_BASE_URL}/api/employee/my-address-details/`;
const ADDRESS_COUNTRIES_URL = `${API_BASE_URL}/api/employee/address/choices/countries/`;
const ADDRESS_STATES_URL = `${API_BASE_URL}/api/employee/address/choices/states/`;
const ADDRESS_CITIES_URL = `${API_BASE_URL}/api/employee/address/choices/cities/`;

export interface AddressChoiceApi {
  id: number;
  label: string;
  code?: string | null;
  country_id?: number | null;
  state_id?: number | null;
  pincode?: string | null;
}

export interface EmployeeAddressRowApi {
  id?: string | null;
  address_type: "CURRENT" | "PERMANENT" | "CORRESPONDENCE" | "TEMPORARY";
  address_line1?: string | null;
  address_line2?: string | null;
  landmark?: string | null;
  city_id?: number | null;
  city?: string | null;
  state_id?: number | null;
  state?: string | null;
  country_id?: number | null;
  country?: string | null;
  pincode?: string | null;
  start_date?: string | null;
  to_date?: string | null;
  is_same_as_permanent?: boolean;
}

export interface AddressDetailsResponse {
  current_address?: EmployeeAddressRowApi | null;
  permanent_address?: EmployeeAddressRowApi | null;
  address_details?: EmployeeAddressRowApi[];
}

export type AddressSubmitRow = Partial<{
  id: string | null;
  address_type: "CURRENT" | "PERMANENT";
  address_line1: string | null;
  address_line2: string | null;
  landmark: string | null;
  city_id: number | null;
  state_id: number | null;
  country_id: number | null;
  pincode: string | null;
  start_date: string | null;
  to_date: string | null;
  is_same_as_permanent: boolean;
}>;

export interface AddressDetailsSubmitPayload {
  current_address?: AddressSubmitRow;
  permanent_address?: AddressSubmitRow;
  address_details?: AddressSubmitRow[];
  remarks?: string;
}

export type EmployeeProfileAddress = NonNullable<Employee["currentAddress"]> & {
  apiId?: string | null;
  cityId?: number | null;
  stateId?: number | null;
  countryId?: number | null;
};

interface ChoicesResponse {
  results?: AddressChoiceApi[];
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

export async function getMyAddressDetails() {
  return requestJson<AddressDetailsResponse>(MY_ADDRESS_DETAILS_URL, {
    method: "GET",
  });
}

export async function getAddressCountryChoices() {
  const data = await requestJson<ChoicesResponse>(ADDRESS_COUNTRIES_URL, {
    method: "GET",
  });
  return data.results ?? [];
}

export async function getAddressStateChoices() {
  const data = await requestJson<ChoicesResponse>(ADDRESS_STATES_URL, {
    method: "GET",
  });
  return data.results ?? [];
}

export async function getAddressCityChoices() {
  const data = await requestJson<ChoicesResponse>(ADDRESS_CITIES_URL, {
    method: "GET",
  });
  return data.results ?? [];
}

export async function patchMyAddressDetails(payload: AddressDetailsSubmitPayload) {
  return requestJson(MY_ADDRESS_DETAILS_URL, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function postMyAddressDetails(payload: AddressDetailsSubmitPayload) {
  return requestJson(MY_ADDRESS_DETAILS_URL, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

function toInputDate(value?: string | null) {
  if (!value) return "";
  const match = /^(\d{2})-(\d{2})-(\d{4})$/.exec(value);
  if (match) return `${match[3]}-${match[2]}-${match[1]}`;
  return value;
}

export function addressRowToEmployeeAddress(row?: EmployeeAddressRowApi | null): EmployeeProfileAddress | undefined {
  if (!row) return undefined;

  return {
    apiId: row.id ?? undefined,
    addressLine1: row.address_line1 ?? "",
    addressLine2: row.address_line2 ?? "",
    landmark: row.landmark ?? "",
    city: row.city ?? "",
    state: row.state ?? "",
    country: row.country ?? "",
    pincode: row.pincode ?? "",
    startDate: toInputDate(row.start_date),
    toDate: toInputDate(row.to_date),
    isSameAsPermanent: Boolean(row.is_same_as_permanent),
    cityId: row.city_id ?? null,
    stateId: row.state_id ?? null,
    countryId: row.country_id ?? null,
  };
}

export function addressDetailsToEmployeePatch(
  employee: Employee,
  details: AddressDetailsResponse
): Partial<Employee> {
  return {
    ...employee,
    currentAddress: addressRowToEmployeeAddress(details.current_address),
    permanentAddress: addressRowToEmployeeAddress(details.permanent_address),
  };
}

function resolveChoiceId(label: string | undefined, choices: AddressChoiceApi[], current?: number | null) {
  if (!label) return null;
  const selected = choices.find((choice) => choice.label === label);
  return selected?.id ?? current ?? undefined;
}

export function employeeAddressToSubmitRow(
  address: EmployeeProfileAddress | undefined,
  addressType: "CURRENT" | "PERMANENT",
  choices: {
    countries: AddressChoiceApi[];
    states: AddressChoiceApi[];
    cities: AddressChoiceApi[];
  },
  isSameAsPermanent = false
): AddressSubmitRow {
  return {
    id: address?.apiId ?? undefined,
    address_type: addressType,
    address_line1: address?.addressLine1 ?? "",
    address_line2: address?.addressLine2 ?? "",
    landmark: address?.landmark ?? "",
    city_id: resolveChoiceId(address?.city, choices.cities, address?.cityId),
    state_id: resolveChoiceId(address?.state, choices.states, address?.stateId),
    country_id: resolveChoiceId(address?.country, choices.countries, address?.countryId),
    pincode: address?.pincode ?? "",
    start_date: address?.startDate || null,
    to_date: address?.toDate || null,
    is_same_as_permanent: isSameAsPermanent,
  };
}
