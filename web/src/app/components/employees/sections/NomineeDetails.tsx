import { useEffect, useMemo, useState } from "react";
import { Users, Plus } from "lucide-react";
import { Employee, NomineeEntry } from "../mockData";
import { useAdminSync } from "../../admin/useAdminSync";
import {
  EditableSectionCard,
  ProfileInfoField,
  UploadField,
  EmptyStateCard,
} from "../employee-details";
import { useMasterOptions } from "./useMasterOptions";
import { validateEmail, validateMobile } from "../employee-details/employeeValidation";

interface Props {
  employee: Employee;
  showAddButton?: boolean;
}

const RELATIONSHIP_OPTIONS = [
  { value: "Spouse", label: "Spouse" },
  { value: "Father", label: "Father" },
  { value: "Mother", label: "Mother" },
  { value: "Son", label: "Son" },
  { value: "Daughter", label: "Daughter" },
  { value: "Brother", label: "Brother" },
  { value: "Sister", label: "Sister" },
  { value: "Other", label: "Other" },
];

const NOMINEE_TYPES = [
  { value: 'EPF', label: 'EPF' },
  { value: 'EPS', label: 'EPS' },
  { value: 'Gratuity', label: 'Gratuity' },
  { value: 'Custom', label: 'Custom' },
];

function emptyNominee(): NomineeEntry {
  return {
    id: `nom-${Date.now()}`,
    nomineeName: "",
    nomineeEmail: "",
    relationship: "",
    dateOfBirth: "",
    contactNumber: "",
    address: "",
    nomineeType: 'EPF',
    epfPercentage: "",
    epsPercentage: "",
    gratuityPercentage: "",
    customPercentage: "",
    isMinor: false,
    guardian: {},
    idProofFileName: "",
    idProofDataUrl: "",
  };
}

function validateNominees(nominees: NomineeEntry[]): {
  rowErrors: Record<number, Record<string, string>>;
  formError: string | null;
} {
  const rowErrors: Record<number, Record<string, string>> = {};
  const totals: Record<string, number> = { EPF: 0, EPS: 0, Gratuity: 0, Custom: 0 };

  nominees.forEach((n, idx) => {
    const row: Record<string, string> = {};
    if (!n.nomineeName || !n.nomineeName.trim()) row.nomineeName = "Nominee name is required";
    if (!n.relationship || !n.relationship.trim()) row.relationship = "Relationship is required";
    if (n.nomineeEmail && validateEmail(n.nomineeEmail)) row.nomineeEmail = validateEmail(n.nomineeEmail) || undefined as any;
    const mErr = validateMobile(n.contactNumber || "");
    if (mErr) row.contactNumber = mErr;

    // Percentage checks per chosen nomineeType
    const type = n.nomineeType || 'EPF';
    const parsePct = (v?: string) => {
      if (!v) return 0;
      const num = Number(v);
      return Number.isNaN(num) ? NaN : num;
    };

    const pctFields = {
      EPF: parsePct(n.epfPercentage),
      EPS: parsePct(n.epsPercentage),
      Gratuity: parsePct(n.gratuityPercentage),
      Custom: parsePct(n.customPercentage),
    } as Record<string, number>;

    const chosenPct = pctFields[type];
    if (Number.isNaN(chosenPct) || chosenPct < 0 || chosenPct > 100) {
      row[`${type}Percentage`] = "Enter a value between 0 and 100";
    } else {
      totals[type] += chosenPct;
    }

    // Minor nominee guardian validation
    if (n.isMinor) {
      const g = n.guardian || {};
      if (!g.guardianName || !g.guardianName.trim()) row.guardianName = "Guardian name required for minor";
      if (!g.relationshipWithMinor || !g.relationshipWithMinor.trim()) row.guardianRelationship = "Relationship with minor required";
      const gMobileErr = validateMobile(g.contactNumber || "");
      if (gMobileErr) row.guardianContactNumber = gMobileErr;
      if (!g.address || !g.address.trim()) row.guardianAddress = "Guardian address required";
    }

    if (Object.keys(row).length) rowErrors[idx] = row;
  });

  // Form-level validation: ensure no type exceeds 100
  const overType = Object.entries(totals).find(([k, v]) => v > 100);
  const formError = overType ? `${overType[0]} allocation exceeds 100% (currently ${overType[1]}%)` : null;

  return { rowErrors, formError };
}

export function NomineeDetails({ employee, showAddButton = true }: Props) {
  const { handleAdminSave, handleToggleEditAccess } = useAdminSync();
  const relationOptions = useMasterOptions("Relation");
  const [isEditing, setIsEditing] = useState(false);
  const baseline = useMemo(() => employee.nominees || [], [employee.nominees]);
  const [nominees, setNominees] = useState<NomineeEntry[]>(baseline);
  const [rowErrors, setRowErrors] = useState<Record<number, Record<string, string>>>({});
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!isEditing) setNominees(baseline);
  }, [baseline, isEditing]);

  const isEditable = employee.editableSections?.includes("nominee-details");

  const startEdit = () => {
    if (!baseline.length) return;
    setNominees([...baseline]);
    setRowErrors({});
    setFormError(null);
    setIsEditing(true);
  };

  const handleSave = async () => {
    const rowsToSave = nominees.filter(
      (n) =>
        (n.nomineeName && n.nomineeName.trim()) ||
        (n.relationship && n.relationship.trim()) ||
        (n.contactNumber && n.contactNumber.trim()),
    );
    const { rowErrors: nextRowErrors, formError: nextFormError } = validateNominees(rowsToSave);
    if (Object.keys(nextRowErrors).length || nextFormError) {
      setRowErrors(nextRowErrors);
      setFormError(nextFormError);
      return;
    }
    const ok = await handleAdminSave("Nominee Details", employee, { ...employee, nominees: rowsToSave });
    if (ok) {
      setNominees(rowsToSave);
      setRowErrors({});
      setFormError(null);
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setNominees(baseline);
    setRowErrors({});
    setFormError(null);
    setIsEditing(false);
  };

  const updateNominee = (idx: number, patch: Partial<NomineeEntry>) => {
    setNominees((rows) => rows.map((r, i) => (i === idx ? { ...r, ...patch } : r)));
    if (rowErrors[idx]) {
      setRowErrors((prev) => {
        const next = { ...prev };
        delete next[idx];
        return next;
      });
    }
    if (formError) setFormError(null);
  };

  const addNominee = () => {
    setNominees((rows) => [...(isEditing ? rows : baseline), emptyNominee()]);
    setRowErrors({});
    setFormError(null);
    setIsEditing(true);
  };

  const displayNominees = isEditing ? nominees : baseline;

  const computeTotals = (rows: NomineeEntry[]) => {
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
    <div className="space-y-5 pb-24">
      <div>
        <h2 className="text-lg font-bold text-foreground">Nominee Details</h2>
        <p className="text-sm text-muted-foreground mt-1">Manage nominees for {employee.name}</p>
      </div>

      <EditableSectionCard
        title="Nominee Details"
        icon={Users}
        sectionId="nominee-details"
        canEmployeeEdit={isEditable}
        onToggleEmployeeEdit={(v) => handleToggleEditAccess(employee, "nominee-details", v)}
        requestStatus={employee.editRequestStatus}
        isEditing={isEditing}
        onEdit={startEdit}
        editDisabled={!baseline.length}
        onCancel={handleCancel}
        onSave={handleSave}
        headerExtra={showAddButton ? (
          <button
            type="button"
            onClick={addNominee}
            className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs font-bold transition-colors hover:bg-secondary"
          >
            <Plus className="h-3.5 w-3.5" />
            Add New
          </button>
        ) : null}
      >
        {formError ? (
          <p className="mb-4 text-sm text-destructive font-medium">{formError}</p>
        ) : null}
        {!displayNominees.length ? (
          <EmptyStateCard
            icon={Users}
            title="No nominees on file"
            description={
              showAddButton
                ? "Use Add New to add a nominee, or Edit after records exist."
                : "No nominees on file. Edit is available when records exist."
            }
          />
        ) : (
          <div className="space-y-6">
            {displayNominees.map((n, idx) => {
              const totals = computeTotals(nominees);
              const remainingFor = (type: string) => Math.max(
                0,
                100 - (totals[type] - (type === 'EPF' ? Number(n.epfPercentage || 0) : type === 'EPS' ? Number(n.epsPercentage || 0) : type === 'Gratuity' ? Number(n.gratuityPercentage || 0) : Number(n.customPercentage || 0)))
              );

              const handlePctChange = (field: 'epfPercentage' | 'epsPercentage' | 'gratuityPercentage' | 'customPercentage', value: string) => {
                const num = Number(value);
                if (value.trim() === "") {
                  updateNominee(idx, { [field]: value } as any);
                  setRowErrors((prev) => {
                    const next = { ...prev };
                    if (next[idx]) delete next[idx][field];
                    return next;
                  });
                  return;
                }
                if (Number.isNaN(num) || num < 0) {
                  setRowErrors((prev) => ({ ...prev, [idx]: { ...(prev[idx] || {}), [field]: 'Enter a valid number' } }));
                  return;
                }
                const type = field === 'epfPercentage' ? 'EPF' : field === 'epsPercentage' ? 'EPS' : field === 'gratuityPercentage' ? 'Gratuity' : 'Custom';
                const remaining = remainingFor(type);
                if (num > remaining) {
                  // Cap the value to remaining and show a validation note
                  const capped = remaining;
                  updateNominee(idx, { [field]: String(capped) } as any);
                  setRowErrors((prev) => ({ ...prev, [idx]: { ...(prev[idx] || {}), [field]: `Value capped to available ${remaining}%` } }));
                  return;
                }
                // valid
                updateNominee(idx, { [field]: String(num) } as any);
                setRowErrors((prev) => {
                  const next = { ...prev };
                  if (next[idx]) delete next[idx][field];
                  return next;
                });
              };

              return (
                <div key={n.id} className="rounded-2xl border border-border bg-secondary/10 p-6 space-y-6">
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    <ProfileInfoField
                      label="Nominee Name"
                      value={n.nomineeName}
                      editing={isEditing}
                      error={rowErrors[idx]?.nomineeName}
                      onChange={(v) => updateNominee(idx, { nomineeName: v })}
                    />

                    <ProfileInfoField
                      label="Nominee Email"
                      value={n.nomineeEmail || ''}
                      editing={isEditing}
                      type="email"
                      error={rowErrors[idx]?.nomineeEmail}
                      onChange={(v) => updateNominee(idx, { nomineeEmail: v })}
                    />

                    <ProfileInfoField
                      label="Relationship"
                      value={n.relationship}
                      editing={isEditing}
                      options={relationOptions.length ? relationOptions : RELATIONSHIP_OPTIONS}
                      error={rowErrors[idx]?.relationship}
                      onChange={(v) => updateNominee(idx, { relationship: v })}
                    />

                    <ProfileInfoField
                      label="Date Of Birth"
                      value={n.dateOfBirth}
                      editing={isEditing}
                      type="date"
                      onChange={(v) => updateNominee(idx, { dateOfBirth: v })}
                    />

                    <ProfileInfoField
                      label="Contact Number"
                      value={n.contactNumber}
                      editing={isEditing}
                      type="tel"
                      error={rowErrors[idx]?.contactNumber}
                      onChange={(v) => updateNominee(idx, { contactNumber: v })}
                    />

                    <div className="sm:col-span-2">
                      <ProfileInfoField
                        label="Address"
                        value={n.address}
                        editing={isEditing}
                        type="textarea"
                        onChange={(v) => updateNominee(idx, { address: v })}
                      />
                    </div>

                    <ProfileInfoField
                      label="Nominee Type"
                      value={n.nomineeType || 'EPF'}
                      editing={isEditing}
                      options={NOMINEE_TYPES.map(t => {
                        const currentPct = t.value === 'EPF' ? Number(n.epfPercentage || 0) : t.value === 'EPS' ? Number(n.epsPercentage || 0) : t.value === 'Gratuity' ? Number(n.gratuityPercentage || 0) : Number(n.customPercentage || 0);
                        return { value: t.value, label: t.label, disabled: totals[t.value] >= 100 && currentPct <= 0 };
                      })}
                      onChange={(v) => {
                        const rem = remainingFor(v);
                        const currentPct = v === 'EPF' ? Number(n.epfPercentage || 0) : v === 'EPS' ? Number(n.epsPercentage || 0) : v === 'Gratuity' ? Number(n.gratuityPercentage || 0) : Number(n.customPercentage || 0);
                        if (rem <= 0 && currentPct <= 0) {
                          setRowErrors((prev) => ({ ...prev, [idx]: { ...(prev[idx] || {}), nomineeType: 'No allocation available for selected type' } }));
                          return;
                        }
                        updateNominee(idx, { nomineeType: v });
                      }}
                    />

                    {/* Percentage inputs: show only the field relevant to nomineeType */}
                    { (n.nomineeType || 'EPF') === 'EPF' && (
                      <ProfileInfoField
                        label="EPF (%)"
                        value={n.epfPercentage || ''}
                        editing={isEditing}
                        type="number"
                        error={rowErrors[idx]?.EPFPercentage || rowErrors[idx]?.epfPercentage}
                        onChange={(v) => handlePctChange('epfPercentage', v)}
                      />
                    )}
                    { (n.nomineeType || 'EPF') === 'EPS' && (
                      <ProfileInfoField
                        label="EPS (%)"
                        value={n.epsPercentage || ''}
                        editing={isEditing}
                        type="number"
                        error={rowErrors[idx]?.EPSPercentage || rowErrors[idx]?.epsPercentage}
                        onChange={(v) => handlePctChange('epsPercentage', v)}
                      />
                    )}
                    { (n.nomineeType || 'EPF') === 'Gratuity' && (
                      <ProfileInfoField
                        label="Gratuity (%)"
                        value={n.gratuityPercentage || ''}
                        editing={isEditing}
                        type="number"
                        error={rowErrors[idx]?.GratuityPercentage || rowErrors[idx]?.gratuityPercentage}
                        onChange={(v) => handlePctChange('gratuityPercentage', v)}
                      />
                    )}
                    { (n.nomineeType || 'EPF') === 'Custom' && (
                      <ProfileInfoField
                        label="Custom (%)"
                        value={n.customPercentage || ''}
                        editing={isEditing}
                        type="number"
                        error={rowErrors[idx]?.CustomPercentage || rowErrors[idx]?.customPercentage}
                        onChange={(v) => handlePctChange('customPercentage', v)}
                      />
                    )}

                    <div className="sm:col-span-2">
                      <UploadField
                        label="ID Proof Upload"
                        fileName={n.idProofFileName}
                        dataUrl={n.idProofDataUrl}
                        editing={isEditing}
                        onFileChange={(name, data) =>
                          updateNominee(idx, { idProofFileName: name, idProofDataUrl: data })
                        }
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <label className="flex items-center gap-2">
                      <input type="checkbox" checked={!!n.isMinor} onChange={(e) => updateNominee(idx, { isMinor: !!e.target.checked })} />
                      <span className="text-sm font-medium">Is Minor Nominee?</span>
                    </label>
                  </div>

                  {n.isMinor ? (
                    <div className="pt-4 border-t border-border space-y-4">
                      <h4 className="text-sm font-bold">Guardian Details</h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <ProfileInfoField
                          label="Guardian Name"
                          value={n.guardian?.guardianName || ''}
                          editing={isEditing}
                          error={rowErrors[idx]?.guardianName}
                          onChange={(v) => updateNominee(idx, { guardian: { ...(n.guardian || {}), guardianName: v } })}
                        />
                        <ProfileInfoField
                          label="Relationship With Minor"
                          value={n.guardian?.relationshipWithMinor || ''}
                          editing={isEditing}
                          error={rowErrors[idx]?.guardianRelationship}
                          onChange={(v) => updateNominee(idx, { guardian: { ...(n.guardian || {}), relationshipWithMinor: v } })}
                        />
                        <ProfileInfoField
                          label="Contact Number"
                          value={n.guardian?.contactNumber || ''}
                          editing={isEditing}
                          type="tel"
                          error={rowErrors[idx]?.guardianContactNumber}
                          onChange={(v) => updateNominee(idx, { guardian: { ...(n.guardian || {}), contactNumber: v } })}
                        />
                        <ProfileInfoField
                          label="Guardian DOB"
                          value={n.guardian?.dateOfBirth || ''}
                          editing={isEditing}
                          type="date"
                          onChange={(v) => updateNominee(idx, { guardian: { ...(n.guardian || {}), dateOfBirth: v } })}
                        />
                        <div className="sm:col-span-2">
                          <ProfileInfoField
                            label="Guardian Address"
                            value={n.guardian?.address || ''}
                            editing={isEditing}
                            type="textarea"
                            error={rowErrors[idx]?.guardianAddress}
                            onChange={(v) => updateNominee(idx, { guardian: { ...(n.guardian || {}), address: v } })}
                          />
                        </div>
                        <div className="sm:col-span-2">
                          <UploadField
                            label="Guardian ID Proof Upload"
                            fileName={n.guardian?.idProofFileName}
                            dataUrl={n.guardian?.idProofDataUrl}
                            editing={isEditing}
                            onFileChange={(name, data) => updateNominee(idx, { guardian: { ...(n.guardian || {}), idProofFileName: name, idProofDataUrl: data } })}
                          />
                        </div>
                      </div>
                    </div>
                  ) : null}

                  {isEditing && displayNominees.length > 1 ? (
                    <button
                      type="button"
                      className="text-xs font-semibold text-destructive hover:underline"
                      onClick={() => setNominees((rows) => rows.filter((_, i) => i !== idx))}
                    >
                      Remove nominee
                    </button>
                  ) : null}
                </div>
              );
            })}
          </div>
        )}
      </EditableSectionCard>
    </div>
  );
}
