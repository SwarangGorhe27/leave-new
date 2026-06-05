import { useState } from 'react';
import {
  BookOpen,
  Briefcase,
  Check,
  CreditCard,
  Edit2,
  Fingerprint,
  GraduationCap,
  Landmark,
  Languages,
  Laptop,
  Loader2,
  MapPin,
  MapPinned,
  Plus,
  Shield,
  Trash2,
  User,
  UserRound,
  Users,
  X,
} from 'lucide-react';
import { useMyProfile } from '@hooks/useMyProfile';
import type {
  AddressInfo,
  BankInfo,
  EducationInfo,
  FamilyMemberInfo,
  LanguageInfo,
  MyProfileData,
  NomineeInfo,
} from '@hooks/useMyProfile';
import { useProfileChangeRequest } from '@hooks/useProfileChangeRequest';
import { Avatar, Badge } from '@components/ui';
import { cn } from '@utils/utils';

/* ------------------------------------------------------------------ */
/*  Sidebar sections                                                   */
/* ------------------------------------------------------------------ */

type SectionId =
  | 'profile'
  | 'personal'
  | 'employment'
  | 'address'
  | 'family'
  | 'education'
  | 'bank'
  | 'nominee'
  | 'language'
  | 'insurance'
  | 'assets';

interface SidebarItem {
  id: SectionId;
  label: string;
  icon: React.ElementType;
}

const sidebarItems: SidebarItem[] = [
  { id: 'profile',    label: 'Profile',              icon: User },
  { id: 'personal',   label: 'Personal',             icon: UserRound },
  { id: 'employment', label: 'Employment & Job',     icon: Briefcase },
  { id: 'address',    label: 'Address',              icon: MapPin },
  { id: 'family',     label: 'Family',               icon: Users },
  { id: 'education',  label: 'Education',            icon: GraduationCap },
  { id: 'bank',       label: 'Accounts & Statutory', icon: Landmark },
  { id: 'nominee',    label: 'Nominees',             icon: Shield },
  { id: 'insurance',  label: 'Insurance',            icon: Shield },
  { id: 'language',   label: 'Languages',            icon: Languages },
  { id: 'assets',     label: 'Assets',               icon: Laptop },
];

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
  });
}

/* ------------------------------------------------------------------ */
/*  Shared UI atoms                                                    */
/* ------------------------------------------------------------------ */

function InfoField({
  label,
  value,
  masked,
}: {
  label: string;
  value?: string | null;
  masked?: boolean;
}) {
  const [revealed, setRevealed] = useState(false);
  const display = value || '—';
  const maskedDisplay =
    masked && !revealed && value
      ? value.slice(0, -4).replace(/./g, 'X') + value.slice(-4)
      : display;

  return (
    <div className="min-w-0">
      <p className="text-xs text-surface-500 dark:text-white/40">{label}</p>
      <div className="mt-0.5 flex items-center gap-1.5">
        <p className="text-sm font-medium text-surface-900 dark:text-white">{maskedDisplay}</p>
        {masked && value && (
          <button
            type="button"
            onClick={() => setRevealed(!revealed)}
            className="text-xs text-brand-600 hover:text-brand-700 dark:text-brand-400"
          >
            {revealed ? 'Hide' : 'Show'}
          </button>
        )}
      </div>
    </div>
  );
}

/* Shared input styling */
const inputCls =
  'w-full rounded-lg border border-surface-200 bg-white px-3 py-1.5 text-sm text-surface-900 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder:text-white/25 dark:focus:border-brand-400 dark:focus:ring-brand-400/20';
const labelCls = 'block text-xs font-medium text-surface-500 dark:text-white/40 mb-1';

function FormInput({
  label,
  value,
  onChange,
  type = 'text',
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
}) {
  return (
    <div className="min-w-0">
      <label className={labelCls}>{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder ?? label}
        className={inputCls}
      />
    </div>
  );
}

function FormSelect({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <div className="min-w-0">
      <label className={labelCls}>{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)} className={inputCls}>
        <option value="">— Select —</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  );
}

function FormCheckbox({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label className="flex cursor-pointer items-center gap-2 text-sm text-surface-700 dark:text-white/70">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 rounded border-surface-300 text-brand-600 accent-brand-600 dark:border-white/20"
      />
      {label}
    </label>
  );
}

/* ------------------------------------------------------------------ */
/*  Submit result banner                                               */
/* ------------------------------------------------------------------ */

function SubmitBanner({
  status,
  onClose,
}: {
  status: 'success' | 'error';
  onClose: () => void;
}) {
  return (
    <div
      className={cn(
        'flex items-start gap-3 rounded-xl border px-4 py-3 text-sm',
        status === 'success'
          ? 'border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-emerald-300'
          : 'border-red-200 bg-red-50 text-red-800 dark:border-red-500/20 dark:bg-red-500/10 dark:text-red-300'
      )}
    >
      {status === 'success'
        ? <Check className="mt-0.5 h-4 w-4 shrink-0" />
        : <X className="mt-0.5 h-4 w-4 shrink-0" />
      }
      <span className="flex-1">
        {status === 'success'
          ? 'Change request submitted successfully. Your profile will be updated once an admin approves it.'
          : 'Failed to submit change request. Please try again.'}
      </span>
      <button type="button" onClick={onClose} className="shrink-0 opacity-50 hover:opacity-100">
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Section Card with per-section edit controls                       */
/* ------------------------------------------------------------------ */

function SectionCard({
  id,
  title,
  icon: Icon,
  children,
  collapsible = true,
  isEditing,
  isSaving,
  onEdit,
  onCancel,
  onSubmit,
  hasPendingApproval,
}: {
  id: string;
  title: string;
  icon: React.ElementType;
  children: React.ReactNode;
  collapsible?: boolean;
  isEditing?: boolean;
  isSaving?: boolean;
  onEdit?: () => void;
  onCancel?: () => void;
  onSubmit?: () => void;
  hasPendingApproval?: boolean;
}) {
  const [open, setOpen] = useState(true);

  return (
    <section id={id} className="surface-card scroll-mt-6 rounded-2xl">
      {/* Header row */}
      <div className="flex w-full items-center justify-between px-6 py-4">
        {/* Left: icon + title */}
        <button
          type="button"
          className="flex items-center gap-3"
          onClick={() => collapsible && !isEditing && setOpen(!open)}
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-brand-50 dark:bg-brand-500/10">
            <Icon className="h-4 w-4 text-brand-600 dark:text-brand-400" />
          </div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-surface-700 dark:text-white/80">
            {title}
          </h2>
          {hasPendingApproval && (
            <Badge variant="warning" size="sm" dot>Pending Approval</Badge>
          )}
        </button>

        {/* Right: action buttons */}
        <div className="flex items-center gap-2">
          {isEditing ? (
            <>
              <button
                type="button"
                onClick={onCancel}
                className="flex items-center gap-1.5 rounded-lg border border-surface-200 px-3 py-1.5 text-xs font-medium text-surface-600 transition hover:bg-surface-50 dark:border-white/10 dark:text-white/60 dark:hover:bg-white/5"
              >
                <X className="h-3.5 w-3.5" />
                Cancel
              </button>
              <button
                type="button"
                onClick={onSubmit}
                disabled={isSaving}
                className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-brand-500 dark:hover:bg-brand-400"
              >
                {isSaving
                  ? <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  : <Check className="h-3.5 w-3.5" />
                }
                {isSaving ? 'Submitting…' : 'Request Change'}
              </button>
            </>
          ) : (
            <>
              {onEdit && (
                <button
                  type="button"
                  onClick={() => { setOpen(true); onEdit(); }}
                  className="flex items-center gap-1.5 rounded-lg border border-surface-200 px-3 py-1.5 text-xs font-medium text-surface-600 transition hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700 dark:border-white/10 dark:text-white/50 dark:hover:border-brand-400/40 dark:hover:bg-brand-500/10 dark:hover:text-brand-300"
                >
                  <Edit2 className="h-3.5 w-3.5" />
                  Edit
                </button>
              )}
              {collapsible && (
                <button
                  type="button"
                  onClick={() => setOpen(!open)}
                  className="text-surface-400 dark:text-white/30"
                >
                  <svg
                    className={cn('h-4 w-4 transition-transform', open && 'rotate-180')}
                    fill="none" viewBox="0 0 24 24" stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Body */}
      {open && (
        <div className="border-t border-surface-100 px-6 py-5 dark:border-white/5">
          {children}
        </div>
      )}
    </section>
  );
}

/* ------------------------------------------------------------------ */
/*  Skeleton / jump links                                              */
/* ------------------------------------------------------------------ */

function JumpLinks({ active }: { active: SectionId }) {
  return (
    <div className="flex flex-wrap gap-1 text-xs">
      <span className="text-surface-400 dark:text-white/30">JUMP TO</span>
      {sidebarItems.slice(0, 5).map((item) => (
        <a
          key={item.id}
          href={`#${item.id}`}
          className={cn(
            'px-1 transition-colors',
            active === item.id
              ? 'font-semibold text-brand-600 dark:text-brand-400'
              : 'text-brand-500 hover:text-brand-700 dark:text-brand-400/70 dark:hover:text-brand-300'
          )}
        >
          {item.label}
        </a>
      ))}
    </div>
  );
}

function ProfileSkeleton() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="surface-card rounded-2xl p-6">
        <div className="flex items-center gap-6">
          <div className="h-20 w-20 rounded-full bg-surface-200 dark:bg-white/10" />
          <div className="flex-1 space-y-3">
            <div className="h-6 w-48 rounded bg-surface-200 dark:bg-white/10" />
            <div className="h-4 w-32 rounded bg-surface-200 dark:bg-white/10" />
          </div>
        </div>
      </div>
      {[1, 2, 3].map((i) => (
        <div key={i} className="surface-card rounded-2xl p-6">
          <div className="h-4 w-32 rounded bg-surface-200 dark:bg-white/10" />
          <div className="mt-4 grid grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((j) => (
              <div key={j} className="space-y-2">
                <div className="h-3 w-20 rounded bg-surface-200 dark:bg-white/10" />
                <div className="h-4 w-28 rounded bg-surface-200 dark:bg-white/10" />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ================================================================== */
/*  Shared section props                                               */
/* ================================================================== */

interface SectionProps {
  data: MyProfileData;
  editing: boolean;
  isSaving: boolean;
  hasPendingApproval: boolean;
  onEdit: () => void;
  onCancel: () => void;
  onSubmit: (sectionId: SectionId, label: string, changes: Record<string, unknown>) => void;
}

/* ================================================================== */
/*  Per-section form components                                        */
/* ================================================================== */

/* ── Profile ──────────────────────────────────────────────────────── */

function ProfileSection({ data, editing, isSaving, hasPendingApproval, onEdit, onCancel, onSubmit }: SectionProps) {
  const [form, setForm] = useState({
    first_name: data.first_name ?? '',
    middle_name: data.middle_name ?? '',
    last_name: data.last_name ?? '',
    personal_mobile: data.contact?.personal_mobile ?? '',
    personal_email: data.contact?.personal_email ?? '',
    work_mobile: data.contact?.work_mobile ?? '',
    emergency_contact_name: data.contact?.emergency_contact_name ?? '',
    emergency_contact_number: data.contact?.emergency_contact_number ?? '',
  });
  const set = (k: keyof typeof form) => (v: string) => setForm((f) => ({ ...f, [k]: v }));

  return (
    <SectionCard
      id="profile"
      title="Profile"
      icon={User}
      collapsible={false}
      isEditing={editing}
      isSaving={isSaving}
      hasPendingApproval={hasPendingApproval}
      onEdit={onEdit}
      onCancel={onCancel}
      onSubmit={() => onSubmit('profile', 'Profile', form)}
    >
      {editing ? (
        <div className="grid gap-5 sm:grid-cols-3">
          <FormInput label="First Name"                value={form.first_name}               onChange={set('first_name')} />
          <FormInput label="Middle Name"               value={form.middle_name}              onChange={set('middle_name')} />
          <FormInput label="Last Name"                 value={form.last_name}                onChange={set('last_name')} />
          <FormInput label="Personal Mobile"          value={form.personal_mobile}          onChange={set('personal_mobile')}          type="tel" />
          <FormInput label="Personal Email"           value={form.personal_email}           onChange={set('personal_email')}           type="email" />
          <FormInput label="Work Mobile"              value={form.work_mobile}              onChange={set('work_mobile')}              type="tel" />
          <FormInput label="Emergency Contact Name"   value={form.emergency_contact_name}   onChange={set('emergency_contact_name')} />
          <FormInput label="Emergency Contact Number" value={form.emergency_contact_number} onChange={set('emergency_contact_number')} type="tel" />
        </div>
      ) : (
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
          <Avatar name={data.full_name} size="2xl" />
          <div className="grid flex-1 gap-5 sm:grid-cols-3">
            <InfoField label="Name"               value={data.full_name} />
            <InfoField label="Employee ID"        value={data.employee_code} />
            <InfoField label="Company Email"      value={data.contact?.work_email} />
            <InfoField label="Location"           value={data.employment?.company_location_detail?.name} />
            <InfoField label="Primary Contact No." value={data.contact?.personal_mobile} masked />
            <InfoField label="Department"         value={data.employment?.department_detail?.name} />
          </div>
        </div>
      )}
    </SectionCard>
  );
}

/* ── Personal ─────────────────────────────────────────────────────── */

const GENDER_OPTIONS    = [{ value: 'Male', label: 'Male' }, { value: 'Female', label: 'Female' }, { value: 'Other', label: 'Other' }];
const MARITAL_OPTIONS   = [{ value: 'Single', label: 'Single' }, { value: 'Married', label: 'Married' }, { value: 'Divorced', label: 'Divorced' }, { value: 'Widowed', label: 'Widowed' }];
const BLOOD_GRP_OPTIONS = ['A+','A-','B+','B-','O+','O-','AB+','AB-'].map((v) => ({ value: v, label: v }));
const SHIFT_OPTIONS     = [
  { value: '9-6', label: '9 AM - 6 PM' },
  { value: '12-9', label: '12 PM - 9 PM' },
  { value: '6-3', label: '6 PM - 3 AM' },
];

function PersonalSection({ data, editing, isSaving, hasPendingApproval, onEdit, onCancel, onSubmit }: SectionProps) {
  const [form, setForm] = useState({
    date_of_birth:          data.date_of_birth ?? '',
    gender:                 data.gender_detail?.name ?? '',
    blood_group:            data.blood_group_detail?.name ?? '',
    marital_status:         data.marital_status_detail?.name ?? '',
    spouse_name:            data.spouse_name ?? '',
    father_name:            data.father_name ?? '',
    place_of_birth:         data.place_of_birth ?? '',
    nationality:            data.nationality_detail?.name ?? '',
    religion:               data.religion_detail?.name ?? '',
    residential_status:     data.residential_status_detail?.name ?? '',
    identification_mark:    data.identification_mark ?? '',
    pan_number:             data.pan_number ?? '',
    aadhaar_number:         data.aadhaar_number ?? '',
    passport_number:        data.passport_number ?? '',
    uan_number:             data.uan_number ?? '',
    is_physically_challenged:  data.is_physically_challenged,
    is_international_employee: data.is_international_employee,
  });
  const set   = (k: keyof typeof form) => (v: string)  => setForm((f) => ({ ...f, [k]: v }));
  const setBool = (k: keyof typeof form) => (v: boolean) => setForm((f) => ({ ...f, [k]: v }));

  return (
    <SectionCard
      id="personal"
      title="Personal"
      icon={UserRound}
      isEditing={editing}
      isSaving={isSaving}
      hasPendingApproval={hasPendingApproval}
      onEdit={onEdit}
      onCancel={onCancel}
      onSubmit={() => onSubmit('personal', 'Personal', form)}
    >
      {editing ? (
        <div className="grid gap-5 sm:grid-cols-3">
          <FormInput   label="Date of Birth"      value={form.date_of_birth}       onChange={set('date_of_birth')}       type="date" />
          <FormSelect  label="Gender"             value={form.gender}              onChange={set('gender')}              options={GENDER_OPTIONS} />
          <FormSelect  label="Blood Group"        value={form.blood_group}         onChange={set('blood_group')}         options={BLOOD_GRP_OPTIONS} />
          <FormSelect  label="Marital Status"     value={form.marital_status}      onChange={set('marital_status')}      options={MARITAL_OPTIONS} />
          <FormInput   label="Spouse Name"        value={form.spouse_name}         onChange={set('spouse_name')} />
          <FormInput   label="Father Name"        value={form.father_name}         onChange={set('father_name')} />
          <FormInput   label="Place of Birth"     value={form.place_of_birth}      onChange={set('place_of_birth')} />
          <FormInput   label="Nationality"        value={form.nationality}         onChange={set('nationality')} />
          <FormInput   label="Religion"           value={form.religion}            onChange={set('religion')} />
          <FormInput   label="Residential Status" value={form.residential_status}  onChange={set('residential_status')} />
          <FormInput   label="Identification Mark" value={form.identification_mark} onChange={set('identification_mark')} />
          <FormInput   label="PAN Number"         value={form.pan_number}          onChange={set('pan_number')} />
          <FormInput   label="Aadhaar Number"     value={form.aadhaar_number}      onChange={set('aadhaar_number')} />
          <FormInput   label="Passport Number"    value={form.passport_number}     onChange={set('passport_number')} />
          <FormInput   label="UAN Number"         value={form.uan_number}          onChange={set('uan_number')} />
          <div className="flex flex-col gap-3">
            <FormCheckbox label="Physically Challenged"  checked={form.is_physically_challenged}  onChange={setBool('is_physically_challenged')} />
            <FormCheckbox label="International Employee" checked={form.is_international_employee} onChange={setBool('is_international_employee')} />
          </div>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-3">
          <InfoField label="Blood Group"         value={data.blood_group_detail?.name}        masked />
          <InfoField label="Date of Birth"       value={formatDate(data.date_of_birth)}       masked />
          <InfoField label="Nationality"         value={data.nationality_detail?.name} />
          <InfoField label="Marital Status"      value={data.marital_status_detail?.name}     masked />
          <InfoField label="Spouse Name"         value={data.spouse_name} />
          <InfoField label="Religion"            value={data.religion_detail?.name} />
          <InfoField label="Gender"              value={data.gender_detail?.name} />
          <InfoField label="Father Name"         value={data.father_name} />
          <InfoField label="Place of Birth"      value={data.place_of_birth} />
          <InfoField label="Residential Status"  value={data.residential_status_detail?.name} />
          <InfoField label="Identification Mark" value={data.identification_mark} />
          <InfoField label="PAN Number"          value={data.pan_number}          masked />
          <InfoField label="Aadhaar Number"      value={data.aadhaar_number}      masked />
          <InfoField label="Passport Number"     value={data.passport_number} />
          <InfoField label="UAN Number"          value={data.uan_number} />
          <div className="min-w-0">
            <p className="text-xs text-surface-500 dark:text-white/40">Physically Challenged</p>
            <div className="mt-0.5">
              <Badge variant={data.is_physically_challenged ? 'warning' : 'neutral'} size="sm">
                {data.is_physically_challenged ? 'Yes' : 'No'}
              </Badge>
            </div>
          </div>
          <div className="min-w-0">
            <p className="text-xs text-surface-500 dark:text-white/40">International Employee</p>
            <div className="mt-0.5">
              <Badge variant={data.is_international_employee ? 'brand' : 'neutral'} size="sm">
                {data.is_international_employee ? 'Yes' : 'No'}
              </Badge>
            </div>
          </div>
        </div>
      )}
    </SectionCard>
  );
}

/* ── Employment ───────────────────────────────────────────────────── */

function EmploymentSection({ data, editing, isSaving, hasPendingApproval, onEdit, onCancel, onSubmit }: SectionProps) {
  const emp       = data.employment;
  const reporting = data.current_reporting;

  const [form, setForm] = useState({
    department:          emp?.department_detail?.name    ?? '',
    designation:         emp?.designation_detail?.name   ?? '',
    employment_type:     emp?.employment_type_detail?.name ?? '',
    work_location:       emp?.company_location_detail?.name ?? '',
    employee_category:   emp?.employee_category_detail?.name ?? '',
    shift:               emp?.shift                      ?? '',
    notice_period_days:  String(emp?.notice_period_days ?? ''),
    reporting_manager:   reporting?.reporting_manager_name  ?? '',
    functional_manager:  reporting?.functional_manager_name ?? '',
    hr_partner:          reporting?.hr_partner_name          ?? '',
  });
  const set = (k: keyof typeof form) => (v: string) => setForm((f) => ({ ...f, [k]: v }));

  return (
    <SectionCard
      id="employment"
      title="Employment & Job"
      icon={Briefcase}
      isEditing={editing}
      isSaving={isSaving}
      hasPendingApproval={hasPendingApproval}
      onEdit={onEdit}
      onCancel={onCancel}
      onSubmit={() => onSubmit('employment', 'Employment & Job', form)}
    >
      {editing ? (
        <div className="space-y-4">
          <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700 dark:bg-amber-500/10 dark:text-amber-300">
            Employment details are subject to HR approval. Dates of joining and confirmation are managed by HR and cannot be modified here.
          </p>
          <div className="grid gap-5 sm:grid-cols-3">
            <FormInput label="Department"          value={form.department}         onChange={set('department')} />
            <FormInput label="Designation"         value={form.designation}        onChange={set('designation')} />
            <FormInput label="Employment Type"     value={form.employment_type}    onChange={set('employment_type')} />
            <FormInput label="Work Location"       value={form.work_location}      onChange={set('work_location')} />
            <FormInput label="Employee Category"   value={form.employee_category}  onChange={set('employee_category')} />
            <FormSelect label="Shift"               value={form.shift}              onChange={set('shift')} options={SHIFT_OPTIONS} />
            <FormInput label="Notice Period (days)" value={form.notice_period_days} onChange={set('notice_period_days')} type="number" />
            <FormInput label="Reporting Manager"   value={form.reporting_manager}  onChange={set('reporting_manager')} />
            <FormInput label="Functional Manager"  value={form.functional_manager} onChange={set('functional_manager')} />
            <FormInput label="HR Partner"          value={form.hr_partner}         onChange={set('hr_partner')} />
          </div>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-3">
          <InfoField label="Department"             value={emp?.department_detail?.name} />
          <InfoField label="Designation"            value={emp?.designation_detail?.name} />
          <InfoField label="Employment Type"        value={emp?.employment_type_detail?.name} />
          <InfoField label="Date of Joining"        value={formatDate(emp?.date_of_joining)} />
          <InfoField label="Date of Confirmation"   value={formatDate(emp?.date_of_confirmation)} />
          <InfoField label="Probation End Date"     value={formatDate(emp?.probation_end_date)} />
          <InfoField label="Shift"                  value={emp?.shift} />
          <InfoField label="Notice Period"          value={emp?.notice_period_days ? `${emp.notice_period_days} days` : '—'} />
          <InfoField label="Employee Category"      value={emp?.employee_category_detail?.name} />
          <InfoField label="Work Location"          value={emp?.company_location_detail?.name} />
          {reporting && (
            <>
              <InfoField label="Reporting Manager"  value={reporting.reporting_manager_name} />
              <InfoField label="Functional Manager" value={reporting.functional_manager_name || '—'} />
              <InfoField label="HR Partner"         value={reporting.hr_partner_name || '—'} />
            </>
          )}
        </div>
      )}
    </SectionCard>
  );
}

/* ── Address ──────────────────────────────────────────────────────── */

function AddressSection({ data, editing, isSaving, hasPendingApproval, onEdit, onCancel, onSubmit }: SectionProps) {
  const [selectedType, setSelectedType] = useState('CURRENT');
  const [addresses, setAddresses] = useState<AddressInfo[]>(
    data.addresses.length > 0
      ? data.addresses
      : [{ id: 'new', address_type: 'CURRENT', address_line1: '', address_line2: '', landmark: '', city: '', state: '', country: 'India', pincode: '' }]
  );

  const typeLabel: Record<string, string> = {
    CURRENT:   'Current Address',
    PERMANENT: 'Permanent Address',
    TEMPORARY: 'Temporary Address',
  };

  const activeAddr = addresses.find((a) => a.address_type === selectedType) ?? addresses[0];

  const updateAddr = (type: string, key: keyof AddressInfo, value: string) =>
    setAddresses((prev) => prev.map((a) => a.address_type === type ? { ...a, [key]: value } : a));

  return (
    <SectionCard
      id="address"
      title="Address"
      icon={MapPinned}
      isEditing={editing}
      isSaving={isSaving}
      hasPendingApproval={hasPendingApproval}
      onEdit={onEdit}
      onCancel={onCancel}
      onSubmit={() => onSubmit('address', 'Address', { addresses })}
    >
      {addresses.length > 1 && (
        <div className="mb-5 flex gap-2">
          {addresses.map((a) => (
            <button
              key={a.address_type}
              type="button"
              onClick={() => setSelectedType(a.address_type)}
              className={cn(
                'rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors',
                selectedType === a.address_type
                  ? 'border-brand-500 bg-brand-50 text-brand-700 dark:border-brand-400 dark:bg-brand-500/10 dark:text-brand-300'
                  : 'border-surface-300 text-surface-600 hover:border-surface-400 dark:border-white/10 dark:text-white/50'
              )}
            >
              {typeLabel[a.address_type] ?? a.address_type}
            </button>
          ))}
        </div>
      )}

      {editing && activeAddr ? (
        <div className="grid gap-5 sm:grid-cols-3">
          <div className="sm:col-span-2">
            <FormInput label="Address Line 1" value={activeAddr.address_line1} onChange={(v) => updateAddr(activeAddr.address_type, 'address_line1', v)} />
          </div>
          <FormInput label="Address Line 2" value={activeAddr.address_line2} onChange={(v) => updateAddr(activeAddr.address_type, 'address_line2', v)} />
          <FormInput label="Landmark"       value={activeAddr.landmark}       onChange={(v) => updateAddr(activeAddr.address_type, 'landmark', v)} />
          <FormInput label="City"           value={activeAddr.city ?? ''}     onChange={(v) => updateAddr(activeAddr.address_type, 'city', v)} />
          <FormInput label="State"          value={activeAddr.state ?? ''}    onChange={(v) => updateAddr(activeAddr.address_type, 'state', v)} />
          <FormInput label="Pincode"        value={activeAddr.pincode}        onChange={(v) => updateAddr(activeAddr.address_type, 'pincode', v)} />
          <FormInput label="Country"        value={activeAddr.country ?? ''}  onChange={(v) => updateAddr(activeAddr.address_type, 'country', v)} />
        </div>
      ) : activeAddr ? (
        <div className="grid gap-5 sm:grid-cols-3">
          <div className="sm:col-span-2">
            <InfoField
              label={typeLabel[activeAddr.address_type] ?? 'Address'}
              value={[activeAddr.address_line1, activeAddr.address_line2].filter(Boolean).join(', ')}
            />
          </div>
          <InfoField label="Landmark" value={activeAddr.landmark} />
          <InfoField label="City"     value={activeAddr.city} />
          <InfoField label="State"    value={activeAddr.state} />
          <InfoField label="Pincode"  value={activeAddr.pincode} />
        </div>
      ) : (
        <p className="text-sm text-surface-400 dark:text-white/30">No address on record.</p>
      )}
    </SectionCard>
  );
}

/* ── Family ───────────────────────────────────────────────────────── */

function FamilySection({ data, editing, isSaving, hasPendingApproval, onEdit, onCancel, onSubmit }: SectionProps) {
  const [members, setMembers] = useState<FamilyMemberInfo[]>(data.family_members);

  const update = (id: string, key: keyof FamilyMemberInfo, value: unknown) =>
    setMembers((prev) => prev.map((m) => m.id === id ? { ...m, [key]: value } : m));
  const add = () =>
    setMembers((prev) => [
      ...prev,
      { id: `new-${Date.now()}`, name: '', relation_detail: undefined, date_of_birth: null, gender: null, blood_group_detail: undefined, is_dependent: false, is_emergency_contact: false, phone: '', occupation: '' },
    ]);
  const remove = (id: string) => setMembers((prev) => prev.filter((m) => m.id !== id));

  return (
    <SectionCard
      id="family"
      title="Family"
      icon={Users}
      isEditing={editing}
      isSaving={isSaving}
      hasPendingApproval={hasPendingApproval}
      onEdit={onEdit}
      onCancel={onCancel}
      onSubmit={() => onSubmit('family', 'Family', { family_members: members })}
    >
      {editing ? (
        <div className="space-y-4">
          {members.map((m) => (
            <div key={m.id} className="rounded-xl border border-surface-100 p-4 dark:border-white/5">
              <div className="mb-3 flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wide text-surface-500 dark:text-white/40">
                  Family Member
                </span>
                <button type="button" onClick={() => remove(m.id)} className="text-red-400 transition hover:text-red-600 dark:text-red-400/70 dark:hover:text-red-400">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
              <div className="grid gap-4 sm:grid-cols-3">
                <FormInput   label="Name"        value={m.name}                              onChange={(v) => update(m.id, 'name', v)} />
                <FormInput   label="Relation"    value={m.relation_detail?.name ?? ''}       onChange={(v) => update(m.id, 'relation_detail', { id: '', name: v, code: '' })} />
                <FormInput   label="Date of Birth" value={m.date_of_birth ?? ''}            onChange={(v) => update(m.id, 'date_of_birth', v)} type="date" />
                <FormInput   label="Phone"       value={m.phone}                             onChange={(v) => update(m.id, 'phone', v)} type="tel" />
                <FormInput   label="Occupation"  value={m.occupation}                        onChange={(v) => update(m.id, 'occupation', v)} />
                <FormSelect  label="Blood Group" value={m.blood_group_detail?.name ?? ''}    onChange={(v) => update(m.id, 'blood_group_detail', { id: '', name: v, code: '' })} options={BLOOD_GRP_OPTIONS} />
                <div className="flex flex-col gap-2 pt-1">
                  <FormCheckbox label="Is Dependent"      checked={m.is_dependent}        onChange={(v) => update(m.id, 'is_dependent', v)} />
                  <FormCheckbox label="Emergency Contact" checked={m.is_emergency_contact} onChange={(v) => update(m.id, 'is_emergency_contact', v)} />
                </div>
              </div>
            </div>
          ))}
          <button type="button" onClick={add} className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-surface-300 py-3 text-sm text-surface-500 transition hover:border-brand-400 hover:text-brand-600 dark:border-white/10 dark:text-white/40 dark:hover:border-brand-400/50 dark:hover:text-brand-400">
            <Plus className="h-4 w-4" /> Add Family Member
          </button>
        </div>
      ) : members.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-100 text-left text-xs text-surface-500 dark:border-white/5 dark:text-white/40">
                <th className="pb-3 pr-4 font-medium">Name</th>
                <th className="pb-3 pr-4 font-medium">Relation</th>
                <th className="pb-3 pr-4 font-medium">Date of Birth</th>
                <th className="pb-3 pr-4 font-medium">Blood Group</th>
                <th className="pb-3 pr-4 font-medium">Occupation</th>
                <th className="pb-3 pr-4 font-medium">Phone</th>
                <th className="pb-3 font-medium">Dependent</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-100 dark:divide-white/5">
              {members.map((fm) => (
                <tr key={fm.id}>
                  <td className="py-3 pr-4 font-medium text-surface-900 dark:text-white">{fm.name}</td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">{fm.relation_detail?.name ?? '—'}</td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">{formatDate(fm.date_of_birth)}</td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">{fm.blood_group_detail?.name ?? '—'}</td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">{fm.occupation || '—'}</td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">{fm.phone || '—'}</td>
                  <td className="py-3">
                    <Badge variant={fm.is_dependent ? 'warning' : 'neutral'} size="sm">
                      {fm.is_dependent ? 'Yes' : 'No'}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-sm text-surface-400 dark:text-white/30">No family members on record.</p>
      )}
    </SectionCard>
  );
}

/* ── Education ────────────────────────────────────────────────────── */

function EducationSection({ data, editing, isSaving, hasPendingApproval, onEdit, onCancel, onSubmit }: SectionProps) {
  const [records, setRecords] = useState<EducationInfo[]>(data.education);

  const update = (id: string, key: keyof EducationInfo, value: unknown) =>
    setRecords((prev) => prev.map((r) => r.id === id ? { ...r, [key]: value } : r));
  const add = () =>
    setRecords((prev) => [
      ...prev,
      { id: `new-${Date.now()}`, qualification_detail: undefined, qualification_type_detail: undefined, university_detail: undefined, institution_name: '', specialization: '', year_of_passing: null, percentage_or_cgpa: '', grade: '' },
    ]);
  const remove = (id: string) => setRecords((prev) => prev.filter((r) => r.id !== id));

  return (
    <SectionCard
      id="education"
      title="Education"
      icon={GraduationCap}
      isEditing={editing}
      isSaving={isSaving}
      hasPendingApproval={hasPendingApproval}
      onEdit={onEdit}
      onCancel={onCancel}
      onSubmit={() => onSubmit('education', 'Education', { education: records })}
    >
      {editing ? (
        <div className="space-y-4">
          {records.map((ed) => (
            <div key={ed.id} className="rounded-xl border border-surface-100 p-4 dark:border-white/5">
              <div className="mb-3 flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wide text-surface-500 dark:text-white/40">Education Record</span>
                <button type="button" onClick={() => remove(ed.id)} className="text-red-400 transition hover:text-red-600 dark:text-red-400/70 dark:hover:text-red-400">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
              <div className="grid gap-4 sm:grid-cols-3">
                <FormInput  label="Qualification"    value={ed.qualification_detail?.name ?? ''}  onChange={(v) => update(ed.id, 'qualification_detail', { id: '', name: v, code: '' })} />
                <FormInput  label="Specialization"   value={ed.specialization}                    onChange={(v) => update(ed.id, 'specialization', v)} />
                <FormInput  label="Institution Name" value={ed.institution_name}                  onChange={(v) => update(ed.id, 'institution_name', v)} />
                <FormInput  label="University"       value={ed.university_detail?.name ?? ''}     onChange={(v) => update(ed.id, 'university_detail', { id: '', name: v, code: '' })} />
                <FormInput  label="Year of Passing"  value={String(ed.year_of_passing ?? '')}     onChange={(v) => update(ed.id, 'year_of_passing', Number(v) || null)} type="number" />
                <FormInput  label="Percentage / CGPA" value={ed.percentage_or_cgpa}              onChange={(v) => update(ed.id, 'percentage_or_cgpa', v)} />
                <FormInput  label="Grade"            value={ed.grade}                             onChange={(v) => update(ed.id, 'grade', v)} />
              </div>
            </div>
          ))}
          <button type="button" onClick={add} className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-surface-300 py-3 text-sm text-surface-500 transition hover:border-brand-400 hover:text-brand-600 dark:border-white/10 dark:text-white/40 dark:hover:border-brand-400/50 dark:hover:text-brand-400">
            <Plus className="h-4 w-4" /> Add Education
          </button>
        </div>
      ) : records.length > 0 ? (
        <div className="space-y-4">
          {records.map((ed) => (
            <div key={ed.id} className="flex items-start gap-4 rounded-xl border border-surface-100 p-4 dark:border-white/5">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-50 dark:bg-violet-500/10">
                <BookOpen className="h-4 w-4 text-violet-600 dark:text-violet-400" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-medium text-surface-900 dark:text-white">{ed.qualification_detail?.name ?? 'Qualification'}</p>
                  {ed.grade && <Badge variant="brand" size="sm">Grade: {ed.grade}</Badge>}
                </div>
                <p className="mt-0.5 text-sm text-surface-600 dark:text-white/55">
                  {[ed.specialization, ed.institution_name].filter(Boolean).join(' — ')}
                </p>
                <div className="mt-2 flex flex-wrap gap-4 text-xs text-surface-500 dark:text-white/40">
                  {ed.university_detail && <span>{ed.university_detail.name}</span>}
                  {ed.year_of_passing && <span>Passed: {ed.year_of_passing}</span>}
                  {ed.percentage_or_cgpa && <span>{ed.percentage_or_cgpa}</span>}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-surface-400 dark:text-white/30">No education records.</p>
      )}
    </SectionCard>
  );
}

/* ── Bank / Statutory ─────────────────────────────────────────────── */

function BankSection({ data, editing, isSaving, hasPendingApproval, onEdit, onCancel, onSubmit }: SectionProps) {
  const [accounts, setAccounts] = useState<BankInfo[]>(data.bank_details);
  const [statutory, setStatutory] = useState({
    pan_number:      data.pan_number      ?? '',
    aadhaar_number:  data.aadhaar_number  ?? '',
    uan_number:      data.uan_number      ?? '',
    passport_number: data.passport_number ?? '',
  });

  const updateAccount = (id: string, key: keyof BankInfo, value: unknown) =>
    setAccounts((prev) => prev.map((a) => a.id === id ? { ...a, [key]: value } : a));
  const addAccount = () =>
    setAccounts((prev) => [
      ...prev,
      { id: `new-${Date.now()}`, bank_detail: undefined, branch_detail: undefined, branch_name: '', account_number: '', ifsc_code: '', account_holder_name: '', account_type: 'SAVINGS', is_primary: false },
    ]);
  const removeAccount = (id: string) => setAccounts((prev) => prev.filter((a) => a.id !== id));

  return (
    <SectionCard
      id="bank"
      title="Accounts & Statutory"
      icon={Landmark}
      isEditing={editing}
      isSaving={isSaving}
      hasPendingApproval={hasPendingApproval}
      onEdit={onEdit}
      onCancel={onCancel}
      onSubmit={() => onSubmit('bank', 'Accounts & Statutory', { bank_details: accounts, ...statutory })}
    >
      {editing ? (
        <div className="space-y-4">
          {accounts.map((bd) => (
            <div key={bd.id} className="rounded-xl border border-surface-100 p-4 dark:border-white/5">
              <div className="mb-3 flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wide text-surface-500 dark:text-white/40">Bank Account</span>
                <button type="button" onClick={() => removeAccount(bd.id)} className="text-red-400 transition hover:text-red-600 dark:text-red-400/70 dark:hover:text-red-400">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
              <div className="grid gap-4 sm:grid-cols-3">
                <FormInput  label="Bank Name"          value={bd.bank_detail?.name ?? ''}   onChange={(v) => updateAccount(bd.id, 'bank_detail', { id: '', name: v, code: '' })} />
                <FormInput  label="Account Number"     value={bd.account_number}             onChange={(v) => updateAccount(bd.id, 'account_number', v)} />
                <FormInput  label="IFSC Code"          value={bd.ifsc_code}                  onChange={(v) => updateAccount(bd.id, 'ifsc_code', v)} />
                <FormInput  label="Account Holder"     value={bd.account_holder_name}        onChange={(v) => updateAccount(bd.id, 'account_holder_name', v)} />
                <FormInput  label="Branch Name"        value={bd.branch_name}                onChange={(v) => updateAccount(bd.id, 'branch_name', v)} />
                <FormSelect label="Account Type"       value={bd.account_type}               onChange={(v) => updateAccount(bd.id, 'account_type', v)} options={[{ value: 'SAVINGS', label: 'Savings' }, { value: 'CURRENT', label: 'Current' }]} />
                <div className="flex items-end">
                  <FormCheckbox label="Primary Account" checked={bd.is_primary} onChange={(v) => updateAccount(bd.id, 'is_primary', v)} />
                </div>
              </div>
            </div>
          ))}
          <button type="button" onClick={addAccount} className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-surface-300 py-3 text-sm text-surface-500 transition hover:border-brand-400 hover:text-brand-600 dark:border-white/10 dark:text-white/40 dark:hover:border-brand-400/50 dark:hover:text-brand-400">
            <Plus className="h-4 w-4" /> Add Bank Account
          </button>
          <div className="border-t border-surface-100 pt-5 dark:border-white/5">
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-wide text-surface-500 dark:text-white/40">Statutory Information</h3>
            <div className="grid gap-5 sm:grid-cols-3">
              <FormInput label="PAN Number"      value={statutory.pan_number}      onChange={(v) => setStatutory((s) => ({ ...s, pan_number: v }))} />
              <FormInput label="Aadhaar Number"  value={statutory.aadhaar_number}  onChange={(v) => setStatutory((s) => ({ ...s, aadhaar_number: v }))} />
              <FormInput label="UAN Number"      value={statutory.uan_number}      onChange={(v) => setStatutory((s) => ({ ...s, uan_number: v }))} />
              <FormInput label="Passport Number" value={statutory.passport_number} onChange={(v) => setStatutory((s) => ({ ...s, passport_number: v }))} />
            </div>
          </div>
        </div>
      ) : (
        <>
          {accounts.length > 0 ? (
            <div className="space-y-4">
              {accounts.map((bd) => (
                <div key={bd.id} className="rounded-xl border border-surface-100 p-4 dark:border-white/5">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-emerald-50 dark:bg-emerald-500/10">
                      <CreditCard className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <div>
                      <p className="font-medium text-surface-900 dark:text-white">{bd.bank_detail?.name ?? 'Bank'}</p>
                      <p className="text-xs text-surface-500 dark:text-white/40">{bd.branch_detail?.name ?? ''} {bd.is_primary && '· Primary Account'}</p>
                    </div>
                    {bd.is_primary && <Badge variant="success" size="sm" className="ml-auto">Primary</Badge>}
                  </div>
                  <div className="mt-4 grid gap-4 sm:grid-cols-3">
                    <InfoField label="Account Number"  value={bd.account_number} masked />
                    <InfoField label="IFSC Code"       value={bd.ifsc_code} />
                    <InfoField label="Account Holder"  value={bd.account_holder_name} />
                    <InfoField label="Account Type"    value={bd.account_type} />
                    <InfoField label="Branch"          value={bd.branch_name || bd.branch_detail?.name} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-surface-400 dark:text-white/30">No bank details on record.</p>
          )}
          <div className="mt-6 border-t border-surface-100 pt-5 dark:border-white/5">
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-wide text-surface-500 dark:text-white/40">Statutory Information</h3>
            <div className="grid gap-5 sm:grid-cols-3">
              <InfoField label="PAN Number"      value={data.pan_number}      masked />
              <InfoField label="Aadhaar Number"  value={data.aadhaar_number}  masked />
              <InfoField label="UAN Number"      value={data.uan_number} />
              <InfoField label="Passport Number" value={data.passport_number} />
            </div>
          </div>
        </>
      )}
    </SectionCard>
  );
}

/* ── Nominees ─────────────────────────────────────────────────────── */

function NomineeSection({ data, editing, isSaving, hasPendingApproval, onEdit, onCancel, onSubmit }: SectionProps) {
  const [nominees, setNominees] = useState<NomineeInfo[]>(data.nominees);

  const update = (id: string, key: keyof NomineeInfo, value: unknown) =>
    setNominees((prev) => prev.map((n) => n.id === id ? { ...n, [key]: value } : n));
  const add = () =>
    setNominees((prev) => [...prev, { id: `new-${Date.now()}`, name: '', relation_detail: undefined, percentage: '', phone: '' }]);
  const remove = (id: string) => setNominees((prev) => prev.filter((n) => n.id !== id));

  return (
    <SectionCard
      id="nominee"
      title="Nominees"
      icon={Shield}
      isEditing={editing}
      isSaving={isSaving}
      hasPendingApproval={hasPendingApproval}
      onEdit={onEdit}
      onCancel={onCancel}
      onSubmit={() => onSubmit('nominee', 'Nominees', { nominees })}
    >
      {editing ? (
        <div className="space-y-4">
          {nominees.map((n) => (
            <div key={n.id} className="rounded-xl border border-surface-100 p-4 dark:border-white/5">
              <div className="mb-3 flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wide text-surface-500 dark:text-white/40">Nominee</span>
                <button type="button" onClick={() => remove(n.id)} className="text-red-400 transition hover:text-red-600 dark:text-red-400/70 dark:hover:text-red-400">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
              <div className="grid gap-4 sm:grid-cols-4">
                <FormInput label="Name"      value={n.name}                          onChange={(v) => update(n.id, 'name', v)} />
                <FormInput label="Relation"  value={n.relation_detail?.name ?? ''}   onChange={(v) => update(n.id, 'relation_detail', { id: '', name: v, code: '' })} />
                <FormInput label="Share %"   value={String(n.percentage)}             onChange={(v) => update(n.id, 'percentage', v)} type="number" />
                <FormInput label="Phone"     value={n.phone}                          onChange={(v) => update(n.id, 'phone', v)} type="tel" />
              </div>
            </div>
          ))}
          <button type="button" onClick={add} className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-surface-300 py-3 text-sm text-surface-500 transition hover:border-brand-400 hover:text-brand-600 dark:border-white/10 dark:text-white/40 dark:hover:border-brand-400/50 dark:hover:text-brand-400">
            <Plus className="h-4 w-4" /> Add Nominee
          </button>
        </div>
      ) : nominees.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-100 text-left text-xs text-surface-500 dark:border-white/5 dark:text-white/40">
                <th className="pb-3 pr-4 font-medium">Name</th>
                <th className="pb-3 pr-4 font-medium">Relation</th>
                <th className="pb-3 pr-4 font-medium">Share %</th>
                <th className="pb-3 font-medium">Phone</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-100 dark:divide-white/5">
              {nominees.map((n) => (
                <tr key={n.id}>
                  <td className="py-3 pr-4 font-medium text-surface-900 dark:text-white">{n.name}</td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">{n.relation_detail?.name ?? '—'}</td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">{n.percentage}%</td>
                  <td className="py-3 text-surface-600 dark:text-white/60">{n.phone || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-sm text-surface-400 dark:text-white/30">No nominees on record.</p>
      )}
    </SectionCard>
  );
}

/* ── Insurance ─────────────────────────────────────────────────────── */
function InsuranceSection({
  data,
  editing,
  isSaving,
  hasPendingApproval,
  onEdit,
  onCancel,
  onSubmit,
}: SectionProps) {

  const [form, setForm] = useState({
    policy_number: data.insurance?.policy_number || '',
    provider: data.insurance?.provider || '',
    start_date: data.insurance?.start_date || '',
    end_date: data.insurance?.end_date || '',
    coverage_amount: data.insurance?.coverage_amount || '',
    nominee_name: data.insurance?.nominee_name || '',
  });

  const update = (key: string, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <SectionCard
      id="insurance"
      title="Insurance Details"
      icon={Shield}
      isEditing={editing}
      isSaving={isSaving}
      hasPendingApproval={hasPendingApproval}
      onEdit={onEdit}
      onCancel={onCancel}
      onSubmit={() =>
        onSubmit('insurance', 'Insurance Details', form)
      }
    >
      {editing ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInput
            label="Policy Number"
            value={form.policy_number}
            onChange={(v) => update('policy_number', v)}
          />

          <FormInput
            label="Insurance Provider"
            value={form.provider}
            onChange={(v) => update('provider', v)}
          />

          <FormInput
            label="Start Date"
            type="date"
            value={form.start_date}
            onChange={(v) => update('start_date', v)}
          />

          <FormInput
            label="End Date"
            type="date"
            value={form.end_date}
            onChange={(v) => update('end_date', v)}
          />

          <FormInput
            label="Coverage Amount"
            value={form.coverage_amount}
            onChange={(v) => update('coverage_amount', v)}
          />

          <FormInput
            label="Nominee Name"
            value={form.nominee_name}
            onChange={(v) => update('nominee_name', v)}
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <InfoField label="Policy Number" value={form.policy_number} />
          <InfoField label="Provider" value={form.provider} />
          <InfoField label="Start Date" value={formatDate(form.start_date)} />
          <InfoField label="End Date" value={formatDate(form.end_date)} />
          <InfoField label="Coverage" value={form.coverage_amount} />
          <InfoField label="Nominee" value={form.nominee_name} />
        </div>
      )}
    </SectionCard>
  );
}

/* ── Languages ────────────────────────────────────────────────────── */

const PROFICIENCY_OPTIONS = [
  { value: 'NATIVE',       label: 'Native' },
  { value: 'ADVANCED',     label: 'Advanced' },
  { value: 'INTERMEDIATE', label: 'Intermediate' },
  { value: 'BEGINNER',     label: 'Beginner' },
];

function LanguageSection({ data, editing, isSaving, hasPendingApproval, onEdit, onCancel, onSubmit }: SectionProps) {
  const [langs, setLangs] = useState<LanguageInfo[]>(data.languages);

  const update = (id: string, key: keyof LanguageInfo, value: unknown) =>
    setLangs((prev) => prev.map((l) => l.id === id ? { ...l, [key]: value } : l));
  const add = () =>
    setLangs((prev) => [...prev, { id: `new-${Date.now()}`, language_detail: undefined, can_read: false, can_write: false, can_speak: false, proficiency_level: 'INTERMEDIATE' }]);
  const remove = (id: string) => setLangs((prev) => prev.filter((l) => l.id !== id));

  return (
    <SectionCard
      id="language"
      title="Languages"
      icon={Languages}
      isEditing={editing}
      isSaving={isSaving}
      hasPendingApproval={hasPendingApproval}
      onEdit={onEdit}
      onCancel={onCancel}
      onSubmit={() => onSubmit('language', 'Languages', { languages: langs })}
    >
      {editing ? (
        <div className="space-y-4">
          {langs.map((lang) => (
            <div key={lang.id} className="rounded-xl border border-surface-100 p-4 dark:border-white/5">
              <div className="mb-3 flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wide text-surface-500 dark:text-white/40">Language</span>
                <button type="button" onClick={() => remove(lang.id)} className="text-red-400 transition hover:text-red-600 dark:text-red-400/70 dark:hover:text-red-400">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
              <div className="grid gap-4 sm:grid-cols-3">
                <FormInput   label="Language"    value={lang.language_detail?.name ?? ''} onChange={(v) => update(lang.id, 'language_detail', { id: '', name: v, code: '' })} />
                <FormSelect  label="Proficiency" value={lang.proficiency_level}           onChange={(v) => update(lang.id, 'proficiency_level', v)} options={PROFICIENCY_OPTIONS} />
                <div className="flex flex-col gap-2 pt-5">
                  <FormCheckbox label="Can Read"  checked={lang.can_read}  onChange={(v) => update(lang.id, 'can_read', v)} />
                  <FormCheckbox label="Can Write" checked={lang.can_write} onChange={(v) => update(lang.id, 'can_write', v)} />
                  <FormCheckbox label="Can Speak" checked={lang.can_speak} onChange={(v) => update(lang.id, 'can_speak', v)} />
                </div>
              </div>
            </div>
          ))}
          <button type="button" onClick={add} className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-surface-300 py-3 text-sm text-surface-500 transition hover:border-brand-400 hover:text-brand-600 dark:border-white/10 dark:text-white/40 dark:hover:border-brand-400/50 dark:hover:text-brand-400">
            <Plus className="h-4 w-4" /> Add Language
          </button>
        </div>
      ) : langs.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-100 text-left text-xs text-surface-500 dark:border-white/5 dark:text-white/40">
                <th className="pb-3 pr-4 font-medium">Language</th>
                <th className="pb-3 pr-4 font-medium">Proficiency</th>
                <th className="pb-3 pr-4 font-medium">Read</th>
                <th className="pb-3 pr-4 font-medium">Write</th>
                <th className="pb-3 font-medium">Speak</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-100 dark:divide-white/5">
              {langs.map((lang) => (
                <tr key={lang.id}>
                  <td className="py-3 pr-4 font-medium text-surface-900 dark:text-white">{lang.language_detail?.name ?? '—'}</td>
                  <td className="py-3 pr-4">
                    <Badge variant={lang.proficiency_level === 'NATIVE' ? 'success' : lang.proficiency_level === 'ADVANCED' ? 'brand' : 'neutral'} size="sm">
                      {lang.proficiency_level}
                    </Badge>
                  </td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">{lang.can_read  ? '✓' : '—'}</td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">{lang.can_write ? '✓' : '—'}</td>
                  <td className="py-3 text-surface-600 dark:text-white/60">{lang.can_speak ? '✓' : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-sm text-surface-400 dark:text-white/30">No language records.</p>
      )}
    </SectionCard>
  );
}

/* ── Assets (read-only — admin managed) ───────────────────────────── */

function AssetsSection({ data }: { data: MyProfileData }) {
  return (
    <SectionCard id="assets" title="Assets" icon={Laptop}>
      <div className="mb-4 flex items-center gap-2 rounded-lg bg-surface-50 px-3 py-2 text-xs text-surface-500 dark:bg-white/5 dark:text-white/40">
        <Fingerprint className="h-3.5 w-3.5 shrink-0" />
        Assets are assigned and managed by IT / Admin. Contact your admin to request changes.
      </div>
      {data.assets.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-100 text-left text-xs text-surface-500 dark:border-white/5 dark:text-white/40">
                <th className="pb-3 pr-4 font-medium">Asset</th>
                <th className="pb-3 pr-4 font-medium">Code</th>
                <th className="pb-3 pr-4 font-medium">Type</th>
                <th className="pb-3 pr-4 font-medium">Assigned Date</th>
                <th className="pb-3 pr-4 font-medium">Return Date</th>
                <th className="pb-3 pr-4 font-medium">Condition</th>
                <th className="pb-3 font-medium">Remarks</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-100 dark:divide-white/5">
              {data.assets.map((asset) => (
                <tr key={asset.id}>
                  <td className="py-3 pr-4 font-medium text-surface-900 dark:text-white">{asset.asset_name}</td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">
                    <span className="rounded-md bg-surface-100 px-1.5 py-0.5 font-mono text-xs dark:bg-white/10">{asset.asset_code}</span>
                  </td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">{asset.asset_type}</td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">{formatDate(asset.assigned_date)}</td>
                  <td className="py-3 pr-4 text-surface-600 dark:text-white/60">{asset.return_date ? formatDate(asset.return_date) : '—'}</td>
                  <td className="py-3 pr-4">
                    <Badge variant={asset.condition === 'Good' ? 'success' : asset.condition === 'Damaged' ? 'danger' : 'neutral'} size="sm">
                      {asset.condition}
                    </Badge>
                  </td>
                  <td className="py-3 text-surface-600 dark:text-white/60">{asset.remarks || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-sm text-surface-400 dark:text-white/30">No assets assigned.</p>
      )}
    </SectionCard>
  );
}

/* ================================================================== */
/*  Main: My Profile Page                                              */
/* ================================================================== */

export function MyProfilePage() {
  const { data, isLoading, isError } = useMyProfile();
  const { mutate: submitChangeRequest, isPending: isSaving } = useProfileChangeRequest();

  const [activeSection,    setActiveSection]    = useState<SectionId>('profile');
  const [editingSection,   setEditingSection]   = useState<SectionId | null>(null);
  const [pendingSections,  setPendingSections]  = useState<Set<SectionId>>(new Set());
  const [banner, setBanner] = useState<{ status: 'success' | 'error' } | null>(null);

  if (isLoading) return <ProfileSkeleton />;

  if (isError || !data) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <User className="h-10 w-10 text-surface-400 dark:text-white/30" />
        <p className="mt-3 text-sm text-surface-600 dark:text-white/50">Unable to load your profile.</p>
      </div>
    );
  }

  /* Handlers */
  const handleEdit   = (id: SectionId) => { setEditingSection(id); setBanner(null); };
  const handleCancel = ()               => setEditingSection(null);

  const handleSubmit = (
    sectionId: SectionId,
    sectionLabel: string,
    changes: Record<string, unknown>
  ) => {
    submitChangeRequest(
      { section: sectionId, section_label: sectionLabel, changes },
      {
        onSuccess: () => {
          setPendingSections((prev) => new Set([...prev, sectionId]));
          setBanner({ status: 'success' });
          setEditingSection(null);
        },
        onError: () => {
          setBanner({ status: 'error' });
        },
      }
    );
  };

  /* Factory for per-section props */
  const sp = (id: SectionId): SectionProps => ({
    data,
    editing:            editingSection === id,
    isSaving:           isSaving && editingSection === id,
    hasPendingApproval: pendingSections.has(id),
    onEdit:             () => handleEdit(id),
    onCancel:           handleCancel,
    onSubmit:           handleSubmit,
  });

  return (
    <div className="flex items-start gap-6">

      {/* ── Sidebar ─────────────────────────────────────────────────── */}
      <aside className="sticky top-6 hidden h-fit w-56 shrink-0 lg:block">
        <div className="surface-card rounded-2xl p-4">
          <div className="mb-4 flex flex-col items-center gap-2 border-b border-surface-100 pb-4 dark:border-white/5">
            <Avatar name={data.full_name} size="xl" />
            <div className="text-center">
              <p className="text-sm font-semibold text-surface-900 dark:text-white">Hi {data.first_name}</p>
              {pendingSections.size > 0 && (
                <p className="mt-1 text-xs text-amber-600 dark:text-amber-400">
                  {pendingSections.size} change{pendingSections.size > 1 ? 's' : ''} pending approval
                </p>
              )}
            </div>
          </div>
          <nav className="space-y-0.5">
            {sidebarItems.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  onClick={() => setActiveSection(item.id)}
                  className={cn(
                    'flex items-center gap-2.5 rounded-xl px-3 py-2 text-sm transition-colors',
                    activeSection === item.id
                      ? 'bg-brand-50 font-medium text-brand-700 dark:bg-brand-500/10 dark:text-brand-300'
                      : 'text-surface-600 hover:bg-surface-100 hover:text-surface-900 dark:text-white/55 dark:hover:bg-white/5 dark:hover:text-white'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                  {pendingSections.has(item.id) && (
                    <span className="ml-auto h-2 w-2 rounded-full bg-amber-500" />
                  )}
                </a>
              );
            })}
          </nav>
        </div>
      </aside>

      {/* ── Main content ────────────────────────────────────────────── */}
      <div className="min-w-0 flex-1 space-y-4">

        {/* Page header */}
        <div className="mb-2 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-surface-900 dark:text-white">Employee Information</h1>
            <JumpLinks active={activeSection} />
          </div>
          <Badge variant={data.status_detail?.code === 'ACTIVE' ? 'success' : 'warning'} size="sm" dot>
            {data.status_detail?.name ?? 'Unknown'}
          </Badge>
        </div>

        {/* Submission feedback banner */}
        {banner && (
          <SubmitBanner status={banner.status} onClose={() => setBanner(null)} />
        )}

        {/* Sections */}
        <ProfileSection    {...sp('profile')} />
        <PersonalSection   {...sp('personal')} />
        <EmploymentSection {...sp('employment')} />
        <AddressSection    {...sp('address')} />
        <FamilySection     {...sp('family')} />
        <EducationSection  {...sp('education')} />
        <BankSection       {...sp('bank')} />
        <NomineeSection    {...sp('nominee')} />
        <InsuranceSection  {...sp('insurance')} />
        <LanguageSection   {...sp('language')} />
        <AssetsSection     data={data} />

      </div>
    </div>
  );
}