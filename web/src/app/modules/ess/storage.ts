import { ESS_SECTIONS, getSeedProfile } from "./data";
import { EmployeeProfile, ProfileChangeRequest, RequestStatus, SectionKey } from "./types";
import { mergeAdminEmployeeIntoEssProfile, applyApprovedSectionToAdmin } from "./adminEssSync";
import type { Employee } from "../../components/employees/mockData";
import { findEmployeeByStorageId } from "../../utils/resolveLoggedInEmployee";

const PROFILES_KEY = "hrms_ess_profiles";
const REQUESTS_KEY = "hrms_profile_change_requests";
const LEGACY_REQUESTS_KEY = "mock_requests_db";

type ProfilesStore = Record<string, EmployeeProfile>;

const deepClone = <T>(value: T): T => JSON.parse(JSON.stringify(value));

const readProfiles = (): ProfilesStore => {
  try {
    const raw = localStorage.getItem(PROFILES_KEY);
    return raw ? (JSON.parse(raw) as ProfilesStore) : {};
  } catch {
    return {};
  }
};

const writeProfiles = (profiles: ProfilesStore) => {
  localStorage.setItem(PROFILES_KEY, JSON.stringify(profiles));
};

const readRequests = (): ProfileChangeRequest[] => {
  try {
    const raw = localStorage.getItem(REQUESTS_KEY);
    return raw ? (JSON.parse(raw) as ProfileChangeRequest[]) : [];
  } catch {
    return [];
  }
};

const writeRequests = (requests: ProfileChangeRequest[]) => {
  localStorage.setItem(REQUESTS_KEY, JSON.stringify(requests));
};

interface LegacyProfileRequest {
  id: string;
  employeeId: string;
  section: SectionKey;
  sectionLabel: string;
  changes: Array<{ fieldName: string; fieldLabel?: string; oldValue?: unknown; newValue?: unknown }>;
  status: RequestStatus;
  createdAt: string;
  reviewedBy: string | null;
  reviewedAt: string | null;
  rejectionComment?: string;
}

const legacyFieldChangesToObject = (
  changes: LegacyProfileRequest["changes"],
): Record<string, unknown> => {
  const result: Record<string, unknown> = {};
  for (const change of changes) {
    const keys = change.fieldName.split(".");
    let current = result as Record<string, unknown>;
    keys.forEach((key, index) => {
      if (index === keys.length - 1) {
        current[key] = change.newValue ?? "";
      } else {
        current[key] = (current[key] as Record<string, unknown>) || {};
        current = current[key] as Record<string, unknown>;
      }
    });
  }
  return result;
};

const convertLegacyRequest = (request: LegacyProfileRequest): ProfileChangeRequest => ({
  id: request.id,
  employee_id: request.employeeId,
  section: request.section,
  section_label: request.sectionLabel,
  changes: {
    oldValue: legacyFieldChangesToObject(
      request.changes.map((change) => ({
        ...change,
        newValue: change.oldValue,
      })),
    ),
    newValue: legacyFieldChangesToObject(request.changes),
  },
  status: request.status,
  created_at: request.createdAt,
  reviewed_by: request.reviewedBy,
  reviewed_at: request.reviewedAt,
  rejection_comment: request.rejectionComment,
  _source: "legacy",
});

/** Pull legacy mock_requests_db entries into the shared ESS store once. */
const syncLegacyRequestsIntoStore = () => {
  try {
    const raw = localStorage.getItem(LEGACY_REQUESTS_KEY);
    if (!raw) return;
    const legacy = JSON.parse(raw) as LegacyProfileRequest[];
    if (!Array.isArray(legacy) || legacy.length === 0) return;

    const existing = readRequests();
    const existingIds = new Set(existing.map((request) => request.id));
    let changed = false;

    for (const request of legacy) {
      if (existingIds.has(request.id)) continue;
      existing.push(convertLegacyRequest(request));
      changed = true;
    }

    if (changed) writeRequests(existing);
  } catch {
    /* ignore corrupt legacy data */
  }
};

const readAllLocalRequests = (): ProfileChangeRequest[] => {
  syncLegacyRequestsIntoStore();
  return readRequests();
};

const matchesEmployeeFilter = (
  request: ProfileChangeRequest,
  employeeFilter: string | string[],
): boolean => {
  const aliases = Array.isArray(employeeFilter) ? employeeFilter : [employeeFilter];
  const aliasSet = new Set(aliases.filter(Boolean));
  if (aliasSet.size === 0) return true;
  if (aliasSet.has(request.employee_id)) return true;

  try {
    const raw = localStorage.getItem("admin_employees_db");
    if (!raw) return false;
    const employees = JSON.parse(raw) as Employee[];
    for (const alias of aliasSet) {
      const employee = findEmployeeByStorageId(employees, alias);
      if (!employee) continue;
      if (employee.id === request.employee_id || employee.employeeId === request.employee_id) {
        return true;
      }
    }
  } catch {
    /* ignore */
  }

  return false;
};

export const mergeChangeRequests = (
  local: ProfileChangeRequest[],
  remote: ProfileChangeRequest[],
): ProfileChangeRequest[] => {
  const byId = new Map<string, ProfileChangeRequest>();
  for (const request of local) {
    byId.set(request.id, { ...request, _source: request._source ?? "local" });
  }
  for (const request of remote) {
    byId.set(request.id, request);
  }
  return Array.from(byId.values()).sort((a, b) =>
    a.created_at < b.created_at ? 1 : -1,
  );
};

export const ensureProfile = (employeeId: string): EmployeeProfile => {
  const profiles = readProfiles();
  if (!profiles[employeeId]) {
    profiles[employeeId] = getSeedProfile(employeeId);
    writeProfiles(profiles);
  }
  return deepClone(profiles[employeeId]);
};

export const getProfile = (employeeId: string): EmployeeProfile => ensureProfile(employeeId);

export const getChangeRequests = (
  employeeFilter?: string | string[],
): ProfileChangeRequest[] => {
  const requests = readAllLocalRequests().sort((a, b) =>
    a.created_at < b.created_at ? 1 : -1,
  );
  if (!employeeFilter) return requests;
  return requests.filter((request) => matchesEmployeeFilter(request, employeeFilter));
};

export const getPendingSections = (employeeId: string): SectionKey[] => {
  const pending = new Set<SectionKey>();
  getChangeRequests(employeeId).forEach((request) => {
    if (request.status === "pending") pending.add(request.section);
  });
  return Array.from(pending);
};

export const saveDraftChangeRequest = (params: {
  employeeId: string;
  section: SectionKey;
  newValue: unknown;
  supportingDoc?: { fileName: string; dataUrl: string; uploadedAt: string };
}): ProfileChangeRequest => {
  const profiles = readProfiles();
  const requests = readRequests();
  const profile = ensureProfile(params.employeeId);
  profiles[params.employeeId] = profile;

  const sectionMeta = ESS_SECTIONS.find((entry) => entry.key === params.section);
  const oldValue = deepClone(profile[params.section as keyof EmployeeProfile] || {});

  const draftIndex = requests.findIndex(
    (request) =>
      request.employee_id === params.employeeId &&
      request.section === params.section &&
      request.status === "draft"
  );

  let changeRequest: ProfileChangeRequest;
  if (draftIndex >= 0) {
    requests[draftIndex].changes.newValue = deepClone(params.newValue);
    requests[draftIndex].supportingDoc = params.supportingDoc;
    requests[draftIndex].created_at = new Date().toISOString();
    changeRequest = requests[draftIndex];
  } else {
    const hasPending = requests.some(
      (request) =>
        request.employee_id === params.employeeId &&
        request.section === params.section &&
        request.status === "pending"
    );
    if (hasPending) {
      throw new Error("A pending request already exists for this section.");
    }
    changeRequest = {
      id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
      employee_id: params.employeeId,
      section: params.section,
      section_label: sectionMeta?.label ?? params.section,
      changes: {
        oldValue,
        newValue: deepClone(params.newValue),
      },
      status: "draft",
      created_at: new Date().toISOString(),
      reviewed_by: null,
      reviewed_at: null,
      supportingDoc: params.supportingDoc,
    };
    requests.push(changeRequest);
  }

  writeProfiles(profiles);
  writeRequests(requests);
  return changeRequest;
};

export const submitDraftChangeRequest = (requestId: string): ProfileChangeRequest => {
  const requests = readRequests();
  const index = requests.findIndex((r) => r.id === requestId);
  if (index < 0) {
    throw new Error("Request not found");
  }
  requests[index].status = "pending";
  requests[index].created_at = new Date().toISOString();
  writeRequests(requests);
  return requests[index];
};

export const deleteDraftChangeRequest = (requestId: string) => {
  const requests = readRequests();
  const next = requests.filter((r) => r.id !== requestId);
  writeRequests(next);
};

export const submitSectionChangeRequest = (params: {
  employeeId: string;
  section: SectionKey;
  newValue: unknown;
}): ProfileChangeRequest => {
  const profiles = readProfiles();
  const requests = readRequests();
  const profile = ensureProfile(params.employeeId);
  profiles[params.employeeId] = profile;

  const sectionMeta = ESS_SECTIONS.find((entry) => entry.key === params.section);
  const oldValue = deepClone(profile[params.section as keyof EmployeeProfile] || {});
  const hasPending = requests.some(
    (request) =>
      request.employee_id === params.employeeId &&
      request.section === params.section &&
      request.status === "pending",
  );
  if (hasPending) {
    throw new Error("A pending request already exists for this section.");
  }
  const changeRequest: ProfileChangeRequest = {
    id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    employee_id: params.employeeId,
    section: params.section,
    section_label: sectionMeta?.label ?? params.section,
    changes: {
      oldValue,
      newValue: deepClone(params.newValue),
    },
    status: "pending",
    created_at: new Date().toISOString(),
    reviewed_by: null,
    reviewed_at: null,
  };

  requests.push(changeRequest);
  writeProfiles(profiles);
  writeRequests(requests);
  return changeRequest;
};

export const getEmployeeDisplayName = (
  employeeId: string,
  employees?: Employee[],
  request?: Pick<ProfileChangeRequest, "_employeeName" | "_employeeCode">,
): string => {
  if (request?._employeeName?.trim()) return request._employeeName.trim();

  const fromList = employees?.length
    ? findEmployeeByStorageId(employees, employeeId)
    : undefined;
  if (fromList?.name?.trim()) return fromList.name.trim();

  try {
    const raw = localStorage.getItem("admin_employees_db");
    if (raw) {
      const stored = JSON.parse(raw) as Employee[];
      const match = findEmployeeByStorageId(stored, employeeId);
      if (match?.name?.trim()) return match.name.trim();
    }
  } catch {
    /* ignore */
  }

  const profile = ensureProfile(employeeId);
  const { firstName, middleName, lastName } = profile.profile;
  const fromProfile = [firstName, middleName, lastName].filter(Boolean).join(" ");
  if (fromProfile) return fromProfile;

  return request?._employeeCode?.trim() || employeeId;
};

export const reviewChangeRequest = (params: {
  requestId: string;
  status: Exclude<RequestStatus, "pending" | "draft">;
  reviewer: string;
  rejectionComment?: string;
}) => {
  const requests = readRequests();
  const profiles = readProfiles();
  const request = requests.find((entry) => entry.id === params.requestId);
  if (!request || request.status !== "pending") return;

  request.status = params.status;
  request.reviewed_by = params.reviewer;
  request.reviewed_at = new Date().toISOString();
  if (params.status === "rejected") {
    request.rejection_comment = params.rejectionComment?.trim() || "";
  }

  if (params.status === "approved") {
    const profile = ensureProfile(request.employee_id);
    let nextProfile: EmployeeProfile;

    try {
      const rawEmps = localStorage.getItem("admin_employees_db");
      if (rawEmps) {
        const emps = JSON.parse(rawEmps) as Employee[];
        const adminIndex = emps.findIndex(
          (e) =>
            e.id === request.employee_id ||
            e.employeeId === request.employee_id ||
            e.id === request._employeeCode ||
            e.employeeId === request._employeeCode,
        );
        if (adminIndex >= 0) {
          const mergedAdmin = applyApprovedSectionToAdmin(
            emps[adminIndex],
            request.section,
            request.changes.newValue,
          );
          emps[adminIndex] = mergedAdmin;
          localStorage.setItem("admin_employees_db", JSON.stringify(emps));
          nextProfile = mergeAdminEmployeeIntoEssProfile(mergedAdmin, profile);
        } else {
          nextProfile = {
            ...profile,
            [request.section]: deepClone(request.changes.newValue),
          };
        }
      } else {
        nextProfile = {
          ...profile,
          [request.section]: deepClone(request.changes.newValue),
        };
      }
    } catch (e) {
      console.error("Error syncing approved request to admin employee", e);
      nextProfile = {
        ...profile,
        [request.section]: deepClone(request.changes.newValue),
      };
    }

    profiles[request.employee_id] = nextProfile;
    writeProfiles(profiles);
  }

  writeRequests(requests);
};
