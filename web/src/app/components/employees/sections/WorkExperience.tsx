import { useEffect, useMemo, useState } from "react";
import { Building2, Plus } from "lucide-react";
import { Employee, WorkExperienceEntry } from "../mockData";
import { useAdminSync } from "../../admin/useAdminSync";
import {
  EditableFormCard,
  EditableSectionCard,
  ProfileInfoField,
  EmptyStateCard,
  UploadField,
  ConfirmationDialog,
  validateDateOrder,
} from "../employee-details";
import { useMasterOptions } from "./useMasterOptions";

const emptyWorkExperience = (): WorkExperienceEntry => ({
  id: `we-${Date.now()}`,
  companyName: "",
  jobTitle: "",
  employmentType: "",
  department: "",
  responsibilities: "",
  technologiesUsed: "",
  location: "",
  experienceLetterFileName: "",
  experienceLetterDataUrl: "",
  reasonForLeaving: "",
  startDate: "",
  endDate: "",
});

interface Props {
  employee: Employee;
  showAddButton?: boolean;
}

export function WorkExperience({ employee, showAddButton = true }: Props) {
  const { handleAdminSave, handleToggleEditAccess } = useAdminSync();
  const employeeTypeOptions = useMasterOptions("EmployeeType");
  const departmentOptions = useMasterOptions("Department");
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState<WorkExperienceEntry[]>(employee.workExperience || []);
  const [deleteIndex, setDeleteIndex] = useState<number | null>(null);
  const [dateError, setDateError] = useState<string | null>(null);

  const baseline = useMemo(() => employee.workExperience || [], [employee.workExperience]);

  useEffect(() => {
    if (!isEditing) setDraft(baseline);
  }, [baseline, isEditing]);

  const updateRow = (index: number, patch: Partial<WorkExperienceEntry>) => {
    setDraft((rows) => rows.map((r, i) => (i === index ? { ...r, ...patch } : r)));
  };

  const startEdit = () => {
    if (!baseline.length) return;
    setDraft([...baseline]);
    setDateError(null);
    setIsEditing(true);
  };

  const addRow = () => {
    setDraft((rows) => [...(isEditing ? rows : baseline), emptyWorkExperience()]);
    setDateError(null);
    setIsEditing(true);
  };

  const confirmDelete = () => {
    if (deleteIndex === null) return;
    setDraft((rows) => rows.filter((_, i) => i !== deleteIndex));
    setDeleteIndex(null);
  };

  const handleSave = async () => {
    for (let i = 0; i < draft.length; i++) {
      const err = validateDateOrder(draft[i].startDate, draft[i].endDate);
      if (err) {
        setDateError(`Row ${i + 1}: ${err}`);
        return;
      }
    }
    setDateError(null);
    const updated = { ...employee, workExperience: draft };
    const ok = await handleAdminSave("Work Experience", employee, updated);
    if (ok) {
      setDraft(draft);
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setDraft(baseline);
    setDateError(null);
    setIsEditing(false);
  };

  const isEditable = employee.editableSections?.includes("work-experience");
  const displayRows = isEditing ? draft : baseline;

  return (
    <div className="space-y-5 pb-24">
      <div>
        <h2 className="text-lg font-bold text-foreground">Work Experience</h2>
        <p className="text-sm text-muted-foreground mt-1">Prior employment history for {employee.name}</p>
      </div>

      <EditableSectionCard
        title="Work Experience"
        icon={Building2}
        sectionId="work-experience"
        canEmployeeEdit={isEditable}
        onToggleEmployeeEdit={(v) => handleToggleEditAccess(employee, "work-experience", v)}
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
        {dateError ? <p className="text-sm text-destructive mb-3">{dateError}</p> : null}
        {!displayRows.length ? (
          <EmptyStateCard
            icon={Building2}
            title="No work experience on file"
            description={
              showAddButton
                ? "Use Add New to add prior employment, or Edit after records exist."
                : "No work experience on file. Edit is available when records exist."
            }
          />
        ) : (
          <div className="space-y-4">
            {displayRows.map((row, index) => (
              <EditableFormCard
                key={row.id}
                showDelete={isEditing}
                onDelete={() => setDeleteIndex(index)}
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <ProfileInfoField
                    label="Company Name"
                    value={row.companyName}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { companyName: v })}
                  />
                  <ProfileInfoField
                    label="Job Title"
                    value={row.jobTitle}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { jobTitle: v })}
                  />
                  <ProfileInfoField
                    label="Employment Type"
                    value={row.employmentType}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { employmentType: v })}
                    options={employeeTypeOptions}
                  />
                  <ProfileInfoField
                    label="Department"
                    value={row.department}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { department: v })}
                    options={departmentOptions}
                  />
                  <ProfileInfoField
                    label="Start Date"
                    value={row.startDate}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { startDate: v })}
                    type="date"
                  />
                  <ProfileInfoField
                    label="End Date"
                    value={row.endDate}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { endDate: v })}
                    type="date"
                  />
                  <ProfileInfoField
                    label="Location"
                    value={row.location}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { location: v })}
                  />
                  <ProfileInfoField
                    label="Reason for Leaving"
                    value={row.reasonForLeaving}
                    editing={isEditing}
                    onChange={(v) => updateRow(index, { reasonForLeaving: v })}
                  />
                  <div className="md:col-span-2">
                    <ProfileInfoField
                      label="Technologies Used"
                      value={row.technologiesUsed}
                      editing={isEditing}
                      onChange={(v) => updateRow(index, { technologiesUsed: v })}
                    />
                  </div>
                  <div className="md:col-span-2">
                    <ProfileInfoField
                      label="Responsibilities"
                      value={row.responsibilities}
                      editing={isEditing}
                      onChange={(v) => updateRow(index, { responsibilities: v })}
                      type="textarea"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <UploadField
                      label="Experience Letter Upload"
                      fileName={row.experienceLetterFileName}
                      dataUrl={row.experienceLetterDataUrl}
                      editing={isEditing}
                      onFileChange={(name, data) => updateRow(index, { experienceLetterFileName: name, experienceLetterDataUrl: data })}
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
        title="Remove work experience?"
        description="This entry will be removed from the employee record. You can save or cancel section edits afterward."
        confirmLabel="Remove"
        destructive
        onConfirm={confirmDelete}
      />
    </div>
  );
}
