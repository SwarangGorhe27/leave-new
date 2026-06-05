import type { BankAccount, Employee } from '../components/employees/mockData';
import { normalizeTaxRegimeId } from './employeeApiMappers';

const PAN_RE = /^[A-Z]{5}[0-9]{4}[A-Z]$/;
const IFSC_RE = /^[A-Z]{4}0[A-Z0-9]{6}$/;
const ACCOUNT_RE = /^[0-9]{6,30}$/;
const AADHAAR_RE = /^\d{12}$/;
const UAN_RE = /^\d{12}$/;
const ESIC_RE = /^\d{17}$/;

export type BankRowFieldErrors = Partial<
  Record<'accountHolderName' | 'ifscCode' | 'bankName' | 'accountNumber' | 'accountType' | 'paymentType', string>
>;

export type BankStatutoryFieldErrors = Partial<
  Record<
    | 'panNumber'
    | 'aadhaarNumber'
    | 'taxRegimeId'
    | 'uanNumber'
    | 'pfNumber'
    | 'esiNumber'
    | 'linNumber',
    string
  >
>;

export class BankStatutoryApiError extends Error {
  fieldErrors: BankStatutoryFieldErrors;
  bankRowErrors: Record<number, BankRowFieldErrors>;

  constructor(
    message: string,
    fieldErrors: BankStatutoryFieldErrors = {},
    bankRowErrors: Record<number, BankRowFieldErrors> = {},
  ) {
    super(message);
    this.name = 'BankStatutoryApiError';
    this.fieldErrors = fieldErrors;
    this.bankRowErrors = bankRowErrors;
  }
}

function firstMessage(value: unknown): string | undefined {
  if (Array.isArray(value) && typeof value[0] === 'string') return value[0];
  if (typeof value === 'string' && value.trim()) return value;
  return undefined;
}

const STATUTORY_API_TO_UI: Record<string, keyof BankStatutoryFieldErrors> = {
  pan: 'panNumber',
  pan_number: 'panNumber',
  aadhaar_no: 'aadhaarNumber',
  aadhaar_number: 'aadhaarNumber',
  tax_regime: 'taxRegimeId',
  tax_regime_id: 'taxRegimeId',
  uan: 'uanNumber',
  uan_number: 'uanNumber',
  pf_account_no: 'pfNumber',
  pf_number: 'pfNumber',
  esic_no: 'esiNumber',
  esic_number: 'esiNumber',
  lin_number: 'linNumber',
};

const BANK_API_TO_UI: Record<string, keyof BankRowFieldErrors> = {
  ifsc: 'ifscCode',
  ifsc_code: 'ifscCode',
  account_no: 'accountNumber',
  account_number: 'accountNumber',
  bank: 'bankName',
  bank_name: 'bankName',
  type: 'accountType',
  account_type: 'accountType',
  account_type_id: 'accountType',
  account_holder_name: 'accountHolderName',
  payment_type_id: 'paymentType',
};

function mapStatutoryBlock(
  block: Record<string, unknown>,
  target: BankStatutoryFieldErrors,
) {
  for (const [key, val] of Object.entries(block)) {
    const uiKey = STATUTORY_API_TO_UI[key];
    const msg = firstMessage(val);
    if (uiKey && msg) target[uiKey] = msg;
  }
}

function mapBankRowBlock(
  block: Record<string, unknown>,
  rowIndex: number,
  target: Record<number, BankRowFieldErrors>,
) {
  const row: BankRowFieldErrors = target[rowIndex] ?? {};
  for (const [key, val] of Object.entries(block)) {
    const uiKey = BANK_API_TO_UI[key];
    const msg = firstMessage(val);
    if (uiKey && msg) row[uiKey] = msg;
  }
  if (Object.keys(row).length) target[rowIndex] = row;
}

/** Parse DRF validation payloads for bank / statutory save. */
export function parseBankStatutoryApiError(err: unknown): BankStatutoryApiError {
  const fieldErrors: BankStatutoryFieldErrors = {};
  const bankRowErrors: Record<number, BankRowFieldErrors> = {};
  let message = 'Failed to save bank / statutory details.';

  const data =
    err && typeof err === 'object' && 'response' in err
      ? (err as { response?: { data?: unknown } }).response?.data
      : undefined;

  if (typeof data === 'string' && data.trim()) {
    return new BankStatutoryApiError(data, fieldErrors, bankRowErrors);
  }

  if (!data || typeof data !== 'object') {
    if (err instanceof Error && err.message.trim()) message = err.message;
    return new BankStatutoryApiError(message, fieldErrors, bankRowErrors);
  }

  const record = data as Record<string, unknown>;
  if (typeof record.detail === 'string' && record.detail.trim()) {
    message = record.detail;
  }

  for (const [key, val] of Object.entries(record)) {
    if (key === 'detail') continue;

    const rowMatch = key.match(/^bank_accounts(?:\.(\d+))?$/);
    if (rowMatch && val && typeof val === 'object' && !Array.isArray(val)) {
      const idx = rowMatch[1] ? Number(rowMatch[1]) : 0;
      mapBankRowBlock(val as Record<string, unknown>, idx, bankRowErrors);
      continue;
    }

    if (
      (key === 'statutory_details' || key === 'statutory_documents') &&
      val &&
      typeof val === 'object' &&
      !Array.isArray(val)
    ) {
      mapStatutoryBlock(val as Record<string, unknown>, fieldErrors);
      continue;
    }

    if (
      (key === 'pf_details' || key === 'esi_details' || key === 'lwf_details') &&
      val &&
      typeof val === 'object' &&
      !Array.isArray(val)
    ) {
      mapStatutoryBlock(val as Record<string, unknown>, fieldErrors);
      continue;
    }

    if (key === 'bank_account' && val && typeof val === 'object' && !Array.isArray(val)) {
      mapBankRowBlock(val as Record<string, unknown>, 0, bankRowErrors);
      continue;
    }

    const rowMsg = firstMessage(val);
    if (key === 'bank_accounts' && rowMsg) {
      const idxMatch = rowMsg.match(/Row\s+(\d+)/i);
      const idx = idxMatch ? Number(idxMatch[1]) - 1 : 0;
      bankRowErrors[idx] = { ...(bankRowErrors[idx] ?? {}), accountNumber: rowMsg };
      continue;
    }

    const uiKey = STATUTORY_API_TO_UI[key] ?? BANK_API_TO_UI[key];
    if (uiKey && rowMsg) {
      if (uiKey in BANK_API_TO_UI) {
        bankRowErrors[0] = { ...(bankRowErrors[0] ?? {}), [uiKey]: rowMsg };
      } else {
        fieldErrors[uiKey as keyof BankStatutoryFieldErrors] = rowMsg;
      }
    }
  }

  const firstField =
    Object.values(fieldErrors)[0] ?? Object.values(bankRowErrors[0] ?? {})[0];
  if (firstField) message = firstField;

  return new BankStatutoryApiError(message, fieldErrors, bankRowErrors);
}

function bankRowHasInput(row: BankAccount): boolean {
  return Boolean(
    row.accountNumber?.trim() ||
      row.ifscCode?.trim() ||
      row.bankId ||
      row.bankName?.trim(),
  );
}

/** Client-side validation before API call (mirrors backend rules). */
export function validateBankStatutoryClient(
  employee: Employee,
  banks: BankAccount[],
): { fieldErrors: BankStatutoryFieldErrors; bankRowErrors: Record<number, BankRowFieldErrors> } {
  const fieldErrors: BankStatutoryFieldErrors = {};
  const bankRowErrors: Record<number, BankRowFieldErrors> = {};

  const rows = banks.filter(bankRowHasInput);
  rows.forEach((row, index) => {
    const rowErr: BankRowFieldErrors = {};
    const ifsc = row.ifscCode?.trim().toUpperCase() ?? '';
    if (!ifsc) rowErr.ifscCode = 'IFSC code is required.';
    else if (!IFSC_RE.test(ifsc)) rowErr.ifscCode = 'IFSC must be 11 characters (e.g. HDFC0001234).';
    if (!row.bankId && !row.bankName?.trim()) {
      rowErr.bankName = 'Enter a valid IFSC to load the bank name.';
    }
    if (!row.accountTypeId && !row.accountType) {
      rowErr.accountType = 'Account type is required.';
    }
    const acct = row.accountNumber?.replace(/\s/g, '') ?? '';
    if (!acct && !row.accountNumberMasked) {
      rowErr.accountNumber = 'Bank account number is required.';
    } else if (acct && !ACCOUNT_RE.test(acct)) {
      rowErr.accountNumber = 'Account number must be 6 to 30 digits.';
    }
    if (Object.keys(rowErr).length) bankRowErrors[index] = rowErr;
  });

  const pan = employee.panNumber?.trim().toUpperCase() ?? '';
  if (pan && !PAN_RE.test(pan)) {
    fieldErrors.panNumber = 'PAN must follow AAAAA9999A format.';
  }
  const aadhaar = employee.aadhaarNumber?.replace(/\D/g, '') ?? '';
  if (aadhaar && !AADHAAR_RE.test(aadhaar)) {
    fieldErrors.aadhaarNumber = 'Aadhaar must be exactly 12 digits.';
  }
  const taxId = normalizeTaxRegimeId(employee.taxRegimeId);
  if (employee.taxRegimeId && !taxId) {
    fieldErrors.taxRegimeId = 'Select a valid tax regime.';
  }
  const uan = employee.uanNumber?.replace(/\D/g, '') ?? '';
  if (uan && !UAN_RE.test(uan)) {
    fieldErrors.uanNumber = 'UAN must be exactly 12 digits.';
  }
  if (employee.isEsiCovered) {
    const esic = employee.esiNumber?.replace(/[\s-]/g, '') ?? '';
    if (esic && !ESIC_RE.test(esic)) {
      fieldErrors.esiNumber = 'ESI number must be exactly 17 digits.';
    }
  }

  return { fieldErrors, bankRowErrors };
}

export function hasValidationErrors(
  fieldErrors: BankStatutoryFieldErrors,
  bankRowErrors: Record<number, BankRowFieldErrors>,
): boolean {
  return Object.keys(fieldErrors).length > 0 || Object.keys(bankRowErrors).length > 0;
}
