import { useEffect, useMemo, useState } from "react";
import { Employee } from "../mockData";
import { Users, User, AlertCircle, ShieldCheck, Edit2, Save, X, Plus } from "lucide-react";
import { useAdminSync } from "../../admin/useAdminSync";
import { useMasterOptions } from "./useMasterOptions";

interface Props {
  employee: Employee;
  essMode?: boolean;
  showAddButton?: boolean;
}

function normalizeDobForInput(value?: string): string {
  const raw = value?.trim();
  if (!raw || raw === "—") return "";
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw;
  const parsed = new Date(raw);
  if (!Number.isNaN(parsed.getTime())) {
    return parsed.toISOString().slice(0, 10);
  }
  const match = raw.match(/^(\d{2})[-/](\d{2})[-/](\d{4})$/);
  if (match) {
    const [, day, month, year] = match;
    return `${year}-${month}-${day}`;
  }
  return "";
}

function formatDobDisplay(value?: string): string {
  const iso = normalizeDobForInput(value);
  if (!iso) return "—";
  const date = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(date.getTime())) return value?.trim() || "—";
  return date.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

function calculateAgeFromDob(dob?: string): number | null {
  const iso = normalizeDobForInput(dob);
  if (!iso) return null;
  const birth = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(birth.getTime())) return null;
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age -= 1;
  }
  return age >= 0 ? age : null;
}

const todayIso = () => new Date().toISOString().slice(0, 10);

const RELATIONSHIP_SHADES: Record<string, string> = {
  Spouse: "bg-rose-500/10 text-rose-600 border-rose-500/20",
  Father: "bg-blue-500/10 text-blue-600 border-blue-500/20",
  Mother: "bg-purple-500/10 text-purple-600 border-purple-500/20",
  Son: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20",
  Daughter: "bg-pink-500/10 text-pink-600 border-pink-500/20",
};

function StatusBadge({ icon: Icon, label, active }: { icon: any, label: string, active: boolean }) {
  if (!active) return null;
  return (
    <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-foreground/5 border border-border text-[10px] font-bold text-foreground/70 uppercase tracking-tight">
      <Icon size={11} className="text-emerald-500" />
      {label}
    </div>
  );
}

function EditableField({
  label,
  value,
  onChange,
  isEditing,
  options,
  inputType = "text",
  max,
  readOnly = false,
}: {
  label: string;
  value: string;
  onChange?: (v: string) => void;
  isEditing: boolean;
  options?: Array<{ value: string; label: string }>;
  inputType?: "text" | "date";
  max?: string;
  readOnly?: boolean;
}) {
  const selectOptions = options
    ? options.some((option) => option.value === value) || !value
      ? options
      : [{ value, label: value }, ...options]
    : undefined;

  return (
    <div className="flex flex-col gap-1">
      <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">{label}</span>
      {isEditing && selectOptions?.length ? (
        <select
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          title={label}
          className="text-xs font-bold text-foreground bg-secondary/50 border border-border rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary/30"
        >
          <option value="">Select {label}</option>
          {selectOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : isEditing && !readOnly ? (
        <input
          type={inputType}
          value={value}
          max={inputType === "date" ? max : undefined}
          onChange={(e) => onChange?.(e.target.value)}
          placeholder={inputType === "date" ? undefined : label}
          className="text-xs font-bold text-foreground bg-secondary/50 border border-border rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary/30"
        />
      ) : (
        <span className="text-xs font-bold text-foreground truncate">{value || "—"}</span>
      )}
    </div>
  );
}

export function FamilyDetails({ employee, showAddButton = true }: Props) {
  const relationOptions = useMasterOptions("Relation");
  const genderOptions = useMasterOptions("Gender");
  const bloodGroupOptions = useMasterOptions("BloodGroup");
  const [isEditing, setIsEditing] = useState(false);
  const [editedFamily, setEditedFamily] = useState(employee.family || []);
  const { handleAdminSave } = useAdminSync();
  const baseline = useMemo(() => employee.family || [], [employee.family]);

  useEffect(() => {
    if (!isEditing) {
      setEditedFamily(baseline);
    }
  }, [baseline, isEditing]);

  const updateMember = (idx: number, field: string, value: any) => {
    setEditedFamily(prev => prev.map((m, i) => i === idx ? { ...m, [field]: value } : m));
  };

  const startEdit = () => {
    if (!baseline.length) return;
    setEditedFamily([...baseline]);
    setIsEditing(true);
  };

  const addFamilyMember = () => {
    setEditedFamily((prev) => [
      ...(isEditing ? prev : baseline),
      {
        name: "",
        relationship: "",
        dob: "",
        gender: "",
        bloodGroup: "",
        phone: "",
        occupation: "",
        isDependent: false,
        isEmergencyContact: false,
      },
    ]);
    setIsEditing(true);
  };

  const handleSave = async () => {
    const updatedEmployee = { ...employee, family: editedFamily };
    const success = await handleAdminSave('Family Details', employee, updatedEmployee);
    if (success) {
      setEditedFamily(editedFamily);
      setIsEditing(false);
    }
  };

  const isEditable = employee.editableSections?.includes("family-details");
  const getStatusLabel = () => {
    if (employee.editRequestStatus === 'Pending') return { l: 'Pending Employee Update', c: 'bg-amber-500/10 text-amber-600 border-amber-200' };
    if (employee.editRequestStatus === 'Updated') return { l: 'Updated by Employee', c: 'bg-emerald-500/10 text-emerald-600 border-emerald-200' };
    if (isEditable) return { l: 'Editable by Employee', c: 'bg-indigo-500/10 text-indigo-600 border-indigo-200' };
    return { l: '', c: '' };
  };

  const status = getStatusLabel();
  const displayFamily = isEditing ? editedFamily : baseline;
  const canEdit = baseline.length > 0;

  return (
    <div className="flex flex-col gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-24">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div>
            <h2 className="text-xl font-black text-foreground flex items-center gap-2.5">
              <Users size={20} className="text-indigo-500" />
              Family & Dependents
            </h2>
            <p className="text-xs font-bold text-muted-foreground mt-1 uppercase tracking-widest">
              {displayFamily.length} Registered Members
            </p>
          </div>
          {status.l ? (
            <span className={`text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded border transition-all ${status.c}`}>
              {status.l}
            </span>
          ) : null}
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            {isEditing ? (
              <>
                <button onClick={handleSave} className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-bold transition-all hover:bg-primary/90">
                  <Save size={12} /> Save Changes
                </button>
                <button onClick={() => { setEditedFamily(baseline); setIsEditing(false); }}
                  className="flex items-center gap-1.5 px-3 py-1.5 border border-border rounded-lg text-xs font-bold transition-all hover:bg-secondary">
                  <X size={12} /> Cancel
                </button>
              </>
            ) : (
              <>
                {showAddButton ? (
                  <button onClick={addFamilyMember} className="flex items-center gap-1.5 px-3 py-1.5 border border-border rounded-lg text-xs font-bold transition-all hover:bg-secondary">
                    <Plus size={12} /> Add New
                  </button>
                ) : null}
                <button
                  onClick={startEdit}
                  disabled={!canEdit}
                  title={!canEdit ? (showAddButton ? "Add a family member first using Add New" : "No family members on file to edit") : undefined}
                  className={`flex items-center gap-1.5 px-3 py-1.5 border border-border rounded-lg text-xs font-bold transition-all ${canEdit ? "hover:bg-secondary" : "opacity-50 cursor-not-allowed"}`}
                >
                  <Edit2 size={12} /> Edit Section
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {displayFamily.map((member, index) => {
          const badgeStyle = RELATIONSHIP_SHADES[member.relationship] || "bg-secondary text-muted-foreground border-border";
          const dobIso = normalizeDobForInput(member.dob);
          const ageYears = calculateAgeFromDob(member.dob);
          const ageDisplay = ageYears !== null ? `${ageYears} Years` : "—";

          return (
            <div key={index} className="group relative bg-card border border-border rounded-3xl p-6 transition-all duration-300 hover:shadow-2xl hover:shadow-foreground/5 hover:-translate-y-1 overflow-hidden">
              <div className={`absolute top-0 left-0 w-1.5 h-full ${badgeStyle.split(' ')[0]}`} />
              
              <div className="flex flex-col sm:flex-row gap-6">
                <div className="flex flex-col items-center gap-3">
                  <div className="w-16 h-16 rounded-2xl bg-secondary flex items-center justify-center border border-border shadow-inner group-hover:scale-105 transition-transform duration-300">
                    <User size={28} className="text-muted-foreground/40" />
                  </div>
                  <span className={`text-[10px] font-black px-3 py-1 rounded-full border uppercase tracking-widest ${badgeStyle}`}>
                    {member.relationship}
                  </span>
                </div>

                <div className="flex-1">
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex-1">
                      <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Name</span>
                      {isEditing ? (
                        <input type="text" value={member.name} onChange={e => updateMember(index, 'name', e.target.value)}
                          placeholder="Enter family member name"
                          className="w-full text-base font-black text-foreground bg-secondary/50 border border-border rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary/30 mb-2" />
                      ) : (
                        <h4 className="text-base font-black text-foreground">{member.name || "—"}</h4>
                      )}
                      <div className="flex flex-wrap gap-2 mt-2">
                        <StatusBadge icon={ShieldCheck} label="Dependent" active={member.isDependent} />
                        <StatusBadge icon={AlertCircle} label="Emergency Contact" active={member.isEmergencyContact} />
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-y-6 gap-x-8">
                    <EditableField
                      label="Date of Birth"
                      isEditing={isEditing}
                      inputType="date"
                      max={todayIso()}
                      value={isEditing ? dobIso : formatDobDisplay(member.dob)}
                      onChange={(v) => updateMember(index, "dob", v)}
                    />
                    <EditableField label="Relationship" isEditing={isEditing} value={member.relationship} onChange={v => updateMember(index, 'relationship', v)} options={relationOptions} />
                    <EditableField label="Gender" isEditing={isEditing} value={member.gender} onChange={v => updateMember(index, 'gender', v)} options={genderOptions} />
                    <EditableField label="Age" isEditing={isEditing} readOnly value={ageDisplay} />
                    <EditableField label="Blood Group" isEditing={isEditing} value={member.bloodGroup} onChange={v => updateMember(index, 'bloodGroup', v)} options={bloodGroupOptions} />
                    <EditableField label="Phone" isEditing={isEditing} value={member.phone} onChange={v => updateMember(index, 'phone', v)} />
                    <EditableField label="Occupation" isEditing={isEditing} value={member.occupation} onChange={v => updateMember(index, 'occupation', v)} />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {displayFamily.length === 0 && (
        <div className="flex flex-col items-center justify-center p-16 border-2 border-dashed border-border rounded-[2rem] bg-secondary/5 text-center animate-in zoom-in-95 duration-500">
          <div className="w-16 h-16 rounded-2xl bg-secondary flex items-center justify-center mb-4">
            <Users size={32} className="text-muted-foreground/30" />
          </div>
          <p className="text-sm font-bold text-muted-foreground">No family details added yet.</p>
          <p className="text-xs text-muted-foreground/60 mt-1 uppercase tracking-widest">
            {showAddButton ? "Use Add New to add a family member" : "No family members on file"}
          </p>
        </div>
      )}
    </div>
  );
}
