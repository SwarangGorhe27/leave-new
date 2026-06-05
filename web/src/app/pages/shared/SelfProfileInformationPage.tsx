import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Building2,
  Check,
  ChevronDown,
  ChevronRight,
  ClipboardList,
  CreditCard,
  Edit2,
  FileText,
  Globe,
  GraduationCap,
  IndianRupee,
  Lock,
  Paperclip,
  Plus,
  Send,
  ShieldCheck,
  Trash2,
  Upload,
  User,
  Users,
  X,
} from "lucide-react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../../store";
import { addNotification } from "../../../store/slices/notificationSlice";
import { updateAdminEmployee } from "../../../store/slices/adminSlice";
import { saveEssProfileWithAdminSync } from "../../../store/slices/employeeSlice";
import { ContentSection } from "../../components/employees/ContentSection";
import { EmployeeFormProvider } from "../../components/employees/employee-details/EmployeeFormContext";
import { SidebarSection } from "../../components/employees/SidebarMenu";
import { Employee } from "../../components/employees/mockData";
import { EssEmployeeProfile } from "../../components/employees/sections/EssEmployeeProfile";
import { useAuth } from "../../context/AuthContext";
import {
  ensureProfile,
  getChangeRequests,
  saveDraftChangeRequest,
  submitDraftChangeRequest,
} from "../../modules/ess/storage";
import { ProfileChangeRequest, SectionKey } from "../../modules/ess/types";
import { employeeIdAliases } from "../../utils/resolveLoggedInEmployee";
import { useMyEmployeeModuleProfile } from "../../../hooks/useEmployeeModuleProfile";
import { cacheEmployeeInRedux } from "../../services/employeeProfilePersistence";
import { usePassportVisaMasterOptions } from "../../components/employees/sections/usePassportVisaMasterOptions";

/* ─── Types & helpers ─────────────────────────────────────────────────────── */

type SelfSection = SidebarSection | "myRequest";

interface MenuItem {
  id: SelfSection;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const menuItems: MenuItem[] = [
  { id: "profile", label: "Employee Profile", icon: User },
  { id: "education", label: "Education Details", icon: GraduationCap },
  { id: "family", label: "Family Details", icon: Users },
  { id: "nominee", label: "Nominee Details", icon: Users },
  { id: "insurance", label: "Insurance Details", icon: ShieldCheck },
  { id: "work", label: "Work Experience", icon: Building2 },
  { id: "bank", label: "Bank / PF / ESI", icon: CreditCard },
  { id: "passport", label: "Passport & Visa", icon: Globe },
  { id: "documents", label: "Employee Documents", icon: FileText },
  { id: "salary", label: "Employee Salary", icon: IndianRupee },
  { id: "myRequest", label: "My Request", icon: ClipboardList },
];

/** Sections that are editable inside My Request */
const EDITABLE_SECTIONS: SelfSection[] = [
  "profile",
  "education",
  "family",
  "nominee",
  "insurance",
  "work",
  "bank",
  "passport",
  "documents",
];

const sectionToStorageKey: Partial<Record<SelfSection, SectionKey>> = {
  profile: "personalDetails",
  education: "educationDetails",
  family: "familyDetails",
  nominee: "nomineeDetails",
  insurance: "insuranceDetails",
  work: "previousEmployment",
  bank: "bankAndStatutoryDetails",
  passport: "passportAndVisa",
  documents: "documentsRepository",
};

const statusStyle: Record<string, string> = {
  Active: "bg-[#212529] text-[#F8F9FA]",
  "On Leave": "bg-[#6C757D] text-white",
  Inactive: "bg-[#CED4DA] text-[#212529]",
};

const requestStatusColors: Record<string, string> = {
  draft: "bg-slate-100 border-slate-300 text-slate-600",
  pending: "bg-amber-50 border-amber-200 text-amber-700",
  approved: "bg-emerald-50 border-emerald-200 text-emerald-700",
  rejected: "bg-rose-50 border-rose-200 text-rose-700",
};

/* ─── Shared small UI ─────────────────────────────────────────────────────── */

function FieldRow({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1">
      <label className="block text-[11px] font-bold uppercase tracking-wide text-muted-foreground">
        {label}
      </label>
      {children}
    </div>
  );
}

function Input({
  value,
  onChange,
  type = "text",
  placeholder = "",
}: {
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
}) {
  return (
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full h-9 rounded-md border border-border bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
    />
  );
}

function Select({
  value,
  onChange,
  options,
  emptyLabel = "— Select —",
}: {
  value: string;
  onChange: (v: string) => void;
  options: string[];
  emptyLabel?: string;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full h-9 rounded-md border border-border bg-background px-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/30"
    >
      <option value="">{emptyLabel}</option>
      {options.map((o) => (
        <option key={o} value={o}>
          {o}
        </option>
      ))}
    </select>
  );
}

function Checkbox({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-2 cursor-pointer select-none text-sm text-foreground">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 rounded border-border accent-foreground"
      />
      {label}
    </label>
  );
}

function CardRow({
  index,
  onRemove,
  children,
}: {
  index: number;
  onRemove: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-border bg-card/60 p-4 space-y-3 relative">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
          Record #{index + 1}
        </span>
        <button
          type="button"
          onClick={onRemove}
          className="h-7 w-7 flex items-center justify-center rounded-lg text-muted-foreground hover:bg-rose-50 hover:text-rose-600 transition-colors"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">{children}</div>
    </div>
  );
}

function AddMoreBtn({
  label,
  onClick,
}: {
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center gap-1.5 rounded-lg border border-dashed border-border px-4 py-2 text-xs font-bold text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
    >
      <Plus className="h-3.5 w-3.5" />
      {label}
    </button>
  );
}

/* ─── File upload helper ──────────────────────────────────────────────────── */

interface UploadedFile {
  fileName: string;
  dataUrl: string;
  uploadedAt: string;
}

function FileUploadField({
  label,
  file,
  onChange,
  required,
}: {
  label: string;
  file: UploadedFile | null;
  onChange: (f: UploadedFile | null) => void;
  required?: boolean;
}) {
  const ref = useRef<HTMLInputElement>(null);
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () =>
      onChange({
        fileName: f.name,
        dataUrl: reader.result as string,
        uploadedAt: new Date().toISOString(),
      });
    reader.readAsDataURL(f);
  };
  return (
    <div className="space-y-1.5">
      <label className="block text-[11px] font-bold uppercase tracking-wide text-muted-foreground">
        {label}
        {required && <span className="text-rose-500 ml-0.5">*</span>}
      </label>
      {file ? (
        <div className="flex items-center gap-2 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-xs font-medium text-foreground">
          <Paperclip className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
          <span className="truncate flex-1">{file.fileName}</span>
          <button
            type="button"
            onClick={() => onChange(null)}
            className="text-muted-foreground hover:text-rose-600 transition-colors"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => ref.current?.click()}
          className="flex items-center gap-2 rounded-lg border border-dashed border-border px-3 py-2 text-xs font-medium text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors w-full"
        >
          <Upload className="h-3.5 w-3.5" />
          Click to upload
        </button>
      )}
      <input
        ref={ref}
        type="file"
        accept="image/*,application/pdf,.doc,.docx"
        className="hidden"
        onChange={handleChange}
      />
    </div>
  );
}

/* ─── Section form components ─────────────────────────────────────────────── */

/* 1. EMPLOYEE PROFILE ─────────────────────────────────────────────────────── */
function ProfileForm({
  employee,
  value,
  onChange,
}: {
  employee: Employee;
  value: any;
  onChange: (v: any) => void;
}) {
  const set = useCallback(
    (key: string, v: any) => onChange({ ...value, [key]: v }),
    [value, onChange]
  );
  const setLang = (idx: number, patch: any) => {
    const arr = [...(value.languages || employee.languages || [])];
    arr[idx] = { ...arr[idx], ...patch };
    set("languages", arr);
  };
  const addLang = () => {
    const arr = [...(value.languages || employee.languages || [])];
    arr.push({ language: "", proficiency: "Intermediate", canRead: true, canWrite: true, canSpeak: true });
    set("languages", arr);
  };
  const removeLang = (idx: number) => {
    const arr = (value.languages || employee.languages || []).filter((_: any, i: number) => i !== idx);
    set("languages", arr);
  };

  const langs: any[] = value.languages ?? employee.languages ?? [];
  const ec = value.emergencyContact ?? employee.emergencyContact ?? {};
  const med = value.medicalInfo ?? employee.medicalInfo ?? {};
  const cur = value.currentAddress ?? employee.currentAddress ?? {};
  const perm = value.permanentAddress ?? employee.permanentAddress ?? {};

  const setAddr = (type: "currentAddress" | "permanentAddress", key: string, v: string) => {
    const existing = value[type] ?? (type === "currentAddress" ? employee.currentAddress : employee.permanentAddress) ?? {};
    set(type, { ...existing, [key]: v });
  };
  const setEc = (key: string, v: string) => onChange({ ...value, emergencyContact: { ...ec, [key]: v } });
  const setMed = (key: string, v: any) => onChange({ ...value, medicalInfo: { ...med, [key]: v } });

  return (
    <div className="space-y-6">
      {/* Profile Photo */}
      <div>
        <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">Profile Photo</h4>
        <FileUploadField
          label="Upload new profile photo (JPG/PNG, max 3 MB)"
          file={value._profilePhoto ?? null}
          onChange={(f) => set("_profilePhoto", f)}
        />
      </div>

      {/* Personal Information */}
      <div>
        <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">Personal Information</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FieldRow label="First Name">
            <Input value={value.firstName ?? employee.firstName ?? ""} onChange={(v) => set("firstName", v)} />
          </FieldRow>
          <FieldRow label="Middle Name">
            <Input value={value.middleName ?? employee.middleName ?? ""} onChange={(v) => set("middleName", v)} />
          </FieldRow>
          <FieldRow label="Last Name">
            <Input value={value.lastName ?? employee.lastName ?? ""} onChange={(v) => set("lastName", v)} />
          </FieldRow>
          <FieldRow label="Preferred Name">
            <Input value={value.preferredName ?? employee.preferredName ?? ""} onChange={(v) => set("preferredName", v)} />
          </FieldRow>
          <FieldRow label="Date of Birth">
            <Input type="date" value={value.dateOfBirth ?? employee.dateOfBirth ?? ""} onChange={(v) => set("dateOfBirth", v)} />
          </FieldRow>
          <FieldRow label="Actual Date of Birth">
            <Input type="date" value={value.actualDob ?? employee.actualDob ?? ""} onChange={(v) => set("actualDob", v)} />
          </FieldRow>
          <FieldRow label="Place of Birth">
            <Input value={value.placeOfBirth ?? employee.placeOfBirth ?? ""} onChange={(v) => set("placeOfBirth", v)} />
          </FieldRow>
          <FieldRow label="Gender">
            <Select value={value.gender ?? employee.gender ?? ""} onChange={(v) => set("gender", v)} options={["Male", "Female", "Other", "Prefer not to say"]} />
          </FieldRow>
          <FieldRow label="Marital Status">
            <Select value={value.maritalStatus ?? employee.maritalStatus ?? ""} onChange={(v) => set("maritalStatus", v)} options={["Single", "Married", "Divorced", "Widowed", "Separated"]} />
          </FieldRow>
          <FieldRow label="Blood Group">
            <Select value={value.bloodGroup ?? employee.bloodGroup ?? ""} onChange={(v) => set("bloodGroup", v)} options={["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]} />
          </FieldRow>
          <FieldRow label="Nationality">
            <Input value={value.nationality ?? employee.nationality ?? ""} onChange={(v) => set("nationality", v)} />
          </FieldRow>
          <FieldRow label="Religion">
            <Input value={value.religion ?? employee.religion ?? ""} onChange={(v) => set("religion", v)} />
          </FieldRow>
          <FieldRow label="Caste">
            <Input value={value.caste ?? employee.caste ?? ""} onChange={(v) => set("caste", v)} />
          </FieldRow>
          <FieldRow label="Caste Category">
            <Select value={value.casteCategory ?? employee.casteCategory ?? ""} onChange={(v) => set("casteCategory", v)} options={["General", "OBC", "SC", "ST", "EWS"]} />
          </FieldRow>
          <FieldRow label="Father's Name">
            <Input value={value.fathersName ?? employee.fathersName ?? ""} onChange={(v) => set("fathersName", v)} />
          </FieldRow>
          <FieldRow label="Mother's Name">
            <Input value={value.motherName ?? employee.motherName ?? ""} onChange={(v) => set("motherName", v)} />
          </FieldRow>
          <FieldRow label="Spouse Name">
            <Input value={value.spouseName ?? employee.spouseName ?? ""} onChange={(v) => set("spouseName", v)} />
          </FieldRow>
          <FieldRow label="Identification Mark">
            <Input value={value.identificationMark ?? employee.identificationMark ?? ""} onChange={(v) => set("identificationMark", v)} />
          </FieldRow>
          <FieldRow label="Height">
            <Input value={value.height ?? employee.height ?? ""} onChange={(v) => set("height", v)} placeholder="e.g. 175 cm" />
          </FieldRow>
          <FieldRow label="Weight">
            <Input value={value.weight ?? employee.weight ?? ""} onChange={(v) => set("weight", v)} placeholder="e.g. 72 kg" />
          </FieldRow>
          <FieldRow label="Phone">
            <Input value={value.phone ?? employee.phone ?? ""} onChange={(v) => set("phone", v)} />
          </FieldRow>
          <FieldRow label="Alternate Mobile">
            <Input value={value.alternateMobile ?? employee.alternateMobile ?? ""} onChange={(v) => set("alternateMobile", v)} />
          </FieldRow>
          <FieldRow label="Personal Email">
            <Input type="email" value={value.email ?? employee.email ?? ""} onChange={(v) => set("email", v)} />
          </FieldRow>
          <FieldRow label="Bio">
            <Input value={value.bio ?? employee.bio ?? ""} onChange={(v) => set("bio", v)} />
          </FieldRow>
          <div className="sm:col-span-2 flex flex-wrap gap-4">
            <Checkbox label="Physically Challenged" checked={value.isPhysicallyChallenged ?? employee.isPhysicallyChallenged ?? false} onChange={(v) => set("isPhysicallyChallenged", v)} />
            <Checkbox label="International Employee" checked={value.isInternationalEmployee ?? employee.isInternationalEmployee ?? false} onChange={(v) => set("isInternationalEmployee", v)} />
          </div>
        </div>
      </div>

      {/* Address Details */}
      <div>
        <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">Current Address</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {["addressLine1", "addressLine2", "landmark", "city", "state", "country", "pincode"].map((k) => (
            <FieldRow key={k} label={k.replace(/([A-Z])/g, " $1").trim()}>
              <Input value={(cur as any)[k] ?? ""} onChange={(v) => setAddr("currentAddress", k, v)} />
            </FieldRow>
          ))}
        </div>
      </div>
      <div>
        <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">Permanent Address</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {["addressLine1", "addressLine2", "landmark", "city", "state", "country", "pincode"].map((k) => (
            <FieldRow key={k} label={k.replace(/([A-Z])/g, " $1").trim()}>
              <Input value={(perm as any)[k] ?? ""} onChange={(v) => setAddr("permanentAddress", k, v)} />
            </FieldRow>
          ))}
        </div>
      </div>

      {/* Emergency & Medical */}
      <div>
        <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">Emergency Contact</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FieldRow label="Contact Name"><Input value={ec.name ?? ""} onChange={(v) => setEc("name", v)} /></FieldRow>
          <FieldRow label="Relationship"><Input value={ec.relationship ?? ""} onChange={(v) => setEc("relationship", v)} /></FieldRow>
          <FieldRow label="Phone"><Input value={ec.phone ?? ""} onChange={(v) => setEc("phone", v)} /></FieldRow>
          <FieldRow label="Alternate Phone"><Input value={ec.alternatePhone ?? ""} onChange={(v) => setEc("alternatePhone", v)} /></FieldRow>
        </div>
      </div>
      <div>
        <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">Medical Information</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FieldRow label="Medical Conditions"><Input value={med.conditions ?? ""} onChange={(v) => setMed("conditions", v)} /></FieldRow>
          <FieldRow label="Allergies"><Input value={med.allergies ?? ""} onChange={(v) => setMed("allergies", v)} /></FieldRow>
          <FieldRow label="Doctor Name"><Input value={med.doctorName ?? ""} onChange={(v) => setMed("doctorName", v)} /></FieldRow>
          <FieldRow label="Insurance Provider"><Input value={med.insuranceProvider ?? ""} onChange={(v) => setMed("insuranceProvider", v)} /></FieldRow>
          <FieldRow label="Insurance Policy Number"><Input value={med.insurancePolicyNumber ?? ""} onChange={(v) => setMed("insurancePolicyNumber", v)} /></FieldRow>
          <div className="sm:col-span-2 flex flex-wrap gap-4">
            <Checkbox label="Has Disease/Condition" checked={med.hasDisease ?? false} onChange={(v) => setMed("hasDisease", v)} />
            {med.hasDisease && (
              <FieldRow label="Disease Description">
                <Input value={med.diseaseDescription ?? ""} onChange={(v) => setMed("diseaseDescription", v)} />
              </FieldRow>
            )}
            <Checkbox label="Has had Surgery" checked={med.hasSurgery ?? false} onChange={(v) => setMed("hasSurgery", v)} />
            {med.hasSurgery && (
              <FieldRow label="Surgery Description">
                <Input value={med.surgeryDescription ?? ""} onChange={(v) => setMed("surgeryDescription", v)} />
              </FieldRow>
            )}
          </div>
        </div>
      </div>

      {/* Language Details */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground">Language Details</h4>
          <AddMoreBtn label="Add Language" onClick={addLang} />
        </div>
        {langs.length === 0 ? (
          <p className="text-sm text-muted-foreground italic">No languages added.</p>
        ) : (
          <div className="space-y-3">
            {langs.map((lang, i) => (
              <CardRow key={i} index={i} onRemove={() => removeLang(i)}>
                <FieldRow label="Language"><Input value={lang.language ?? ""} onChange={(v) => setLang(i, { language: v })} /></FieldRow>
                <FieldRow label="Proficiency">
                  <Select value={lang.proficiency ?? ""} onChange={(v) => setLang(i, { proficiency: v })} options={["Beginner", "Intermediate", "Advanced", "Native"]} />
                </FieldRow>
                <div className="sm:col-span-2 flex gap-4 flex-wrap">
                  <Checkbox label="Can Read" checked={lang.canRead ?? false} onChange={(v) => setLang(i, { canRead: v })} />
                  <Checkbox label="Can Write" checked={lang.canWrite ?? false} onChange={(v) => setLang(i, { canWrite: v })} />
                  <Checkbox label="Can Speak" checked={lang.canSpeak ?? false} onChange={(v) => setLang(i, { canSpeak: v })} />
                </div>
              </CardRow>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/* 2. EDUCATION DETAILS ────────────────────────────────────────────────────── */
function EducationForm({ employee, value, onChange }: { employee: Employee; value: any[]; onChange: (v: any[]) => void }) {
  const add = () => onChange([...value, { qualification: "", specialization: "", institutionName: "", university: "", fromDate: "", toDate: "", percentageCgpa: "", grade: "" }]);
  const remove = (i: number) => onChange(value.filter((_, idx) => idx !== i));
  const update = (i: number, key: string, v: string) => {
    const arr = [...value];
    arr[i] = { ...arr[i], [key]: v };
    onChange(arr);
  };
  return (
    <div className="space-y-4">
      {value.length === 0 && <p className="text-sm text-muted-foreground italic">No education records. Add one below.</p>}
      {value.map((row, i) => (
        <CardRow key={i} index={i} onRemove={() => remove(i)}>
          <FieldRow label="Qualification"><Input value={row.qualification ?? ""} onChange={(v) => update(i, "qualification", v)} /></FieldRow>
          <FieldRow label="Specialization"><Input value={row.specialization ?? ""} onChange={(v) => update(i, "specialization", v)} /></FieldRow>
          <FieldRow label="Institution Name"><Input value={row.institutionName ?? ""} onChange={(v) => update(i, "institutionName", v)} /></FieldRow>
          <FieldRow label="University / Board"><Input value={row.university ?? ""} onChange={(v) => update(i, "university", v)} /></FieldRow>
          <FieldRow label="From Date"><Input type="date" value={row.fromDate ?? ""} onChange={(v) => update(i, "fromDate", v)} /></FieldRow>
          <FieldRow label="To Date"><Input type="date" value={row.toDate ?? ""} onChange={(v) => update(i, "toDate", v)} /></FieldRow>
          <FieldRow label="Percentage / CGPA"><Input value={row.percentageCgpa ?? ""} onChange={(v) => update(i, "percentageCgpa", v)} /></FieldRow>
          <FieldRow label="Grade"><Input value={row.grade ?? ""} onChange={(v) => update(i, "grade", v)} /></FieldRow>
        </CardRow>
      ))}
      <AddMoreBtn label="Add Education Record" onClick={add} />
    </div>
  );
}

/* 3. FAMILY DETAILS ──────────────────────────────────────────────────────── */
function FamilyForm({ employee, value, onChange }: { employee: Employee; value: any[]; onChange: (v: any[]) => void }) {
  const add = () => onChange([...value, { name: "", relationship: "", dob: "", gender: "", bloodGroup: "", phone: "", occupation: "", isDependent: false, isEmergencyContact: false, isNominee: false }]);
  const remove = (i: number) => onChange(value.filter((_, idx) => idx !== i));
  const update = (i: number, key: string, v: any) => {
    const arr = [...value];
    arr[i] = { ...arr[i], [key]: v };
    onChange(arr);
  };
  return (
    <div className="space-y-4">
      {value.length === 0 && <p className="text-sm text-muted-foreground italic">No family records.</p>}
      {value.map((row, i) => (
        <CardRow key={i} index={i} onRemove={() => remove(i)}>
          <FieldRow label="Name"><Input value={row.name ?? ""} onChange={(v) => update(i, "name", v)} /></FieldRow>
          <FieldRow label="Relationship"><Input value={row.relationship ?? ""} onChange={(v) => update(i, "relationship", v)} /></FieldRow>
          <FieldRow label="Date of Birth"><Input type="date" value={row.dob ?? ""} onChange={(v) => update(i, "dob", v)} /></FieldRow>
          <FieldRow label="Gender">
            <Select value={row.gender ?? ""} onChange={(v) => update(i, "gender", v)} options={["Male", "Female", "Other"]} />
          </FieldRow>
          <FieldRow label="Blood Group">
            <Select value={row.bloodGroup ?? ""} onChange={(v) => update(i, "bloodGroup", v)} options={["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]} />
          </FieldRow>
          <FieldRow label="Phone"><Input value={row.phone ?? ""} onChange={(v) => update(i, "phone", v)} /></FieldRow>
          <FieldRow label="Occupation"><Input value={row.occupation ?? ""} onChange={(v) => update(i, "occupation", v)} /></FieldRow>
          <div className="sm:col-span-2 flex flex-wrap gap-4">
            <Checkbox label="Dependent" checked={row.isDependent ?? false} onChange={(v) => update(i, "isDependent", v)} />
            <Checkbox label="Emergency Contact" checked={row.isEmergencyContact ?? false} onChange={(v) => update(i, "isEmergencyContact", v)} />
            <Checkbox label="Is Nominee" checked={row.isNominee ?? false} onChange={(v) => update(i, "isNominee", v)} />
          </div>
        </CardRow>
      ))}
      <AddMoreBtn label="Add Family Member" onClick={add} />
    </div>
  );
}

/* 4. NOMINEE DETAILS ─────────────────────────────────────────────────────── */
function NomineeForm({ employee, value, onChange }: { employee: Employee; value: any[]; onChange: (v: any[]) => void }) {
  const add = () => onChange([...value, { id: `nom-${Date.now()}`, nomineeName: "", nomineeEmail: "", relationship: "", dateOfBirth: "", contactNumber: "", address: "", nomineeType: 'EPF', epfPercentage: "", epsPercentage: "", gratuityPercentage: "", customPercentage: "", isMinor: false, guardian: {} }]);
  const remove = (i: number) => onChange(value.filter((_, idx) => idx !== i));
  const update = (i: number, key: string, v: any) => {
    const arr = [...value];
    arr[i] = { ...arr[i], [key]: v };
    onChange(arr);
  };
  const computeTotals = (rows: any[]) => {
    const totals: Record<string, number> = { EPF: 0, EPS: 0, Gratuity: 0, Custom: 0 };
    rows.forEach((r) => {
      const add = (v?: string) => (v ? Number(v) || 0 : 0);
      totals.EPF += add(r.epfPercentage);
      totals.EPS += add(r.epsPercentage);
      totals.Gratuity += add(r.gratuityPercentage);
      totals.Custom += add(r.customPercentage);
    });
    return totals;
  };
  return (
    <div className="space-y-4">
      {value.length === 0 && <p className="text-sm text-muted-foreground italic">No nominee records.</p>}
      {value.map((row, i) => {
        const totals = computeTotals(value);
        const remainingFor = (type: string) => Math.max(0, 100 - (totals[type] - (type === 'EPF' ? Number(row.epfPercentage || 0) : type === 'EPS' ? Number(row.epsPercentage || 0) : type === 'Gratuity' ? Number(row.gratuityPercentage || 0) : Number(row.customPercentage || 0))));
        return (
          <CardRow key={i} index={i} onRemove={() => remove(i)}>
            <FieldRow label="Nominee Name"><Input value={row.nomineeName ?? ""} onChange={(v) => update(i, "nomineeName", v)} /></FieldRow>
            <FieldRow label="Relationship"><Input value={row.relationship ?? ""} onChange={(v) => update(i, "relationship", v)} /></FieldRow>
            <FieldRow label="Date of Birth"><Input type="date" value={row.dateOfBirth ?? ""} onChange={(v) => update(i, "dateOfBirth", v)} /></FieldRow>
            <FieldRow label="Contact Number"><Input value={row.contactNumber ?? ""} onChange={(v) => update(i, "contactNumber", v)} /></FieldRow>
            <FieldRow label="Email"><Input type="email" value={row.nomineeEmail ?? row.email ?? ""} onChange={(v) => update(i, "nomineeEmail", v)} /></FieldRow>
            <FieldRow label="Address"><Input value={row.address ?? ""} onChange={(v) => update(i, "address", v)} /></FieldRow>
            <FieldRow label="Nominee Type">
              <Select
                value={row.nomineeType ?? 'EPF'}
                onChange={(v) => {
                  const currentPct = v === 'EPF' ? Number(row.epfPercentage || 0) : v === 'EPS' ? Number(row.epsPercentage || 0) : v === 'Gratuity' ? Number(row.gratuityPercentage || 0) : Number(row.customPercentage || 0);
                  const rem = remainingFor(v);
                  if (rem <= 0 && currentPct <= 0) return; // prevent selection if no allocation
                  update(i, "nomineeType", v);
                }}
                options={[
                  { value: 'EPF', label: 'EPF', disabled: totals.EPF >= 100 && Number(row.epfPercentage || 0) <= 0 },
                  { value: 'EPS', label: 'EPS', disabled: totals.EPS >= 100 && Number(row.epsPercentage || 0) <= 0 },
                  { value: 'Gratuity', label: 'Gratuity', disabled: totals.Gratuity >= 100 && Number(row.gratuityPercentage || 0) <= 0 },
                  { value: 'Custom', label: 'Custom', disabled: totals.Custom >= 100 && Number(row.customPercentage || 0) <= 0 },
                ] as any}
              />
            </FieldRow>
            { (row.nomineeType || 'EPF') === 'EPF' && <FieldRow label="EPF (%)"><Input value={row.epfPercentage ?? ''} onChange={(v) => update(i, 'epfPercentage', v)} /></FieldRow> }
            { (row.nomineeType || 'EPF') === 'EPS' && <FieldRow label="EPS (%)"><Input value={row.epsPercentage ?? ''} onChange={(v) => update(i, 'epsPercentage', v)} /></FieldRow> }
            { (row.nomineeType || 'EPF') === 'Gratuity' && <FieldRow label="Gratuity (%)"><Input value={row.gratuityPercentage ?? ''} onChange={(v) => update(i, 'gratuityPercentage', v)} /></FieldRow> }
            { (row.nomineeType || 'EPF') === 'Custom' && <FieldRow label="Custom (%)"><Input value={row.customPercentage ?? ''} onChange={(v) => update(i, 'customPercentage', v)} /></FieldRow> }
            <div className="sm:col-span-2">
              <Checkbox label="Minor Nominee" checked={row.isMinor ?? false} onChange={(v) => update(i, "isMinor", v)} />
            </div>
            {row.isMinor && (
              <>
                <FieldRow label="Guardian Name"><Input value={row.guardian?.guardianName ?? row.guardian?.name ?? ""} onChange={(v) => update(i, "guardian", { ...(row.guardian ?? {}), guardianName: v })} /></FieldRow>
                <FieldRow label="Guardian Relationship"><Input value={row.guardian?.relationshipWithMinor ?? row.guardian?.relationship ?? ""} onChange={(v) => update(i, "guardian", { ...(row.guardian ?? {}), relationshipWithMinor: v })} /></FieldRow>
                <FieldRow label="Guardian Contact"><Input value={row.guardian?.contactNumber ?? ""} onChange={(v) => update(i, "guardian", { ...(row.guardian ?? {}), contactNumber: v })} /></FieldRow>
              </>
            )}
          </CardRow>
        );
      })}
      <AddMoreBtn label="Add Nominee" onClick={add} />
    </div>
  );
}

/* 5. INSURANCE DETAILS ───────────────────────────────────────────────────── */
function InsuranceForm({ employee, value, onChange }: { employee: Employee; value: any[]; onChange: (v: any[]) => void }) {
  const add = () => onChange([...value, { id: `ins-${Date.now()}`, insuranceProvider: "", policyNumber: "", coverageType: "", coverageAmount: "", validTill: "", dependentsCovered: "" }]);
  const remove = (i: number) => onChange(value.filter((_, idx) => idx !== i));
  const update = (i: number, key: string, v: string) => {
    const arr = [...value];
    arr[i] = { ...arr[i], [key]: v };
    onChange(arr);
  };
  return (
    <div className="space-y-4">
      {value.length === 0 && <p className="text-sm text-muted-foreground italic">No insurance records.</p>}
      {value.map((row, i) => (
        <CardRow key={i} index={i} onRemove={() => remove(i)}>
          <FieldRow label="Insurance Provider"><Input value={row.insuranceProvider ?? ""} onChange={(v) => update(i, "insuranceProvider", v)} /></FieldRow>
          <FieldRow label="Policy Number"><Input value={row.policyNumber ?? ""} onChange={(v) => update(i, "policyNumber", v)} /></FieldRow>
          <FieldRow label="Coverage Type">
            <Select value={row.coverageType ?? ""} onChange={(v) => update(i, "coverageType", v)} options={["Health", "Life", "Accidental", "Term", "Group"]} />
          </FieldRow>
          <FieldRow label="Coverage Amount"><Input value={row.coverageAmount ?? ""} onChange={(v) => update(i, "coverageAmount", v)} placeholder="e.g. 1000000" /></FieldRow>
          <FieldRow label="Valid Till"><Input type="date" value={row.validTill ?? ""} onChange={(v) => update(i, "validTill", v)} /></FieldRow>
          <FieldRow label="Dependents Covered"><Input value={row.dependentsCovered ?? ""} onChange={(v) => update(i, "dependentsCovered", v)} /></FieldRow>
        </CardRow>
      ))}
      <AddMoreBtn label="Add Insurance Record" onClick={add} />
    </div>
  );
}

/* 6. WORK EXPERIENCE ─────────────────────────────────────────────────────── */
function WorkExperienceForm({ employee, value, onChange }: { employee: Employee; value: any[]; onChange: (v: any[]) => void }) {
  const add = () => onChange([...value, { id: `we-${Date.now()}`, companyName: "", jobTitle: "", employmentType: "", department: "", location: "", startDate: "", endDate: "", responsibilities: "", technologiesUsed: "", reasonForLeaving: "" }]);
  const remove = (i: number) => onChange(value.filter((_, idx) => idx !== i));
  const update = (i: number, key: string, v: string) => {
    const arr = [...value];
    arr[i] = { ...arr[i], [key]: v };
    onChange(arr);
  };
  return (
    <div className="space-y-4">
      {value.length === 0 && <p className="text-sm text-muted-foreground italic">No work experience records.</p>}
      {value.map((row, i) => (
        <CardRow key={i} index={i} onRemove={() => remove(i)}>
          <FieldRow label="Company Name"><Input value={row.companyName ?? ""} onChange={(v) => update(i, "companyName", v)} /></FieldRow>
          <FieldRow label="Job Title"><Input value={row.jobTitle ?? ""} onChange={(v) => update(i, "jobTitle", v)} /></FieldRow>
          <FieldRow label="Employment Type">
            <Select value={row.employmentType ?? ""} onChange={(v) => update(i, "employmentType", v)} options={["Full Time", "Part Time", "Contract", "Internship", "Freelance"]} />
          </FieldRow>
          <FieldRow label="Department"><Input value={row.department ?? ""} onChange={(v) => update(i, "department", v)} /></FieldRow>
          <FieldRow label="Location"><Input value={row.location ?? ""} onChange={(v) => update(i, "location", v)} /></FieldRow>
          <FieldRow label="Start Date"><Input type="date" value={row.startDate ?? ""} onChange={(v) => update(i, "startDate", v)} /></FieldRow>
          <FieldRow label="End Date"><Input type="date" value={row.endDate ?? ""} onChange={(v) => update(i, "endDate", v)} /></FieldRow>
          <FieldRow label="Reason for Leaving"><Input value={row.reasonForLeaving ?? ""} onChange={(v) => update(i, "reasonForLeaving", v)} /></FieldRow>
          <FieldRow label="Responsibilities"><Input value={row.responsibilities ?? ""} onChange={(v) => update(i, "responsibilities", v)} /></FieldRow>
          <FieldRow label="Technologies Used"><Input value={row.technologiesUsed ?? ""} onChange={(v) => update(i, "technologiesUsed", v)} /></FieldRow>
        </CardRow>
      ))}
      <AddMoreBtn label="Add Work Experience" onClick={add} />
    </div>
  );
}

/* 7. BANK / PF / ESI ─────────────────────────────────────────────────────── */
function BankForm({
  employee,
  value,
  onChange,
  supportingDoc,
  onSupportingDocChange,
}: {
  employee: Employee;
  value: any;
  onChange: (v: any) => void;
  supportingDoc: UploadedFile | null;
  onSupportingDocChange: (f: UploadedFile | null) => void;
}) {
  const set = (key: string, v: any) => onChange({ ...value, [key]: v });

  const updateBank = (i: number, key: string, v: string) => {
    const arr = [...(value.bankAccounts ?? employee.bankAccounts ?? [])];
    arr[i] = { ...arr[i], [key]: v };
    set("bankAccounts", arr);
  };
  const addBank = () => {
    const arr = [...(value.bankAccounts ?? employee.bankAccounts ?? [])];
    arr.push({ id: `ba-${Date.now()}`, bankName: "", accountNumber: "", ifscCode: "", accountType: "", isPrimary: false });
    set("bankAccounts", arr);
  };
  const removeBank = (i: number) => set("bankAccounts", (value.bankAccounts ?? employee.bankAccounts ?? []).filter((_: any, idx: number) => idx !== i));

  const banks: any[] = value.bankAccounts ?? employee.bankAccounts ?? [];

  return (
    <div className="space-y-6">
      {/* Statutory Numbers */}
      <div>
        <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">Statutory Numbers</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FieldRow label="PAN Number"><Input value={value.panNumber ?? employee.panNumber ?? ""} onChange={(v) => set("panNumber", v)} /></FieldRow>
          <FieldRow label="Aadhaar Number"><Input value={value.aadhaarNumber ?? employee.aadhaarNumber ?? ""} onChange={(v) => set("aadhaarNumber", v)} /></FieldRow>
          <FieldRow label="UAN Number"><Input value={value.uanNumber ?? employee.uanNumber ?? ""} onChange={(v) => set("uanNumber", v)} /></FieldRow>
          <FieldRow label="PF Number"><Input value={value.pfNumber ?? employee.pfNumber ?? ""} onChange={(v) => set("pfNumber", v)} /></FieldRow>
          <FieldRow label="ESI Number"><Input value={value.esiNumber ?? employee.esiNumber ?? ""} onChange={(v) => set("esiNumber", v)} /></FieldRow>
          <FieldRow label="LWF/LIN Number"><Input value={value.linNumber ?? employee.linNumber ?? ""} onChange={(v) => set("linNumber", v)} /></FieldRow>
          <FieldRow label="Tax Regime">
            <Select value={value.taxRegime ?? employee.taxRegime ?? ""} onChange={(v) => set("taxRegime", v)} options={["Old Regime", "New Regime"]} />
          </FieldRow>
          <div className="sm:col-span-2 flex flex-wrap gap-4">
            <Checkbox label="PF Covered" checked={value.isPfCovered ?? employee.isPfCovered ?? false} onChange={(v) => set("isPfCovered", v)} />
            <Checkbox label="ESI Covered" checked={value.isEsiCovered ?? employee.isEsiCovered ?? false} onChange={(v) => set("isEsiCovered", v)} />
            <Checkbox label="LWF Covered" checked={value.isLwfCovered ?? employee.isLwfCovered ?? false} onChange={(v) => set("isLwfCovered", v)} />
            <Checkbox label="Earlier Member of Pension on Higher Wages" checked={value.isEarlierMemberOfPensionOnHigherWages ?? employee.isEarlierMemberOfPensionOnHigherWages ?? false} onChange={(v) => set("isEarlierMemberOfPensionOnHigherWages", v)} />
          </div>
        </div>
      </div>

      {/* Bank Accounts */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground">Bank Accounts</h4>
          <AddMoreBtn label="Add Bank Account" onClick={addBank} />
        </div>
        {banks.length === 0 && <p className="text-sm text-muted-foreground italic">No bank accounts.</p>}
        {banks.map((bank, i) => (
          <CardRow key={i} index={i} onRemove={() => removeBank(i)}>
            <FieldRow label="Bank Name"><Input value={bank.bankName ?? ""} onChange={(v) => updateBank(i, "bankName", v)} /></FieldRow>
            <FieldRow label="Account Number"><Input value={bank.accountNumber ?? ""} onChange={(v) => updateBank(i, "accountNumber", v)} /></FieldRow>
            <FieldRow label="IFSC Code"><Input value={bank.ifscCode ?? ""} onChange={(v) => updateBank(i, "ifscCode", v)} /></FieldRow>
            <FieldRow label="Account Type">
              <Select value={bank.accountType ?? ""} onChange={(v) => updateBank(i, "accountType", v)} options={["Savings", "Current", "Salary", "NRI"]} />
            </FieldRow>
            <div className="sm:col-span-2">
              <Checkbox label="Primary Account" checked={bank.isPrimary ?? false} onChange={(v) => updateBank(i, "isPrimary", v)} />
            </div>
          </CardRow>
        ))}
      </div>

      {/* Mandatory proof upload */}
      <div className="rounded-xl border border-amber-200 bg-amber-50/50 p-4 space-y-3">
        <div className="flex items-start gap-2">
          <div className="h-5 w-5 rounded-full bg-amber-500 flex items-center justify-center shrink-0 mt-0.5">
            <span className="text-white text-[10px] font-black">!</span>
          </div>
          <div>
            <p className="text-sm font-bold text-amber-800">Supporting Document Required</p>
            <p className="text-xs text-amber-700 mt-0.5">
              Any change to Bank, PF, ESI, UAN, LWF or statutory details requires an uploaded proof document before submission.
            </p>
          </div>
        </div>
        <FileUploadField
          label="Upload Supporting Proof (Bank Statement / Passbook / PF Statement)"
          file={supportingDoc}
          onChange={onSupportingDocChange}
          required
        />
      </div>
    </div>
  );
}

/* 8. PASSPORT & VISA ─────────────────────────────────────────────────────── */
function PassportForm({ employee, value, onChange }: { employee: Employee; value: any; onChange: (v: any) => void }) {
  const { options: passportCategoryOptions } = usePassportVisaMasterOptions("passport-categories");
  const { options: passportStatusOptions } = usePassportVisaMasterOptions("passport-statuses");
  const set = (key: string, v: string) => onChange({ ...value, [key]: v });

  const resolveLabel = (
    options: Array<{ value: string; label: string }>,
    current: string,
  ) => {
    const match = options.find((o) => o.value === current || o.label === current);
    return match?.label ?? current;
  };
  return (
    <div className="space-y-6">
      <div>
        <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">Passport Details</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FieldRow label="Passport Number"><Input value={value.passportNumber ?? employee.passportNumber ?? ""} onChange={(v) => set("passportNumber", v)} /></FieldRow>
          <FieldRow label="Passport Holder Name"><Input value={value.passportHolderName ?? employee.passportHolderName ?? ""} onChange={(v) => set("passportHolderName", v)} /></FieldRow>
          <FieldRow label="Issue Date"><Input type="date" value={value.passportIssueDate ?? employee.passportIssueDate ?? ""} onChange={(v) => set("passportIssueDate", v)} /></FieldRow>
          <FieldRow label="Expiry Date"><Input type="date" value={value.passportExpiry ?? employee.passportExpiry ?? ""} onChange={(v) => set("passportExpiry", v)} /></FieldRow>
          <FieldRow label="Place of Issue"><Input value={value.passportPlaceOfIssue ?? employee.passportPlaceOfIssue ?? ""} onChange={(v) => set("passportPlaceOfIssue", v)} /></FieldRow>
          <FieldRow label="Country of Issue"><Input value={value.passportCountryOfIssue ?? employee.passportCountryOfIssue ?? ""} onChange={(v) => set("passportCountryOfIssue", v)} /></FieldRow>
          <FieldRow label="Passport Category">
            <Select
              value={resolveLabel(
                passportCategoryOptions,
                value.passportCategory ?? employee.passportCategory ?? "",
              )}
              onChange={(v) => set("passportCategory", v)}
              options={passportCategoryOptions.map((o) => o.label)}
              emptyLabel={
                passportCategoryOptions.length
                  ? "— Select —"
                  : "No categories configured in Masters"
              }
            />
          </FieldRow>
          <FieldRow label="Passport Status">
            <Select
              value={resolveLabel(
                passportStatusOptions,
                value.passportStatus ?? employee.passportStatus ?? "",
              )}
              onChange={(v) => set("passportStatus", v)}
              options={passportStatusOptions.map((o) => o.label)}
              emptyLabel={
                passportStatusOptions.length
                  ? "— Select —"
                  : "No statuses configured in Masters"
              }
            />
          </FieldRow>
          <FieldRow label="Nationality"><Input value={value.nationality ?? employee.nationality ?? ""} onChange={(v) => set("nationality", v)} /></FieldRow>
        </div>
      </div>
      <div>
        <h4 className="text-xs font-black uppercase tracking-widest text-muted-foreground mb-3">Visa Details</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <FieldRow label="Visa Type"><Input value={value.visaType ?? employee.visaType ?? ""} onChange={(v) => set("visaType", v)} /></FieldRow>
          <FieldRow label="Visa Number"><Input value={value.visaNumber ?? employee.visaNumber ?? ""} onChange={(v) => set("visaNumber", v)} /></FieldRow>
          <FieldRow label="Visa Country"><Input value={value.visaCountry ?? employee.visaCountry ?? ""} onChange={(v) => set("visaCountry", v)} /></FieldRow>
          <FieldRow label="Visa Sponsor"><Input value={value.visaSponsor ?? employee.visaSponsor ?? ""} onChange={(v) => set("visaSponsor", v)} /></FieldRow>
          <FieldRow label="Issue Date"><Input type="date" value={value.visaIssueDate ?? employee.visaIssueDate ?? ""} onChange={(v) => set("visaIssueDate", v)} /></FieldRow>
          <FieldRow label="Expiry Date"><Input type="date" value={value.visaExpiry ?? employee.visaExpiry ?? ""} onChange={(v) => set("visaExpiry", v)} /></FieldRow>
          <FieldRow label="Visa Status">
            <Select value={value.visaStatus ?? employee.visaStatus ?? ""} onChange={(v) => set("visaStatus", v)} options={["Valid", "Expired", "Pending", "Cancelled"]} />
          </FieldRow>
        </div>
      </div>
    </div>
  );
}

/* 9. EMPLOYEE DOCUMENTS ──────────────────────────────────────────────────── */
const DOC_KEYS = [
  { key: "panCard", label: "PAN Card" },
  { key: "aadhaarCard", label: "Aadhaar Card" },
  { key: "resume", label: "Resume / CV" },
  { key: "offerLetter", label: "Offer Letter" },
  { key: "joiningDocuments", label: "Joining Documents" },
  { key: "educationalCertificates", label: "Educational Certificates" },
  { key: "salarySlips", label: "Salary Slips" },
  { key: "experienceLetters", label: "Experience Letters" },
  { key: "passport", label: "Passport Copy" },
  { key: "visa", label: "Visa Copy" },
  { key: "taxDocuments", label: "Tax Documents" },
  { key: "insuranceDocuments", label: "Insurance Documents" },
  { key: "relievingLetter", label: "Relieving Letter" },
  { key: "appraisalLetters", label: "Appraisal Letters" },
  { key: "incrementLetters", label: "Increment Letters" },
];

function DocumentsForm({ employee, value, onChange }: { employee: Employee; value: any; onChange: (v: any) => void }) {
  const set = (key: string, f: UploadedFile | null) => {
    if (f) onChange({ ...value, [key]: { fileName: f.fileName, dataUrl: f.dataUrl, uploadedAt: f.uploadedAt } });
    else {
      const next = { ...value };
      delete next[key];
      onChange(next);
    }
  };
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {DOC_KEYS.map(({ key, label }) => {
        const existing = (value[key] ?? employee.employeeDocuments?.[key]) as any;
        return (
          <FileUploadField
            key={key}
            label={label}
            file={existing ? { fileName: existing.fileName ?? key, dataUrl: existing.dataUrl ?? "", uploadedAt: existing.uploadedAt ?? "" } : null}
            onChange={(f) => set(key, f)}
          />
        );
      })}
    </div>
  );
}
/* ─── Initial form value builders ─────────────────────────────────────────── */
function buildInitialValue(section: SelfSection, employee: Employee): any {
  switch (section) {
    case "profile":
      return {
        firstName: employee.firstName,
        middleName: employee.middleName,
        lastName: employee.lastName,
        preferredName: employee.preferredName,
        dateOfBirth: employee.dateOfBirth,
        actualDob: employee.actualDob,
        placeOfBirth: employee.placeOfBirth,
        gender: employee.gender,
        maritalStatus: employee.maritalStatus,
        bloodGroup: employee.bloodGroup,
        nationality: employee.nationality,
        religion: employee.religion,
        caste: employee.caste,
        casteCategory: employee.casteCategory,
        fathersName: employee.fathersName,
        motherName: employee.motherName,
        spouseName: employee.spouseName,
        identificationMark: employee.identificationMark,
        height: employee.height,
        weight: employee.weight,
        phone: employee.phone,
        alternateMobile: employee.alternateMobile,
        email: employee.email,
        bio: employee.bio,
        isPhysicallyChallenged: employee.isPhysicallyChallenged,
        isInternationalEmployee: employee.isInternationalEmployee,
        languages: [...(employee.languages ?? [])],
        emergencyContact: { ...(employee.emergencyContact ?? {}) },
        medicalInfo: { ...(employee.medicalInfo ?? {}) },
        currentAddress: { ...(employee.currentAddress ?? {}) },
        permanentAddress: { ...(employee.permanentAddress ?? {}) },
      };
    case "education": return [...(employee.education ?? [])];
    case "family": return [...(employee.family ?? [])];
    case "nominee": return [...(employee.nominees ?? [])];
    case "insurance": return [...(employee.insurance ?? [])];
    case "work": return [...(employee.workExperience ?? [])];
    case "bank":
      return {
        bankAccounts: [...(employee.bankAccounts ?? [])],
        panNumber: employee.panNumber,
        aadhaarNumber: employee.aadhaarNumber,
        uanNumber: employee.uanNumber,
        pfNumber: employee.pfNumber,
        esiNumber: employee.esiNumber,
        linNumber: employee.linNumber,
        taxRegime: employee.taxRegime,
        isPfCovered: employee.isPfCovered,
        isEsiCovered: employee.isEsiCovered,
      };
    case "passport":
      return {
        passportNumber: employee.passportNumber,
        passportHolderName: employee.passportHolderName,
        passportIssueDate: employee.passportIssueDate,
        passportPlaceOfIssue: employee.passportPlaceOfIssue,
        passportCountryOfIssue: employee.passportCountryOfIssue,
        passportCategory: employee.passportCategory,
        passportStatus: employee.passportStatus,
        passportExpiry: employee.passportExpiry,
        visaNumber: employee.visaNumber,
        visaType: employee.visaType,
        visaIssueDate: employee.visaIssueDate,
        visaExpiry: employee.visaExpiry,
        visaCountry: employee.visaCountry,
      };
    case "documents": return { ...(employee.employeeDocuments ?? {}) };
    default: return {};
  }
}

/* ─── My Request Section ──────────────────────────────────────────────────── */

function MyRequestSection({
  employee,
  requestEmployeeIds,
}: {
  employee: Employee;
  requestEmployeeIds: string[];
}) {
  const dispatch = useDispatch<AppDispatch>();
  const [tick, setTick] = useState(0); // force re-read from storage
  const [filter, setFilter] = useState<"all" | "draft" | "pending" | "approved" | "rejected">("all");
  const [activeSection, setActiveSection] = useState<SelfSection | "">("");
  const [formValue, setFormValue] = useState<any>(null);
  const [supportingDoc, setSupportingDoc] = useState<UploadedFile | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingDraftId, setEditingDraftId] = useState<string | null>(null);
  const [expandedRequest, setExpandedRequest] = useState<string | null>(null);

  const allRequests: ProfileChangeRequest[] = useMemo(() => {
    return getChangeRequests(requestEmployeeIds);
  }, [requestEmployeeIds, tick]);

  const filtered = useMemo(() => {
    if (filter === "all") return allRequests;
    return allRequests.filter((r) => r.status === filter);
  }, [filter, allRequests]);

  const counts = useMemo(() => ({
    total: allRequests.length,
    draft: allRequests.filter((r) => r.status === "draft").length,
    pending: allRequests.filter((r) => r.status === "pending").length,
    approved: allRequests.filter((r) => r.status === "approved").length,
    rejected: allRequests.filter((r) => r.status === "rejected").length,
  }), [allRequests]);

  const openSection = (section: SelfSection) => {
    // Check if there's already a pending request for this section
    const sectionKey = sectionToStorageKey[section];
    const hasPending = allRequests.some((r) => r.section === sectionKey && r.status === "pending");
    // Allow education edits even if there's a pending request — users can create additional change requests for education
    if (hasPending && section !== "education") {
      dispatch(addNotification({ type: "warning", message: "A pending request already exists for this section. Wait for admin review." }));
      return;
    }
    // Check if there's a draft to resume
    const existingDraft = allRequests.find((r) => r.section === sectionKey && r.status === "draft");
    setActiveSection(section);
    setSupportingDoc(null);
    if (existingDraft) {
      setEditingDraftId(existingDraft.id);
      setFormValue(existingDraft.changes.newValue);
    } else {
      setEditingDraftId(null);
      setFormValue(buildInitialValue(section, employee));
    }
  };

  const closeForm = () => {
    setActiveSection("");
    setFormValue(null);
    setSupportingDoc(null);
    setEditingDraftId(null);
  };

  const handleSaveDraft = async () => {
    if (!activeSection) return;
    const sectionKey = sectionToStorageKey[activeSection];
    if (!sectionKey) return;
    setIsSaving(true);
    try {
      saveDraftChangeRequest({
        employeeId: employee.id,
        section: sectionKey,
        newValue: formValue,
        supportingDoc: supportingDoc ?? undefined,
      });
      dispatch(addNotification({ type: "info", message: "Draft saved. You can continue editing later." }));
      setTick((t) => t + 1);
      const draft = getChangeRequests(employee.id).find((r) => r.section === sectionKey && r.status === "draft");
      if (draft) setEditingDraftId(draft.id);
    } catch (err: any) {
      dispatch(addNotification({ type: "error", message: err?.message ?? "Failed to save draft." }));
    } finally {
      setIsSaving(false);
    }
  };

  const handleSubmit = async () => {
    if (!activeSection) return;
    const sectionKey = sectionToStorageKey[activeSection];
    if (!sectionKey) return;

    // Bank validation
    if (activeSection === "bank" && !supportingDoc) {
      dispatch(addNotification({ type: "warning", message: "Please upload a supporting document before submitting Bank / PF / ESI changes." }));
      return;
    }

    setIsSubmitting(true);
    try {
      // First save draft with current state
      const saved = saveDraftChangeRequest({
        employeeId: employee.id,
        section: sectionKey,
        newValue: formValue,
        supportingDoc: supportingDoc ?? undefined,
      });
      // Then submit it
      submitDraftChangeRequest(saved.id);
      dispatch(addNotification({ type: "success", message: "Request submitted successfully. Pending admin review." }));
      setTick((t) => t + 1);
      closeForm();
    } catch (err: any) {
      dispatch(addNotification({ type: "error", message: err?.message ?? "Failed to submit request." }));
    } finally {
      setIsSubmitting(false);
    }
  };

  const resumeDraft = (request: ProfileChangeRequest) => {
    const selfSection = Object.entries(sectionToStorageKey).find(([, v]) => v === request.section)?.[0] as SelfSection | undefined;
    if (!selfSection) return;
    setActiveSection(selfSection);
    setEditingDraftId(request.id);
    setFormValue(request.changes.newValue);
    setSupportingDoc(request.supportingDoc ?? null);
  };

  const renderForm = () => {
    if (!activeSection || formValue === null) return null;
    switch (activeSection) {
      case "profile": return <ProfileForm employee={employee} value={formValue} onChange={setFormValue} />;
      case "education": return <EducationForm employee={employee} value={formValue} onChange={setFormValue} />;
      case "family": return <FamilyForm employee={employee} value={formValue} onChange={setFormValue} />;
      case "nominee": return <NomineeForm employee={employee} value={formValue} onChange={setFormValue} />;
      case "insurance": return <InsuranceForm employee={employee} value={formValue} onChange={setFormValue} />;
      case "work": return <WorkExperienceForm employee={employee} value={formValue} onChange={setFormValue} />;
      case "bank": return <BankForm employee={employee} value={formValue} onChange={setFormValue} supportingDoc={supportingDoc} onSupportingDocChange={setSupportingDoc} />;
      case "passport": return <PassportForm employee={employee} value={formValue} onChange={setFormValue} />;
      case "documents": return <DocumentsForm employee={employee} value={formValue} onChange={setFormValue} />;
      default: return null;
    }
  };

  // Auto-open a section if triggered via global request (Request Change button)
  useEffect(() => {
    const pending = (window as any).__ess_open_request_for as SelfSection | undefined;
    if (pending) {
      // clear the global marker
      try { delete (window as any).__ess_open_request_for; } catch { (window as any).__ess_open_request_for = undefined; }
      openSection(pending);
    }
  }, []);

  const sectionLabel = activeSection ? menuItems.find((m) => m.id === activeSection)?.label : "";

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-foreground">My Request</h2>
        <p className="text-sm text-muted-foreground mt-0.5">Submit and track profile update requests for admin approval.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-5">
        {([
          ["Total", counts.total, ""],
          ["Draft", counts.draft, "text-slate-600"],
          ["Pending", counts.pending, "text-amber-600"],
          ["Approved", counts.approved, "text-emerald-600"],
          ["Rejected", counts.rejected, "text-rose-600"],
        ] as const).map(([label, value, cls]) => (
          <div key={label} className="rounded-xl border border-border bg-card p-4">
            <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">{label}</p>
            <p className={`mt-1 text-2xl font-black text-foreground ${cls}`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Create New Request */}
      {!activeSection && (
        <div className="rounded-xl border border-border bg-card p-5 space-y-4">
          <div>
            <h3 className="text-sm font-bold text-foreground">Create New Update Request</h3>
            <p className="text-xs text-muted-foreground mt-0.5">Select a section to modify and submit for admin approval.</p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {EDITABLE_SECTIONS.map((sec) => {
              const item = menuItems.find((m) => m.id === sec)!;
              const Icon = item.icon;
              const sKey = sectionToStorageKey[sec];
              const hasDraft = allRequests.some((r) => r.section === sKey && r.status === "draft");
              const hasPending = allRequests.some((r) => r.section === sKey && r.status === "pending");
              // Education should not be blocked by pending requests
              const isBlocked = hasPending && sec !== "education";
              return (
                <button
                  key={sec}
                  onClick={() => openSection(sec)}
                  disabled={isBlocked}
                  className={`flex flex-col items-start gap-2 rounded-xl border p-4 text-left transition-all ${isBlocked
                    ? "border-border bg-secondary/20 opacity-60 cursor-not-allowed"
                    : "border-border bg-card hover:border-foreground/30 hover:bg-secondary/30 cursor-pointer"
                    }`}
                >
                  <div className="flex items-center justify-between w-full">
                    <Icon className="h-4 w-4 text-muted-foreground" />
                    {hasDraft && (
                      <span className="rounded-full bg-slate-100 border border-slate-200 text-slate-600 text-[9px] font-bold px-1.5 py-0.5 uppercase tracking-wider">Draft</span>
                    )}
                    {isBlocked && (
                      <Lock className="h-3.5 w-3.5 text-amber-500" />
                    )}
                  </div>
                  <span className="text-xs font-bold text-foreground leading-snug">{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Edit Form */}
      {activeSection && formValue !== null && (
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          {/* Form header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-border bg-secondary/20">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-foreground flex items-center justify-center">
                <Edit2 className="h-4 w-4 text-primary-foreground" />
              </div>
              <div>
                <p className="text-sm font-bold text-foreground">Editing: {sectionLabel}</p>
                {editingDraftId && (
                  <p className="text-[10px] text-muted-foreground font-medium">Resuming draft • changes saved automatically when you save draft</p>
                )}
              </div>
            </div>
            <button onClick={closeForm} className="h-8 w-8 flex items-center justify-center rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors">
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Form body */}
          <div className="p-5">
            {renderForm()}
          </div>

          {/* Form actions */}
          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border px-5 py-4 bg-secondary/10">
            <button
              type="button"
              onClick={handleSaveDraft}
              disabled={isSaving}
              className="h-10 rounded-lg border border-border bg-card px-5 text-xs font-bold text-foreground hover:bg-secondary transition-colors disabled:opacity-50"
            >
              {isSaving ? "Saving..." : "Save as Draft"}
            </button>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={closeForm}
                className="h-10 rounded-lg border border-border px-4 text-xs font-bold text-muted-foreground hover:bg-secondary transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="inline-flex items-center gap-2 h-10 rounded-lg bg-foreground text-primary-foreground px-5 text-xs font-bold hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                <Send className="h-3.5 w-3.5" />
                {isSubmitting ? "Submitting..." : "Submit Request"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Requests list */}
      <div className="space-y-3">
        <div className="flex flex-wrap gap-2">
          {(["all", "draft", "pending", "approved", "rejected"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`h-8 rounded-lg border px-4 text-xs font-bold capitalize transition-colors ${filter === f
                ? "border-foreground bg-foreground text-primary-foreground"
                : "border-border bg-card text-muted-foreground hover:bg-secondary hover:text-foreground"
                }`}
            >
              {f} {f === "all" ? `(${counts.total})` : `(${counts[f]})`}
            </button>
          ))}
        </div>

        {filtered.length === 0 ? (
          <div className="rounded-xl border border-dashed border-border bg-card p-10 text-center text-sm text-muted-foreground">
            No requests found.
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((request) => (
              <RequestCard
                key={request.id}
                request={request}
                isExpanded={expandedRequest === request.id}
                onToggle={() => setExpandedRequest(expandedRequest === request.id ? null : request.id)}
                onResumeDraft={resumeDraft}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Request Card ────────────────────────────────────────────────────────── */
function RequestCard({
  request,
  isExpanded,
  onToggle,
  onResumeDraft,
}: {
  request: ProfileChangeRequest;
  isExpanded: boolean;
  onToggle: () => void;
  onResumeDraft: (r: ProfileChangeRequest) => void;
}) {
  return (
    <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden">
      {/* Header */}
      <button
        className="flex w-full items-center justify-between gap-3 px-5 py-4 hover:bg-secondary/20 transition-colors text-left"
        onClick={onToggle}
      >
        <div className="flex items-center gap-3 min-w-0">
          <div className="shrink-0">
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            )}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-bold text-foreground truncate">{request.section_label}</p>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              {new Date(request.created_at).toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {request.status === "draft" && (
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); onResumeDraft(request); }}
              className="inline-flex items-center gap-1.5 h-7 rounded-lg border border-border bg-card px-3 text-[10px] font-bold text-foreground hover:bg-secondary transition-colors"
            >
              <Edit2 className="h-3 w-3" /> Resume
            </button>
          )}
          <span className={`rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-wider ${requestStatusColors[request.status] ?? ""}`}>
            {request.status}
          </span>
        </div>
      </button>

      {/* Expanded diff */}
      {isExpanded && (
        <div className="border-t border-border px-5 py-4 space-y-4 bg-secondary/5">
          <ChangeDiff oldValue={request.changes.oldValue} newValue={request.changes.newValue} />
          {request.supportingDoc && (
            <div className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-xs font-medium text-foreground">
              <Paperclip className="h-3.5 w-3.5 text-muted-foreground" />
              <span>Supporting Doc: {request.supportingDoc.fileName}</span>
              <span className="text-muted-foreground text-[10px] ml-auto">
                {new Date(request.supportingDoc.uploadedAt).toLocaleDateString("en-IN")}
              </span>
            </div>
          )}
          {request.rejection_comment && (
            <div className="rounded-lg bg-rose-50/60 border border-rose-100 p-3 text-xs">
              <p className="font-bold text-rose-700">Rejection Reason:</p>
              <p className="text-rose-600 mt-1">{request.rejection_comment}</p>
            </div>
          )}
          {request.status === "approved" && (
            <div className="flex items-center gap-2 text-emerald-700 text-xs font-medium">
              <Check className="h-4 w-4" />
              Approved by {request.reviewed_by ?? "Admin"} on{" "}
              {request.reviewed_at ? new Date(request.reviewed_at).toLocaleDateString("en-IN") : "—"}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ─── Diff viewer ─────────────────────────────────────────────────────────── */
function flattenObject(obj: any, prefix = ""): Record<string, string> {
  if (typeof obj !== "object" || obj === null) return { [prefix]: String(obj ?? "") };
  const result: Record<string, string> = {};
  for (const key of Object.keys(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    const val = obj[key];
    if (typeof val === "object" && val !== null && !Array.isArray(val)) {
      Object.assign(result, flattenObject(val, fullKey));
    } else if (Array.isArray(val)) {
      val.forEach((item, i) => Object.assign(result, flattenObject(item, `${fullKey}[${i}]`)));
    } else {
      result[fullKey] = String(val ?? "");
    }
  }
  return result;
}

function ChangeDiff({ oldValue, newValue }: { oldValue: unknown; newValue: unknown }) {
  const rows = useMemo(() => {
    const oldFlat = flattenObject(oldValue as any);
    const newFlat = flattenObject(newValue as any);
    const allKeys = new Set([...Object.keys(oldFlat), ...Object.keys(newFlat)]);
    return Array.from(allKeys)
      .filter((k) => !k.startsWith("_") && oldFlat[k] !== newFlat[k])
      .map((k) => ({ field: k, old: oldFlat[k] ?? "—", new: newFlat[k] ?? "—" }));
  }, [oldValue, newValue]);

  if (rows.length === 0) {
    return <p className="text-xs text-muted-foreground italic">No field-level changes detected.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-xs">
        <thead className="bg-secondary/60">
          <tr>
            <th className="text-left p-2.5 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Field</th>
            <th className="text-left p-2.5 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Previous Value</th>
            <th className="text-left p-2.5 font-bold text-foreground uppercase tracking-wider text-[10px]">Requested Value</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border/60">
          {rows.map((row) => (
            <tr key={row.field}>
              <td className="p-2.5 font-medium text-foreground font-mono text-[11px]">{row.field}</td>
              <td className="p-2.5 text-muted-foreground">{String(row.old).startsWith("data:") ? "[file]" : (row.old || "—")}</td>
              <td className="p-2.5 text-foreground font-semibold">{String(row.new).startsWith("data:") ? "[file]" : (row.new || "—")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* ─── Main page ───────────────────────────────────────────────────────────── */

export function SelfProfileInformationPage() {
  const { user } = useAuth();
  const [activeSection, setActiveSection] = useState<SelfSection>("profile");
  const dispatch = useDispatch<AppDispatch>();
  const [ack, setAck] = useState(false);
  const [localSubmitted, setLocalSubmitted] = useState(false);

  const { data: employee, isLoading, isError, error, refetch } = useMyEmployeeModuleProfile();

  useEffect(() => {
    if (employee) cacheEmployeeInRedux(dispatch, employee);
  }, [dispatch, employee]);

  const requestEmployeeIds = useMemo(
    () => (employee ? employeeIdAliases(employee, user) : []),
    [employee, user],
  );

  const employeeId = employee?.id;

  const isProfileFinalSubmitted = useMemo(() => {
    if (localSubmitted) return true;
    if (employee?.profileLocked) return true;
    return false;
  }, [localSubmitted, employee?.profileLocked]);

  // Listen for request-change events fired by EditableSectionCard
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail as any;
      const sectionId: string = detail?.sectionId;
      if (!sectionId) return;
      let mapped: SelfSection | undefined;
      if (sectionId.startsWith('profile')) mapped = 'profile';
      else if (sectionId.startsWith('education')) mapped = 'education';
      else if (sectionId.startsWith('family')) mapped = 'family';
      else if (sectionId.startsWith('nominee')) mapped = 'nominee';
      else if (sectionId.startsWith('insurance')) mapped = 'insurance';
      else if (sectionId.startsWith('work')) mapped = 'work';
      else if (sectionId.startsWith('bank')) mapped = 'bank';
      else if (sectionId.startsWith('passport')) mapped = 'passport';
      else if (sectionId.startsWith('documents')) mapped = 'documents';
      else mapped = 'profile';

      (window as any).__ess_open_request_for = mapped;
      setActiveSection('myRequest');
    };
    window.addEventListener('ess:request_change', handler as EventListener);
    return () => window.removeEventListener('ess:request_change', handler as EventListener);
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center p-6 text-sm text-muted-foreground">
        Loading profile…
      </div>
    );
  }

  if (isError || !employee) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 p-6 text-center">
        <p className="text-sm font-semibold text-foreground">Unable to load profile</p>
        <p className="text-xs text-muted-foreground max-w-md">
          {(error as Error)?.message ?? "Connect to the HRMS API and ensure your account is linked to an employee record."}
        </p>
        <button
          type="button"
          onClick={() => refetch()}
          className="rounded-lg border border-border px-3 py-1.5 text-xs font-bold hover:bg-secondary"
        >
          Retry
        </button>
      </div>
    );
  }

  const activeLabel = menuItems.find((item) => item.id === activeSection)?.label ?? "Employee Profile";

  // Keep these sections visible in the main view (render ContentSection)
  // but they remain non-editable via My Request (not listed in EDITABLE_SECTIONS).
  const isReadOnlySection = false;
  const isMyRequest = activeSection === "myRequest";

  return (
    <EmployeeFormProvider value={{ finalSubmitted: isProfileFinalSubmitted, essReadOnly: isProfileFinalSubmitted }}>
    <div className="flex h-full flex-col bg-background">
      {/* Top bar */}
      <div className="flex flex-shrink-0 items-center justify-between border-b border-border bg-card px-6 py-3">
        <div className="flex flex-wrap items-center gap-1.5 text-sm text-muted-foreground">
          <span className="font-medium">My Profile</span>
          <span className="text-border">/</span>
          <span className="font-semibold text-foreground">{employee.name}</span>
          <span className="text-border">/</span>
          <span className="rounded-md border border-border bg-secondary px-2.5 py-0.5 text-xs font-semibold text-foreground">{activeLabel}</span>
        </div>
        <div className="flex items-center gap-4">
          {!isProfileFinalSubmitted ? (
            <>
              <div className="flex items-center gap-2">
                <input
                  id="final-ack"
                  type="checkbox"
                  checked={ack}
                  onChange={(e) => setAck(e.target.checked)}
                  className="h-4 w-4 rounded border-border"
                />
                <label htmlFor="final-ack" className="text-xs text-muted-foreground">
                  I understand I cannot directly edit after final submission.
                </label>
              </div>
              <button
                type="button"
                onClick={async () => {
                  if (!ack) {
                    dispatch(addNotification({ type: "warning", message: "Please acknowledge before final submission." }));
                    return;
                  }
                  if (isProfileFinalSubmitted) return;
                  try {
                    const updatedAdmin = { ...employee, profileLocked: true };
                    dispatch(updateAdminEmployee(updatedAdmin));
                    const profile = ensureProfile(employee.id);
                    await dispatch(
                      saveEssProfileWithAdminSync({
                        employeeId: employee.id,
                        profile: { ...profile, profileLocked: true },
                      }) as any,
                    );
                    setLocalSubmitted(true);
                    dispatch(addNotification({ type: "success", message: "Profile final submitted. Use My Request for future updates." }));
                  } catch {
                    dispatch(addNotification({ type: "error", message: "Failed to finalize profile submission." }));
                  }
                }}
                className="inline-flex items-center gap-2 h-9 px-3 rounded-lg text-xs font-bold bg-foreground text-primary-foreground hover:opacity-95 transition-opacity"
              >
                Final Submit
              </button>
            </>
          ) : (
            !isMyRequest && (
              <button
                type="button"
                onClick={() => setActiveSection("myRequest")}
                className="inline-flex items-center gap-2 h-9 px-3 rounded-lg border border-border text-xs font-bold hover:bg-secondary transition-colors"
              >
                <Send className="h-3.5 w-3.5" />
                Update via My Request
              </button>
            )
          )}
          <span className={`rounded-md px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest ${statusStyle[employee.status] ?? "bg-secondary text-muted-foreground"}`}>
            {employee.status}
          </span>
        </div>
      </div>

      <div className="relative flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-60 min-w-[240px] flex-shrink-0 overflow-y-auto border-r border-border bg-card">
          <div className="px-3 py-5">
            <p className="px-3 pb-3 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
              Employee Sections
            </p>
            <nav className="space-y-0.5">
              {menuItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeSection === item.id;
                // Do not show lock icon in the sidebar — keep items visible without a lock
                const isLocked = false;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    className={`relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium transition-all ${isActive
                      ? "bg-secondary font-semibold text-foreground"
                      : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                      }`}
                  >
                    {isActive && <span className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-r-full bg-foreground" />}
                    <Icon className="h-4 w-4 flex-shrink-0" />
                    <span className="truncate flex-1">{item.label}</span>
                    {isLocked && <Lock className="h-3 w-3 text-muted-foreground/50 shrink-0" />}
                    {isActive && <span className="h-1.5 w-1.5 flex-shrink-0 rounded-full bg-foreground" />}
                  </button>
                );
              })}
            </nav>
          </div>
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto p-6">
          {isMyRequest ? (
            <MyRequestSection employee={employee} requestEmployeeIds={requestEmployeeIds} />
          ) : isReadOnlySection ? (
            <div className="rounded-xl border border-border bg-card p-8 text-center space-y-3">
              <Lock className="h-8 w-8 mx-auto text-muted-foreground/40" />
              <p className="text-base font-semibold text-foreground">{activeLabel}</p>
              <p className="text-sm text-muted-foreground max-w-sm mx-auto">
                This section is managed by your administrator and cannot be updated via My Request.
              </p>
            </div>
          ) : activeSection === "profile" ? (
            <EssEmployeeProfile employee={employee} />
          ) : (
            <div className="space-y-4">
              {isProfileFinalSubmitted && (
                <div className="rounded-xl border border-border bg-secondary/30 px-4 py-3 text-sm text-muted-foreground">
                  Your profile has been submitted. To update information, open{" "}
                  <button type="button" onClick={() => setActiveSection("myRequest")} className="font-semibold text-foreground underline underline-offset-2 hover:opacity-80">
                    My Request
                  </button>{" "}
                  and submit changes for admin approval.
                </div>
              )}
              <ContentSection
                employee={employee}
                activeSection={activeSection}
                essReadOnly={isProfileFinalSubmitted}
                showAssetAccessActions={false}
                showSalaryActions={false}
                showAddButtons={!isProfileFinalSubmitted}
                isFinalSubmitted={isProfileFinalSubmitted}
              />
            </div>
          )}
        </main>
      </div>
    </div>
    </EmployeeFormProvider>
  );
}
