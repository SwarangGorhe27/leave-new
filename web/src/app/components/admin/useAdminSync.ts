import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../../store';
import { updateAdminEmployee } from '../../../store/slices/adminSlice';
import { addNotification } from '../../../store/slices/notificationSlice';
import { Employee } from '../employees/mockData';
import { useAuth } from '../../context/AuthContext';
import {
  cacheEmployeeInRedux,
  persistEmployeeProfile,
} from '../../services/employeeProfilePersistence';
import type { EmployeePortal } from '../../../api/employeeModuleApi';
import { useInvalidateEmployeeProfile } from '../../../hooks/useEmployeeModuleProfile';
const LIST_FIELDS: (keyof Employee)[] = [
  'education',
  'family',
  'nominees',
  'insurance',
  'workExperience',
];

function hasListFieldChanges(original: Employee, edited: Employee): boolean {
  return LIST_FIELDS.some(
    (key) =>
      JSON.stringify(original[key] ?? []) !== JSON.stringify(edited[key] ?? []),
  );
}

const BANK_STATUTORY_KEYS: (keyof Employee)[] = [
  'panNumber',
  'aadhaarNumber',
  'uanNumber',
  'pfNumber',
  'esiNumber',
  'taxRegime',
  'taxRegimeId',
  'linNumber',
  'isPfCovered',
  'isEsiCovered',
  'isLwfCovered',
  'isEarlierMemberOfPensionOnHigherWages',
  'bankName',
  'accountNumber',
  'ifscCode',
];

function hasBankStatutoryChanges(original: Employee, edited: Employee): boolean {
  if (JSON.stringify(original.bankAccounts ?? []) !== JSON.stringify(edited.bankAccounts ?? [])) {
    return true;
  }
  return BANK_STATUTORY_KEYS.some((key) => original[key] !== edited[key]);
}

const BANK_SECTION_NAMES = new Set([
  'Bank / PF / ESI Details',
  'Bank Details',
  'Statutory Details',
]);

const PASSPORT_VISA_KEYS: (keyof Employee)[] = [
  'passportNumber',
  'passportHolderName',
  'passportIssueDate',
  'passportExpiry',
  'passportPlaceOfIssue',
  'passportCountryOfIssue',
  'passportCategory',
  'passportStatus',
  'visaType',
  'visaNumber',
  'visaExpiry',
  'visaCountry',
  'visaSponsor',
  'visaIssueDate',
  'visaStatus',
];

function hasPassportVisaChanges(original: Employee, edited: Employee): boolean {
  return PASSPORT_VISA_KEYS.some((key) => original[key] !== edited[key]);
}

const PASSPORT_SECTION_NAMES = new Set(['Passport & Visa Details']);

function getDifferences(oldObj: Record<string, unknown>, newObj: Record<string, unknown>, prefix = ''): { fieldName: string; oldValue: unknown; newValue: unknown }[] {
  let diffs: { fieldName: string; oldValue: unknown; newValue: unknown }[] = [];
  for (const key of Object.keys(newObj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    const oldVal = oldObj[key];
    const newVal = newObj[key];
    if (typeof newVal === 'object' && newVal !== null && !Array.isArray(newVal)) {
      diffs = diffs.concat(getDifferences((oldVal as Record<string, unknown>) || {}, newVal as Record<string, unknown>, fullKey));
    } else if (Array.isArray(newVal)) {
      if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
        diffs.push({ fieldName: fullKey, oldValue: 'List Changed', newValue: 'List Changed' });
      }
    } else if (oldVal !== newVal) {
      diffs.push({ fieldName: fullKey, oldValue: oldVal, newValue: newVal });
    }
  }
  return diffs;
}

function portalFromRole(role?: string): EmployeePortal {
  if (role === 'admin') return 'admin';
  return role === 'manager' ? 'manager' : 'employee';
}

export function useAdminSync() {
  const dispatch = useDispatch<AppDispatch>();
  const { user } = useAuth();
  const invalidateProfile = useInvalidateEmployeeProfile();
  const portal = portalFromRole(user?.role);

  const handleAdminSave = async (
    sectionName: string,
    originalData: Employee,
    editedData: Employee,
  ) => {
    const diffs = getDifferences(
      originalData as unknown as Record<string, unknown>,
      editedData as unknown as Record<string, unknown>,
    );
    const listChanged = hasListFieldChanges(originalData, editedData);
    const bankChanged =
      BANK_SECTION_NAMES.has(sectionName) &&
      hasBankStatutoryChanges(originalData, editedData);
    const passportChanged =
      PASSPORT_SECTION_NAMES.has(sectionName) &&
      hasPassportVisaChanges(originalData, editedData);

    if (diffs.length === 0 && !listChanged && !bankChanged && !passportChanged) {
      dispatch(addNotification({ type: 'warning', message: 'No changes detected.' }));
      return false;
    }

    const employeeId = editedData.id;
    const result = await persistEmployeeProfile(
      dispatch,
      portal,
      employeeId,
      originalData,
      editedData,
      sectionName,
    );

    if (!result.ok) {
      dispatch(addNotification({ type: 'error', message: result.message }));
      return false;
    }

    cacheEmployeeInRedux(dispatch, result.employee);
    if (BANK_SECTION_NAMES.has(sectionName)) {
      invalidateProfile(portal, employeeId, result.employee);
    } else {
      invalidateProfile(portal, employeeId);
    }

    const successMessages: Record<string, string> = {
      'Nominee Details': 'Nominee details submitted successfully.',
      'Education Details': 'Education details saved successfully.',
      'Family Details': 'Family details saved successfully.',
      'Insurance Details': 'Insurance details saved successfully.',
      'Work Experience': 'Work experience saved successfully.',
      'Bank / PF / ESI Details':
        portal === 'admin'
          ? 'Bank and statutory details saved successfully.'
          : 'Bank and statutory changes submitted for HR approval.',
      'Bank Details':
        portal === 'admin'
          ? 'Bank details saved successfully.'
          : 'Bank changes submitted for HR approval.',
      'Statutory Details':
        portal === 'admin'
          ? 'Statutory details saved successfully.'
          : 'Statutory changes submitted for HR approval.',
      'Passport & Visa Details':
        portal === 'admin'
          ? 'Passport and visa details saved successfully.'
          : 'Passport and visa changes submitted for HR approval.',
    };

    dispatch(addNotification({
      type: 'success',
      message: successMessages[sectionName] ?? 'Employee profile updated successfully.',
    }));
    return true;
  };

  const handleToggleEditAccess = async (employee: Employee, sectionId: string, checked: boolean) => {
    const currentSections = employee.editableSections || [];
    const nextSections = checked
      ? [...currentSections, sectionId]
      : currentSections.filter((id) => id !== sectionId);

    dispatch(updateAdminEmployee({ ...employee, editableSections: nextSections }));
    return true;
  };

  return { handleAdminSave, handleToggleEditAccess };
}
