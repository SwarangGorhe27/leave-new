import {
  useState,
  useEffect,
  useCallback,
  useRef,
  type ReactNode,
  type InputHTMLAttributes,
  type SelectHTMLAttributes,
  type ElementType,
  type FormEvent,
} from "react";
import { useNavigate } from "react-router";
import { useDispatch } from "react-redux";
import { addAdminEmployee } from "@/store/slices/adminSlice";
import { Employee, normalizeLegacyEmployee } from "@/app/components/employees/mockData";
import {
  createEmployee,
  saveDraft,
  type AddEmployeePayload,
  type AddEmployeeResponse,
} from "@/api/addEmployeeApi";
import {
  User,
  Briefcase,
  Clock,
  CreditCard,
  Calendar,
  FileText,
  Shield,
  Search,
  Mail,
  Hash,
  Phone,
  MapPin,
  UserPlus,
  Building2,
  RefreshCw,
  Eye,
  EyeOff,
  Upload,
  X,
  Check,
  AlertCircle,
  CheckCircle,
  ChevronDown,
  Loader2,
  ArrowLeft,
  Save,
  ExternalLink,
  GraduationCap,
  Plus,
  Trash2,
  Monitor,
} from "lucide-react";
import { MasterSelect } from "@/app/components/ui/MasterSelect";
import { SearchableSelect } from "@/app/components/ui/SearchableSelect";
import {
  MasterDropdown,
  MasterMultiDropdown,
  MasterSearchableDropdown,
} from "@/app/components/ui/MasterDropdown";
import { BulkImportTab } from "./BulkImportTab";
import { useSystemRoles } from "@/app/hooks/useSystemRoles";
import { fetchManagers, type Manager } from "@/api/managersClient";

// ═══════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════

interface UploadedFile {
  name: string;
  size: number;
  type: string;
  url: string;
}

interface FormState {
  employeeSeries: string;
  employeeId: string;
  firstName: string;
  lastName: string;
  dob: string;
  aadhaarNumber: string;
  gender: string;
  reportingManager: string;
  status: string;
  joiningDate: string;
  referredBy: string;
  allowSelfFill: boolean;
  probationPeriod: string;
  probationUnit: string;
  email: string;
  phoneCode: string;
  phone: string;
  emergencyName: string;
  emergencyPhone: string;
  fathersName: string;
  spouseName: string;
  photo: UploadedFile | null;
  department: string;
  designation: string;
  employmentType: string;
  workLocation: string;
  shiftType: string;
  workStart: string;
  workEnd: string;
  weeklyOff: string[];
  trackingMode: string;
  salaryStructure: string;
  basicSalary: string;
  bankName: string;
  accountNumber: string;
  accountType: string;
  ifscCode: string;
  taxId: string;
  leavePolicy: string;
  annualLeave: string;
  sickLeave: string;
  username: string;
  password: string;
  role: string;
  sendInvite: boolean;
  salutation: string;
  attendanceSchemeId: string;
  shiftAssignmentId: string;
  assetCategory: string;
  assetCondition: string;
  assetName: string;
  assetId: string;
  serialNumber: string;
  assignDate: string;
  returnDate: string;
  assetStatus: string;
  assetRemarks: string;
  activeTab: "new" | "rehire" | "bulk";
  // NEW FIELDS
  bgcStatus: string;
  bgcAgency: string;
  bgcVerifiedBy: string;
  bgcReference: string;
  bgcRemarks: string;
  rehireDate: string;
  rehireRemarks: string;
  restoreSalary: boolean;
  restoreAssets: boolean;
  restoreLeaves: boolean;
}

type Errors = Partial<Record<keyof FormState, string>>;
type Touched = Partial<Record<keyof FormState, boolean>>;

// ═══════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════

const SECTIONS = [
  { id: "s-basic", label: "Basic Information", Icon: User },
  { id: "s-job", label: "Job Details", Icon: Briefcase },
  { id: "s-attendance", label: "Attendance Settings", Icon: Clock },
  // { id: "s-payroll", label: "Payroll Information", Icon: CreditCard },
  { id: "s-leave", label: "Leave Configuration", Icon: Calendar },
  { id: "s-background", label: "Background Check", Icon: Shield },
  { id: "s-assets", label: "Asset Management", Icon: Monitor },
  { id: "s-account", label: "Account Access", Icon: Shield },
];

const DEPTS = [
  "Engineering",
  "Product",
  "Design",
  "Marketing",
  "Sales",
  "Human Resources",
  "Finance",
  "Operations",
  "Legal",
];
const ROLES = [
  "Software Engineer",
  "Senior Software Engineer",
  "Engineering Manager",
  "Product Manager",
  "UX / UI Designer",
  "Marketing Specialist",
  "Sales Executive",
  "HR Business Partner",
  "Finance Analyst",
  "Operations Lead",
];
const SALARY_STRUCTS = ["Standard", "Senior", "Executive", "Contract", "Intern / Trainee"];
const LEAVE_POLICIES = [
  { v: "standard", l: "Standard Policy  — 24 AL + 12 SL" },
  { v: "senior", l: "Senior Policy    — 30 AL + 15 SL" },
  { v: "executive", l: "Executive Policy — 36 AL + 18 SL" },
  { v: "contract", l: "Contract Policy  — 14 AL + 7 SL" },
];
const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const PHONE_CODES = [
  { v: "+1", l: "+1  US" },
  { v: "+44", l: "+44 UK" },
  { v: "+91", l: "+91 IN" },
  { v: "+49", l: "+49 DE" },
  { v: "+33", l: "+33 FR" },
  { v: "+81", l: "+81 JP" },
  { v: "+86", l: "+86 CN" },
  { v: "+61", l: "+61 AU" },
  { v: "+65", l: "+65 SG" },
];

const SERIES = [
  { v: "EMP", l: "EMP - Standard" },
  { v: "TECH", l: "TECH - Technology" },
  { v: "SALES", l: "SALES - Sales" },
  { v: "HR", l: "HR - Human Resources" },
];

const GENDER_OPTS = [
  { v: "male", l: "Male" },
  { v: "female", l: "Female" },
  { v: "others", l: "Others" },
];

const genId = () => `EMP-${Math.floor(10000 + Math.random() * 90000)}`;
const genPwd = () => {
  const c = "ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789@#$!";
  return Array.from({ length: 14 }, () => c[Math.floor(Math.random() * c.length)]).join("");
};
const fmtSize = (b: number) =>
  b < 1024
    ? `${b} B`
    : b < 1048576
    ? `${(b / 1024).toFixed(1)} KB`
    : `${(b / 1048576).toFixed(1)} MB`;

const INIT: FormState = {
  employeeSeries: "EMP",
  employeeId: genId(),
  firstName: "",
  lastName: "",
  dob: "",
  aadhaarNumber: "",
  gender: "male",
  reportingManager: "",
  status: "active",
  joiningDate: "",
  referredBy: "",
  allowSelfFill: false,
  probationPeriod: "90",
  probationUnit: "days",
  
  email: "",
  phoneCode: "+91",
  phone: "",
  emergencyName: "",
  emergencyPhone: "",
  fathersName: "",
  spouseName: "",
  photo: null,
  department: "",
  designation: "",
  employmentType: "",
  workLocation: "",
  shiftType: "general",
  workStart: "09:00",
  workEnd: "18:00",
  weeklyOff: ["Saturday", "Sunday"],
  trackingMode: "biometric",
  salaryStructure: "",
  basicSalary: "",
  bankName: "",
  accountNumber: "",
  accountType: "",
  ifscCode: "",
  taxId: "",
  leavePolicy: "",
  annualLeave: "24",
  sickLeave: "12",
  username: "",
  password: "",
  role: "employee",
  sendInvite: true,
  salutation: "",
  attendanceSchemeId: "",
  shiftAssignmentId: "",
  assetCategory: "",
  assetCondition: "",
  assetName: "",
  assetId: "",
  serialNumber: "",
  assignDate: "",
  returnDate: "",
  assetStatus: "ASSIGNED",
  assetRemarks: "",
  activeTab: "new",
  rehireDate: "",
  rehireRemarks: "",
  restoreSalary: false,
  restoreAssets: false,
  restoreLeaves: false,
  bgcStatus: "",
  bgcAgency: "",
  bgcVerifiedBy: "",
  bgcReference: "",
  bgcRemarks: "",
};

// ═══════════════════════════════════════════════════════════
// PRIMITIVES
// ═══════════════════════════════════════════════════════════

function FF({
  label,
  icon,
  required,
  error,
  ok,
  hint,
  children,
  span2,
}: {
  label: string;
  icon?: ReactNode;
  required?: boolean;
  error?: string;
  ok?: boolean;
  hint?: string;
  children: ReactNode;
  span2?: boolean;
}) {
  const hasError = Boolean(error);
  return (
    <div className={span2 ? "sm:col-span-2" : ""}>
      <label
        className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider mb-2"
        style={{ color: hasError ? '#f70909' : undefined }}
      >
        {icon && (
          <span style={{ color: hasError ? '#f70909' : undefined }} className="shrink-0">
            {icon}
          </span>
        )}
        <span>
          {label}
          {required && <span className="ml-1" style={{ color: '#f70909' }}>*</span>}
        </span>
      </label>
      <div
        className={hasError ? "rounded-lg" : ""}
        style={
          hasError
            ? {
                border: '1px solid #f70909',
                backgroundColor: 'rgba(247,9,9,0.04)',
                boxShadow: '0 0 0 3px rgba(247,9,9,0.08)'
              }
            : undefined
        }
      >
        {children}
      </div>
      {error ? (
        <div className="flex items-center gap-1 mt-1.5 text-xs text-destructive font-medium">
          <AlertCircle size={14} strokeWidth={2} />
          <span>{error}</span>
        </div>
      ) : hint ? (
        <p className="mt-1.5 text-xs text-muted-foreground">{hint}</p>
      ) : null}
    </div>
  );
}

function Inp({
  err,
  success,
  icon,
  wfull = true,
  ...p
}: InputHTMLAttributes<HTMLInputElement> & {
  err?: boolean;
  success?: boolean;
  icon?: ReactNode;
  wfull?: boolean;
}) {
  return (
    <div className="relative">
      {icon && (
        <div className="form-control-icon-left">
          {icon}
        </div>
      )}
      <input
        className={[
          "form-control",
          wfull ? "w-full" : "",
          icon ? "form-control--icon-left" : "",
          err ? "form-control--error" : "",
          success && !err ? "form-control--success border-success" : "",
          p.readOnly ? "opacity-60 cursor-not-allowed" : "",
        ]
          .filter(Boolean)
          .join(" ")}
        {...p}
      />
      
    </div>
  );
}

function Sel({
  err,
  success,
  opts,
  ph,
  ...p
}: SelectHTMLAttributes<HTMLSelectElement> & {
  err?: boolean;
  success?: boolean;
  opts: { v: string; l: string }[];
  ph?: string;
}) {
  return (
    <div className="relative">
      <select
        className={[
          "form-control form-control--select",
          "w-full",
          err ? "form-control--error" : "",
          success && !err ? "form-control--success" : "",
        ]
          .filter(Boolean)
          .join(" ")}
        {...p}
      >
        {ph && <option value="">{ph}</option>}
        {opts.map((o) => (
          <option key={o.v} value={o.v}>
            {o.l}
          </option>
        ))}
      </select>
      
    </div>
  );
}

function MultiSel({
  opts,
  sel,
  onChange,
  ph = "Select…",
}: {
  opts: string[];
  sel: string[];
  onChange: (v: string[]) => void;
  ph?: string;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", h);
    return () => document.removeEventListener("mousedown", h);
  }, []);
  const toggle = (v: string) => onChange(sel.includes(v) ? sel.filter((s) => s !== v) : [...sel, v]);
  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flat-input w-full h-9 px-3 text-sm flex items-center justify-between gap-2 text-left"
      >
        <span className={`truncate ${sel.length ? "text-foreground" : "text-muted-foreground"}`}>
          {sel.length ? sel.join(", ") : ph}
        </span>
        <ChevronDown
          size={13}
          className={`text-muted-foreground shrink-0 transition-transform duration-150 ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>
      {open && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-lg z-50 py-1 overflow-hidden">
          {opts.map((o) => (
            <button
              key={o}
              type="button"
              onClick={() => toggle(o)}
              className="w-full px-3 py-2 text-sm flex items-center gap-2.5 hover:bg-secondary transition-colors text-left"
            >
              <span
                className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 transition-all ${
                  sel.includes(o) ? "bg-foreground border-foreground" : "border-border bg-card"
                }`}
              >
                {sel.includes(o) && (
                  <Check size={10} className="text-primary-foreground" strokeWidth={3} />
                )}
              </span>
              <span className="text-foreground">{o}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function PhoneInp({
  cc,
  ph,
  onCC,
  onPh,
  err,
}: {
  cc: string;
  ph: string;
  onCC: (v: string) => void;
  onPh: (v: string) => void;
  err?: boolean;
}) {
  return (
    <div className={`flex h-10 form-control overflow-hidden p-0 border border-border rounded-lg bg-card ${err ? "form-control--error border-destructive" : ""}`}>
      <select
        value={cc}
        onChange={(e) => onCC(e.target.value)}
        className="bg-secondary text-foreground text-xs px-2 border-r border-border appearance-none cursor-pointer focus:outline-none shrink-0 w-[76px] font-mono"
      >
        {PHONE_CODES.map((c) => (
          <option key={c.v} value={c.v}>
            {c.l}
          </option>
        ))}
      </select>
      <input
        type="tel"
        value={ph}
        onChange={(e) => onPh(e.target.value)}
        placeholder="Phone number"
        className="flex-1 px-3 text-sm bg-transparent focus:outline-none text-foreground placeholder:text-muted-foreground border-0"
      />
    </div>
  );
}

function MaskInp({
  val,
  onChange,
  ph = "••••••••",
}: {
  val: string;
  onChange: (v: string) => void;
  ph?: string;
}) {
  const [show, setShow] = useState(false);
  return (
    <div className="flex h-10 form-control overflow-hidden p-0 border border-border rounded-lg bg-card">
      <input
        type={show ? "text" : "password"}
        value={val}
        onChange={(e) => onChange(e.target.value)}
        placeholder={ph}
        className="flex-1 px-3 text-sm bg-transparent focus:outline-none text-foreground placeholder:text-muted-foreground font-mono border-0"
      />
      <button
        type="button"
        onClick={() => setShow(!show)}
        tabIndex={-1}
        className="w-10 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors shrink-0"
      >
        {show ? <EyeOff size={16} /> : <Eye size={16} />}
      </button>
    </div>
  );
}

function SearchSel({
  value,
  onChange,
  opts,
  ph = "Search…",
}: {
  value: string;
  onChange: (v: string) => void;
  opts: { v: string; l: string }[];
  ph?: string;
}) {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const ref = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const filtered = opts.filter((o) => o.l.toLowerCase().includes(q.toLowerCase()));
  const selected = opts.find((o) => o.v === value);

  useEffect(() => {
    const h = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
        setQ("");
      }
    };
    document.addEventListener("mousedown", h);
    return () => document.removeEventListener("mousedown", h);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => {
          setOpen(!open);
          setTimeout(() => inputRef.current?.focus(), 50);
          setQ("");
        }}
        className="form-control w-full flex items-center justify-between gap-2 text-left px-3"
      >
        <span className={selected ? "text-foreground truncate" : "text-muted-foreground"}>
          {selected?.l ?? ph}
        </span>
        <ChevronDown
          size={16}
          className={`text-muted-foreground shrink-0 transition-transform duration-150 ${
            open ? "rotate-180" : ""
          }`}
        />
      </button>
      {open && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-card dark:bg-slate-900 border border-border dark:border-slate-700 rounded-lg shadow-lg z-50 overflow-hidden">
          <div className="p-2 border-b border-border dark:border-slate-700">
            <div className="relative">
              <Search
                size={13}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground dark:text-slate-400 pointer-events-none"
              />
              <input
                ref={inputRef}
                type="text"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search managers…"
                className="w-full h-8 pl-9 pr-3 text-xs bg-background dark:bg-slate-800 rounded-md border border-border dark:border-slate-700 focus:outline-none focus:border-foreground/40 dark:focus:border-slate-500 text-foreground dark:text-white placeholder:text-muted-foreground dark:placeholder:text-slate-400"
              />
            </div>
          </div>
          <div className="max-h-44 overflow-y-auto py-1">
            {filtered.length === 0 ? (
              <p className="px-3 py-2.5 text-xs text-muted-foreground dark:text-slate-400">No results</p>
            ) : (
              filtered.map((o) => (
                <button
                  key={o.v}
                  type="button"
                  onClick={() => {
                    onChange(o.v);
                    setOpen(false);
                    setQ("");
                  }}
                  className={`w-full px-3 py-2 text-sm text-left transition-colors flex items-center gap-2 ${
                    value === o.v
                      ? "bg-secondary font-medium text-foreground"
                      : "hover:bg-secondary text-foreground"
                  }`}
                >
                  {value === o.v && (
                    <Check size={12} className="text-foreground shrink-0" strokeWidth={2.5} />
                  )}
                  <span className={value === o.v ? "" : "pl-[20px]"}>{o.l}</span>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function Toggle({
  on,
  setOn,
  label,
  desc,
}: {
  on: boolean;
  setOn: (v: boolean) => void;
  label: string;
  desc?: string;
}) {
  return (
    <div
      className="flex items-center justify-between gap-6 p-4 rounded-lg border border-border bg-secondary/30 cursor-pointer select-none"
      onClick={() => setOn(!on)}
    >
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground">{label}</p>
        {desc && <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{desc}</p>}
      </div>
      <div
        className={`relative shrink-0 w-10 rounded-full transition-colors duration-200 ${
          on ? "bg-foreground" : "bg-muted"
        }`}
        style={{ height: "22px" }}
      >
        <span
          className={`absolute top-[3px] left-[3px] w-4 h-4 rounded-full bg-card shadow transition-transform duration-200 ${
            on ? "translate-x-[18px]" : ""
          }`}
        />
      </div>
    </div>
  );
}

function FileUp({
  label,
  file,
  onChange,
  accept = "*",
}: {
  label: string;
  file: UploadedFile | null;
  onChange: (f: UploadedFile | null) => void;
  accept?: string;
}) {
  const [drag, setDrag] = useState(false);
  const ref = useRef<HTMLInputElement>(null);
  const handle = (f: File) => {
    const url = URL.createObjectURL(f);
    onChange({ name: f.name, size: f.size, type: f.type, url });
  };

  if (file)
    return (
      <div className="flex items-center gap-3 p-3 rounded-lg border border-border bg-card">
        <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center shrink-0">
          <FileText size={14} className="text-muted-foreground" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-foreground truncate">{file.name}</p>
          <p className="text-[11px] text-green-600 flex items-center gap-1 mt-0.5">
            <CheckCircle size={10} strokeWidth={2.5} />
            {fmtSize(file.size)} · Uploaded
          </p>
        </div>
        <button
          type="button"
          onClick={() => onChange(null)}
          className="w-6 h-6 rounded-md border border-border flex items-center justify-center hover:bg-secondary transition-colors shrink-0"
        >
          <X size={11} className="text-muted-foreground" />
        </button>
      </div>
    );

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-5 text-center cursor-pointer transition-all duration-150 ${
        drag
          ? "border-foreground bg-secondary/60 scale-[0.99]"
          : "border-border hover:border-muted hover:bg-secondary/20"
      }`}
      onDragOver={(e) => {
        e.preventDefault();
        setDrag(true);
      }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDrag(false);
        const f = e.dataTransfer.files[0];
        if (f) handle(f);
      }}
      onClick={() => ref.current?.click()}
    >
      <input
        ref={ref}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) handle(f);
        }}
      />
      <Upload size={16} className="mx-auto mb-2 text-muted-foreground" />
      <p className="text-xs text-foreground">
        <span className="font-semibold">Click to upload</span>
        <span className="text-muted-foreground"> or drag & drop</span>
      </p>
      <p className="text-[11px] text-muted-foreground mt-1">{label}</p>
    </div>
  );
}

function PhotoUp({
  file,
  onChange,
}: {
  file: UploadedFile | null;
  onChange: (f: UploadedFile | null) => void;
}) {
  const [drag, setDrag] = useState(false);
  const ref = useRef<HTMLInputElement>(null);
  const handle = (f: File) => {
    const url = URL.createObjectURL(f);
    onChange({ name: f.name, size: f.size, type: f.type, url });
  };
  return (
    <div className="flex items-center gap-5">
      <div
        className={`relative w-[80px] h-[80px] rounded-xl overflow-hidden cursor-pointer shrink-0 border-2 transition-all duration-150 ${
          file
            ? "border-border"
            : `border-dashed ${drag ? "border-foreground" : "border-border hover:border-muted"}`
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          const f = e.dataTransfer.files[0];
          if (f) handle(f);
        }}
        onClick={() => ref.current?.click()}
      >
        {file ? (
          <img src={file.url} alt="Profile preview" className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-secondary/50">
            <User size={26} className="text-muted-foreground" />
          </div>
        )}
        <input
          ref={ref}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handle(f);
          }}
        />
      </div>
      <div>
        <button
          type="button"
          onClick={() => ref.current?.click()}
          className="text-sm font-semibold text-foreground hover:text-muted-foreground transition-colors underline-offset-2 hover:underline"
        >
          {file ? "Change photo" : "Upload photo"}
        </button>
        <p className="text-xs text-muted-foreground mt-1">
          JPG or PNG · Recommended 400×400 px · Max 2 MB
        </p>
        {file && (
          <button
            type="button"
            onClick={() => onChange(null)}
            className="mt-1.5 text-xs text-red-500 hover:text-red-600 transition-colors flex items-center gap-1"
          >
            <X size={10} />
            Remove photo
          </button>
        )}
      </div>
    </div>
  );
}

// Section card wrapper
function SC({
  id,
  n,
  title,
  desc,
  Icon,
  children,
}: {
  id: string;
  n: number;
  title: string;
  desc: string;
  Icon: ElementType;
  children: ReactNode;
}) {
  return (
    <section id={id} className="flat-card bg-card p-6 scroll-mt-4">
      <div className="flex items-start gap-4 pb-5 mb-6 border-b border-border">
        <div className="w-10 h-10 rounded-xl bg-foreground flex items-center justify-center shrink-0">
          <Icon size={16} className="text-primary-foreground" />
        </div>
        <div>
          <h2 className="text-[15px] font-semibold text-foreground mt-0.5 leading-snug">{title}</h2>
          <p className="text-xs text-muted-foreground mt-0.5">{desc}</p>
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-5">{children}</div>
    </section>
  );
}

// Segment button group
function Segs({ opts, val, set }: { opts: string[]; val: string; set: (v: string) => void }) {
  return (
    <div className="flex gap-2 flex-wrap">
      {opts.map((o) => (
        <button
          key={o}
          type="button"
          onClick={() => set(o)}
          className={`h-9 px-4 rounded-lg text-sm font-medium transition-all border capitalize ${
            val === o
              ? "bg-foreground text-primary-foreground border-foreground"
              : "border-border text-muted-foreground hover:text-foreground hover:border-muted"
          }`}
        >
          {o}
        </button>
      ))}
    </div>
  );
}

function Radio({
  opts,
  val,
  set,
  name,
}: {
  opts: { v: string; l: string }[];
  val: string;
  set: (v: string) => void;
  name: string;
}) {
  return (
    <div className="flex items-center gap-6 h-9">
      {opts.map((o) => (
        <label key={o.v} className="flex items-center gap-2.5 cursor-pointer group">
          <div className="relative flex items-center justify-center">
            <input
              type="radio"
              name={name}
              value={o.v}
              checked={val === o.v}
              onChange={() => set(o.v)}
              className="sr-only"
            />
            <div
              className={`w-4 h-4 rounded-full border transition-all duration-150 ${
                val === o.v
                  ? "border-foreground bg-foreground shadow-[0_0_0_3px_rgba(0,0,0,0.05)]"
                  : "border-border bg-card group-hover:border-muted-foreground"
              }`}
            />
            {val === o.v && <div className="w-1.5 h-1.5 rounded-full bg-primary-foreground absolute" />}
          </div>
          <span className="text-sm text-foreground font-medium">{o.l}</span>
        </label>
      ))}
    </div>
  );
}

function CheckInput({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-3 p-3 rounded-lg border border-border bg-secondary/20 hover:bg-secondary/40 transition-colors cursor-pointer group">
      <div className="relative flex items-center justify-center">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          className="sr-only"
        />
        <div
          className={`w-5 h-5 rounded border transition-all duration-150 ${
            checked ? "bg-foreground border-foreground" : "border-border bg-card group-hover:border-muted-foreground"
          }`}
        />
        {checked && (
          <CheckCircle size={14} className="text-primary-foreground absolute" strokeWidth={3} />
        )}
      </div>
      <span className="text-sm font-medium text-foreground">{label}</span>
    </label>
  );
}

// Section nav
function SectionNav({ active, onSelect }: { active: string; onSelect: (id: string) => void }) {
  return (
    <aside className="hidden lg:block w-[200px] shrink-0 relative">
      <div className="sticky top-6 z-20 space-y-4">
        <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-[0.14em] px-2 mb-3">
          Form Sections
        </p>
        <nav className="flex flex-col gap-0.5">
          {SECTIONS.map(({ id, label, Icon }) => {
            const isActive = active === id;
            return (
              <a
                key={id}
                href={`#${id}`}
                onClick={(e) => {
                  e.preventDefault();
                  onSelect(id);
                  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
                }}
                className={`flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? "bg-foreground text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                }`}
              >
                <span
                  className={`w-[24px] h-[24px] rounded flex items-center justify-center text-[12px] font-medium shrink-0 ${
                    isActive ? "bg-white/10 text-primary-foreground" : "text-muted-foreground"
                  }`}
                >
                  <Icon size={14} />
                </span>
                <span className="truncate">{label}</span>
              </a>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}

// Mock data for former employees
const FORMER_EMPLOYEES = [
  { id: "EMP-10204", name: "Sarah Jenkins", email: "sarah.j@company.com", phone: "9876543210", dept: "Engineering", desig: "Senior Dev", lastWorking: "2024-01-15", reason: "Resigned" },
  { id: "EMP-10355", name: "Michael Chen", email: "m.chen@company.com", phone: "9822334455", dept: "Marketing", desig: "Manager", lastWorking: "2023-11-30", reason: "Relieved" },
  { id: "EMP-09882", name: "Priya Sharma", email: "priya.s@company.com", phone: "9000111222", dept: "HR", desig: "Generalist", lastWorking: "2024-03-20", reason: "Separated" },
];

function RehireSearch({ onSelect }: { onSelect: (emp: any) => void }) {
  const [q, setQ] = useState("");
  const filtered = FORMER_EMPLOYEES.filter(e => 
    e.name.toLowerCase().includes(q.toLowerCase()) || 
    e.id.toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flat-card p-6 border-indigo-500/20 bg-indigo-500/5">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
            <Search size={20} />
          </div>
          <div>
            <h3 className="text-sm font-black text-foreground">Find Former Employee</h3>
            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Search by ID, Name, Email or Mobile</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <Inp 
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Start typing name or employee ID..."
              icon={<Search size={14} />}
            />
          </div>
          <Sel ph="All Departments" opts={[{ v: "eng", l: "Engineering" }, { v: "mkt", l: "Marketing" }]} />
          <Sel ph="All Reasons" opts={[{ v: "res", l: "Resigned" }, { v: "term", l: "Terminated" }]} />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {filtered.map(emp => (
          <button
            key={emp.id}
            type="button"
            onClick={() => onSelect(emp)}
            className="group flex items-center justify-between p-4 rounded-2xl border border-border bg-card hover:border-indigo-500/50 hover:bg-indigo-500/[0.02] hover:shadow-xl hover:shadow-indigo-500/5 transition-all duration-300 text-left"
          >
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-secondary flex items-center justify-center text-xs font-black text-muted-foreground group-hover:bg-indigo-500 group-hover:text-white transition-colors">
                {emp.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-black text-foreground">{emp.name}</span>
                  <span className="text-[9px] font-black px-1.5 py-0.5 rounded bg-secondary text-muted-foreground uppercase tracking-widest">{emp.id}</span>
                </div>
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-[10px] font-bold text-muted-foreground">{emp.desig} · {emp.dept}</span>
                  <span className="w-1 h-1 rounded-full bg-border" />
                  <span className="text-[10px] font-bold text-indigo-500">Last Day: {emp.lastWorking}</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
               <div className="text-right hidden sm:block">
                 <p className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Reason</p>
                 <p className="text-[11px] font-black text-foreground mt-0.5">{emp.reason}</p>
               </div>
               <div className="w-8 h-8 rounded-full border border-border flex items-center justify-center text-muted-foreground group-hover:text-indigo-500 group-hover:border-indigo-500/30 group-hover:bg-indigo-500/10 transition-all">
                 <Plus size={16} />
               </div>
            </div>
          </button>
        ))}
        {filtered.length === 0 && (
          <div className="p-12 text-center border-2 border-dashed border-border rounded-3xl">
            <User size={32} className="mx-auto mb-3 text-muted-foreground/30" />
            <p className="text-sm font-bold text-muted-foreground">No former employees found matching your search.</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// SYSTEM ROLE SELECT — fetches live from /api/security/rbac/roles/
// ═══════════════════════════════════════════════════════════

function SystemRoleSelect({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  const { data: roles = [], isLoading, isError } = useSystemRoles();

  if (isLoading) {
    return (
      <div className="form-control w-full flex items-center gap-2 text-muted-foreground text-sm">
        <Loader2 size={13} className="animate-spin shrink-0" />
        Loading roles…
      </div>
    );
  }

  if (isError) {
    return (
      <div className="form-control w-full flex items-center gap-2 text-destructive text-sm">
        <AlertCircle size={13} className="shrink-0" />
        Failed to load roles
      </div>
    );
  }

  return (
    <Sel
      value={value}
      onChange={(e) => onChange(e.target.value)}
      opts={roles}
      ph="Select role"
    />
  );
}

// ═══════════════════════════════════════════════════════════
// MAIN PAGE
// ═══════════════════════════════════════════════════════════

export function AddEmployeePage() {

  
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [form, setForm] = useState<FormState>({ ...INIT });
  const [errors, setErrors] = useState<Errors>({});
  const [touched, setTouched] = useState<Touched>({});
  const [submitting, setSubmitting] = useState(false);
  const [draftSaving, setDraftSaving] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [activeSection, setActiveSection] = useState("s-basic");
  const [managers, setManagers] = useState<Manager[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Fetch managers on component mount
  useEffect(() => {
    const loadManagers = async () => {
      try {
        const managersData = await fetchManagers();
        setManagers(managersData);
      } catch (error) {
        console.error('Failed to load managers:', error);
      }
    };
    loadManagers();
  }, []);

  // IntersectionObserver for active section
  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            setActiveSection(e.target.id);
          }
        });
      },
      { 
        root: scrollRef.current,
        rootMargin: "-20% 0px -60% 0px",
        threshold: 0
      }
    );
    SECTIONS.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) obs.observe(el);
    });
    return () => obs.disconnect();
  }, [submitted, form.activeTab, form.firstName]);

  // Auto-generate username from name
  useEffect(() => {
    const u = `${form.firstName}${form.firstName && form.lastName ? "." : ""}${form.lastName}`
      .toLowerCase()
      .replace(/[^a-z0-9.]/g, "");
    setForm((f) => ({ ...f, username: u }));
  }, [form.firstName, form.lastName]);

  // date limits for inputs
  const _today = new Date();
  const DOB_MAX_ISO = new Date(_today.getFullYear() - 18, _today.getMonth(), _today.getDate()).toISOString().split('T')[0];
  const DOJ_MIN_ISO = new Date(_today.getFullYear(), _today.getMonth(), _today.getDate() - 15).toISOString().split('T')[0];
  const DOJ_MAX_ISO = new Date(_today.getFullYear(), _today.getMonth(), _today.getDate() + 15).toISOString().split('T')[0];

  

  const set = useCallback(<K extends keyof FormState>(k: K, v: FormState[K]) => {
    let value: any = v;
    // sanitize and enforce limits for specific fields
    try {
      const key = String(k);
      if (typeof value === 'string') {
        // limit all text inputs to 150 chars
        if (value.length > 150) value = value.slice(0, 150);

        if (key === 'phone' || key === 'emergencyPhone') {
          // keep digits only and max 10
          value = value.replace(/\D/g, '').slice(0, 10);
        }
        if (key === 'aadhaarNumber') {
          value = value.replace(/\D/g, '').slice(0, 12);
        }
        if (key === 'height') {
          // allow numeric and optional unit, but limit numeric part to reasonable length
          const num = parseFloat(value.replace(/[^0-9.]/g, ''));
          if (!isNaN(num)) {
            if (num > 300) value = String(300);
          }
        }
        if (key === 'weight') {
          const num = parseFloat(value.replace(/[^0-9.]/g, ''));
          if (!isNaN(num)) {
            if (num > 200) value = String(200);
          }
        }
      }
    } catch (err) {
      // ignore sanitization errors
    }
    setForm((f) => ({ ...f, [k]: value }));
    setErrors((e) => ({ ...e, [k]: undefined }));
  }, []);

  const blur = (k: keyof FormState) => {
    setTouched((t) => ({ ...t, [k]: true }));
    vField(k);
  };

  const vField = useCallback(
    (k: keyof FormState): boolean => {
      const REQ: (keyof FormState)[] = [
        "salutation",
        "employeeSeries",
        "employeeId",
        "firstName",
        "lastName",
        "dob",
        "gender",
        "status",
        "email",
        "phone",
        "department",
        "designation",
        "employmentType",
        "workLocation",
        "joiningDate",
        "aadhaarNumber",
      ];
      if (form.activeTab === "rehire") REQ.push("rehireDate");

      if (REQ.includes(k) && !form[k]) {
        setErrors((e) => ({ ...e, [k]: "This field is required" }));
        return false;
      }
      // Phone number validation (10 digits)
      if ((k === 'phone' || k === 'emergencyPhone') && form[k]) {
        const digits = String(form[k]).replace(/\D/g, '');
        if (digits.length !== 10) {
          setErrors((e) => ({ ...e, [k]: 'Enter a 10-digit mobile number' }));
          return false;
        }
      }
      // Aadhaar: 12 digits
      if (k === 'aadhaarNumber' && form.aadhaarNumber) {
        if (!/^\d{12}$/.test(String(form.aadhaarNumber).replace(/\s/g, ''))) {
          setErrors((e) => ({ ...e, aadhaarNumber: 'Must be 12 digits' }));
          return false;
        }
      }
      // DOB: at least 18 years old
      if (k === 'dob' && form.dob) {
        const d = new Date(String(form.dob));
        if (isNaN(d.getTime())) {
          setErrors((e) => ({ ...e, dob: 'Enter a valid date' }));
          return false;
        }
        const today = new Date();
        const minDob = new Date(today.getFullYear() - 18, today.getMonth(), today.getDate());
        if (d > minDob) {
          setErrors((e) => ({ ...e, dob: 'Employee must be at least 18 years old' }));
          return false;
        }
      }
      // Joining date: within -15..+15 days of today
      if (k === 'joiningDate' && form.joiningDate) {
        const jd = new Date(String(form.joiningDate));
        if (isNaN(jd.getTime())) {
          setErrors((e) => ({ ...e, joiningDate: 'Enter a valid date' }));
          return false;
        }
        const today = new Date();
        const low = new Date(today);
        low.setDate(today.getDate() - 15);
        const high = new Date(today);
        high.setDate(today.getDate() + 15);
        // normalize
        low.setHours(0,0,0,0); high.setHours(23,59,59,999);
        if (jd < low || jd > high) {
          setErrors((e) => ({ ...e, joiningDate: 'Joining date must be within 15 days of today' }));
          return false;
        }
      }
      // Height/Weight numeric limits
      if (k === 'height' && form.height) {
        const num = parseFloat(String(form.height).replace(/[^0-9.]/g, ''));
        if (!isNaN(num) && num > 300) {
          setErrors((e) => ({ ...e, height: 'Height must be ≤ 300 cm' }));
          return false;
        }
      }
      if (k === 'weight' && form.weight) {
        const num = parseFloat(String(form.weight).replace(/[^0-9.]/g, ''));
        if (!isNaN(num) && num > 200) {
          setErrors((e) => ({ ...e, weight: 'Weight must be ≤ 200 kg' }));
          return false;
        }
      }
      if (k === "email" && form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
        setErrors((e) => ({ ...e, email: "Enter a valid email address" }));
        return false;
      }
      if (
        k === "aadhaarNumber" &&
        form.aadhaarNumber &&
        !/^\d{12}$/.test(form.aadhaarNumber.replace(/\s/g, ""))
      ) {
        setErrors((e) => ({ ...e, aadhaarNumber: "Must be 12 digits" }));
        return false;
      }
      if (k === "basicSalary" && form.basicSalary && isNaN(Number(form.basicSalary))) {
        setErrors((e) => ({ ...e, basicSalary: "Must be a valid number" }));
        return false;
      }
      return true;
    },
    [form]
  );

  const validateAll = (): boolean => {
    const REQ: (keyof FormState)[] = [
      "firstName",
      "lastName",
      "email",
      "department",
      "designation",
      "employmentType",
      "joiningDate",
      "aadhaarNumber",
    ];
    if (form.activeTab === "rehire") REQ.push("rehireDate");

    const errs: Errors = {};
    let ok = true;
    REQ.forEach((k) => {
      if (!form[k]) {
        errs[k] = "This field is required";
        ok = false;
      }
    });
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      errs.email = "Enter a valid email address";
      ok = false;
    }
    if (form.aadhaarNumber && !/^\d{12}$/.test(form.aadhaarNumber.replace(/\s/g, ""))) {
      errs.aadhaarNumber = "Must be 12 digits";
      ok = false;
    }
    // phone checks
    if (form.phone) {
      const digits = String(form.phone).replace(/\D/g, '');
      if (digits.length !== 10) {
        errs.phone = 'Enter a 10-digit mobile number';
        ok = false;
      }
    }
    if (form.emergencyPhone) {
      const digits = String(form.emergencyPhone).replace(/\D/g, '');
      if (digits.length !== 10) {
        errs.emergencyPhone = 'Enter a 10-digit mobile number';
        ok = false;
      }
    }
    // DOB age
    if (form.dob) {
      const d = new Date(String(form.dob));
      const today = new Date();
      const minDob = new Date(today.getFullYear() - 18, today.getMonth(), today.getDate());
      if (isNaN(d.getTime()) || d > minDob) {
        errs.dob = 'Employee must be at least 18 years old';
        ok = false;
      }
    }
    // joining date range
    if (form.joiningDate) {
      const jd = new Date(String(form.joiningDate));
      const today = new Date();
      const low = new Date(today); low.setDate(today.getDate() - 15); low.setHours(0,0,0,0);
      const high = new Date(today); high.setDate(today.getDate() + 15); high.setHours(23,59,59,999);
      if (isNaN(jd.getTime()) || jd < low || jd > high) {
        errs.joiningDate = 'Joining date must be within 15 days of today';
        ok = false;
      }
    }
    // height/weight limits
    if (form.height) {
      const num = parseFloat(String(form.height).replace(/[^0-9.]/g, ''));
      if (!isNaN(num) && num > 300) { errs.height = 'Height must be ≤ 300 cm'; ok = false; }
    }
    if (form.weight) {
      const num = parseFloat(String(form.weight).replace(/[^0-9.]/g, ''));
      if (!isNaN(num) && num > 200) { errs.weight = 'Weight must be ≤ 200 kg'; ok = false; }
    }
    if (form.assetName || form.assetId || form.assetCategory || form.assignDate) {
      (["assetName", "assetId", "assetCategory", "assignDate"] as (keyof FormState)[]).forEach((k) => {
        if (!form[k]) {
          errs[k] = "This field is required when assigning an asset";
          ok = false;
        }
      });
    }
    setErrors(errs);
    const allT: Touched = {};
    (Object.keys(form) as (keyof FormState)[]).forEach((k) => (allT[k] = true));
    setTouched(allT);
    if (!ok) document.getElementById("s-basic")?.scrollIntoView({ behavior: "smooth", block: "start" });
    return ok;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!validateAll()) return;
    setSubmitting(true);

    const assets =
      form.assetId && form.assetName
        ? [
            {
              asset_name: form.assetName,
              asset_id: form.assetId,
              asset_category: form.assetCategory || undefined,
              asset_condition: form.assetCondition || undefined,
              serial_number: form.serialNumber || undefined,
              asset_assign_date: form.assignDate,
              asset_return_date: form.returnDate || undefined,
              asset_status: form.assetStatus || "ASSIGNED",
              asset_remarks: form.assetRemarks || undefined,
            },
          ]
        : [];

    const masterValue = (value: string) =>
      value && !value.includes("-demo-") ? value : null;

    const payload: AddEmployeePayload = {
      employee_code: form.employeeId,
      first_name: form.firstName,
      last_name: form.lastName,
      date_of_birth: form.dob,
      joining_date: form.joiningDate,
      official_email: form.email,
      mobile_number: `${form.phoneCode}${form.phone}`,
      emergency_contact_name: form.emergencyName,
      emergency_contact_number: form.emergencyPhone,
      gender: masterValue(form.gender),
      salutation: masterValue(form.salutation),
      marital_status: null,
      blood_group: null,
      personal_email: null,
      
      employee_status: "ACTIVE",
      referred_by: masterValue(form.referredBy),
      allow_employee_to_fill_information: form.allowSelfFill,
      probation_period: form.probationPeriod ? parseInt(form.probationPeriod) : null,
      father_name: form.fathersName || null,
      spouse_name: form.spouseName || null,
      employment_type: masterValue(form.employmentType),
      department: masterValue(form.department),
      designation: masterValue(form.designation),
      work_location: masterValue(form.workLocation),
      reporting_manager: masterValue(form.reportingManager),
      working_hours_start: form.workStart || null,
      working_hours_end: form.workEnd || null,
      weekly_off_days: form.weeklyOff,
      attendance_tracking_mode: masterValue(form.trackingMode),
      salary_structure: masterValue(form.salaryStructure),
      basic_salary: form.basicSalary ? parseFloat(form.basicSalary) : null,
      bank_account:
        form.accountNumber && form.accountType
          ? {
              bank_name: masterValue(form.bankName) || undefined,
              account_number: form.accountNumber,
              account_type: form.accountType,
              ifsc_code: form.ifscCode || undefined,
              account_holder_name: `${form.firstName} ${form.lastName}`,
            }
          : null,
      pan_number: form.taxId || null,
      leave_policy: masterValue(form.leavePolicy),
      annual_leave_balance: form.annualLeave ? parseInt(form.annualLeave) : null,
      sick_leave_balance: form.sickLeave ? parseInt(form.sickLeave) : null,
      verification_status: masterValue(form.bgcStatus),
      agency_name: form.bgcAgency || null,
      verified_by: form.bgcVerifiedBy || null,
      reference_number: form.bgcReference || null,
      background_remarks: form.bgcRemarks || null,
      assets,
      username: form.username || null,
      temporary_password: form.password || null,
      system_role: form.role?.toUpperCase() || null,
      is_draft: false,
      is_active: true,
    };

    try {
      const response: AddEmployeeResponse = await createEmployee(payload);

      // Also keep local Redux store in sync so the directory updates immediately
      const newEmp = normalizeLegacyEmployee({
        ...form,
        id: response.employee_id,
        name: response.full_name,
        phone: `${form.phoneCode}${form.phone}`,
        status: "Active",
      });
      dispatch(addAdminEmployee(newEmp));

      setSubmitting(false);
      setSubmitted(true);
    } catch (err: any) {
      setSubmitting(false);
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.errors ||
        "Failed to create employee. Please check your inputs and try again.";
      alert(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
  };

  const handleDraft = async () => {
    setDraftSaving(true);
    try {
      await saveDraft(
        {
          ...form,
          // strip File objects — not serialisable
          photo: null,
        },
        "new",
      );
    } catch {
      // draft save is best-effort; silently ignore network errors
    } finally {
      setDraftSaving(false);
    }
  };

  const ok = (k: keyof FormState) => !!(touched[k] && !errors[k] && form[k]);

  // ── Success screen ───────────────────────────────────────
  if (submitted) {
    return (
      <div className="flex items-center justify-center p-8 min-h-full bg-background">
        <div className="flat-card bg-card p-10 max-w-sm w-full text-center">
          <div className="w-14 h-14 rounded-2xl bg-foreground flex items-center justify-center mx-auto mb-6">
            <Check size={22} className="text-primary-foreground" strokeWidth={2.5} />
          </div>
          <h2 className="text-lg font-semibold text-foreground">Employee Created</h2>
          <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
            <span className="font-semibold text-foreground">
              {form.firstName} {form.lastName}
            </span>{" "}
            has been successfully added with ID{" "}
            <span className="font-mono font-semibold text-foreground">{form.employeeId}</span>.
          </p>
          {form.sendInvite && form.email && (
            <p className="mt-3 text-xs text-muted-foreground p-3 bg-secondary rounded-lg leading-relaxed">
              A welcome email has been queued to{" "}
              <span className="font-semibold text-foreground">{form.email}</span>.
            </p>
          )}
          <div className="flex gap-3 mt-8">
            <button
              onClick={() => {
                setSubmitted(false);
                setForm({ ...INIT, employeeId: genId() });
                setErrors({});
                setTouched({});
              }}
              className="flex-1 h-9 rounded-lg border border-border text-sm font-medium text-foreground hover:bg-secondary transition-colors"
            >
              Add Another
            </button>
            <button
              onClick={() => navigate("/admin/employees")}
              className="flex-1 h-9 rounded-lg bg-foreground text-primary-foreground text-sm font-semibold hover:bg-accent transition-colors"
            >
              View Directory
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── Form ─────────────────────────────────────────────────
  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Tabs Navigation */}
      <div className="px-6 py-3 border-b border-border bg-card/50 backdrop-blur-md sticky top-0 z-30">
        <div className="flex items-center gap-1 p-1 bg-secondary/50 rounded-xl w-fit border border-border/50">
          <button
            type="button"
            onClick={() => set("activeTab", "new")}
            className={`px-6 py-2 text-xs font-bold rounded-lg transition-all duration-200 ${
              form.activeTab === "new"
                ? "bg-foreground text-primary-foreground shadow-lg scale-[1.02]"
                : "text-muted-foreground hover:text-foreground hover:bg-secondary"
            }`}
          >
            New Employee
          </button>
          <button
            type="button"
            onClick={() => set("activeTab", "rehire")}
            className={`px-6 py-2 text-xs font-bold rounded-lg transition-all duration-200 ${
              form.activeTab === "rehire"
                ? "bg-foreground text-primary-foreground shadow-lg scale-[1.02]"
                : "text-muted-foreground hover:text-foreground hover:bg-secondary"
            }`}
          >
            Rehire Employee
          </button>
          <button
            type="button"
            onClick={() => set("activeTab", "bulk")}
            className={`px-6 py-2 text-xs font-bold rounded-lg transition-all duration-200 ${
              form.activeTab === "bulk"
                ? "bg-foreground text-primary-foreground shadow-lg scale-[1.02]"
                : "text-muted-foreground hover:text-foreground hover:bg-secondary"
            }`}
          >
            Bulk Import
          </button>
        </div>
      </div>

      {/* Scrollable form area */}
      <div ref={scrollRef} className="flex-1 min-h-0 overflow-y-auto p-6 pb-4">
        {/* Page header removed for cleaner layout */}

        {/* Layout: SectionNav + Form */}
        <div className="flex gap-8 items-stretch">
          {form.activeTab === "new" || (form.activeTab === "rehire" && form.firstName) ? (
            <SectionNav active={activeSection} onSelect={setActiveSection} />
          ) : null}

          <div className="flex-1 min-w-0">
            {form.activeTab === "bulk" ? (
              <BulkImportTab />
            ) : form.activeTab === "rehire" && !form.firstName ? (
              <RehireSearch 
                onSelect={(emp) => {
                  setForm(f => ({
                    ...f,
                    firstName: emp.name.split(' ')[0],
                    lastName: emp.name.split(' ')[1] || "",
                    email: emp.email,
                    phone: emp.phone,
                    department: emp.dept,
                    designation: emp.desig,
                    // In a real app, you'd fetch the full profile here
                  }));
                }}
              />
            ) : (
              <form
                id="add-employee-form"
                onSubmit={handleSubmit}
                noValidate
                className="flex flex-col gap-4"
              >
                {form.activeTab === "rehire" && (
                  <div>
                    {/* Back Button */}
                    <button
                      type="button"
                      onClick={() => {
                        setForm(f => ({
                          ...f,
                          firstName: "",
                          lastName: "",
                          email: "",
                          phone: "",
                          department: "",
                          designation: "",
                          rehireDate: "",
                          rehireRemarks: "",
                          employeeId: "",
                          restoreSalary: false,
                          restoreAssets: false,
                          restoreLeaves: false,
                        }));
                      }}
                      className="mb-4 flex items-center gap-2 h-9 px-4 rounded-lg border border-border text-xs font-semibold text-muted-foreground hover:text-foreground hover:bg-secondary transition-all"
                    >
                      <ArrowLeft size={14} />
                      Back to Employees
                    </button>
                    
                    <div className="p-6 rounded-3xl border-2 border-indigo-500/30 bg-indigo-500/[0.03] shadow-xl shadow-indigo-500/5 mb-6 animate-in zoom-in-95 duration-500">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 rounded-xl bg-indigo-500 flex items-center justify-center text-white shadow-lg">
                        <RefreshCw size={20} />
                      </div>
                      <div>
                        <h3 className="text-sm font-black text-foreground">Rehire Configuration</h3>
                        <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Update details for the new employment period</p>
                      </div>
                      <div className="ml-auto">
                        <span className="px-3 py-1 rounded-full bg-indigo-500 text-white text-[10px] font-black uppercase tracking-widest animate-pulse">Rehiring</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <FF label="New Rehire Date" required error={errors.rehireDate}>
                        <Inp 
                          type="date"
                          value={form.rehireDate}
                          onChange={(e) => set("rehireDate", e.target.value)}
                        />
                      </FF>
                      <FF label="New Employee ID (Optional)" hint="Leave blank for auto-generation">
                        <Inp 
                          value={form.employeeId}
                          onChange={(e) => set("employeeId", e.target.value)}
                          placeholder="E.g. EMP-2024-001"
                        />
                      </FF>
                      <div className="md:col-span-2">
                        <FF label="Rehire Remarks">
                          <Inp 
                            value={form.rehireRemarks}
                            onChange={(e) => set("rehireRemarks", e.target.value)}
                            placeholder="Reason for rehire or additional notes..."
                          />
                        </FF>
                      </div>
                    </div>

                    <div className="mt-6 pt-6 border-t border-indigo-500/10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                      <Toggle on={form.restoreSalary} setOn={(v) => set("restoreSalary", v)} label="Restore Salary" desc="Prev. structure" />
                      <Toggle on={form.restoreAssets} setOn={(v) => set("restoreAssets", v)} label="Restore Assets" desc="Prev. assignments" />
                      <Toggle on={form.restoreLeaves} setOn={(v) => set("restoreLeaves", v)} label="Restore Leaves" desc="Prev. balances" />
                    </div>
                    </div>
                  </div>
                )}

                {/* ─────────────────────────────────────────────
                    SECTION 1 · BASIC INFORMATION
                ───────────────────────────────────────────── */}
            <SC
              id="s-basic"
              n={1}
              title="Basic Information"
              desc="Personal details, employment setup, and contact information"
              Icon={User}
            >
              {/* LEFT SIDE */}
              <div className="flex flex-col gap-5">
                <FF label="Salutation" required error={errors.salutation} ok={ok("salutation")}>
                  <MasterSelect
                    masterName="Salutation"
                    value={form.salutation}
                    onChange={(v) => set("salutation", v)}
                  />
                </FF>

                <FF label="Employee Number Series" required error={errors.employeeSeries} ok={ok("employeeSeries")}>
                  <MasterSelect
                    masterName="EmployeeNumberSeries"
                    value={form.employeeSeries}
                    onChange={(v) => set("employeeSeries", v)}
                  />
                </FF>

                <FF label="Employee No" icon={<Hash size={13} />} required hint="Based on selected series" error={errors.employeeId} ok={ok("employeeId")}>
                  <Inp
                    value={form.employeeId}
                    onChange={(e) => set("employeeId", e.target.value)}
                    placeholder="EMP-001"
                    err={!!errors.employeeId}
                  />
                </FF>

                <div className="grid grid-cols-2 gap-4">
                  <FF label="First Name" required error={errors.firstName} ok={ok("firstName")}>
                    <Inp
                      name="firstName"
                      value={form.firstName}
                      onChange={(e) => set("firstName", e.target.value)}
                      onBlur={() => blur("firstName")}
                      placeholder="James"
                      err={!!errors.firstName}
                      success={ok("firstName")}
                    />
                  </FF>
                  <FF label="Last Name" required error={errors.lastName} ok={ok("lastName")}>
                    <Inp
                      name="lastName"
                      value={form.lastName}
                      onChange={(e) => set("lastName", e.target.value)}
                      onBlur={() => blur("lastName")}
                      placeholder="Anderson"
                      err={!!errors.lastName}
                      success={ok("lastName")}
                    />
                  </FF>
                </div>

                <FF label="Date of Birth" required error={errors.dob} ok={ok("dob")}>
                  <Inp
                    type="date"
                    value={form.dob}
                    onChange={(e) => set("dob", e.target.value)}
                    max={DOB_MAX_ISO}
                    className="cursor-pointer"
                    err={!!errors.dob}
                    onBlur={() => blur("dob")}
                  />
                </FF>

                <FF label="Aadhaar Number" icon={<FileText size={13} />} required error={errors.aadhaarNumber} ok={ok("aadhaarNumber")}>
                  <Inp
                    value={form.aadhaarNumber}
                    onChange={(e) => set("aadhaarNumber", e.target.value)}
                    placeholder="XXXX XXXX XXXX"
                    err={!!errors.aadhaarNumber}
                    success={ok("aadhaarNumber")}
                  />
                </FF>

                <FF label="Gender" required error={errors.gender} ok={ok("gender")}>
                  <MasterSelect
                    masterName="Gender"
                    value={form.gender}
                    onChange={(v) => set("gender", v)}
                  />
                </FF>

                <FF label="Reporting Manager" hint="Optional — Select if applicable">
                  <SearchableSelect
                    options={managers.map((m) => ({ value: m.id, label: `${m.name} — ${m.designation || ""}` }))}
                    value={form.reportingManager}
                    onChange={(v) => set("reportingManager", v)}
                    placeholder="Search Manager..."
                  />
                </FF>

                <FF label="Status" required error={errors.status} ok={ok("status")}>
                  <MasterSelect
                    masterName="EmployeeStatus"
                    value={form.status}
                    onChange={(v) => set("status", v)}
                  />
                </FF>

                <FF label="Date of Joining" required error={errors.joiningDate} ok={ok("joiningDate")}>
                  <Inp
                    type="date"
                    value={form.joiningDate}
                    onChange={(e) => set("joiningDate", e.target.value)}
                    min={DOJ_MIN_ISO}
                    max={DOJ_MAX_ISO}
                    onBlur={() => blur("joiningDate")}
                    err={!!errors.joiningDate}
                    success={ok("joiningDate")}
                    className="cursor-pointer"
                  />
                </FF>

                <div className="grid grid-cols-2 gap-4">
                  <FF label="Height" error={errors.height} ok={ok("height")}>
                    <Inp value={form.height} onChange={(e) => set("height", e.target.value)} placeholder="e.g. 175 cm" err={!!errors.height} />
                  </FF>
                  <FF label="Weight" error={errors.weight} ok={ok("weight")}>
                    <Inp value={form.weight} onChange={(e) => set("weight", e.target.value)} placeholder="e.g. 72 kg" err={!!errors.weight} />
                  </FF>
                </div>

                <FF label="Referred By">
                  <MasterSearchableDropdown
                    masterName="Employee"
                    value={form.referredBy}
                    onChange={(v) => set("referredBy", v)}
                    placeholder="Search referrer..."
                  />
                </FF>

                <div className="pt-2 flex flex-col gap-3">
                  <CheckInput
                    label="Allow the employee to fill in their information"
                    checked={form.allowSelfFill}
                    onChange={(v) => set("allowSelfFill", v)}
                  />
                </div>
              </div>

              {/* RIGHT SIDE */}
              <div className="flex flex-col gap-5">
                <FF label="Probation Period" hint="Specify duration in days">
                  <div className="flex items-center gap-2">
                    <Inp
                      type="number"
                      value={form.probationPeriod}
                      onChange={(e) => set("probationPeriod", e.target.value)}
                      placeholder="90"
                      className="flex-1"
                    />
                    <div className="h-9 px-3 bg-secondary border border-border rounded-lg flex items-center justify-center text-xs font-semibold text-muted-foreground min-w-[60px]">
                      Days
                    </div>
                  </div>
                </FF>

                

                <FF label="Email" icon={<Mail size={13} />} required error={errors.email} ok={ok("email")}>
                  <Inp
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={(e) => set("email", e.target.value)}
                    onBlur={() => blur("email")}
                    placeholder="official@company.com"
                    err={!!errors.email}
                    success={ok("email")}
                  />
                </FF>

                <FF label="Mobile Number" required hint="Include area code" error={errors.phone} ok={ok("phone")}>
                  <PhoneInp
                    cc={form.phoneCode}
                    ph={form.phone}
                    onCC={(v) => set("phoneCode", v)}
                    onPh={(v) => set("phone", v)}
                    err={!!errors.phone}
                  />
                </FF>

                <FF label="Emergency Contact Name" icon={<UserPlus size={13} />}>
                  <Inp
                    value={form.emergencyName}
                    onChange={(e) => set("emergencyName", e.target.value)}
                    placeholder="Contact Name"
                  />
                </FF>

                <FF label="Emergency Contact Number" icon={<Phone size={13} />} error={errors.emergencyPhone} ok={ok("emergencyPhone")}>
                  <Inp
                    value={form.emergencyPhone}
                    onChange={(e) => set("emergencyPhone", e.target.value)}
                    placeholder="Contact Number"
                    err={!!errors.emergencyPhone}
                  />
                </FF>

                <FF label="Father's Name" icon={<User size={13} />}>
                  <Inp
                    value={form.fathersName}
                    onChange={(e) => set("fathersName", e.target.value)}
                    placeholder="Full Name"
                  />
                </FF>

                <FF label="Spouse Name" icon={<User size={13} />}>
                  <Inp
                    value={form.spouseName}
                    onChange={(e) => set("spouseName", e.target.value)}
                    placeholder="Full Name"
                  />
                </FF>

                <FF label="Profile Photo" hint="JPG or PNG · Max 2 MB">
                  <PhotoUp file={form.photo} onChange={(v) => set("photo", v)} />
                </FF>
              </div>
            </SC>



            {/* ─────────────────────────────────────────────
                SECTION 2 · JOB DETAILS
            ───────────────────────────────────────────── */}
            <SC
              id="s-job"
              n={2}
              title="Job Details"
              desc="Role, department, and employment configuration"
              Icon={Briefcase}
            >
              <FF label="Department" required error={errors.department} ok={ok("department")}>
                <MasterDropdown
                  masterName="Department"
                  value={form.department}
                  onChange={(v) => {
                    set("department", v);
                    setTouched((t) => ({ ...t, department: true }));
                  }}
                  placeholder="Select department"
                  required
                />
              </FF>

              <FF label="Designation / Role" required error={errors.designation} ok={ok("designation")}>
                <MasterDropdown
                  masterName="Designation"
                  value={form.designation}
                  onChange={(v) => {
                    set("designation", v);
                    setTouched((t) => ({ ...t, designation: true }));
                  }}
                  placeholder="Select role"
                  required
                />
              </FF>

              <FF label="Employment Type" required error={errors.employmentType} ok={ok("employmentType")}>
                <MasterDropdown
                  masterName="EmployeeType"
                  value={form.employmentType}
                  onChange={(v) => {
                    set("employmentType", v);
                    setTouched((t) => ({ ...t, employmentType: true }));
                  }}
                  placeholder="Select type"
                  required
                />
              </FF>

              <FF label="Work Location" required error={errors.workLocation} ok={ok("workLocation")} icon={<MapPin size={13} />}>
                <MasterDropdown
                  masterName="OfficeLocation"
                  value={form.workLocation}
                  onChange={(v) => {
                    set("workLocation", v);
                    setTouched((t) => ({ ...t, workLocation: true }));
                  }}
                  placeholder="Select work location"
                  required
                />
              </FF>
            </SC>

            {/* ─────────────────────────────────────────────
                SECTION 3 · ATTENDANCE SETTINGS
            ───────────────────────────────────────────── */}
            <SC
              id="s-attendance"
              n={3}
              title="Attendance Settings"
              desc="Shift allocation, leave policy, and attendance tracking"
              Icon={Clock}
            >
              <FF label="Working Hours" hint="Start time → End time">
                <div className="flex items-center gap-2">
                  <input
                    type="time"
                    value={form.workStart}
                    onChange={(e) => set("workStart", e.target.value)}
                    className="flat-input flex-1 h-9 px-3 text-sm cursor-pointer"
                  />
                  <span className="text-xs font-semibold text-muted-foreground shrink-0">→</span>
                  <input
                    type="time"
                    value={form.workEnd}
                    onChange={(e) => set("workEnd", e.target.value)}
                    className="flat-input flex-1 h-9 px-3 text-sm cursor-pointer"
                  />
                </div>
              </FF>

              <FF label="Weekly Off Days">
                <MasterMultiDropdown
                  masterName="WeeklyOffDays"
                  values={form.weeklyOff}
                  onChange={(v) => set("weeklyOff", v)}
                />
              </FF>

              <FF label="Attendance Tracking Mode">
                <MasterDropdown
                  masterName="AttendanceTrackingMode"
                  value={form.trackingMode}
                  onChange={(v) => set("trackingMode", v)}
                  placeholder="Select mode"
                />
              </FF>
            </SC>

            {/* ─────────────────────────────────────────────
                SECTION 4 · PAYROLL INFORMATION
            ───────────────────────────────────────────── */}
            {/* <SC
              id="s-payroll"
              n={4}
              title="Payroll Information"
              desc="Salary structure and banking details"
              Icon={CreditCard}
            >
              <FF label="Salary Structure">
                <MasterDropdown
                  masterName="SalaryStructure"
                  value={form.salaryStructure}
                  onChange={(v) => set("salaryStructure", v)}
                  placeholder="Select structure"
                />
              </FF>

              <FF label="Basic Salary (Annual)" error={errors.basicSalary} ok={ok("basicSalary")}>
                <Inp
                  type="number"
                  name="basicSalary"
                  value={form.basicSalary}
                  onChange={(e) => set("basicSalary", e.target.value)}
                  onBlur={() => blur("basicSalary")}
                  placeholder="85,000"
                  icon={<span className="text-xs font-bold">₹</span>}
                  err={!!errors.basicSalary}
                  success={ok("basicSalary")}
                />
              </FF>

              <FF label="Bank Name">
                <MasterDropdown
                  masterName="Bank"
                  value={form.bankName}
                  onChange={(v) => set("bankName", v)}
                  placeholder="Select bank"
                />
              </FF>

              <FF label="Account Type" required hint="Required for bank account">
                <MasterDropdown
                  masterName="AccountType"
                  value={form.accountType}
                  onChange={(v) => set("accountType", v)}
                  placeholder="Select account type"
                />
              </FF>

              <FF label="Account Number" hint="Encrypted at rest — masked for security">
                <MaskInp
                  val={form.accountNumber}
                  onChange={(v) => set("accountNumber", v)}
                  ph="Enter account number"
                />
              </FF>

              <FF label="IFSC / Routing Code">
                <Inp
                  value={form.ifscCode}
                  onChange={(e) => set("ifscCode", e.target.value.toUpperCase())}
                  placeholder="HDFC0001234"
                  className="font-mono tracking-wider"
                />
              </FF>

              <FF label="Tax ID / PAN">
                <Inp
                  value={form.taxId}
                  onChange={(e) => set("taxId", e.target.value.toUpperCase())}
                  placeholder="ABCDE1234F"
                  className="font-mono tracking-wider"
                />
              </FF>
            </SC> */}

            {/* ─────────────────────────────────────────────
                SECTION 5 · LEAVE CONFIGURATION
            ───────────────────────────────────────────── */}
            <SC
              id="s-leave"
              n={5}
              title="Leave Configuration"
              desc="Leave policy and opening balances for the employee"
              Icon={Calendar}
            >
              <FF label="Leave Policy" span2>
                <MasterDropdown
                  masterName="LeavePolicy"
                  value={form.leavePolicy}
                  onChange={(v) => set("leavePolicy", v)}
                  placeholder="Select policy"
                />
              </FF>
              
            </SC>



            {/* ─────────────────────────────────────────────
                SECTION 8 · BACKGROUND CHECK
            ───────────────────────────────────────────── */}
            <SC
              id="s-background"
              n={6}
              title="Background Check"
              desc="Verification status and agency audit details"
              Icon={Shield}
            >
              <FF label="Verification Status">
                <MasterDropdown
                  masterName="VerificationStatus"
                  value={form.bgcStatus}
                  onChange={(v) => set("bgcStatus", v)}
                  placeholder="Select status"
                />
              </FF>
              <FF label="Agency Name">
                <Inp 
                  value={form.bgcAgency} 
                  onChange={(e) => set("bgcAgency", e.target.value)}
                  placeholder="Verification Agency"
                />
              </FF>
              <FF label="Verified By">
                <Inp 
                  value={form.bgcVerifiedBy} 
                  onChange={(e) => set("bgcVerifiedBy", e.target.value)}
                  placeholder="Auditor Name"
                />
              </FF>
              <FF label="Reference Number">
                <Inp 
                  value={form.bgcReference} 
                  onChange={(e) => set("bgcReference", e.target.value)}
                  placeholder="Case Reference ID"
                />
              </FF>
              <FF label="Remarks" span2>
                <textarea
                  value={form.bgcRemarks}
                  onChange={(e) => set("bgcRemarks", e.target.value)}
                  placeholder="Add any internal remarks regarding the background check..."
                  className="flat-input w-full min-h-[80px] p-3 text-sm resize-none"
                />
              </FF>
            </SC>

            <SC
              id="s-assets"
              n={7}
              title="Asset Management"
              desc="Company property and equipment assigned to the employee"
              Icon={Monitor}
            >
              <FF label="Asset Name" error={errors.assetName}>
                <Inp
                  value={form.assetName}
                  onChange={(e) => set("assetName", e.target.value)}
                  placeholder="E.g. MacBook Pro M3"
                />
              </FF>

              <FF label="Asset ID" icon={<Hash size={13} />} error={errors.assetId}>
                <Inp
                  value={form.assetId}
                  onChange={(e) => set("assetId", e.target.value)}
                  placeholder="E.g. AST-2024-001"
                />
              </FF>

              <FF label="Asset Category" error={errors.assetCategory}>
                <MasterDropdown
                  masterName="AssetCategory"
                  value={form.assetCategory}
                  onChange={(v) => {
                    set("assetCategory", v);
                    setTouched((t) => ({ ...t, assetCategory: true }));
                  }}
                  placeholder="Select category"
                />
              </FF>

              <FF label="Serial Number" error={errors.serialNumber}>
                <Inp
                  value={form.serialNumber}
                  onChange={(e) => set("serialNumber", e.target.value)}
                  placeholder="E.g. C02X1234YYYY"
                />
              </FF>

              <FF label="Assign Date" error={errors.assignDate}>
                <Inp
                  type="date"
                  value={form.assignDate}
                  onChange={(e) => set("assignDate", e.target.value)}
                  className="cursor-pointer"
                />
              </FF>

              <FF label="Return Date" error={errors.returnDate}>
                <Inp
                  type="date"
                  value={form.returnDate}
                  onChange={(e) => set("returnDate", e.target.value)}
                  className="cursor-pointer"
                />
              </FF>

              <FF label="Asset Condition" error={errors.assetCondition}>
                <MasterDropdown
                  masterName="AssetCondition"
                  value={form.assetCondition}
                  onChange={(v) => {
                    set("assetCondition", v);
                    setTouched((t) => ({ ...t, assetCondition: true }));
                  }}
                  placeholder="Select condition"
                />
              </FF>

              <FF label="Status" error={errors.assetStatus}>
                <Sel
                  value={form.assetStatus}
                  onChange={(e) => set("assetStatus", e.target.value)}
                  opts={[
                    { v: "ASSIGNED", l: "Assigned" },
                    { v: "RETURNED", l: "Returned" },
                    { v: "LOST", l: "Lost" },
                    { v: "DAMAGED", l: "Damaged" },
                  ]}
                />
              </FF>

              <FF label="Remarks" span2 error={errors.assetRemarks}>
                <textarea
                  value={form.assetRemarks}
                  onChange={(e) => set("assetRemarks", e.target.value)}
                  placeholder="Add any internal remarks regarding the asset..."
                  className="flat-input w-full min-h-[80px] p-3 text-sm resize-none"
                />
              </FF>
            </SC>

            {/* ─────────────────────────────────────────────
                SECTION 10 · ACCOUNT ACCESS
            ───────────────────────────────────────────── */}
            <SC
              id="s-account"
              n={8}
              title="Account Access"
              desc="System credentials and role-based access permissions"
              Icon={Shield}
            >
              <FF label="Username" icon={<User size={13} />} hint="Auto-generated from name · Can be edited manually">
                <Inp
                  value={form.username}
                  onChange={(e) => set("username", e.target.value)}
                  placeholder="james.anderson"
                />
              </FF>

              <FF label="Temporary Password" hint="Leave blank to auto-generate on creation">
                <div className="flex flex-col gap-2">
                  <MaskInp
                    val={form.password}
                    onChange={(v) => set("password", v)}
                    ph="Auto-generate if empty"
                  />
                  <button
                    type="button"
                    onClick={() => set("password", genPwd())}
                    className="flex items-center gap-1.5 text-[11px] text-muted-foreground hover:text-foreground transition-colors w-fit font-medium"
                  >
                    <RefreshCw size={11} />
                    Generate strong password
                  </button>
                </div>
              </FF>

              <FF label="System Role">
                <SystemRoleSelect
                  value={form.role}
                  onChange={(v) => set("role", v)}
                />
              </FF>

              <div className="sm:col-span-2">
                <Toggle
                  on={form.sendInvite}
                  setOn={(v) => set("sendInvite", v)}
                  label="Send Welcome Email"
                  desc="An email with login credentials and onboarding info will be sent to the employee upon account creation."
                />
              </div>
            </SC>
          </form>
          )}
        </div>
      </div>

      {/* ── Sticky Action Bar ─────────────────────────────── */}
      {(form.activeTab === "new" || (form.activeTab === "rehire" && form.firstName)) && (
      <div className="sticky bottom-0 z-10 bg-card border-t border-border">
        <div className="px-6 py-3 flex items-center justify-between gap-4">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <AlertCircle size={12} className="shrink-0" />
            <span className="hidden sm:block">
              Fields marked <span className="text-red-500 font-bold mx-0.5">*</span> are required
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => navigate("/admin/employees")}
              className="h-8 px-4 rounded-lg border border-border text-xs font-semibold text-muted-foreground hover:text-foreground hover:bg-secondary transition-all"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleDraft}
              disabled={draftSaving}
              className="flex items-center gap-1.5 h-8 px-4 rounded-lg border border-border text-xs font-semibold text-foreground hover:bg-secondary transition-all disabled:opacity-50"
            >
              {draftSaving ? <Loader2 size={12} className="animate-spin" /> : <Save size={12} />}
              Save Draft
            </button>
            <button
              type="submit"
              form="add-employee-form"
              disabled={submitting}
              className="flex items-center gap-1.5 h-8 px-5 rounded-lg bg-foreground text-primary-foreground text-xs font-bold hover:bg-accent transition-all disabled:opacity-60"
            >
              {submitting ? (
                <>
                  <Loader2 size={12} className="animate-spin" />
                  Creating…
                </>
              ) : (
                <>
                  <UserPlus size={12} />
                  Create Employee
                </>
              )}
            </button>
          </div>
        </div>
      </div>
      )}
    </div>
  </div>
  );
}
