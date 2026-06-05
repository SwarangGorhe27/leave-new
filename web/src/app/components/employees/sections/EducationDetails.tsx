import { useEffect, useMemo, useState } from "react";
import { GraduationCap, Plus } from "lucide-react";
import { EducationEntry, Employee } from "../mockData";
import { useAdminSync } from "../../admin/useAdminSync";
import {
  EditableFormCard,
  EditableSectionCard,
  ProfileInfoField,
  EmptyStateCard,
  ConfirmationDialog,
  validateDateOrder,
  validatePercentageCgpa,
} from "../employee-details";
import { useMasterOptions } from "./useMasterOptions";

interface Props {
  employee: Employee;
  showAddButton?: boolean;
}

const emptyEdu = (): EducationEntry => ({
  qualification: "",
  specialization: "",
  institutionName: "",
  university: "",
  fromDate: "",
  toDate: "",
  percentageCgpa: "",
  grade: "",
});

export function EducationDetails({ employee, showAddButton = true }: Props) {
  const { handleAdminSave, handleToggleEditAccess } = useAdminSync();
  const qualificationOptions = useMasterOptions("Qualification");
  const specializationOptions = useMasterOptions("EducationSpecialization");
  const boardOptions = useMasterOptions("Board");
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState<EducationEntry[]>(employee.education || []);
  const [deleteIndex, setDeleteIndex] = useState<number | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const baseline = useMemo(() => employee.education || [], [employee.education]);

  useEffect(() => {
    if (!isEditing) setDraft(baseline);
  }, [baseline, isEditing]);

  const updateRow = (index: number, patch: Partial<EducationEntry>) => {
    setDraft((rows) => rows.map((r, i) => (i === index ? { ...r, ...patch } : r)));
  };

  const startEdit = () => {
    if (!baseline.length) return;
    setDraft([...baseline]);
    setFormError(null);
    setIsEditing(true);
  };

  const addRow = () => {
    setDraft((rows) => [...(isEditing ? rows : baseline), emptyEdu()]);
    setFormError(null);
    setIsEditing(true);
  };

  const confirmDelete = () => {
    if (deleteIndex === null) return;
    setDraft((rows) => rows.filter((_, i) => i !== deleteIndex));
    setDeleteIndex(null);
  };

  const handleSave = async () => {
    for (let i = 0; i < draft.length; i++) {
      const row = draft[i];
      const hasAny = Object.values(row).some((v) => String(v).trim() !== "");
      if (!hasAny) continue;
      const dErr = validateDateOrder(row.fromDate || "", row.toDate || "");
      if (dErr) {
        setFormError(`Education ${i + 1}: ${dErr}`);
        return;
      }
      const pErr = validatePercentageCgpa(row.percentageCgpa);
      if (pErr) {
        setFormError(`Education ${i + 1}: ${pErr}`);
        return;
      }
    }
    setFormError(null);
    const savedEducation = draft.filter((r) => Object.values(r).some((v) => String(v).trim() !== ""));
    const updated = { ...employee, education: savedEducation };
    const ok = await handleAdminSave("Education Details", employee, updated);
    if (ok) {
      setDraft(savedEducation);
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setDraft(baseline);
    setFormError(null);
    setIsEditing(false);
  };

  const isEditable = employee.editableSections?.includes("education-details");
  const displayRows = isEditing ? draft : baseline;

  return (
    <div className="space-y-5 pb-24">
      <div>
        <h2 className="text-lg font-bold text-foreground">Education Details</h2>
        <p className="text-sm text-muted-foreground mt-1">Academic qualifications for {employee.name}</p>
      </div>

      <EditableSectionCard
        title="Education Details"
        icon={GraduationCap}
        sectionId="education-details"
        canEmployeeEdit={isEditable}
        onToggleEmployeeEdit={(v) => handleToggleEditAccess(employee, "education-details", v)}
        requestStatus={employee.editRequestStatus}
        isEditing={isEditing}
        onEdit={startEdit}
        editDisabled={!baseline.length}
        onSave={handleSave}
        onCancel={handleCancel}
        headerExtra={showAddButton ? (
          <button
            type="button"
            onClick={addRow}
            className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs font-bold transition-colors hover:bg-secondary"
          >
            <Plus className="h-3.5 w-3.5" />
            Add New
          </button>
        ) : null}
      >
        {formError ? <p className="text-sm text-destructive mb-3">{formError}</p> : null}
        {!displayRows.length ? (
          <EmptyStateCard
            icon={GraduationCap}
            title="No education records"
            description={
              showAddButton
                ? "Use Add New to add a qualification, or Edit after records exist."
                : "No education records on file. Edit is available when records exist."
            }
          />
        ) : (
          <div className="space-y-4">
            {displayRows.map((row, index) => (
              <EditableFormCard
                key={`edu-${index}-${row.institutionName}`}
                showDelete={isEditing}
                onDelete={() => setDeleteIndex(index)}
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <ProfileInfoField
                    label="Qualification"
                    value={row.qualification}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { qualification: v })}
                    options={qualificationOptions}
                  />
                  <ProfileInfoField
                    label="Specialization"
                    value={row.specialization}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { specialization: v })}
                    options={specializationOptions}
                  />
                  <ProfileInfoField
                    label="Institution Name"
                    value={row.institutionName}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { institutionName: v })}
                  />
                  <ProfileInfoField
                    label="University"
                    value={row.university}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { university: v })}
                    options={boardOptions}
                  />
                  <ProfileInfoField
                    label="From"
                    value={row.fromDate || ''}
                    editing={isEditing}
                    type="date"
                    onChange={(v) => updateRow(index, { fromDate: v })}
                  />
                  <ProfileInfoField
                    label="To"
                    value={row.toDate || ''}
                    editing={isEditing}
                    type="date"
                    onChange={(v) => updateRow(index, { toDate: v })}
                  />
                  <ProfileInfoField
                    label="Percentage / CGPA"
                    value={row.percentageCgpa}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { percentageCgpa: v })}
                  />
                  <div className="md:col-span-2 max-w-md">
                    <ProfileInfoField
                      label="Grade"
                      value={row.grade}
                      editing={isEditing}
                      onChange={(v) => updateRow(index, { grade: v })}
                    />
                  </div>
                </div>
              </EditableFormCard>
            ))}
          </div>
        )}
      </EditableSectionCard>

      <ConfirmationDialog
        open={deleteIndex !== null}
        onOpenChange={(o) => !o && setDeleteIndex(null)}
        title="Remove education entry?"
        description="This qualification row will be removed. Save the section to persist."
        confirmLabel="Remove"
        destructive
        onConfirm={confirmDelete}
      />
    </div>
  );
}
