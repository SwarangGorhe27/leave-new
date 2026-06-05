import type { Employee } from "../components/employees/mockData";
import type { AuthUser } from "../context/AuthContext";

function normalize(value?: string | null): string {
  return (value ?? "").trim().toLowerCase();
}

export function findEmployeeMatch(
  employees: Employee[],
  user: AuthUser | null | undefined,
): Employee | undefined {
  if (!user) return undefined;

  const jwtEmployeeId = user.employeeId?.trim();
  const employeeCode = user.employeeCode?.trim();
  const email = normalize(user.email);

  return employees.find((item) => {
    if (jwtEmployeeId && (item.id === jwtEmployeeId || item.employeeId === jwtEmployeeId)) {
      return true;
    }
    if (employeeCode && item.employeeId === employeeCode) return true;
    if (email && normalize(item.email) === email) return true;
    return false;
  });
}

export function findEmployeeByStorageId(
  employees: Employee[],
  storageId: string,
): Employee | undefined {
  const key = storageId.trim();
  if (!key) return undefined;
  return employees.find((item) => item.id === key || item.employeeId === key);
}

/** Resolve the logged-in user to an employee record without falling back to the wrong person. */
export function resolveLoggedInEmployee(
  employees: Employee[],
  user: AuthUser | null | undefined,
): Employee {
  const matched = findEmployeeMatch(employees, user);
  if (matched) return matched;

  const storageId =
    user?.employeeId?.trim() ||
    user?.employeeCode?.trim() ||
    (user?.email ? normalize(user.email) : "") ||
    (user?.id != null ? `user-${user.id}` : "unknown-user");

  const displayName =
    user?.name?.trim() ||
    user?.email?.split("@")[0] ||
    "Employee";

  return {
    id: storageId,
    employeeId: user?.employeeCode?.trim() || storageId,
    name: displayName,
    email: user?.email ?? "",
    designation: "",
    department: "",
    team: "",
    phone: "",
    joiningDate: "",
    location: "",
    status: "Active",
    initials: user?.initials ?? displayName.slice(0, 2).toUpperCase(),
    avatarColor: "#64748B",
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

/** All identifiers that may have been used when saving profile change requests. */
export function employeeIdAliases(
  employee: Employee,
  user?: AuthUser | null,
): string[] {
  const ids = new Set<string>();
  if (employee.id) ids.add(employee.id);
  if (employee.employeeId) ids.add(employee.employeeId);
  if (user?.employeeId?.trim()) ids.add(user.employeeId.trim());
  if (user?.employeeCode?.trim()) ids.add(user.employeeCode.trim());
  if (user?.email?.trim()) ids.add(normalize(user.email));
  return Array.from(ids);
}
