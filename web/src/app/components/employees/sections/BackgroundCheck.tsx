import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { RefreshCw, ShieldCheck } from "lucide-react";
import { useDispatch } from "react-redux";
import { BackgroundCheckRecord, Employee } from "../mockData";
import { EditableSectionCard, ProfileInfoField } from "../employee-details";
import { useMasterOptions } from "./useMasterOptions";
import {
  BackgroundVerificationApiError,
  apiToBackgroundCheckRecord,
  backgroundCheckToWritePayload,
  createEmployeeBackgroundVerification,
  emptyBackgroundCheckRecord,
  extractBackgroundVerificationApiError,
  getEmployeeBackgroundVerification,
  isPersistedBackgroundCheckId,
  mapBackgroundFieldErrors,
  resolveStatusDisplay,
  updateEmployeeBackgroundVerification,
} from "../../../api/employeeBackgroundVerification";
import { AppDispatch } from "../../../../store";
import { updateAdminEmployee } from "../../../../store/slices/adminSlice";
import { addNotification } from "../../../../store/slices/notificationSlice";

interface Props {
  employee: Employee;
  showActions?: boolean;
}

function validateRecord(
  record: BackgroundCheckRecord,
): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!record.verificationStatus.trim()) {
    errors.verificationStatus = "Verification status is required";
  }
  return errors;
}

export function BackgroundCheck({ employee, showActions = true }: Props) {
  const dispatch = useDispatch<AppDispatch>();
  const statusOptions = useMasterOptions("VerificationStatus");

  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [serverRecord, setServerRecord] = useState<BackgroundCheckRecord | null>(null);
  const [record, setRecord] = useState<BackgroundCheckRecord>(emptyBackgroundCheckRecord());
  const [errors, setErrors] = useState<Record<string, string>>({});
  const isEditingRef = useRef(isEditing);

  useEffect(() => {
    isEditingRef.current = isEditing;
  }, [isEditing]);

  const employeeId = employee.id;
  const hasSavedRecord = serverRecord !== null && isPersistedBackgroundCheckId(serverRecord.id);

  const baseline = useMemo(
    () => serverRecord ?? emptyBackgroundCheckRecord(),
    [serverRecord],
  );

  const loadBackgroundCheck = useCallback(async () => {
    if (!employeeId) return;
    setIsLoading(true);
    setLoadError(null);
    try {
      const row = await getEmployeeBackgroundVerification(employeeId);
      const mapped = row ? apiToBackgroundCheckRecord(row) : null;
      setServerRecord(mapped);
      if (!isEditingRef.current) {
        setRecord(mapped ?? emptyBackgroundCheckRecord());
      }
    } catch (error) {
      const message = extractBackgroundVerificationApiError(
        error,
        "Could not load background check details.",
      );
      setLoadError(message);
      dispatch(addNotification({ type: "error", message }));
    } finally {
      setIsLoading(false);
    }
  }, [dispatch, employeeId]);

  useEffect(() => {
    void loadBackgroundCheck();
  }, [loadBackgroundCheck]);

  const startEdit = () => {
    setRecord(hasSavedRecord ? { ...baseline } : emptyBackgroundCheckRecord());
    setErrors({});
    setIsEditing(true);
  };

  const handleSave = async () => {
    const nextErrors = validateRecord(record);
    if (Object.keys(nextErrors).length) {
      setErrors(nextErrors);
      return;
    }

    if (!employeeId) {
      dispatch(addNotification({ type: "error", message: "Employee ID is missing." }));
      return;
    }

    setIsSaving(true);
    try {
      const payload = backgroundCheckToWritePayload(record, statusOptions);
      const saved = hasSavedRecord
        ? await updateEmployeeBackgroundVerification(employeeId, payload)
        : await createEmployeeBackgroundVerification(employeeId, payload);

      const mapped = apiToBackgroundCheckRecord(saved);
      setServerRecord(mapped);
      setRecord(mapped);
      dispatch(
        updateAdminEmployee({
          ...employee,
          backgroundChecks: [mapped],
          backgroundCheck: mapped,
        }),
      );
      setErrors({});
      setIsEditing(false);
      dispatch(addNotification({ type: "success", message: "Background check saved successfully." }));
    } catch (error) {
      if (error instanceof BackgroundVerificationApiError) {
        const fieldErrors = mapBackgroundFieldErrors(error.fieldErrors);
        if (Object.keys(fieldErrors).length) setErrors(fieldErrors);
      }
      dispatch(
        addNotification({
          type: "error",
          message: extractBackgroundVerificationApiError(error, "Failed to save background check."),
        }),
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setRecord(hasSavedRecord ? { ...baseline } : emptyBackgroundCheckRecord());
    setErrors({});
    setIsEditing(false);
  };

  const updateField = (patch: Partial<BackgroundCheckRecord>) => {
    setRecord((prev) => ({ ...prev, ...patch }));
    setErrors((prev) => {
      const next = { ...prev };
      for (const key of Object.keys(patch)) {
        delete next[key];
      }
      return next;
    });
  };

  const display = isEditing ? record : baseline;

  return (
    <div className="space-y-5 pb-24">
      <div>
        <h2 className="text-lg font-bold text-foreground">Background Check</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Verification and compliance for {employee.name}
        </p>
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 rounded-md border border-border bg-card px-4 py-3 text-sm text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          Loading background check…
        </div>
      )}

      {loadError && !isLoading && (
        <div className="flex items-center justify-between gap-3 rounded-md border border-border bg-card px-4 py-3 text-sm">
          <p className="text-muted-foreground">{loadError}</p>
          <button
            type="button"
            onClick={() => void loadBackgroundCheck()}
            className="rounded-md border border-border px-3 py-1.5 text-xs font-semibold hover:bg-secondary"
          >
            Retry
          </button>
        </div>
      )}

      <EditableSectionCard
        title="Background Check"
        icon={ShieldCheck}
        isEditing={isEditing}
        onCancel={handleCancel}
        onSave={() => void handleSave()}
        onEdit={showActions ? startEdit : undefined}
        editLabel={hasSavedRecord ? "Edit" : "Add"}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <ProfileInfoField
            label="Verification Status"
            value={
              isEditing
                ? display.verificationStatus
                : resolveStatusDisplay(display, statusOptions)
            }
            editing={isEditing}
            options={statusOptions}
            placeholder="Select status"
            error={errors.verificationStatus}
            onChange={(v) =>
              updateField({ verificationStatus: v, verificationStatusLabel: "" })
            }
          />
          <ProfileInfoField
            label="Agency Name"
            value={display.agencyName || ""}
            editing={isEditing}
            placeholder="Verification Agency"
            error={errors.agencyName}
            onChange={(v) => updateField({ agencyName: v })}
          />
          <ProfileInfoField
            label="Verified By"
            value={display.verifiedBy || ""}
            editing={isEditing}
            placeholder="Auditor Name"
            error={errors.verifiedBy}
            onChange={(v) => updateField({ verifiedBy: v })}
          />
          <ProfileInfoField
            label="Reference Number"
            value={display.referenceNumber || ""}
            editing={isEditing}
            placeholder="Case Reference ID"
            error={errors.referenceNumber}
            onChange={(v) => updateField({ referenceNumber: v })}
          />
          <div className="sm:col-span-2">
            <ProfileInfoField
              label="Remarks"
              value={display.remarks || ""}
              editing={isEditing}
              type="textarea"
              placeholder="Add any internal remarks regarding the background check..."
              error={errors.remarks}
              onChange={(v) => updateField({ remarks: v })}
            />
          </div>
        </div>
        {isSaving ? (
          <p className="mt-4 text-xs font-medium text-muted-foreground">Saving background check…</p>
        ) : null}
      </EditableSectionCard>
    </div>
  );
}
