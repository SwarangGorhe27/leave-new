import type { Employee } from "../components/employees/mockData";
import type { AuthUser } from "../context/AuthContext";

function normalize(value?: string | null): string {
  return (value ?? "").trim().toLowerCase();
}

export function findEmployeeRecordIndex(
  employees: Employee[],
  employee: Pick<Employee, "id" | "employeeId" | "email">,
): number {
  const id = employee.id?.trim();
  const code = employee.employeeId?.trim();
  const email = normalize(employee.email);

  return employees.findIndex((row) => {
    if (id && (row.id === id || row.employeeId === id)) return true;
    if (code && row.employeeId === code) return true;
    if (email && normalize(row.email) === email) return true;
    return false;
  });
}

/** Build a minimal admin Employee row for demo / first-time self-profile users. */
export function buildEmployeeFromAuthUser(user: AuthUser): Employee {
  const email = user.email?.trim().toLowerCase() || "";
  const storageId =
    user.employeeId?.trim() ||
    user.employeeCode?.trim() ||
    email ||
    (user.id != null ? `user-${user.id}` : `emp-${Date.now()}`);

  const displayName =
    user.name?.trim() ||
    email.split("@")[0]?.replace(/\./g, " ") ||
    "Employee";

  const initials =
    user.initials?.trim() ||
    displayName
      .split(/\s+/)
      .map((p) => p[0])
      .join("")
      .slice(0, 2)
      .toUpperCase() ||
    "EM";

  return {
    id: storageId,
    employeeId: user.employeeCode?.trim() || storageId,
    name: displayName,
    email,
    designation: user.role === "manager" ? "HR Manager" : "",
    department: user.role === "manager" ? "Human Resources" : "",
    team: "",
    phone: "",
    joiningDate: new Date().toISOString().slice(0, 10),
    location: "",
    status: "Active",
    initials,
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
    education: [],
    nominees: [],
    insurance: [],
    workExperience: [],
    positionHistory: [],
    previousEmployment: [],
  } as Employee;
}
