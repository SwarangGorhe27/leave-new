/**
 * Employee profile persistence — API only (no mock localStorage).
 */

import type { AppDispatch } from '../../store';
import type { Employee } from '../components/employees/mockData';
import {
  BankStatutoryApiError,
  fetchFullEmployeeProfile,
  saveEmployeeListSection,
  type EmployeePortal,
} from '../../api/employeeModuleApi';
import type {
  BankRowFieldErrors,
  BankStatutoryFieldErrors,
} from '../utils/bankStatutoryValidation';

const BANK_SECTION_NAMES = new Set([
  'Bank / PF / ESI Details',
  'Bank Details',
  'Statutory Details',
]);
import { updateAdminEmployee } from '../../store/slices/adminSlice';

export function useLocalEmployeeStore(): boolean {
  return false;
}

export async function persistEmployeeProfile(
  _dispatch: AppDispatch,
  portal: EmployeePortal,
  employeeId: string,
  original: Employee,
  updated: Employee,
  sectionName: string,
): Promise<
  | { ok: true; employee: Employee }
  | {
      ok: false;
      message: string;
      fieldErrors?: BankStatutoryFieldErrors;
      bankRowErrors?: Record<number, BankRowFieldErrors>;
    }
> {
  try {
    const sectionPatch = await saveEmployeeListSection(
      portal,
      employeeId,
      sectionName,
      original,
      updated,
    );
    if (BANK_SECTION_NAMES.has(sectionName)) {
      const bankPatch = sectionPatch ?? {};
      const employee: Employee = {
        ...original,
        ...updated,
        ...bankPatch,
        id: employeeId,
      };
      return { ok: true, employee };
    }
    const fresh = await fetchFullEmployeeProfile(portal, employeeId);
    return { ok: true, employee: fresh };
  } catch (err: unknown) {
    if (err instanceof BankStatutoryApiError) {
      return {
        ok: false,
        message: err.message,
        fieldErrors: err.fieldErrors,
        bankRowErrors: err.bankRowErrors,
      };
    }
    const message = err instanceof Error ? err.message : 'Failed to save employee profile.';
    return { ok: false, message };
  }
}

/** Keep admin Redux cache in sync after API load/save (in-memory only). */
export function cacheEmployeeInRedux(dispatch: AppDispatch, employee: Employee) {
  dispatch(updateAdminEmployee(employee));
}
