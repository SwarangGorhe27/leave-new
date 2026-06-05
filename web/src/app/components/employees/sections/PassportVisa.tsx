import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { Employee } from "../mockData";
import { Globe, BookOpen, AlertCircle, CheckCircle2, Edit2, Save, X, Send } from "lucide-react";
import { useAdminSync } from "../../admin/useAdminSync";
import { addNotification } from "../../../../store/slices/notificationSlice";
import { AppDispatch } from "../../../../store";
import { validatePassport } from "../employee-details";
import { useMasterOptions } from "./useMasterOptions";
import { usePassportVisaMasterOptions } from "./usePassportVisaMasterOptions";
import { useEmployeeFormContext } from "../employee-details/EmployeeFormContext";


interface Props {
  employee: Employee;
  essMode?: boolean;
}

function isExpired(dateStr: string): boolean {
  if (!dateStr) return false;
  return new Date(dateStr) < new Date();
}

function isExpiringSoon(dateStr: string): boolean {
  if (!dateStr) return false;
  const expiry = new Date(dateStr);
  const cutoff = new Date();
  cutoff.setMonth(cutoff.getMonth() + 3);
  return expiry > new Date() && expiry <= cutoff;
}

const VALID_BADGE   = "bg-[#212529] text-[#F8F9FA]";
const EXPIRING_BADGE = "bg-[#6C757D] text-white";
const EXPIRED_BADGE  = "bg-[#CED4DA] text-[#212529]";

function withCurrentOption(options: Array<{ value: string; label: string }>, value?: string) {
  if (!value || options.some((option) => option.value === value || option.label === value)) {
    return options;
  }
  return [{ value, label: value }, ...options];
}

function resolveSelectValue(
  options: Array<{ value: string; label: string }>,
  current?: string,
): string {
  if (!current) return "";
  if (options.some((o) => o.value === current)) return current;
  const byLabel = options.find(
    (o) => o.label.toLowerCase() === current.toLowerCase(),
  );
  return byLabel?.value ?? current;
}

function labelForSelect(
  options: Array<{ value: string; label: string }>,
  current?: string,
): string {
  if (!current) return "—";
  const match = options.find((o) => o.value === current || o.label === current);
  return match?.label ?? current;
}

function formatDisplayDate(value?: string): string {
  if (!value) return "—";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

const passportDarkInput =
  "text-sm font-bold mt-0.5 bg-white/10 border border-white/20 rounded px-2 py-1 text-white w-full focus:outline-none focus:ring-2 focus:ring-white/20";
const passportDarkSelect = passportDarkInput;

export function PassportVisa({ employee }: Props) {
  const nationalityOptions = useMasterOptions("Nationality");
  const countryOptions = useMasterOptions("Country");
  const { options: passportCategoryOptions } = usePassportVisaMasterOptions("passport-categories");
  const { options: passportStatusOptions } = usePassportVisaMasterOptions("passport-statuses");
  const essReadOnly = useEmployeeFormContext()?.essReadOnly;
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState(employee);
  const { handleAdminSave } = useAdminSync();

  useEffect(() => {
    setEditedData(employee);
    setIsEditing(false);
  }, [employee]);
  const dispatch = useDispatch<AppDispatch>();

  const handleUpdate = (field: keyof Employee, value: string) => {
    setEditedData(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    const pErr = validatePassport(editedData.passportNumber || "");
    if (pErr) {
      dispatch(addNotification({ type: "warning", message: pErr }));
      return;
    }
    const success = await handleAdminSave('Passport & Visa Details', employee, editedData);
    if (success) setIsEditing(false);
  };

  const passportExpired      = isExpired(editedData.passportExpiry);
  const passportExpiringSoon = isExpiringSoon(editedData.passportExpiry);
  const visaExpired          = editedData.visaExpiry ? isExpired(editedData.visaExpiry) : false;

  const isPassportEditable = employee.editableSections?.includes("passport-details");
  const isVisaEditable = employee.editableSections?.includes("visa-details");
  const nationalitySelectOptions = withCurrentOption(nationalityOptions, editedData.nationality);
  const passportCountryOptions = withCurrentOption(countryOptions, editedData.passportCountryOfIssue);
  const visaCountryOptions = withCurrentOption(countryOptions, editedData.visaCountry);
  const categorySelectOptions = withCurrentOption(
    passportCategoryOptions,
    editedData.passportCategory,
  );
  const statusSelectOptions = withCurrentOption(
    passportStatusOptions,
    editedData.passportStatus,
  );

  const getStatusLabel = (editable: boolean) => {
    if (employee.editRequestStatus === 'Pending') return { l: 'Pending Employee Update', c: 'bg-amber-500/10 text-amber-600 border-amber-200' };
    if (employee.editRequestStatus === 'Updated') return { l: 'Updated by Employee', c: 'bg-emerald-500/10 text-emerald-600 border-emerald-200' };
    if (editable) return { l: 'Editable by Employee', c: 'bg-indigo-500/10 text-indigo-600 border-indigo-200' };
    return { l: '', c: '' };
  };

  return (
    <div className="space-y-5 pb-24">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-foreground">Passport & Visa Details</h2>
          <p className="text-sm text-muted-foreground mt-1">Travel document information for {employee.name}</p>
        </div>
        <div className="flex items-center gap-2">
          {isEditing ? (
            <>
              <button onClick={handleSave} className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-bold hover:bg-primary/90 transition-all">
                <Save size={12} /> Save Changes
              </button>
              <button onClick={() => { setEditedData(employee); setIsEditing(false); }}
                className="flex items-center gap-1.5 px-3 py-1.5 border border-border rounded-lg text-xs font-bold hover:bg-secondary transition-all">
                <X size={12} /> Cancel
              </button>
            </>
          ) : essReadOnly ? (
            <button
              type="button"
              onClick={() => window.dispatchEvent(new CustomEvent("ess:request_change", { detail: { sectionId: "passport-visa" } }))}
              className="flex items-center gap-1.5 px-3 py-1.5 border border-border rounded-lg text-xs font-bold hover:bg-secondary transition-all"
            >
              <Send size={12} /> Request Change
            </button>
          ) : (
            <button onClick={() => setIsEditing(true)} className="flex items-center gap-1.5 px-3 py-1.5 border border-border rounded-lg text-xs font-bold hover:bg-secondary transition-all">
              <Edit2 size={12} /> Edit Section
            </button>
          )}
        </div>
      </div>

      {/* ── Passport ──────────────────────────────────────── */}
      <div className="flat-card bg-card p-6">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
          <div className="flex items-center gap-3">
            <h3 className="text-sm font-bold text-foreground flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-secondary border border-border flex items-center justify-center">
                <Globe className="w-4 h-4 text-foreground" />
              </div>
              Passport Details
            </h3>
            {(() => {
              const s = getStatusLabel(isPassportEditable);
              return s.l ? (
                <span className={`text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded border transition-all ${s.c}`}>
                  {s.l}
                </span>
              ) : null;
            })()}
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              {passportExpired ? (
                <span className={`flex items-center gap-1.5 text-[10px] uppercase tracking-wider font-bold px-2.5 py-1 rounded-md ${EXPIRED_BADGE}`}>
                  <AlertCircle className="w-3.5 h-3.5" /> Expired
                </span>
              ) : passportExpiringSoon ? (
                <span className={`flex items-center gap-1.5 text-[10px] uppercase tracking-wider font-bold px-2.5 py-1 rounded-md ${EXPIRING_BADGE}`}>
                  <AlertCircle className="w-3.5 h-3.5" /> Expiring Soon
                </span>
              ) : (
                <span className={`flex items-center gap-1.5 text-[10px] uppercase tracking-wider font-bold px-2.5 py-1 rounded-md ${VALID_BADGE}`}>
                  <CheckCircle2 className="w-3.5 h-3.5" /> Valid
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Passport card — flat dark treatment */}
        <div className="bg-foreground text-primary-foreground rounded-lg p-6 mb-2">
          <div className="flex justify-between items-start mb-5">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-primary-foreground/60">Republic of India</p>
              <p className="text-base font-bold mt-0.5">Passport</p>
            </div>
            <Globe className="w-8 h-8 text-primary-foreground/30" />
          </div>
          <div className="grid grid-cols-2 gap-6 mb-5">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-primary-foreground/60">Passport Number</p>
              {isEditing ? (
                <input type="text" value={editedData.passportNumber || ''} onChange={e => handleUpdate('passportNumber', e.target.value)}
                  className="text-base font-mono font-bold mt-0.5 bg-white/10 border border-white/20 rounded px-2 py-1 text-white w-full focus:outline-none" />
              ) : (
                <p className="text-base font-mono font-bold mt-0.5">{editedData.passportNumber}</p>
              )}
            </div>
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-primary-foreground/60">Nationality</p>
              {isEditing && nationalitySelectOptions.length ? (
                <select value={editedData.nationality || ''} onChange={e => handleUpdate('nationality', e.target.value)}
                  className="text-base font-bold mt-0.5 bg-white/10 border border-white/20 rounded px-2 py-1 text-white w-full focus:outline-none">
                  <option value="">Select Nationality</option>
                  {nationalitySelectOptions.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
              ) : isEditing ? (
                <input type="text" value={editedData.nationality || ''} onChange={e => handleUpdate('nationality', e.target.value)}
                  className="text-base font-bold mt-0.5 bg-white/10 border border-white/20 rounded px-2 py-1 text-white w-full focus:outline-none" />
              ) : (
                <p className="text-base font-bold mt-0.5">{editedData.nationality}</p>
              )}
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 pt-4 border-t border-primary-foreground/20">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-primary-foreground/60">
                Holder Name
              </p>
              {isEditing ? (
                <input
                  type="text"
                  value={editedData.passportHolderName || editedData.name}
                  onChange={(e) => handleUpdate("passportHolderName", e.target.value)}
                  className={passportDarkInput}
                />
              ) : (
                <p className="text-sm font-bold mt-0.5">
                  {editedData.passportHolderName || editedData.name || "—"}
                </p>
              )}
            </div>

            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-primary-foreground/60">
                Place of Issue
              </p>
              {isEditing ? (
                <input
                  type="text"
                  value={editedData.passportPlaceOfIssue || ""}
                  onChange={(e) => handleUpdate("passportPlaceOfIssue", e.target.value)}
                  className={passportDarkInput}
                />
              ) : (
                <p className="text-sm font-bold mt-0.5">
                  {editedData.passportPlaceOfIssue || "—"}
                </p>
              )}
            </div>

            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-primary-foreground/60">
                Country of Issue
              </p>
              {isEditing && passportCountryOptions.length ? (
                <select
                  value={resolveSelectValue(
                    passportCountryOptions,
                    editedData.passportCountryOfIssue,
                  )}
                  onChange={(e) => {
                    const opt = passportCountryOptions.find((o) => o.value === e.target.value);
                    handleUpdate("passportCountryOfIssue", opt?.value ?? e.target.value);
                  }}
                  className={passportDarkSelect}
                >
                  <option value="">Select Country of Issue</option>
                  {passportCountryOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : isEditing ? (
                <input
                  type="text"
                  value={editedData.passportCountryOfIssue || ""}
                  onChange={(e) => handleUpdate("passportCountryOfIssue", e.target.value)}
                  className={passportDarkInput}
                />
              ) : (
                <p className="text-sm font-bold mt-0.5">
                  {labelForSelect(
                    passportCountryOptions,
                    editedData.passportCountryOfIssue,
                  )}
                </p>
              )}
            </div>

            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-primary-foreground/60">
                Category
              </p>
              {isEditing ? (
                <select
                  value={resolveSelectValue(
                    categorySelectOptions,
                    editedData.passportCategory,
                  )}
                  onChange={(e) => {
                    const opt = categorySelectOptions.find((o) => o.value === e.target.value);
                    handleUpdate("passportCategory", opt?.label ?? e.target.value);
                  }}
                  className={passportDarkSelect}
                >
                  <option value="">
                    {categorySelectOptions.length
                      ? "Select Category"
                      : "No categories in master — add under Masters"}
                  </option>
                  {categorySelectOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : (
                <p className="text-sm font-bold mt-0.5">
                  {labelForSelect(categorySelectOptions, editedData.passportCategory)}
                </p>
              )}
            </div>

            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-primary-foreground/60">
                Status
              </p>
              {isEditing ? (
                <select
                  value={resolveSelectValue(statusSelectOptions, editedData.passportStatus)}
                  onChange={(e) => {
                    const opt = statusSelectOptions.find((o) => o.value === e.target.value);
                    handleUpdate("passportStatus", opt?.label ?? e.target.value);
                  }}
                  className={passportDarkSelect}
                >
                  <option value="">
                    {statusSelectOptions.length
                      ? "Select Status"
                      : "No statuses in master — add under Masters"}
                  </option>
                  {statusSelectOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : (
                <p className="text-sm font-bold mt-0.5">
                  {labelForSelect(statusSelectOptions, editedData.passportStatus)}
                </p>
              )}
            </div>

            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-primary-foreground/60">
                Issue Date
              </p>
              {isEditing ? (
                <input
                  type="date"
                  value={editedData.passportIssueDate || ""}
                  onChange={(e) => handleUpdate("passportIssueDate", e.target.value)}
                  className={`${passportDarkInput} [color-scheme:dark]`}
                />
              ) : (
                <p className="text-sm font-bold mt-0.5">
                  {formatDisplayDate(editedData.passportIssueDate)}
                </p>
              )}
            </div>

            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-primary-foreground/60">
                Expiry Date
              </p>
              {isEditing ? (
                <input
                  type="date"
                  value={editedData.passportExpiry || ""}
                  onChange={(e) => handleUpdate("passportExpiry", e.target.value)}
                  className={`${passportDarkInput} [color-scheme:dark]`}
                />
              ) : (
                <p className="text-sm font-bold mt-0.5">
                  {formatDisplayDate(editedData.passportExpiry)}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Visa ─────────────────────────────────────────── */}
      <div className="flat-card bg-card p-6">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
          <div className="flex items-center gap-3">
            <h3 className="text-sm font-bold text-foreground flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-secondary border border-border flex items-center justify-center">
                <BookOpen className="w-4 h-4 text-foreground" />
              </div>
              Visa Details
            </h3>
            <span className={`text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded border transition-all ${getStatusLabel(isVisaEditable).c}`}>
               {getStatusLabel(isVisaEditable).l}
            </span>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              {((editedData as any).visaStatus || (!isEditing && (editedData as any).visaStatus)) && (
                <span className={`flex items-center gap-1.5 text-[10px] uppercase tracking-wider font-bold px-2.5 py-1 rounded-md ${(editedData as any).visaStatus === 'Expired' ? EXPIRED_BADGE : VALID_BADGE}`}>
                  {(editedData as any).visaStatus === 'Expired' ? <AlertCircle className="w-3.5 h-3.5" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                  {(editedData as any).visaStatus || 'Active'}
                </span>
              )}
            </div>
          </div>
        </div>

        {editedData.visaCountry || editedData.visaType || isEditing ? (
          <div className="bg-background border border-border rounded-lg p-5 space-y-3">
            {(
              [
                ["visaCountry", "Visa Country"],
                ["visaType", "Visa Type"],
                ["visaSponsor", "Visa Sponsor"],
                ["visaStatus", "Visa Status"],
                ["visaNumber", "Visa Number"],
                ["visaIssueDate", "Visa Issue Date"],
                ["visaExpiry", "Visa Expiry"],
              ] as const
            ).map(([field, label]) => (
              <div key={field} className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-1 py-2 border-b border-border last:border-0">
                <span className="text-sm text-muted-foreground font-medium">{label}</span>
                {isEditing && field === "visaCountry" && visaCountryOptions.length ? (
                  <select
                    value={(editedData as any)[field] || ""}
                    onChange={(e) => handleUpdate(field, e.target.value)}
                    className="text-sm font-semibold text-foreground bg-secondary/50 border border-border rounded-md px-2 py-1 sm:max-w-xs w-full focus:outline-none focus:ring-1 focus:ring-primary/30"
                  >
                    <option value="">Select {label}</option>
                    {visaCountryOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                ) : isEditing ? (
                  field === 'visaStatus' ? (
                    <select
                      value={(editedData as any)[field] || ''}
                      onChange={(e) => handleUpdate(field as any, e.target.value)}
                      className="text-sm font-semibold text-foreground bg-secondary/50 border border-border rounded-md px-2 py-1 sm:max-w-xs w-full focus:outline-none focus:ring-1 focus:ring-primary/30"
                    >
                      <option value="">Select Status</option>
                      <option value="Active">Active</option>
                      <option value="Expired">Expired</option>
                    </select>
                  ) : (
                    <input
                      type={field.includes("Date") || field.includes("Expiry") ? "date" : "text"}
                      value={(editedData as any)[field] || ""}
                      onChange={(e) => handleUpdate(field, e.target.value)}
                      className="text-sm font-semibold text-foreground bg-secondary/50 border border-border rounded-md px-2 py-1 sm:max-w-xs w-full focus:outline-none focus:ring-1 focus:ring-primary/30"
                    />
                  )
                ) : (
                  <span className="text-sm font-semibold text-foreground">
                    {field.includes("Date") || field === "visaExpiry"
                      ? (editedData as any)[field]
                        ? new Date((editedData as any)[field]).toLocaleDateString("en-IN", {
                            day: "2-digit",
                            month: "long",
                            year: "numeric",
                          })
                        : "—"
                      : (editedData as any)[field] || "—"}
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-background border border-dashed border-border rounded-lg p-10 text-center">
            <BookOpen className="w-8 h-8 mx-auto mb-3 text-muted-foreground opacity-30" />
            <p className="text-sm font-medium text-muted-foreground">No visa information available</p>
          </div>
        )}
      </div>
    </div>
  );
}
