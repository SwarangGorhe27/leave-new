import { useEffect, useMemo, useState } from "react";
import { ShieldCheck, Plus } from "lucide-react";
import { Employee, InsuranceEntry } from "../mockData";
import { useAdminSync } from "../../admin/useAdminSync";
import {
  EditableSectionCard,
  ProfileInfoField,
  UploadField,
  EmptyStateCard,
} from "../employee-details";
import { useMasterOptions } from "./useMasterOptions";

interface Props {
  employee: Employee;
  showAddButton?: boolean;
}

function emptyPolicy(): InsuranceEntry {
  return {
    id: `ins-${Date.now()}`,
    insuranceProvider: "",
    policyNumber: "",
    coverageType: "",
    coverageAmount: "",
    validTill: "",
    dependentsCovered: "",
  };
}

export function InsuranceDetails({ employee, showAddButton = true }: Props) {
  const { handleAdminSave, handleToggleEditAccess } = useAdminSync();
  const insuranceCompanyOptions = useMasterOptions("InsuranceCompany");
  const insuranceTypeOptions = useMasterOptions("InsuranceType");
  const policyTypeOptions = useMasterOptions("PolicyType");
  const [isEditing, setIsEditing] = useState(false);
  const baseline = useMemo(() => employee.insurance || [], [employee.insurance]);
  const [insurance, setInsurance] = useState<InsuranceEntry[]>(baseline);

  useEffect(() => {
    if (!isEditing) setInsurance(baseline);
  }, [baseline, isEditing]);

  const isEditable = employee.editableSections?.includes("insurance-details");

  const startEdit = () => {
    if (!baseline.length) return;
    setInsurance([...baseline]);
    setIsEditing(true);
  };

  const addPolicy = () => {
    setInsurance((rows) => [...(isEditing ? rows : baseline), emptyPolicy()]);
    setIsEditing(true);
  };

  const handleSave = async () => {
    const savedPolicies = insurance.filter(
      (p) =>
        (p.insuranceProvider && p.insuranceProvider.trim()) ||
        (p.policyNumber && p.policyNumber.trim()),
    );
    const ok = await handleAdminSave("Insurance Details", employee, { ...employee, insurance: savedPolicies });
    if (ok) {
      setInsurance(savedPolicies);
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setInsurance(baseline);
    setIsEditing(false);
  };

  const display = isEditing ? insurance : baseline;

  const addButton = (
    <button
      type="button"
      onClick={addPolicy}
      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-bold hover:bg-secondary transition-colors"
    >
      <Plus className="w-3.5 h-3.5" />
      Add New
    </button>
  );

  return (
    <div className="space-y-5 pb-24">
      <div>
        <h2 className="text-lg font-bold text-foreground">Insurance Details</h2>
        <p className="text-sm text-muted-foreground mt-1">Manage insurance policies for {employee.name}</p>
      </div>

      <EditableSectionCard
        title="Insurance Details"
        icon={ShieldCheck}
        sectionId="insurance-details"
        canEmployeeEdit={isEditable}
        onToggleEmployeeEdit={(v) => handleToggleEditAccess(employee, "insurance-details", v)}
        requestStatus={employee.editRequestStatus}
        isEditing={isEditing}
        onEdit={startEdit}
        editDisabled={!baseline.length}
        onCancel={handleCancel}
        onSave={handleSave}
        headerExtra={showAddButton ? addButton : null}
      >
        {!display.length ? (
          <EmptyStateCard icon={ShieldCheck} title="No insurance policies" description="Use Add New to add a policy, or Edit after records exist." />
        ) : (
          <div className="space-y-6">
            {display.map((pol, idx) => (
              <div key={pol.id} className="rounded-2xl border border-border bg-secondary/10 p-6 space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <ProfileInfoField
                    label="Insurance Provider"
                    value={pol.insuranceProvider}
                    editing={isEditing}
                    options={insuranceCompanyOptions}
                    onChange={(v) =>
                      setInsurance((rows) => rows.map((r, i) => (i === idx ? { ...r, insuranceProvider: v } : r)))
                    }
                  />
                  <ProfileInfoField
                    label="Policy Number"
                    value={pol.policyNumber}
                    editing={isEditing}
                    onChange={(v) =>
                      setInsurance((rows) => rows.map((r, i) => (i === idx ? { ...r, policyNumber: v } : r)))
                    }
                  />
                  <ProfileInfoField
                    label="Coverage Type"
                    value={pol.coverageType}
                    editing={isEditing}
                    options={insuranceTypeOptions.length ? insuranceTypeOptions : policyTypeOptions}
                    onChange={(v) =>
                      setInsurance((rows) => rows.map((r, i) => (i === idx ? { ...r, coverageType: v } : r)))
                    }
                  />
                  <ProfileInfoField
                    label="Coverage Amount"
                    value={pol.coverageAmount}
                    editing={isEditing}
                    onChange={(v) =>
                      setInsurance((rows) => rows.map((r, i) => (i === idx ? { ...r, coverageAmount: v } : r)))
                    }
                  />
                  <ProfileInfoField
                    label="Valid Till"
                    value={pol.validTill}
                    editing={isEditing}
                    onChange={(v) =>
                      setInsurance((rows) => rows.map((r, i) => (i === idx ? { ...r, validTill: v } : r)))
                    }
                    type="date"
                  />
                  <ProfileInfoField
                    label="Dependents Covered"
                    value={pol.dependentsCovered}
                    editing={isEditing}
                    onChange={(v) =>
                      setInsurance((rows) => rows.map((r, i) => (i === idx ? { ...r, dependentsCovered: v } : r)))
                    }
                  />
                  <div className="sm:col-span-2">
                    <UploadField
                      label="Insurance Document Upload"
                      fileName={pol.documentFileName}
                      dataUrl={pol.documentDataUrl}
                      editing={isEditing}
                      onFileChange={(name, data) =>
                        setInsurance((rows) =>
                          rows.map((r, i) => (i === idx ? { ...r, documentFileName: name, documentDataUrl: data } : r))
                        )
                      }
                    />
                  </div>
                </div>
                {isEditing && display.length > 1 ? (
                  <button
                    type="button"
                    className="text-xs font-semibold text-destructive hover:underline"
                    onClick={() => setInsurance((rows) => rows.filter((_, i) => i !== idx))}
                  >
                    Remove policy
                  </button>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </EditableSectionCard>
    </div>
  );
}
