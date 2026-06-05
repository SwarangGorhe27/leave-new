import { useMemo, useState } from 'react';
import { CheckCircle2, Copy, Link2, UserPlus, X } from 'lucide-react';
import { FormField } from '@components/forms/FormField';
import {
  useCostCenters,
  useDesignations,
  useDepartments,
  useEmployeeCategories,
  useEmployeeList,
  useGenders,
  useGrades,
  useInviteEmployee,
  useShiftTypes,
  useSourceOfHire,
  useTransportTypes,
  useAccountTypes,
} from '@hooks/useEmployees';

interface AddEmployeeFormProps {
  onClose: () => void;
  onSuccess?: () => void;
}

type EmployeeExperience = {
  company_name: string;
  designation: string;
  from_date: string;
  to_date: string;
  last_drawn_salary: string;
  reason_for_leaving: string;
};

type AddEmployeeFormState = {
  series: string;
  employee_number: string;
  first_name: string;
  middle_name: string;
  last_name: string;
  date_of_birth: string;
  aadhaar_number: string;
  gender: string;
  status: string;
  date_of_joining: string;
  probation_period: string;
  email: string;
  alternate_email: string;
  personal_mobile: string;
  alternate_mobile: string;
  emergency_contact_name: string;
  emergency_contact_number: string;
  father_name: string;
  spouse_name: string;
  marital_status: string;
  blood_group: string;
  reporting_manager: string;
  designation: string;
  department: string;
  grade: string;
  location: string;
  attendance_scheme: string;
  referred_by: string;
  referral_name: string;
  allow_employee_fill_info: boolean;
  pan_number: string;
  bank_account_number: string;
  bank_account_type: string;
  ifsc_code: string;
  onboarding_policy: string;
  employment_type: string;
  branch: string;
  employee_category: string;
  total_experience: string;
  relevant_experience: string;
  other_experience: string;
  experience_history: EmployeeExperience[];
  offer_letter: File | null;
  id_proof: File | null;
  resume: File | null;
  other_docs: File[];
  card_number: string;
  access_valid_from: string;
  access_valid_to: string;
};

const initialFormState: AddEmployeeFormState = {
  series: 'Permanent Employees',
  employee_number: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  date_of_birth: '',
  aadhaar_number: '',
  gender: '',
  status: 'Confirmed',
  date_of_joining: '',
  probation_period: '',
  
  email: '',
  alternate_email: '',
  personal_mobile: '',
  alternate_mobile: '',
  emergency_contact_name: '',
  emergency_contact_number: '',
  father_name: '',
  spouse_name: '',
  marital_status: '',
  blood_group: '',
  reporting_manager: '',
  designation: '',
  department: '',
  grade: '',
  location: '',
  attendance_scheme: 'General Scheme',
  referred_by: '',
  referral_name: '',
  allow_employee_fill_info: false,
  pan_number: '',
  bank_account_number: '',
  bank_account_type: '',
  ifsc_code: '',
  onboarding_policy: '',
  employment_type: '',
  branch: '',
  employee_category: '',
  total_experience: '',
  relevant_experience: '',
  other_experience: '',
  experience_history: [
    {
      company_name: '',
      designation: '',
      from_date: '',
      to_date: '',
      last_drawn_salary: '',
      reason_for_leaving: '',
    },
  ],
  offer_letter: null,
  id_proof: null,
  resume: null,
  other_docs: [],
  card_number: '',
  access_valid_from: '',
  access_valid_to: '',
};

const seriesOptions = ['Permanent Employees', 'Temporary Employees', 'Manual Entry'];
const statusOptions = ['Confirmed', 'Contract', 'Probation', 'Trainee'];
const employmentTypeOptions = ['Permanent', 'Temporary', 'Contract', 'Trainee'];
const attendanceSchemes = ['Contract Employees', 'General Scheme', 'Probation Scheme', 'Trainee Scheme'];
const policyOptions = ['Standard Onboarding', 'Fast Track', 'Executive Program'];
const locationOptions = ['Mumbai', 'Pune', 'Bengaluru', 'Delhi', 'Hyderabad'];
const maritalStatusOptions = ['Single', 'Married', 'Divorced', 'Widowed'];
const bloodGroupOptions = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

export function AddEmployeeForm({ onClose, onSuccess }: AddEmployeeFormProps) {
  const { data: departments = [] } = useDepartments();
  const { data: designations = [] } = useDesignations();
  const { data: genders = [] } = useGenders();
  const { data: grades = [] } = useGrades();
  const { data: employeeCategories = [] } = useEmployeeCategories();
  const { data: sourceOfHire = [] } = useSourceOfHire();
  const { data: transportTypes = [] } = useTransportTypes();
  const { data: costCenters = [] } = useCostCenters();
  const { data: shiftTypes = [] } = useShiftTypes();
  const { data: employees = [] } = useEmployeeList();
  const { data: accountTypes = [] } = useAccountTypes();
  const invite = useInviteEmployee();

  const [form, setForm] = useState<AddEmployeeFormState>(initialFormState);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [inviteResult, setInviteResult] = useState<{
    employee_code: string;
    full_name: string;
    invite_link: string;
  } | null>(null);
  const [copied, setCopied] = useState(false);

  const managerOptions = useMemo(
    () => employees.map((employee: any) => ({ id: employee.id, name: employee.full_name })),
    [employees],
  );

  const update = (field: keyof AddEmployeeFormState, value: string) => {
    setForm((prev) => ({
      ...prev,
      [field]: value,
      ...(field === 'referred_by' && !value ? { referral_name: '' } : {}),
    }));
    setErrors((prev) => ({ ...prev, [field]: '' }));
  };

  const updateBoolean = (field: 'allow_employee_fill_info', value: boolean) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const updateFile = (field: 'offer_letter' | 'id_proof' | 'resume', file: File | null) => {
    setForm((prev) => ({ ...prev, [field]: file }));
    setErrors((prev) => ({ ...prev, [field]: '' }));
  };

  const updateOtherDocs = (files: FileList | null) => {
    if (!files) return;
    setForm((prev) => ({ ...prev, other_docs: Array.from(files) }));
  };

  const addExperienceEntry = () => {
    setForm((prev) => ({
      ...prev,
      experience_history: [
        ...prev.experience_history,
        {
          company_name: '',
          designation: '',
          from_date: '',
          to_date: '',
          last_drawn_salary: '',
          reason_for_leaving: '',
        },
      ],
    }));
  };

  const removeExperienceEntry = (index: number) => {
    setForm((prev) => ({
      ...prev,
      experience_history: prev.experience_history.filter((_, idx) => idx !== index),
    }));
  };

  const updateExperience = (index: number, field: keyof EmployeeExperience, value: string) => {
    setForm((prev) => {
      const experience_history = [...prev.experience_history];
      experience_history[index] = { ...experience_history[index], [field]: value };
      return { ...prev, experience_history };
    });
    setErrors((prev) => ({ ...prev, [`experience_history.${index}.${field}`]: '' }));
  };

  const hasValue = (value: string | undefined) => Boolean(value?.trim());

  const validateForm = () => {
    const nextErrors: Record<string, string> = {};
    const requiredFields = [
      'series',
      'employee_number',
      'first_name',
      'last_name',
      'date_of_birth',
      'aadhaar_number',
      'gender',
      'status',
      'date_of_joining',
      'email',
      'personal_mobile',
      'emergency_contact_name',
      'emergency_contact_number',
      'father_name',
      'onboarding_policy',
      'reporting_manager',
      'designation',
      'department',
      'grade',
      'location',
      'attendance_scheme',
      'employment_type',
      'pan_number',
      'bank_account_number',
      'bank_account_type',
      'ifsc_code',
    ];

    requiredFields.forEach((field) => {
      const value = form[field as keyof AddEmployeeFormState] as string | undefined;
      if (!hasValue(value)) {
        nextErrors[field] = 'This field is required';
      }
    });

    if (form.referred_by && !hasValue(form.referral_name)) {
      nextErrors.referral_name = 'Referral name is required when referred by is selected';
    }

    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      nextErrors.email = 'Enter a valid email address';
    }

    if (form.alternate_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.alternate_email)) {
      nextErrors.alternate_email = 'Enter a valid alternate email';
    }

    if (form.personal_mobile && !/^\d{10,15}$/.test(form.personal_mobile)) {
      nextErrors.personal_mobile = 'Enter a valid phone number';
    }

    if (form.alternate_mobile && !/^\d{10,15}$/.test(form.alternate_mobile)) {
      nextErrors.alternate_mobile = 'Enter a valid alternate mobile number';
    }

    if (form.aadhaar_number && !/^\d{12}$/.test(form.aadhaar_number)) {
      nextErrors.aadhaar_number = 'Aadhaar must be 12 digits';
    }

    if (form.pan_number && !/^[A-Z]{5}[0-9]{4}[A-Z]$/.test(form.pan_number.toUpperCase())) {
      nextErrors.pan_number = 'Enter a valid PAN number';
    }

    if (form.ifsc_code && !/^[A-Za-z]{4}[0-9]{7}$/.test(form.ifsc_code.toUpperCase())) {
      nextErrors.ifsc_code = 'Enter a valid IFSC code';
    }

    form.experience_history.forEach((entry, index) => {
      const hasAnyField = Object.values(entry).some((value) => value.trim());
      if (hasAnyField) {
        if (!entry.company_name.trim()) {
          nextErrors[`experience_history.${index}.company_name`] = 'Company name is required';
        }
        if (!entry.designation.trim()) {
          nextErrors[`experience_history.${index}.designation`] = 'Designation is required';
        }
        if (!entry.from_date.trim()) {
          nextErrors[`experience_history.${index}.from_date`] = 'From date is required';
        }
        if (!entry.to_date.trim()) {
          nextErrors[`experience_history.${index}.to_date`] = 'To date is required';
        }
        if (!entry.last_drawn_salary.trim()) {
          nextErrors[`experience_history.${index}.last_drawn_salary`] = 'Last drawn salary is required';
        }
        if (!entry.reason_for_leaving.trim()) {
          nextErrors[`experience_history.${index}.reason_for_leaving`] = 'Reason for leaving is required';
        }
      }
    });

    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const buildPayload = () => ({
    employee_code: form.employee_number,
    first_name: form.first_name,
    last_name: form.last_name,
    middle_name: form.middle_name || undefined,
    official_email: form.email,
    personal_email: form.alternate_email || undefined,
    mobile_number: form.personal_mobile,
    alternate_mobile_number: form.alternate_mobile || undefined,
    emergency_contact_name: form.emergency_contact_name || undefined,
    emergency_contact_number: form.emergency_contact_number || undefined,
    father_name: form.father_name || undefined,
    spouse_name: form.spouse_name || undefined,
    gender: form.gender,
    date_of_birth: form.date_of_birth || undefined,
    marital_status: form.marital_status || undefined,
    blood_group: form.blood_group || undefined,
    department: form.department || undefined,
    designation: form.designation || undefined,
    employment_type: form.employment_type || undefined,
    joining_date: form.date_of_joining,
    employee_status: form.status === 'Confirmed' ? 'ACTIVE' : form.status === 'Contract' ? 'CONTRACT' : form.status === 'Probation' ? 'PROBATION' : 'TRAINEE',
    work_location: form.location || undefined,
    grade: form.grade || undefined,
    reporting_manager: form.reporting_manager || undefined,
    referred_by: form.referred_by || undefined,
    onboarding_policy: form.onboarding_policy || undefined,
    allow_employee_to_fill_information: form.allow_employee_fill_info,
    probation_period: form.probation_period ? parseInt(form.probation_period) : undefined,
    employee_number_series: form.series || undefined,
    pan_number: form.pan_number || undefined,
    aadhaar_number: form.aadhaar_number || undefined,
    bank_account: form.bank_account_number && form.ifsc_code && form.bank_account_type ? {
      account_number: form.bank_account_number,
      ifsc_code: form.ifsc_code,
      account_type: form.bank_account_type,
      account_holder_name: `${form.first_name} ${form.last_name}`,
    } : undefined,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    invite.mutate(buildPayload(), {
      onSuccess: (data) => {
        setInviteResult({
          employee_code: data.employee_code,
          full_name: data.full_name,
          invite_link: `${window.location.origin}${data.invite_link}`,
        });
        onSuccess?.();
      },
    });
  };

  const handleCopy = () => {
    if (inviteResult) {
      navigator.clipboard.writeText(inviteResult.invite_link);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const inputClass = 'w-full rounded-xl border border-surface-200 bg-surface-0 px-3 py-2.5 text-sm text-surface-900 outline-none transition-colors focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-white/10 dark:bg-surface-100 dark:text-white';

  const renderField = (label: string, children: React.ReactNode, errorKey?: string) => (
    <FormField label={label} required={Boolean(errorKey)}>
      {children}
      {errorKey && errors[errorKey] ? <p className="mt-1 text-xs text-danger-500">{errors[errorKey]}</p> : null}
    </FormField>
  );

  if (inviteResult) {
    return (
      <div className="mx-auto max-w-lg space-y-5 p-6">
        <div className="flex flex-col items-center text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 dark:bg-emerald-500/10">
            <CheckCircle2 className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
          </div>
          <h3 className="mt-4 text-lg font-semibold text-surface-900 dark:text-white">Employee Created!</h3>
          <p className="mt-1 text-sm text-surface-500 dark:text-white/40">
            <span className="font-medium text-surface-700 dark:text-white/70">{inviteResult.full_name}</span> has been added as{' '}
            <span className="font-mono text-xs font-semibold text-brand-600 dark:text-brand-400">{inviteResult.employee_code}</span>
          </p>
        </div>

        <div className="surface-card rounded-xl border border-surface-100 p-4 dark:border-white/5">
          <p className="mb-2 text-xs font-medium text-surface-600 dark:text-white/50">
            <Link2 className="mr-1 inline h-3 w-3" /> Share this invite link with the employee to set up their password:
          </p>
          <div className="flex items-center gap-2">
            <input
              type="text"
              readOnly
              value={inviteResult.invite_link}
              className="flex-1 rounded-lg border border-surface-200 bg-surface-50 px-3 py-2 text-xs font-mono text-surface-700 dark:border-white/10 dark:bg-white/5 dark:text-white/70"
            />
            <button
              type="button"
              onClick={handleCopy}
              className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-brand-700 dark:bg-brand-500 dark:hover:bg-brand-600"
            >
              {copied ? <CheckCircle2 className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
        </div>

        <p className="text-center text-xs text-surface-400 dark:text-white/30">
          The link expires in 7 days. The employee will set their password and log in to complete their profile.
        </p>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => {
              setInviteResult(null);
              setForm(initialFormState);
              invite.reset();
            }}
            className="flex-1 rounded-xl border border-surface-200 px-4 py-2.5 text-sm font-medium text-surface-700 transition-colors hover:bg-surface-50 dark:border-white/10 dark:text-white/70 dark:hover:bg-white/5"
          >
            <UserPlus className="mr-1.5 inline h-4 w-4" /> Add Another
          </button>
          <button
            type="button"
            onClick={onClose}
            className="flex-1 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700 dark:bg-brand-500 dark:hover:bg-brand-600"
          >
            Done
          </button>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-6xl space-y-6 p-4 pb-32">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-semibold text-surface-900 dark:text-white">Add New Employee</h3>
          <p className="mt-1 text-sm text-surface-500 dark:text-white/40">Complete the employee profile in one page.</p>
        </div>
        <button type="button" onClick={onClose} className="rounded-full p-2 text-surface-400 hover:bg-surface-100 dark:text-white/30 dark:hover:bg-white/5">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border border-surface-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-surface-100">
          <h4 className="text-lg font-semibold text-surface-900 dark:text-white">Basic Information</h4>
          <p className="mt-1 text-sm text-surface-500 dark:text-white/40">Identity and onboarding details.</p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {renderField('Employee Number Series', (
              <select value={form.series} onChange={(e) => update('series', e.target.value)} className={inputClass}>
                {seriesOptions.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            ), 'series')}
            {renderField('Employee Number', (
              <input type="text" value={form.employee_number} onChange={(e) => update('employee_number', e.target.value)} className={inputClass} placeholder="Employee no." />
            ), 'employee_number')}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {renderField('First Name', (
              <input type="text" value={form.first_name} onChange={(e) => update('first_name', e.target.value)} className={inputClass} placeholder="First name" />
            ), 'first_name')}
            {renderField('Last Name', (
              <input type="text" value={form.last_name} onChange={(e) => update('last_name', e.target.value)} className={inputClass} placeholder="Last name" />
            ), 'last_name')}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {renderField('Date of Birth', (
              <input type="date" value={form.date_of_birth} onChange={(e) => update('date_of_birth', e.target.value)} className={inputClass} />
            ), 'date_of_birth')}
            {renderField('Aadhaar Number', (
              <input type="text" value={form.aadhaar_number} onChange={(e) => update('aadhaar_number', e.target.value)} className={inputClass} placeholder="12 digit Aadhaar" />
            ), 'aadhaar_number')}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {renderField('Gender', (
              <select value={form.gender} onChange={(e) => update('gender', e.target.value)} className={inputClass}>
                <option value="">Select gender</option>
                {genders.map((gender) => (
                  <option key={gender.id} value={gender.name}>{gender.name}</option>
                ))}
                <option value="Others">Others</option>
              </select>
            ), 'gender')}
            {renderField('Status', (
              <select value={form.status} onChange={(e) => update('status', e.target.value)} className={inputClass}>
                {statusOptions.map((status) => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
            ), 'status')}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {renderField('Date of Joining', (
              <input type="date" value={form.date_of_joining} onChange={(e) => update('date_of_joining', e.target.value)} className={inputClass} />
            ), 'date_of_joining')}
            {renderField('Probation Period', (
              <input type="text" value={form.probation_period} onChange={(e) => update('probation_period', e.target.value)} className={inputClass} placeholder="e.g. 90 days" />
            ))}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            
            {renderField('Employment Type', (
              <select value={form.employment_type} onChange={(e) => update('employment_type', e.target.value)} className={inputClass}>
                <option value="">Select type</option>
                {employmentTypeOptions.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            ), 'employment_type')}
          </div>

          <div className="mt-4">
            {renderField('Allow Employee to Fill Info', (
              <label className="inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={form.allow_employee_fill_info}
                  onChange={(e) => updateBoolean('allow_employee_fill_info', e.target.checked)}
                  className="h-4 w-4 rounded border-surface-300 text-brand-600 focus:ring-brand-500"
                />
                <span className="text-sm text-surface-700 dark:text-white/80">Allow employee to complete their own details</span>
              </label>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-surface-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-surface-100">
          <h4 className="text-lg font-semibold text-surface-900 dark:text-white">Contact Information</h4>
          <p className="mt-1 text-sm text-surface-500 dark:text-white/40">Email and phone details for onboarding.</p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {renderField('Email', (
              <input type="email" value={form.email} onChange={(e) => update('email', e.target.value)} className={inputClass} placeholder="Email address" />
            ), 'email')}
            {renderField('Alternate Email', (
              <input type="email" value={form.alternate_email} onChange={(e) => update('alternate_email', e.target.value)} className={inputClass} placeholder="Alternate email" />
            ), 'alternate_email')}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {renderField('Mobile Number', (
              <input type="tel" value={form.personal_mobile} onChange={(e) => update('personal_mobile', e.target.value)} className={inputClass} placeholder="Mobile number" />
            ), 'personal_mobile')}
            {renderField('Alternate Mobile Number', (
              <input type="tel" value={form.alternate_mobile} onChange={(e) => update('alternate_mobile', e.target.value)} className={inputClass} placeholder="Alternate mobile" />
            ), 'alternate_mobile')}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {renderField('Emergency Contact Name', (
              <input type="text" value={form.emergency_contact_name} onChange={(e) => update('emergency_contact_name', e.target.value)} className={inputClass} placeholder="Emergency contact" />
            ), 'emergency_contact_name')}
            {renderField('Emergency Contact Number', (
              <input type="tel" value={form.emergency_contact_number} onChange={(e) => update('emergency_contact_number', e.target.value)} className={inputClass} placeholder="Contact number" />
            ), 'emergency_contact_number')}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {renderField('Father’s Name', (
              <input type="text" value={form.father_name} onChange={(e) => update('father_name', e.target.value)} className={inputClass} placeholder="Father's name" />
            ), 'father_name')}
            {renderField('Spouse Name', (
              <input type="text" value={form.spouse_name} onChange={(e) => update('spouse_name', e.target.value)} className={inputClass} placeholder="Spouse name" />
            ))}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {renderField('Marital Status', (
              <select value={form.marital_status} onChange={(e) => update('marital_status', e.target.value)} className={inputClass}>
                <option value="">Select status</option>
                {maritalStatusOptions.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            ))}
            {renderField('Blood Group', (
              <select value={form.blood_group} onChange={(e) => update('blood_group', e.target.value)} className={inputClass}>
                <option value="">Select blood group</option>
                {bloodGroupOptions.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            ))}
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border border-surface-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-surface-100">
          <h4 className="text-lg font-semibold text-surface-900 dark:text-white">Work Information</h4>
          <p className="mt-1 text-sm text-surface-500 dark:text-white/40">Role, team, and attendance configuration.</p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {renderField('Reporting Manager', (
              <select value={form.reporting_manager} onChange={(e) => update('reporting_manager', e.target.value)} className={inputClass}>
                <option value="">Select manager</option>
                {managerOptions.map((manager) => (
                  <option key={manager.id} value={manager.id}>{manager.name}</option>
                ))}
              </select>
            ), 'reporting_manager')}
            {renderField('Designation', (
              <select value={form.designation} onChange={(e) => update('designation', e.target.value)} className={inputClass}>
                <option value="">Select designation</option>
                {designations.map((item) => (
                  <option key={item.id} value={item.name}>{item.name}</option>
                ))}
              </select>
            ), 'designation')}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {renderField('Department', (
              <select value={form.department} onChange={(e) => update('department', e.target.value)} className={inputClass}>
                <option value="">Select department</option>
                {departments.map((item) => (
                  <option key={item.id} value={item.name}>{item.name}</option>
                ))}
              </select>
            ), 'department')}
            {renderField('Grade', (
              <select value={form.grade} onChange={(e) => update('grade', e.target.value)} className={inputClass}>
                <option value="">Select grade</option>
                {grades.map((item) => (
                  <option key={item.id} value={item.name}>{item.name}</option>
                ))}
                <option value="G1">G1</option>
                <option value="G2">G2</option>
                <option value="G3">G3</option>
                <option value="G4">G4</option>
                <option value="G5">G5</option>
              </select>
            ), 'grade')}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {renderField('Location', (
              <select value={form.location} onChange={(e) => update('location', e.target.value)} className={inputClass}>
                <option value="">Select location</option>
                {locationOptions.map((option) => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            ), 'location')}
            {renderField('Attendance Scheme', (
              <select value={form.attendance_scheme} onChange={(e) => update('attendance_scheme', e.target.value)} className={inputClass}>
                {attendanceSchemes.map((scheme) => (
                  <option key={scheme} value={scheme}>{scheme}</option>
                ))}
              </select>
            ), 'attendance_scheme')}
          </div>
        </div>

        <div className="rounded-3xl border border-surface-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-surface-100">
          <h4 className="text-lg font-semibold text-surface-900 dark:text-white">Referral Information</h4>
          <p className="mt-1 text-sm text-surface-500 dark:text-white/40">Only add referral name when referral source is chosen.</p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {renderField('Referred By', (
              <select value={form.referred_by} onChange={(e) => update('referred_by', e.target.value)} className={inputClass}>
                <option value="">Select source</option>
                {sourceOfHire.map((item) => (
                  <option key={item.id} value={item.name}>{item.name}</option>
                ))}
              </select>
            ))}
            {renderField('Referral Name', (
              <input type="text" value={form.referral_name} onChange={(e) => update('referral_name', e.target.value)} className={inputClass} placeholder="Referral name" />
            ), form.referred_by ? 'referral_name' : undefined)}
          </div>
          <p className="mt-3 text-xs text-surface-500 dark:text-white/40">Referral name is optional unless a source is selected.</p>
        </div>
      </div>

      <div className="rounded-3xl border border-surface-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-surface-100">
        <h4 className="text-lg font-semibold text-surface-900 dark:text-white">Experience</h4>
        <p className="mt-1 text-sm text-surface-500 dark:text-white/40">Track total, relevant and other work experience.</p>

        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          {renderField('Total Experience', (
            <input type="text" value={form.total_experience} onChange={(e) => update('total_experience', e.target.value)} className={inputClass} placeholder="e.g. 8 years" />
          ))}
          {renderField('Relevant Experience', (
            <input type="text" value={form.relevant_experience} onChange={(e) => update('relevant_experience', e.target.value)} className={inputClass} placeholder="e.g. 5 years" />
          ))}
          {renderField('Other Experience', (
            <input type="text" value={form.other_experience} onChange={(e) => update('other_experience', e.target.value)} className={inputClass} placeholder="e.g. 3 years" />
          ))}
        </div>

        <div className="mt-6 space-y-5">
          {form.experience_history.map((entry, index) => (
            <div key={index} className="rounded-3xl border border-surface-200 bg-surface-50 p-4 dark:border-white/10 dark:bg-surface-100">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-semibold text-surface-900 dark:text-white">Experience {index + 1}</p>
                {form.experience_history.length > 1 ? (
                  <button
                    type="button"
                    onClick={() => removeExperienceEntry(index)}
                    className="rounded-full border border-surface-200 px-3 py-1 text-xs font-semibold text-surface-700 transition hover:bg-surface-100 dark:border-white/10 dark:text-white/70 dark:hover:bg-white/5"
                  >
                    Remove
                  </button>
                ) : null}
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {renderField('Company Name', (
                  <input type="text" value={entry.company_name} onChange={(e) => updateExperience(index, 'company_name', e.target.value)} className={inputClass} placeholder="Company name" />
                ), `experience_history.${index}.company_name`)}
                {renderField('Designation', (
                  <input type="text" value={entry.designation} onChange={(e) => updateExperience(index, 'designation', e.target.value)} className={inputClass} placeholder="Designation" />
                ), `experience_history.${index}.designation`)}
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {renderField('From Date', (
                  <input type="date" value={entry.from_date} onChange={(e) => updateExperience(index, 'from_date', e.target.value)} className={inputClass} />
                ), `experience_history.${index}.from_date`)}
                {renderField('To Date', (
                  <input type="date" value={entry.to_date} onChange={(e) => updateExperience(index, 'to_date', e.target.value)} className={inputClass} />
                ), `experience_history.${index}.to_date`)}
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                {renderField('Last Drawn Salary', (
                  <input type="text" value={entry.last_drawn_salary} onChange={(e) => updateExperience(index, 'last_drawn_salary', e.target.value)} className={inputClass} placeholder="Salary" />
                ), `experience_history.${index}.last_drawn_salary`)}
                {renderField('Reason for Leaving', (
                  <input type="text" value={entry.reason_for_leaving} onChange={(e) => updateExperience(index, 'reason_for_leaving', e.target.value)} className={inputClass} placeholder="Reason" />
                ), `experience_history.${index}.reason_for_leaving`)}
              </div>
            </div>
          ))}
        </div>

        <button
          type="button"
          onClick={addExperienceEntry}
          className="mt-4 inline-flex items-center justify-center rounded-3xl border border-dashed border-surface-300 px-4 py-3 text-sm font-semibold text-surface-700 transition hover:border-brand-500 hover:text-brand-600 dark:border-white/10 dark:text-white/80 dark:hover:text-brand-400"
        >
          + Add Experience
        </button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border border-surface-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-surface-100">
          <h4 className="text-lg font-semibold text-surface-900 dark:text-white">Statutory Info</h4>
          <p className="mt-1 text-sm text-surface-500 dark:text-white/40">Legal and banking details.</p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {renderField('PAN Number', (
              <input type="text" value={form.pan_number} onChange={(e) => update('pan_number', e.target.value)} className={inputClass} placeholder="PAN number" />
            ), 'pan_number')}
            {renderField('Aadhaar Number', (
              <input type="text" value={form.aadhaar_number} onChange={(e) => update('aadhaar_number', e.target.value)} className={inputClass} placeholder="Aadhaar number" />
            ), 'aadhaar_number')}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {renderField('Bank Account Number', (
              <input type="text" value={form.bank_account_number} onChange={(e) => update('bank_account_number', e.target.value)} className={inputClass} placeholder="Bank account" />
            ), 'bank_account_number')}
            {renderField('IFSC Code', (
              <input type="text" value={form.ifsc_code} onChange={(e) => update('ifsc_code', e.target.value)} className={inputClass} placeholder="IFSC code" />
            ), 'ifsc_code')}
          </div>
        </div>

        <div className="rounded-3xl border border-surface-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-surface-100">
          <h4 className="text-lg font-semibold text-surface-900 dark:text-white">Policies</h4>
          <p className="mt-1 text-sm text-surface-500 dark:text-white/40">Select the onboarding policy for the employee.</p>

          <div className="mt-6 grid gap-4">
            {renderField('Employee Onboarding Policy', (
              <select value={form.onboarding_policy} onChange={(e) => update('onboarding_policy', e.target.value)} className={inputClass}>
                <option value="">Select policy</option>
                {policyOptions.map((policy) => (
                  <option key={policy} value={policy}>{policy}</option>
                ))}
              </select>
            ), 'onboarding_policy')}
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-3xl border border-surface-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-surface-100">
          <h4 className="text-lg font-semibold text-surface-900 dark:text-white">Documents</h4>
          <p className="mt-1 text-sm text-surface-500 dark:text-white/40">Upload employee documents required for onboarding.</p>

          <div className="mt-6 grid gap-4">
            {renderField('Offer Letter', (
              <input type="file" accept=".pdf,.doc,.docx" onChange={(e) => updateFile('offer_letter', e.target.files?.[0] ?? null)} className={inputClass} />
            ))}
            {renderField('ID Proof', (
              <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={(e) => updateFile('id_proof', e.target.files?.[0] ?? null)} className={inputClass} />
            ))}
            {renderField('Resume', (
              <input type="file" accept=".pdf,.doc,.docx" onChange={(e) => updateFile('resume', e.target.files?.[0] ?? null)} className={inputClass} />
            ))}
            {renderField('Other Documents', (
              <input type="file" multiple accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" onChange={(e) => updateOtherDocs(e.target.files)} className={inputClass} />
            ))}
          </div>

          {(form.offer_letter || form.id_proof || form.resume || form.other_docs.length > 0) && (
            <div className="mt-4 rounded-3xl bg-surface-50 p-3 text-sm text-surface-600 dark:bg-surface-900/60 dark:text-white/70">
              <p className="font-medium">Selected files</p>
              <ul className="mt-2 list-disc space-y-1 pl-5">
                {form.offer_letter ? <li>Offer Letter: {form.offer_letter.name}</li> : null}
                {form.id_proof ? <li>ID Proof: {form.id_proof.name}</li> : null}
                {form.resume ? <li>Resume: {form.resume.name}</li> : null}
                {form.other_docs.map((file, idx) => (
                  <li key={idx}>Other: {file.name}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="rounded-3xl border border-surface-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-surface-100">
          <h4 className="text-lg font-semibold text-surface-900 dark:text-white">Access / Biometric</h4>
          <p className="mt-1 text-sm text-surface-500 dark:text-white/40">Optional access details for the employee.</p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {renderField('Card Number', (
              <input type="text" value={form.card_number} onChange={(e) => update('card_number', e.target.value)} className={inputClass} placeholder="Card number" />
            ))}
            {renderField('Access Valid From', (
              <input type="date" value={form.access_valid_from} onChange={(e) => update('access_valid_from', e.target.value)} className={inputClass} />
            ))}
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {renderField('Access Valid To', (
              <input type="date" value={form.access_valid_to} onChange={(e) => update('access_valid_to', e.target.value)} className={inputClass} />
            ))}
            <div />
          </div>
        </div>
      </div>

      <div className="sticky bottom-0 z-10 mt-6 rounded-t-3xl border-t border-surface-200 bg-surface-0/95 px-4 py-4 backdrop-blur dark:border-white/10 dark:bg-surface-900/95 sm:px-6">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <span className="text-sm text-surface-500 dark:text-white/40">Review all fields before submitting.</span>
          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              onClick={onClose}
              className="rounded-3xl border border-surface-200 bg-white px-5 py-3 text-sm font-semibold text-surface-700 transition hover:bg-surface-50 dark:border-white/10 dark:bg-white/5 dark:text-white/80"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={invite.status === 'pending'}
              className="rounded-3xl bg-brand-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {invite.status === 'pending' ? 'Saving...' : 'Save Employee'}
            </button>
          </div>
        </div>
      </div>
    </form>
  );
}
