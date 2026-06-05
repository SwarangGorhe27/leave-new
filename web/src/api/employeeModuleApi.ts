/**
 * Employee profile module — backend API (no mock/localStorage).
 *
 * ESS:  /api/employee/my-*
 * Admin: /api/admin/employees/{employeeId}/...
 */

import api, { unwrap } from './client';
import type {
  EducationEntry,
  Employee,
  InsuranceEntry,
  NomineeEntry,
  WorkExperienceEntry,
} from '../app/components/employees/mockData';
import {
  mapAdminBankStatutoryDetails,
  mapAdminEducationList,
  mapAdminFamilyList,
  mapAdminNomineeList,
  mapAdminProfileToEmployee,
  mapAdminWorkExperienceList,
  mapAdminPassportVisaDetails,
  mapEmployeeToAdminBankStatutoryPayload,
  mapEmployeeToAdminPassportPayload,
  mapEmployeeToEssBankStatutoryPayload,
  mapEmployeeToEssPassportPayload,
  mapEssBankStatutoryDetails,
  mapEssPassportVisaDetails,
  mapEssEducationList,
  mapEssFamilyList,
  mapEssInsuranceList,
  mapEssNomineeList,
  mapEssWorkExperienceList,
  mapMyProfileToEmployee,
  mapNomineesToEssPayload,
  mapEducationToEssPayload,
  mapFamilyToEssPayload,
  mapInsuranceToEssPayload,
  mapWorkExperienceToEssPayload,
} from '../app/utils/employeeApiMappers';
import { BankStatutoryApiError, parseBankStatutoryApiError } from '../app/utils/bankStatutoryValidation';

export type EmployeePortal = 'admin' | 'employee' | 'manager';
export type ListSectionKey = 'education' | 'family' | 'nominee' | 'insurance' | 'work';

const isUuid = (id: string) =>
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(id);

/* ─── Load profile shell ─────────────────────────────────────────────────── */

export async function fetchMyProfileShell(): Promise<Employee> {
  const data = await unwrap<Record<string, unknown>>(await api.get('/employee/my-profile/'));
  return mapMyProfileToEmployee(data);
}

export async function fetchAdminProfileShell(employeeId: string): Promise<Employee> {
  const data = await unwrap<Record<string, unknown>>(
    await api.get(`/admin/employees/${employeeId}/profile/`),
  );
  return mapAdminProfileToEmployee(employeeId, data);
}

/* ─── Load list sections ─────────────────────────────────────────────────── */

export async function fetchListSection(
  portal: EmployeePortal,
  employeeId: string,
  section: ListSectionKey,
): Promise<Partial<Employee>> {
  const ess = portal !== 'admin';

  switch (section) {
    case 'education': {
      if (ess) {
        const res = await unwrap<{ education_details?: unknown[] }>(
          await api.get('/employee/my-education-details/'),
        );
        return { education: mapEssEducationList(res.education_details ?? res) };
      }
      const rows = await unwrap<unknown[]>(
        await api.get(`/admin/employees/${employeeId}/education-details/`),
      );
      return { education: mapAdminEducationList(rows) };
    }
    case 'family': {
      if (ess) {
        const res = await unwrap<{ family_details?: unknown[] }>(
          await api.get('/employee/my-family-details/'),
        );
        return { family: mapEssFamilyList(res.family_details ?? res) };
      }
      const rows = await unwrap<unknown[]>(
        await api.get(`/admin/employees/${employeeId}/family-details`),
      );
      return { family: mapAdminFamilyList(rows) };
    }
    case 'nominee': {
      if (ess) {
        const res = await unwrap<{ nominee_details?: unknown[] }>(
          await api.get('/employee/my-nominee/'),
        );
        return { nominees: mapEssNomineeList(res.nominee_details ?? []) };
      }
      const rows = await unwrap<unknown[]>(
        await api.get(`/admin/employees/${employeeId}/nominee-details`),
      );
      return { nominees: mapAdminNomineeList(rows) };
    }
    case 'insurance': {
      if (ess) {
        const res = await unwrap<{ insurance_details?: unknown }>(
          await api.get('/employee/my-insurance-details/'),
        );
        return { insurance: mapEssInsuranceList(res.insurance_details ?? res) };
      }
      const rows = await unwrap<unknown[]>(
        await api.get(`/admin/employees/${employeeId}/insurance-details/`),
      );
      return { insurance: mapEssInsuranceList(rows) };
    }
    case 'work': {
      if (ess) {
        const res = await unwrap<{ work_experience?: unknown[] } | unknown[]>(
          await api.get('/employee/my-experience/'),
        );
        const rows = Array.isArray(res) ? res : (res as { work_experience?: unknown[] }).work_experience ?? [];
        return { workExperience: mapEssWorkExperienceList(rows) };
      }
      const rows = await unwrap<unknown[]>(
        await api.get(`/admin/employees/${employeeId}/work-experience`),
      );
      return { workExperience: mapAdminWorkExperienceList(rows) };
    }
    default:
      return {};
  }
}

export async function fetchBankStatutorySection(
  portal: EmployeePortal,
  employeeId: string,
): Promise<Partial<Employee>> {
  if (portal !== 'admin') {
    const data = await unwrap<Record<string, unknown>>(
      await api.get('/employee/my-bank-statutory-details/'),
    );
    return mapEssBankStatutoryDetails(data);
  }
  const data = await unwrap<Record<string, unknown>>(
    await api.get(`/employees/${employeeId}/bank-statutory/`),
  );
  return mapAdminBankStatutoryDetails(data);
}

export type BankMasterMatch = { id: string; name: string; code: string; branch?: string };

/** Resolve bank from IFSC via masters API (exact code, then 4-char prefix). */
export async function lookupBankByIfsc(ifsc: string): Promise<BankMasterMatch | null> {
  const normalized = ifsc.trim().toUpperCase();
  if (normalized.length < 4) return null;

  const fetchRows = async (query: string) => {
    const res = await unwrap<{ results?: Record<string, unknown>[] } | Record<string, unknown>[]>(
      await api.get(`/masters/Bank/${query}`),
    );
    return Array.isArray(res) ? res : (res.results ?? []);
  };

  let rows: Record<string, unknown>[] = [];
  if (normalized.length >= 11) {
    rows = await fetchRows(`?ifsc=${encodeURIComponent(normalized)}&is_active=true&page=1&page_size=5`);
  }
  if (!rows.length) {
    rows = await fetchRows(
      `?ifsc_prefix=${encodeURIComponent(normalized.slice(0, 4))}&is_active=true&page=1&page_size=1`,
    );
  }
  const row = rows[0];
  if (!row) return null;
  return {
    id: String(row.id ?? ''),
    name: String(row.name ?? row.label ?? ''),
    code: String(row.code ?? ''),
    branch: row.branch ? String(row.branch) : undefined,
  };
}

export async function fetchPassportVisaSection(
  portal: EmployeePortal,
  employeeId: string,
): Promise<Partial<Employee>> {
  if (portal !== 'admin') {
    const data = await unwrap<Record<string, unknown>>(
      await api.get('/employee/my-passport-details/'),
    );
    return mapEssPassportVisaDetails(data);
  }
  const data = await unwrap<Record<string, unknown>>(
    await api.get(`/employees/${employeeId}/passport-visa/`),
  );
  return mapAdminPassportVisaDetails(data);
}

export async function savePassportVisaSection(
  portal: EmployeePortal,
  employeeId: string,
  updated: Employee,
  remarks = '',
): Promise<void> {
  if (portal !== 'admin') {
    const body = mapEmployeeToEssPassportPayload(updated);
    if (remarks) (body as Record<string, unknown>).employee_remarks = remarks;
    await api.patch('/employee/my-passport-details/', body);
    return;
  }
  await api.patch(`/employees/${employeeId}/passport-visa/`, mapEmployeeToAdminPassportPayload(updated));
}

/** Load profile + all list sections for the employee module UI. */
export async function fetchFullEmployeeProfile(
  portal: EmployeePortal,
  employeeId: string,
): Promise<Employee> {
  const shell =
    portal === 'admin'
      ? await fetchAdminProfileShell(employeeId)
      : await fetchMyProfileShell();

  const id = shell.id || employeeId;
  const sections: ListSectionKey[] = ['education', 'family', 'nominee', 'insurance', 'work'];
  let merged: Employee = { ...shell, id };

  for (const section of sections) {
    try {
      const patch = await fetchListSection(portal, id, section);
      merged = { ...merged, ...patch };
    } catch {
      /* section may be empty or forbidden — keep shell */
    }
  }

  try {
    const bankPatch = await fetchBankStatutorySection(portal, id);
    merged = { ...merged, ...bankPatch };
  } catch {
    /* bank section may be empty */
  }

  try {
    const passportPatch = await fetchPassportVisaSection(portal, id);
    merged = { ...merged, ...passportPatch };
  } catch {
    /* passport section may be empty */
  }

  return merged;
}

/* ─── Save list sections ─────────────────────────────────────────────────── */

export async function saveNomineeSection(
  portal: EmployeePortal,
  employeeId: string,
  nominees: NomineeEntry[],
  remarks = '',
): Promise<void> {
  if (portal !== 'admin') {
    await api.patch('/employee/my-nominee/', {
      nominee_details: mapNomineesToEssPayload(nominees),
      remarks,
    });
    return;
  }

  const existing = nominees.filter((n) => isUuid(n.id));
  const created = nominees.filter((n) => !isUuid(n.id));
  await Promise.all(
    existing.map((n) =>
      api.patch(`/admin/employees/${employeeId}/nominee-details/${n.id}`, {
        first_name: n.nomineeName?.split(' ')[0] ?? '',
        last_name: n.nomineeName?.split(' ').slice(1).join(' ') || null,
        date_of_birth: n.dateOfBirth || null,
        mobile_no: n.contactNumber || null,
        address: n.address || null,
        nominee_percentage: n.epfPercentage || n.epsPercentage || n.gratuityPercentage || n.customPercentage || null,
      }),
    ),
  );
  if (created.length) {
    throw new Error(
      'New nominees must be added by the employee (My Profile) and approved by HR, or created during Add Employee.',
    );
  }
}

export async function saveEducationSection(
  portal: EmployeePortal,
  employeeId: string,
  education: EducationEntry[],
  remarks = '',
): Promise<void> {
  if (portal !== 'admin') {
    await api.patch('/employee/my-education-details/', {
      education_details: mapEducationToEssPayload(education),
      remarks,
    });
    return;
  }

  const newRows = education.filter((row) => {
    const rowId = (row as EducationEntry & { id?: string }).id;
    return !rowId || !isUuid(String(rowId));
  });
  if (newRows.length) {
    throw new Error(
      'New education records must be added by the employee via My Profile (pending HR approval).',
    );
  }

  await Promise.all(
    education.map((row) => {
      const rowId = String((row as EducationEntry & { id?: string }).id);
      return api.patch(`/admin/employees/${employeeId}/education-details/${rowId}/`, {
        institution_name: row.institutionName,
        university_name: row.university,
        from_date: row.fromDate,
        to_date: row.toDate,
        grade_or_cgpa: row.percentageCgpa,
        grade: row.grade,
      });
    }),
  );
}

export async function saveFamilySection(
  portal: EmployeePortal,
  employeeId: string,
  family: Employee['family'],
  remarks = '',
): Promise<void> {
  if (portal !== 'admin') {
    await api.patch('/employee/my-family-details/', {
      family_details: mapFamilyToEssPayload(family),
      remarks,
    });
    return;
  }

  const withUuid = family.filter((m) => (m as { id?: string }).id && isUuid(String((m as { id?: string }).id)));
  for (const member of withUuid) {
    const memberId = String((member as { id?: string }).id);
    await api.patch(`/admin/employees/${employeeId}/family-details/${memberId}`, {
      first_name: member.name?.split(' ')[0] ?? '',
      last_name: member.name?.split(' ').slice(1).join(' ') || null,
      date_of_birth: member.dob || null,
      mobile_no: member.phone || null,
      is_dependent: member.isDependent,
    });
  }

  const newMembers = family.filter((m) => !(m as { id?: string }).id || !isUuid(String((m as { id?: string }).id)));
  if (newMembers.length) {
    throw new Error(
      'New family members must be added by the employee via My Profile (pending HR approval).',
    );
  }
}

export async function saveInsuranceSection(
  portal: EmployeePortal,
  employeeId: string,
  insurance: InsuranceEntry[],
  remarks = '',
): Promise<void> {
  if (portal !== 'admin') {
    await api.patch('/employee/my-insurance-details/', {
      insurance_details: mapInsuranceToEssPayload(insurance),
      remarks,
    });
    return;
  }

  for (const pol of insurance) {
    if (pol.id && isUuid(pol.id)) {
      await api.patch(`/admin/employees/${employeeId}/insurance-details/${pol.id}/`, {
        insurance_provider: pol.insuranceProvider,
        policy_number: pol.policyNumber,
        coverage_type: pol.coverageType,
        coverage_amount: pol.coverageAmount,
        valid_till: pol.validTill,
        dependents_covered: pol.dependentsCovered,
      });
    }
  }
}

export async function saveWorkExperienceSection(
  portal: EmployeePortal,
  _employeeId: string,
  workExperience: WorkExperienceEntry[],
  _remarks = '',
): Promise<void> {
  if (portal !== 'admin') {
    if (!workExperience.length) return;
    throw new Error(
      'Work experience changes must be submitted via the My Request tab (backend change-request API).',
    );
  }
  if (workExperience.length) {
    throw new Error('Work experience is view-only for HR; employees submit updates via My Request.');
  }
}

export { BankStatutoryApiError, parseBankStatutoryApiError } from '../app/utils/bankStatutoryValidation';

export async function deleteAdminBankAccount(
  employeeId: string,
  accountId: string,
): Promise<Partial<Employee>> {
  const data = await unwrap<Record<string, unknown>>(
    await api.delete(`/employees/${employeeId}/bank-statutory/bank-account/${accountId}/`),
  );
  return mapAdminBankStatutoryDetails(data);
}

export async function saveBankStatutorySection(
  portal: EmployeePortal,
  employeeId: string,
  updated: Employee,
  original?: Employee,
  remarks = '',
): Promise<Partial<Employee> | void> {
  const accounts = (updated.bankAccounts ?? []).filter(
    (a) =>
      Boolean(a.accountNumber?.trim()) ||
      Boolean(a.ifscCode?.trim()) ||
      Boolean(a.bankId || a.bankName?.trim()) ||
      Boolean(a.accountNumberMasked),
  );
  const bankTouched =
    JSON.stringify(accounts) !==
    JSON.stringify(
      (original?.bankAccounts ?? []).filter(
        (a) =>
          Boolean(a.accountNumber?.trim()) ||
          Boolean(a.ifscCode?.trim()) ||
          Boolean(a.bankId || a.bankName?.trim()) ||
          Boolean(a.accountNumberMasked),
      ),
    );

  if (portal !== 'admin') {
    await submitEssBankStatutorySection(updated, remarks);
    return;
  }

  const body = mapEmployeeToAdminBankStatutoryPayload(updated, original);
  if (!Object.keys(body).length) {
    return {};
  }
  if (bankTouched) {
    for (let i = 0; i < accounts.length; i += 1) {
      const row = accounts[i];
      const label = accounts.length > 1 ? `Bank account ${i + 1}` : 'Bank account';
      if (!row.accountTypeId && !row.accountType) {
        throw new Error(`${label}: account type is required.`);
      }
      if (!row.accountNumber?.trim() && !row.accountNumberMasked) {
        throw new Error(`${label}: account number is required.`);
      }
      if (row.ifscCode && row.ifscCode.length !== 11) {
        throw new Error(`${label}: IFSC code must be 11 characters (e.g. HDFC0001234).`);
      }
      if (!row.bankId && !row.bankName?.trim()) {
        throw new Error(`${label}: enter a valid IFSC to load the bank name.`);
      }
    }
  }
  try {
    const data = await unwrap<Record<string, unknown>>(
      await api.patch(`/employees/${employeeId}/bank-statutory/`, body),
    );
    return mapAdminBankStatutoryDetails(data);
  } catch (err) {
    throw parseBankStatutoryApiError(err);
  }
}

export async function submitEssBankStatutorySection(
  updated: Employee,
  remarks = '',
): Promise<void> {
  const body = mapEmployeeToEssBankStatutoryPayload(updated, updated.name);
  if (remarks) (body as Record<string, unknown>).employee_remarks = remarks;
  if (
    !(body.bank_accounts as unknown[])?.length &&
    !Object.keys((body.statutory_details as object) ?? {}).length
  ) {
    throw new BankStatutoryApiError('Add bank or statutory details before saving.');
  }
  try {
    await api.patch('/employee/my-bank-statutory-details/', body);
  } catch (err) {
    throw parseBankStatutoryApiError(err);
  }
}

export async function saveEmployeeListSection(
  portal: EmployeePortal,
  employeeId: string,
  sectionName: string,
  original: Employee,
  updated: Employee,
): Promise<Partial<Employee> | void> {
  switch (sectionName) {
    case 'Education Details':
      await saveEducationSection(portal, employeeId, updated.education ?? [], '');
      break;
    case 'Family Details':
      await saveFamilySection(portal, employeeId, updated.family ?? [], '');
      break;
    case 'Nominee Details':
      await saveNomineeSection(portal, employeeId, updated.nominees ?? [], '');
      break;
    case 'Insurance Details':
      await saveInsuranceSection(portal, employeeId, updated.insurance ?? [], '');
      break;
    case 'Work Experience':
      await saveWorkExperienceSection(portal, employeeId, updated.workExperience ?? [], '');
      break;
    case 'Bank / PF / ESI Details':
    case 'Bank Details':
    case 'Statutory Details':
      return saveBankStatutorySection(portal, employeeId, updated, original);
    case 'Passport & Visa Details':
      await savePassportVisaSection(portal, employeeId, updated);
      break;
    default:
      if (JSON.stringify(original) !== JSON.stringify(updated)) {
        throw new Error(`Direct save for "${sectionName}" is not wired to the API yet.`);
      }
  }
}
