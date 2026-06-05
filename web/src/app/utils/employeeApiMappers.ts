import type {
  BankAccount,
  EducationEntry,
  Employee,
  InsuranceEntry,
  NomineeEntry,
  WorkExperienceEntry,
} from '../components/employees/mockData';

const str = (v: unknown) => (v == null ? '' : String(v));
const parseDateToInput = (v: unknown) => {
  const s = str(v);
  const m = s.match(/^(\d{2})-(\d{2})-(\d{4})$/);
  if (m) return `${m[3]}-${m[2]}-${m[1]}`;
  return s;
};

export function mapMyProfileToEmployee(data: Record<string, unknown>): Employee {
  const contacts = (data.contacts as Record<string, unknown>[])?.[0] ?? {};
  const employment = (data.employment_details as Record<string, unknown>) ?? {};
  const personal = (data.personal_details as Record<string, unknown>) ?? {};
  const first = str(personal.first_name ?? data.first_name);
  const last = str(personal.last_name ?? data.last_name);
  const name = [first, str(personal.middle_name), last].filter(Boolean).join(' ').trim() || str(data.employee_code);

  return {
    id: str(data.id),
    employeeId: str(data.employee_code ?? data.id),
    name,
    email: str(contacts.official_email ?? contacts.personal_email ?? ''),
    designation: str(employment.designation ?? ''),
    department: str(employment.department ?? ''),
    team: '',
    phone: str(contacts.mobile_no ?? contacts.personal_mobile ?? ''),
    joiningDate: str(employment.joining_date ?? data.joining_date ?? ''),
    location: str(employment.work_location ?? ''),
    status: str(data.status ?? 'Active'),
    initials: name
      .split(/\s+/)
      .map((p) => p[0])
      .join('')
      .slice(0, 2)
      .toUpperCase(),
    avatarColor: '#64748B',
    dateOfBirth: parseDateToInput(personal.date_of_birth),
    gender: str(personal.gender ?? data.gender ?? ''),
    maritalStatus: str(personal.marital_status ?? ''),
    bloodGroup: str(personal.blood_group ?? ''),
    nationality: str(personal.nationality ?? ''),
    bankName: '',
    accountNumber: '',
    ifscCode: '',
    pfNumber: '',
    esiNumber: '',
    family: [],
    education: [],
    nominees: [],
    insurance: [],
    workExperience: [],
  } as Employee;
}

export function mapAdminProfileToEmployee(employeeId: string, data: Record<string, unknown>): Employee {
  const personal = (data.personal_details as Record<string, unknown>) ?? data;
  const contacts = (data.contacts as Record<string, unknown>) ?? {};
  const employment = (data.employment_details as Record<string, unknown>) ?? {};
  const first = str(personal.first_name);
  const last = str(personal.last_name);
  const name = [first, str(personal.middle_name), last].filter(Boolean).join(' ').trim() || 'Employee';

  return {
    id: employeeId,
    employeeId: str(data.employee_code ?? employeeId),
    name,
    email: str(contacts.official_email ?? contacts.personal_email ?? ''),
    designation: str(employment.designation ?? ''),
    department: str(employment.department ?? ''),
    team: '',
    phone: str(contacts.mobile_no ?? contacts.personal_mobile ?? ''),
    joiningDate: str(employment.joining_date ?? ''),
    location: str(employment.work_location ?? ''),
    status: str(data.status ?? 'Active'),
    initials: name
      .split(/\s+/)
      .map((p) => p[0])
      .join('')
      .slice(0, 2)
      .toUpperCase(),
    avatarColor: '#64748B',
    dateOfBirth: parseDateToInput(personal.date_of_birth),
    gender: str(personal.gender),
    maritalStatus: str(personal.marital_status),
    bloodGroup: str(personal.blood_group),
    nationality: str(personal.nationality),
    bankName: '',
    accountNumber: '',
    ifscCode: '',
    pfNumber: '',
    esiNumber: '',
    family: [],
    education: [],
    nominees: [],
    insurance: [],
    workExperience: [],
  } as Employee;
}

/* ─── ESS list rows (build_*_details shape) ──────────────────────────────── */

export function mapEssNomineeList(rows: unknown): NomineeEntry[] {
  const list = Array.isArray(rows) ? rows : [];
  return list.map((r, i) => {
    const row = r as Record<string, unknown>;
    return {
      id: str(row.id || `nom-${i}`),
      nomineeName: str(row.name),
      nomineeEmail: str(row.email ?? ''),
      relationship: str(row.relation ?? row.relationship),
      dateOfBirth: parseDateToInput(row.date_of_birth),
      contactNumber: str(row.phone),
      address: str(row.address),
      nomineeType: 'EPF',
      epfPercentage: str(row.share_percentage ?? row.epf_percentage ?? ''),
      epsPercentage: str(row.eps_percentage ?? ''),
      gratuityPercentage: str(row.gratuity_percentage ?? ''),
      customPercentage: str(row.custom_percentage ?? ''),
      isMinor: Boolean(row.is_minor),
      guardian: row.guardian as NomineeEntry['guardian'],
      idProofFileName: str(row.identity_proof_name ?? ''),
      idProofDataUrl: str(row.identity_proof_url ?? ''),
    };
  });
}

export function mapEssEducationList(rows: unknown): EducationEntry[] {
  const list = Array.isArray(rows) ? rows : [];
  return list.map((r) => {
    const row = r as Record<string, unknown>;
    return {
      id: str(row.id),
      qualification: str(row.qualification ?? row.education_level),
      specialization: str(row.specialization),
      institutionName: str(row.institution_name ?? row.institution),
      university: str(row.university ?? row.university_name),
      fromDate: parseDateToInput(row.from_date ?? row.start_date),
      toDate: parseDateToInput(row.to_date ?? row.end_date),
      percentageCgpa: str(row.percentage ?? row.grade_or_cgpa ?? row.percentage_cgpa),
      grade: str(row.grade),
    } as EducationEntry & { id?: string };
  });
}

export function mapEssFamilyList(rows: unknown): Employee['family'] {
  const list = Array.isArray(rows) ? rows : [];
  return list.map((r, i) => {
    const row = r as Record<string, unknown>;
    return {
      id: str(row.id || `fam-${i}`),
      name: str(row.name ?? [row.first_name, row.last_name].filter(Boolean).join(' ')),
      relationship: str(row.relation ?? row.relationship),
      dob: parseDateToInput(row.date_of_birth ?? row.dob),
      gender: str(row.gender),
      bloodGroup: str(row.blood_group),
      phone: str(row.phone ?? row.mobile_no),
      occupation: str(row.occupation),
      isDependent: Boolean(row.is_dependent),
      isEmergencyContact: Boolean(row.emergency_contact ?? row.is_emergency_contact),
    };
  });
}

export function mapEssInsuranceList(rows: unknown): InsuranceEntry[] {
  if (!rows) return [];
  const list = Array.isArray(rows) ? rows : [rows];
  return list.map((r, i) => {
    const row = r as Record<string, unknown>;
    return {
      id: str(row.id || `ins-${i}`),
      insuranceProvider: str(row.insurance_provider ?? row.provider),
      policyNumber: str(row.policy_number),
      coverageType: str(row.coverage_type),
      coverageAmount: str(row.coverage_amount),
      validTill: parseDateToInput(row.valid_till ?? row.end_date),
      dependentsCovered: str(row.dependents_covered ?? row.nominee_name),
      documentFileName: str(row.document_file_name),
      documentDataUrl: str(row.document_url),
    };
  });
}

export function mapEssWorkExperienceList(rows: unknown): WorkExperienceEntry[] {
  const list = Array.isArray(rows) ? rows : [];
  return list.map((r, i) => {
    const row = r as Record<string, unknown>;
    return {
      id: str(row.id || `we-${i}`),
      companyName: str(row.company_name ?? row.company),
      jobTitle: str(row.job_title ?? row.designation),
      employmentType: str(row.employment_type),
      department: str(row.department),
      responsibilities: str(row.responsibilities),
      technologiesUsed: str(row.technologies_used),
      location: str(row.location),
      experienceLetterFileName: str(row.experience_letter_file_name),
      experienceLetterDataUrl: str(row.experience_letter_url),
      reasonForLeaving: str(row.reason_for_leaving),
      startDate: parseDateToInput(row.start_date),
      endDate: parseDateToInput(row.end_date),
    };
  });
}

/* ─── Admin list serializers ───────────────────────────────────────────────── */

export function mapAdminNomineeList(rows: unknown[]): NomineeEntry[] {
  return rows.map((r, i) => {
    const row = r as Record<string, unknown>;
    const first = str(row.first_name);
    const last = str(row.last_name);
    return {
      id: str(row.id || `nom-${i}`),
      nomineeName: [first, last].filter(Boolean).join(' '),
      nomineeEmail: str(row.email ?? ''),
      relationship: str(row.relation ?? row.relation_label),
      dateOfBirth: parseDateToInput(row.date_of_birth),
      contactNumber: str(row.mobile_no),
      address: str(row.address),
      nomineeType: str(row.nominee_purpose ?? 'EPF'),
      epfPercentage: str(row.nominee_percentage ?? ''),
      epsPercentage: '',
      gratuityPercentage: '',
      customPercentage: '',
      isMinor: Boolean(row.guardian_name),
      idProofFileName: str(row.identity_proof_name ?? ''),
      idProofDataUrl: str(row.identity_proof_url ?? ''),
    };
  });
}

export function mapAdminEducationList(rows: unknown[]): EducationEntry[] {
  return rows.map((r) => {
    const row = r as Record<string, unknown>;
    return {
      id: str(row.id),
      qualification: str(row.qualification_label ?? row.qualification),
      specialization: str(row.specialization_label ?? row.specialization),
      institutionName: str(row.institution_name),
      university: str(row.university_name ?? row.university),
      fromDate: parseDateToInput(row.from_date ?? row.start_date),
      toDate: parseDateToInput(row.to_date ?? row.end_date),
      percentageCgpa: str(row.percentage ?? row.grade_or_cgpa),
      grade: str(row.grade),
    } as EducationEntry & { id?: string };
  });
}

export function mapAdminFamilyList(rows: unknown[]): Employee['family'] {
  return rows.map((r, i) => {
    const row = r as Record<string, unknown>;
    return {
      id: str(row.id || `fam-${i}`),
      name: str(row.name ?? [row.first_name, row.last_name].filter(Boolean).join(' ')),
      relationship: str(row.relation ?? row.relation_label),
      dob: parseDateToInput(row.date_of_birth),
      gender: str(row.gender ?? row.gender_label),
      bloodGroup: str(row.blood_group ?? row.blood_group_label),
      phone: str(row.mobile_no ?? row.phone),
      occupation: str(row.occupation ?? row.occupation_label),
      isDependent: Boolean(row.is_dependent),
      isEmergencyContact: Boolean(row.is_emergency_contact),
    };
  });
}

export function mapAdminWorkExperienceList(rows: unknown[]): WorkExperienceEntry[] {
  return mapEssWorkExperienceList(rows);
}

/* ─── ESS submit payloads ─────────────────────────────────────────────────── */

export function mapNomineesToEssPayload(nominees: NomineeEntry[]) {
  return nominees.map((n) => ({
    id: /^[0-9a-f-]{36}$/i.test(n.id) ? n.id : undefined,
    name: n.nomineeName,
    relation_id: Number.isFinite(Number(n.relationship)) ? Number(n.relationship) : undefined,
    share_percentage: n.epfPercentage || n.epsPercentage || n.gratuityPercentage || n.customPercentage || undefined,
    phone: n.contactNumber || undefined,
    date_of_birth: n.dateOfBirth || undefined,
    address: n.address || undefined,
  }));
}

export function mapEducationToEssPayload(education: EducationEntry[]) {
  return education.map((e) => ({
    id: (e as EducationEntry & { id?: string }).id,
    qualification: e.qualification,
    specialization: e.specialization,
    institution_name: e.institutionName,
    university: e.university,
    from_date: e.fromDate,
    to_date: e.toDate,
    percentage: e.percentageCgpa,
    grade: e.grade,
  }));
}

export function mapFamilyToEssPayload(family: Employee['family']) {
  return family.map((m) => ({
    id: (m as { id?: string }).id,
    name: m.name,
    relation_id: Number.isFinite(Number(m.relationship)) ? Number(m.relationship) : undefined,
    date_of_birth: m.dob,
    gender: m.gender,
    blood_group: m.bloodGroup,
    phone: m.phone,
    occupation: m.occupation,
    is_dependent: m.isDependent,
    emergency_contact: m.isEmergencyContact,
  }));
}

export function mapInsuranceToEssPayload(insurance: InsuranceEntry[]) {
  return insurance.map((p) => ({
    id: p.id,
    insurance_provider: p.insuranceProvider,
    policy_number: p.policyNumber,
    coverage_type: p.coverageType,
    coverage_amount: p.coverageAmount,
    valid_till: p.validTill,
    dependents_covered: p.dependentsCovered,
  }));
}

export function mapWorkExperienceToEssPayload(work: WorkExperienceEntry[]) {
  return work.map((w) => ({
    id: w.id,
    company_name: w.companyName,
    job_title: w.jobTitle,
    employment_type: w.employmentType,
    department: w.department,
    responsibilities: w.responsibilities,
    technologies_used: w.technologiesUsed,
    location: w.location,
    reason_for_leaving: w.reasonForLeaving,
    start_date: w.startDate,
    end_date: w.endDate,
  }));
}

/* ─── Bank / statutory ───────────────────────────────────────────────────── */

function isMaskedAccountNumber(value: string): boolean {
  return /X{2,}/i.test(value) || /\*{2,}/.test(value);
}

function isMaskedIdentifier(value: string): boolean {
  return isMaskedAccountNumber(value);
}

const UUID_REGEX =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function isValidUuid(value: string | undefined | null): boolean {
  return Boolean(value && UUID_REGEX.test(String(value).trim()));
}

/** Reject corrupted numeric IDs (JS float/scientific notation from UUID mishandling). */
export function normalizeTaxRegimeId(value: string | undefined | null): string {
  const raw = String(value ?? '').trim();
  if (!raw || /e\+|e-/i.test(raw)) return '';
  if (/^\d{16,}$/.test(raw.replace(/-/g, ''))) return '';
  return isValidUuid(raw) ? raw : '';
}

function bankAccountsSnapshot(accounts: BankAccount[]): string {
  return JSON.stringify(
    accounts.map((row) => ({
      id: row.id,
      ifsc: row.ifscCode ?? '',
      bankId: row.bankId ?? '',
      bankName: row.bankName ?? '',
      accountTypeId: row.accountTypeId ?? '',
      branchName: row.branchName ?? '',
      paymentTypeId: row.paymentTypeId ?? '',
      accountHolderName: row.accountHolderName ?? '',
      isPrimary: Boolean(row.isPrimary),
      accountNumber: isMaskedAccountNumber(row.accountNumber ?? '')
        ? '__masked__'
        : (row.accountNumber ?? ''),
    })),
  );
}

function statutorySnapshot(employee: Employee): string {
  return JSON.stringify({
    pan: employee.panNumber ?? '',
    aadhaar: employee.aadhaarNumber ?? '',
    taxRegimeId: normalizeTaxRegimeId(employee.taxRegimeId),
    uan: employee.uanNumber ?? '',
    pf: employee.pfNumber ?? '',
    esi: employee.esiNumber ?? '',
    lin: employee.linNumber ?? '',
    isPfCovered: Boolean(employee.isPfCovered),
    isEsiCovered: Boolean(employee.isEsiCovered),
    isLwfCovered: Boolean(employee.isLwfCovered),
    isEarlierMemberOfPensionOnHigherWages: Boolean(
      employee.isEarlierMemberOfPensionOnHigherWages,
    ),
  });
}

function buildAdminBankAccountsPayload(
  accounts: BankAccount[],
  holderName: string,
): Record<string, unknown>[] {
  return accounts.map((row) => {
    const item: Record<string, unknown> = {
      primary: row.isPrimary === true,
      ifsc: row.ifscCode?.toUpperCase(),
      bank_id: row.bankId || undefined,
      bank: row.bankName || undefined,
      account_type_id: row.accountTypeId || undefined,
      type: row.accountType || undefined,
      account_holder_name: row.accountHolderName || holderName,
      branch_name: row.branchName || undefined,
      payment_type_id: row.paymentTypeId || undefined,
    };
    if (isValidUuid(row.id)) {
      item.id = row.id;
    }
    if (row.accountNumber?.trim() && !isMaskedAccountNumber(row.accountNumber)) {
      item.account_no = row.accountNumber.replace(/\s/g, '');
    }
    return item;
  });
}

function isValidPan(value: string): boolean {
  return /^[A-Z]{5}[0-9]{4}[A-Z]$/i.test(value.replace(/\s/g, ''));
}

function isValidAadhaar(value: string): boolean {
  const cleaned = value.replace(/[\s-]/g, '');
  return /^\d{12}$/.test(cleaned);
}

function isValidUan(value: string): boolean {
  const cleaned = value.replace(/[\s-]/g, '');
  return /^\d{12}$/.test(cleaned);
}

function normalizePanForPayload(value: string): string | undefined {
  if (!value?.trim() || isMaskedIdentifier(value) || !isValidPan(value)) return undefined;
  return value.replace(/\s/g, '').toUpperCase();
}

function normalizeAadhaarForPayload(value: string): string | undefined {
  if (!value?.trim() || isMaskedIdentifier(value) || !isValidAadhaar(value)) return undefined;
  return value.replace(/[\s-]/g, '');
}

function normalizeUanForPayload(value: string): string | undefined {
  if (!value?.trim() || isMaskedIdentifier(value) || !isValidUan(value)) return undefined;
  return value.replace(/[\s-]/g, '');
}

function normalizeIdentifierForEdit(value: string): string {
  if (!value || isMaskedIdentifier(value)) return '';
  return value;
}

function normalizeAccountNumberForEdit(value: string, masked?: boolean): string {
  if (!value || masked || isMaskedAccountNumber(value)) return '';
  return value.replace(/\s/g, '');
}

function mapEssBankAccountRow(row: Record<string, unknown>, index: number): BankAccount {
  return {
    id: str(row.id || `bank-${index}`),
    accountNumber: str(row.account_no ?? ''),
    bankName: str(row.bank ?? ''),
    bankId: str(row.bank_id ?? ''),
    ifscCode: str(row.ifsc ?? ''),
    accountType: str(row.type ?? ''),
    accountTypeId: str(row.account_type_id ?? ''),
    accountHolderName: str(row.account_holder_name ?? ''),
    branchName: str(row.branch_name ?? ''),
    paymentType: str(row.payment_type ?? ''),
    paymentTypeId: str(row.payment_type_id ?? ''),
    isPrimary: row.primary !== false,
  };
}

export function mapEssBankStatutoryDetails(data: Record<string, unknown>): Partial<Employee> {
  const accounts = Array.isArray(data.bank_accounts) ? data.bank_accounts : [];
  const statutory = (data.statutory_details as Record<string, unknown>) ?? {};
  const bankAccounts = accounts.map((r, i) =>
    mapEssBankAccountRow(r as Record<string, unknown>, i),
  );
  const primary = bankAccounts.find((a) => a.isPrimary) ?? bankAccounts[0];

  return {
    bankAccounts: bankAccounts.length ? bankAccounts : undefined,
    bankName: primary?.bankName ?? '',
    accountNumber: primary?.accountNumber ?? '',
    ifscCode: primary?.ifscCode ?? '',
    panNumber: str(statutory.pan_number ?? ''),
    aadhaarNumber: str(statutory.aadhaar_number ?? ''),
    uanNumber: str(statutory.uan_number ?? ''),
    pfNumber: str(statutory.pf_number ?? ''),
    esiNumber: str(statutory.esic_number ?? ''),
    taxRegime: str(statutory.tax_regime_name ?? statutory.tax_regime ?? ''),
    taxRegimeId: normalizeTaxRegimeId(str(statutory.tax_regime_id ?? '')),
    isPfCovered: Boolean(statutory.pf_number),
    isEsiCovered: Boolean(statutory.esic_number),
  };
}

function mapAdminBankAccountRow(bank: Record<string, unknown>, index: number): BankAccount {
  const rawAccount = str(bank.account_number ?? bank.masked_account_number ?? '');
  const accountMasked = isMaskedAccountNumber(rawAccount);
  return {
    id: str(bank.id || `bank-${index}`),
    accountNumber: normalizeAccountNumberForEdit(rawAccount, accountMasked),
    accountNumberMasked: accountMasked,
    bankName: str(bank.bank_name ?? ''),
    bankId: str(bank.bank ?? ''),
    ifscCode: str(bank.ifsc_code ?? ''),
    accountType: str(bank.account_type_label ?? ''),
    accountTypeId: str(bank.account_type ?? ''),
    accountHolderName: str(bank.account_holder_name ?? ''),
    branchName: str(bank.branch_name ?? ''),
    paymentTypeId: str(bank.payment_type_id ?? ''),
    paymentType: str(bank.payment_type_label ?? bank.payment_type_name ?? ''),
    isPrimary: bank.is_primary !== false,
  };
}

export function mapAdminBankStatutoryDetails(data: Record<string, unknown>): Partial<Employee> {
  const listed = Array.isArray(data.bank_accounts) ? data.bank_accounts : [];
  const bank = (data.bank_account as Record<string, unknown> | null) ?? null;
  const docs = (data.statutory_documents as Record<string, unknown>) ?? {};
  const pf = (data.pf_details as Record<string, unknown>) ?? {};
  const esi = (data.esi_details as Record<string, unknown>) ?? {};
  const lwf = (data.lwf_details as Record<string, unknown>) ?? {};

  const bankAccounts: BankAccount[] = listed.length
    ? listed.map((row, index) => mapAdminBankAccountRow(row as Record<string, unknown>, index))
    : bank
      ? [mapAdminBankAccountRow(bank, 0)]
      : [];

  const primary = bankAccounts.find((a) => a.isPrimary) ?? bankAccounts[0];

  return {
    bankAccounts: bankAccounts.length ? bankAccounts : undefined,
    bankName: primary?.bankName ?? '',
    accountNumber: primary?.accountNumber ?? '',
    ifscCode: primary?.ifscCode ?? '',
    panNumber: str(docs.pan ?? ''),
    aadhaarNumber: str(docs.aadhaar_no ?? ''),
    taxRegime: str(docs.tax_regime_name ?? docs.tax_regime_code ?? ''),
    taxRegimeId: normalizeTaxRegimeId(str(docs.tax_regime_id ?? '')),
    uanNumber: str(pf.uan ?? ''),
    pfNumber: str(pf.pf_account_no ?? ''),
    isPfCovered: Boolean(pf.is_pf_covered),
    esiNumber: str(esi.esic_no ?? ''),
    isEsiCovered: Boolean(esi.is_esi_covered),
    isLwfCovered: Boolean(lwf.is_lwf_covered),
    linNumber: str(lwf.lin_number ?? ''),
    isEarlierMemberOfPensionOnHigherWages: Boolean(
      pf.is_higher_pension_wages ?? pf.earlier_member_of_pension_on_higher_wages,
    ),
  };
}

export function mapEmployeeToEssBankStatutoryPayload(
  employee: Employee,
  holderName: string,
): Record<string, unknown> {
  const accounts = employee.bankAccounts?.length
    ? employee.bankAccounts
    : [
        {
          id: `bank-${employee.id}-0`,
          accountNumber: employee.accountNumber,
          bankName: employee.bankName,
          ifscCode: employee.ifscCode,
          isPrimary: true,
        } as BankAccount,
      ];

  const bank_accounts = accounts.map((row) => {
    const item: Record<string, unknown> = {
      account_no: row.accountNumber,
      ifsc: row.ifscCode?.toUpperCase(),
      bank: row.bankName || row.bankId,
      bank_id: row.bankId || undefined,
      type: row.accountType || 'Savings',
      account_type_id: row.accountTypeId || undefined,
      primary: row.isPrimary !== false,
      account_holder_name: row.accountHolderName || holderName,
      branch_name: row.branchName || undefined,
      payment_type_id: row.paymentTypeId || undefined,
    };
    if (row.id && /^[0-9a-f-]{36}$/i.test(row.id)) {
      item.id = row.id;
    }
    return item;
  });

  const statutory_details: Record<string, unknown> = {};
  const pan = normalizePanForPayload(employee.panNumber ?? '');
  const aadhaar = normalizeAadhaarForPayload(employee.aadhaarNumber ?? '');
  if (pan) statutory_details.pan_number = pan;
  if (aadhaar) statutory_details.aadhaar_number = aadhaar;
  if (employee.uanNumber) statutory_details.uan_number = employee.uanNumber;
  if (employee.isPfCovered && employee.pfNumber) statutory_details.pf_number = employee.pfNumber;
  if (employee.isEsiCovered && employee.esiNumber) statutory_details.esic_number = employee.esiNumber;
  const taxRegimeId = normalizeTaxRegimeId(employee.taxRegimeId);
  if (taxRegimeId) statutory_details.tax_regime_id = taxRegimeId;

  return { bank_accounts, statutory_details };
}

function normalizePfNumberForPayload(value: string): string | undefined {
  if (!value?.trim() || isMaskedIdentifier(value)) return undefined;
  return value.trim();
}

function normalizeEsiNumberForPayload(value: string): string | undefined {
  if (!value?.trim() || isMaskedIdentifier(value)) return undefined;
  const cleaned = value.replace(/[\s-]/g, '');
  if (!/^\d{17}$/.test(cleaned)) return undefined;
  return cleaned;
}

function normalizeLinForPayload(value: string): string | undefined {
  if (!value?.trim() || isMaskedIdentifier(value)) return undefined;
  return value.trim();
}

function bankRowHasInput(row: BankAccount): boolean {
  return Boolean(
    row.accountNumber?.trim() ||
      row.ifscCode?.trim() ||
      row.bankId ||
      row.bankName?.trim() ||
      row.accountNumberMasked,
  );
}

function buildAdminBankAccountsPayloadWithRemovals(
  currentAccounts: BankAccount[],
  originalAccounts: BankAccount[],
  holderName: string,
): Record<string, unknown>[] {
  const rows = buildAdminBankAccountsPayload(currentAccounts, holderName);
  const currentIds = new Set(
    currentAccounts.filter((row) => isValidUuid(row.id)).map((row) => row.id),
  );
  for (const orig of originalAccounts) {
    if (isValidUuid(orig.id) && !currentIds.has(orig.id)) {
      rows.push({ id: orig.id, remove: true });
    }
  }
  return rows;
}

function appendAdminStatutoryPayload(
  payload: Record<string, unknown>,
  employee: Employee,
): void {
  const statutory_documents: Record<string, unknown> = {};
  const pan = normalizePanForPayload(employee.panNumber ?? '');
  const aadhaar = normalizeAadhaarForPayload(employee.aadhaarNumber ?? '');
  if (pan) statutory_documents.pan = pan;
  if (aadhaar) statutory_documents.aadhaar_no = aadhaar;
  const taxRegimeId = normalizeTaxRegimeId(employee.taxRegimeId);
  if (taxRegimeId) statutory_documents.tax_regime = taxRegimeId;
  if (Object.keys(statutory_documents).length) {
    payload.statutory_documents = statutory_documents;
  }

  const pf_details: Record<string, unknown> = {
    is_pf_covered: Boolean(employee.isPfCovered),
    earlier_member_of_pension_on_higher_wages: Boolean(
      employee.isEarlierMemberOfPensionOnHigherWages,
    ),
  };
  const uan = normalizeUanForPayload(employee.uanNumber ?? '');
  const pfNo = normalizePfNumberForPayload(employee.pfNumber ?? '');
  if (uan) pf_details.uan = uan;
  if (employee.isPfCovered && pfNo) pf_details.pf_account_no = pfNo;
  payload.pf_details = pf_details;

  const esi_details: Record<string, unknown> = {
    is_esi_covered: Boolean(employee.isEsiCovered),
  };
  const esic = normalizeEsiNumberForPayload(employee.esiNumber ?? '');
  if (employee.isEsiCovered && esic) esi_details.esic_no = esic;
  payload.esi_details = esi_details;

  const lwf_details: Record<string, unknown> = {
    is_lwf_covered: Boolean(employee.isLwfCovered),
  };
  const lin = normalizeLinForPayload(employee.linNumber ?? '');
  if (employee.isLwfCovered && lin) lwf_details.lin_number = lin;
  payload.lwf_details = lwf_details;
}

export function mapEmployeeToAdminBankStatutoryPayload(
  employee: Employee,
  original?: Employee,
): Record<string, unknown> {
  const payload: Record<string, unknown> = {};
  const baseline = original ?? ({} as Employee);
  const currentAccounts = (employee.bankAccounts ?? []).filter(bankRowHasInput);
  const originalAccounts = (baseline.bankAccounts ?? []).filter(bankRowHasInput);
  const banksChanged = bankAccountsSnapshot(currentAccounts) !== bankAccountsSnapshot(originalAccounts);
  const removedPersisted = originalAccounts.some(
    (orig) => isValidUuid(orig.id) && !currentAccounts.some((cur) => cur.id === orig.id),
  );

  if (banksChanged || removedPersisted) {
    payload.bank_accounts = buildAdminBankAccountsPayloadWithRemovals(
      currentAccounts,
      originalAccounts,
      employee.name,
    );
  }

  const statutoryChanged = statutorySnapshot(employee) !== statutorySnapshot(baseline);
  if (statutoryChanged || banksChanged || removedPersisted) {
    appendAdminStatutoryPayload(payload, employee);
  }

  return payload;
}

/* ─── Passport & visa ────────────────────────────────────────────────────── */

function mapPassportVisaRowToEmployee(row: Record<string, unknown>): Partial<Employee> {
  return {
    passportNumber: str(row.passport_number ?? ''),
    passportHolderName: str(row.passport_holder_name ?? ''),
    passportIssueDate: parseDateToInput(row.issue_date),
    passportExpiry: parseDateToInput(row.expiry_date),
    passportPlaceOfIssue: str(row.issue_place ?? ''),
    passportCountryOfIssue: str(row.issue_country ?? ''),
    passportCategory: str(row.passport_category ?? ''),
    passportStatus: str(row.passport_status ?? ''),
    visaType: str(row.visa_type ?? ''),
    visaNumber: str(row.visa_number ?? ''),
    visaExpiry: parseDateToInput(row.visa_expiry_date),
    visaCountry: str(row.visa_country ?? ''),
    visaSponsor: str(row.visa_sponsor ?? ''),
    visaIssueDate: parseDateToInput(row.visa_issue_date),
    visaStatus: str(row.visa_status ?? ''),
  };
}

export function mapAdminPassportVisaDetails(data: Record<string, unknown>): Partial<Employee> {
  const passport = (data.passport_details as Record<string, unknown>) ?? {};
  const visa = (data.visa_details as Record<string, unknown>) ?? {};
  return {
    passportNumber: str(passport.passport_no ?? ''),
    passportHolderName: str(passport.holder_name ?? ''),
    passportIssueDate: parseDateToInput(passport.passport_issue_date),
    passportExpiry: parseDateToInput(passport.passport_expiry),
    passportPlaceOfIssue: str(passport.passport_place_of_issue ?? ''),
    passportCountryOfIssue: str(
      passport.passport_country_of_issue ?? passport.passport_issuing_country_label ?? '',
    ),
    passportCategory: str(passport.passport_category ?? ''),
    passportStatus: str(
      passport.passport_status_label ?? passport.passport_status ?? '',
    ),
    visaType: str(visa.visa_type ?? visa.visaType ?? ''),
    visaNumber: str(visa.visa_number ?? visa.visaNumber ?? ''),
    visaExpiry: parseDateToInput(visa.visa_expiry ?? visa.visaExpiry),
    visaCountry: str(visa.visa_country ?? visa.visaCountry ?? ''),
    visaSponsor: str(visa.visa_sponsor ?? visa.visaSponsor ?? ''),
    visaIssueDate: parseDateToInput(visa.visa_issue_date ?? visa.visaIssueDate),
    visaStatus: str(visa.visa_status ?? visa.visaStatus ?? ''),
  };
}

export function mapEssPassportVisaDetails(data: Record<string, unknown>): Partial<Employee> {
  const rows = Array.isArray(data.passport_visa_records) ? data.passport_visa_records : [];
  const first = (rows[0] as Record<string, unknown>) ?? {};
  return mapPassportVisaRowToEmployee(first);
}

export function mapEmployeeToAdminPassportPayload(employee: Employee): Record<string, unknown> {
  return {
    passport_details: {
      passport_no: employee.passportNumber || undefined,
      passport_issue_date: employee.passportIssueDate || undefined,
      passport_expiry: employee.passportExpiry || undefined,
      passport_place_of_issue: employee.passportPlaceOfIssue || undefined,
      passport_category: employee.passportCategory || undefined,
      passport_status: employee.passportStatus || undefined,
      passport_issuing_country: employee.passportCountryOfIssue || undefined,
    },
    visa_details: {
      visa_country: employee.visaCountry || undefined,
      visa_type: employee.visaType || undefined,
      visa_number: employee.visaNumber || undefined,
      visa_sponsor: employee.visaSponsor || undefined,
      visa_status: employee.visaStatus || undefined,
      visa_issue_date: employee.visaIssueDate || undefined,
      visa_expiry: employee.visaExpiry || undefined,
    },
  };
}

export function mapEmployeeToEssPassportPayload(employee: Employee): Record<string, unknown> {
  return {
    passport_visa_records: [
      {
        passport_number: employee.passportNumber || undefined,
        passport_holder_name: employee.passportHolderName || undefined,
        issue_date: employee.passportIssueDate || undefined,
        expiry_date: employee.passportExpiry || undefined,
        issue_place: employee.passportPlaceOfIssue || undefined,
        issue_country: employee.passportCountryOfIssue || undefined,
        passport_category: employee.passportCategory || undefined,
        passport_status: employee.passportStatus || undefined,
        has_visa: Boolean(employee.visaNumber || employee.visaType || employee.visaExpiry),
        visa_type: employee.visaType || undefined,
        visa_number: employee.visaNumber || undefined,
        visa_expiry_date: employee.visaExpiry || undefined,
        visa_issue_date: employee.visaIssueDate || undefined,
        visa_country: employee.visaCountry || undefined,
        visa_sponsor: employee.visaSponsor || undefined,
        visa_status: employee.visaStatus || undefined,
      },
    ],
  };
}
