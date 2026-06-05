import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Monitor, RefreshCw } from "lucide-react";
import { useDispatch } from "react-redux";
import { Employee, AssetEntry } from "../mockData";
import {
  EditableSectionCard,
  ProfileInfoField,
  EmptyStateCard,
} from "../employee-details";
import { useMasterOptions } from "./useMasterOptions";
import {
  AssetApiError,
  assetEntriesEqual,
  assetEntryToWritePayload,
  assetsToEmployeeEntries,
  buildAssetUpdatePayload,
  createEmployeeAsset,
  deleteEmployeeAsset,
  extractAssetApiError,
  getEmployeeAssets,
  isPersistedAssetId,
  mapAssetFieldErrorsToRowErrors,
  minReturnDate,
  todayIsoDate,
  updateEmployeeAsset,
} from "../../../api/employeeAssets";
import { AppDispatch } from "../../../../store";
import { updateAdminEmployee } from "../../../../store/slices/adminSlice";
import { addNotification } from "../../../../store/slices/notificationSlice";

interface Props {
  employee: Employee;
  showActions?: boolean;
}

const STATUS_OPTIONS = [
  { value: "Assigned", label: "Assigned" },
  { value: "Returned", label: "Returned" },
  { value: "Lost", label: "Lost" },
  { value: "Damaged", label: "Damaged" },
];

function emptyAsset(): AssetEntry {
  return {
    id: `ast-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    assetName: "",
    assetId: "",
    assetCategory: "",
    serialNumber: "",
    assignedDate: todayIsoDate(),
    returnDate: "",
    assetCondition: "",
    status: "Assigned",
    remarks: "",
  };
}

function resolveCategoryDisplay(
  asset: AssetEntry,
  options: Array<{ value: string; label: string }>,
): string {
  if (asset.assetCategoryLabel?.trim()) return asset.assetCategoryLabel;
  const match = options.find((o) => o.value === asset.assetCategory);
  return match?.label ?? asset.assetCategory;
}

function resolveConditionDisplay(
  asset: AssetEntry,
  options: Array<{ value: string; label: string }>,
): string {
  if (asset.assetConditionLabel?.trim()) return asset.assetConditionLabel;
  if (!asset.assetCondition?.trim()) return "";
  const match = options.find((o) => o.value === asset.assetCondition);
  return match?.label ?? asset.assetCondition;
}

function validateAssets(assets: AssetEntry[], today: string): Record<number, Record<string, string>> {
  const errors: Record<number, Record<string, string>> = {};
  assets.forEach((a, idx) => {
    const row: Record<string, string> = {};
    if (!a.assetName.trim()) row.assetName = "Asset name is required";
    if (!a.assetId.trim()) row.assetId = "Asset ID is required";
    if (!a.assetCategory.trim()) row.assetCategory = "Category is required";
    if (!a.assignedDate) row.assignedDate = "Assign date is required";
    else if (a.assignedDate < today) {
      row.assignedDate = "Assign date must be today or a future date";
    }
    if (a.returnDate) {
      const minRet = minReturnDate(a.assignedDate, today);
      if (a.returnDate < minRet) {
        row.returnDate =
          minRet === today
            ? "Return date must be today or a future date"
            : "Return date must be on or after the assign date";
      }
    }
    if (!a.status.trim()) row.status = "Status is required";
    if (Object.keys(row).length) errors[idx] = row;
  });
  return errors;
}

export function AssetManagement({ employee, showActions = true }: Props) {
  const dispatch = useDispatch<AppDispatch>();
  const categoryOptions = useMasterOptions("AssetCategory");
  const conditionOptions = useMasterOptions("AssetCondition");

  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [serverAssets, setServerAssets] = useState<AssetEntry[]>([]);
  const [assets, setAssets] = useState<AssetEntry[]>([]);
  const [errors, setErrors] = useState<Record<number, Record<string, string>>>({});
  const isEditingRef = useRef(isEditing);

  useEffect(() => {
    isEditingRef.current = isEditing;
  }, [isEditing]);

  const baseline = useMemo(() => serverAssets, [serverAssets]);
  const employeeId = employee.id;
  const today = todayIsoDate();
  const masterOptions = useMemo(
    () => ({ categoryOptions, conditionOptions }),
    [categoryOptions, conditionOptions],
  );

  const loadAssets = useCallback(async () => {
    if (!employeeId) return;
    setIsLoading(true);
    setLoadError(null);
    try {
      const rows = await getEmployeeAssets(employeeId);
      const mapped = assetsToEmployeeEntries(rows);
      setServerAssets(mapped);
      if (!isEditingRef.current) {
        setAssets(mapped);
      }
    } catch (error) {
      const message = extractAssetApiError(error, "Could not load asset details.");
      setLoadError(message);
      dispatch(addNotification({ type: "error", message }));
    } finally {
      setIsLoading(false);
    }
  }, [dispatch, employeeId]);

  useEffect(() => {
    void loadAssets();
  }, [loadAssets]);

  const startEdit = () => {
    setAssets(baseline.length ? [...baseline] : [emptyAsset()]);
    setErrors({});
    setIsEditing(true);
  };

  const addAsset = () => {
    setAssets((rows) => [...rows, emptyAsset()]);
  };

  const removeAsset = async (idx: number) => {
    const target = assets[idx];
    if (!target) return;

    if (isPersistedAssetId(target.id) && employeeId) {
      try {
        await deleteEmployeeAsset(employeeId, target.id);
        const rows = await getEmployeeAssets(employeeId);
        const mapped = assetsToEmployeeEntries(rows);
        setServerAssets(mapped);
        setAssets((rows) => rows.filter((_, i) => i !== idx));
        dispatch(
          addNotification({ type: "success", message: "Asset removed successfully." }),
        );
      } catch (error) {
        dispatch(
          addNotification({
            type: "error",
            message: extractAssetApiError(error, "Failed to remove asset."),
          }),
        );
        return;
      }
    }

    setAssets((rows) => rows.filter((_, i) => i !== idx));
    setErrors((prev) => {
      const next: Record<number, Record<string, string>> = {};
      Object.entries(prev).forEach(([key, value]) => {
        const i = Number(key);
        if (i < idx) next[i] = value;
        else if (i > idx) next[i - 1] = value;
      });
      return next;
    });
  };

  const handleSave = async () => {
    const nextErrors = validateAssets(assets, today);
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
      const baselineById = new Map(
        baseline.filter((a) => isPersistedAssetId(a.id)).map((a) => [a.id, a]),
      );
      const nextById = new Map(
        assets.filter((a) => isPersistedAssetId(a.id)).map((a) => [a.id, a]),
      );

      for (const [id] of baselineById) {
        if (!nextById.has(id)) {
          await deleteEmployeeAsset(employeeId, id);
        }
      }

      for (let idx = 0; idx < assets.length; idx += 1) {
        const asset = assets[idx];
        if (isPersistedAssetId(asset.id)) {
          const previous = baselineById.get(asset.id);
          if (!previous || assetEntriesEqual(previous, asset)) continue;
          const patch = buildAssetUpdatePayload(previous, asset, masterOptions);
          if (Object.keys(patch).length === 0) continue;
          try {
            await updateEmployeeAsset(employeeId, asset.id, patch);
          } catch (error) {
            if (error instanceof AssetApiError) {
              const rowErrors = mapAssetFieldErrorsToRowErrors(error.fieldErrors);
              if (Object.keys(rowErrors).length) {
                setErrors({ [idx]: rowErrors });
              }
            }
            throw error;
          }
        } else {
          try {
            await createEmployeeAsset(
              employeeId,
              assetEntryToWritePayload(asset, masterOptions),
            );
          } catch (error) {
            if (error instanceof AssetApiError) {
              const rowErrors = mapAssetFieldErrorsToRowErrors(error.fieldErrors);
              if (Object.keys(rowErrors).length) {
                setErrors({ [idx]: rowErrors });
              }
            }
            throw error;
          }
        }
      }

      const rows = await getEmployeeAssets(employeeId);
      const mapped = assetsToEmployeeEntries(rows);
      setServerAssets(mapped);
      setAssets(mapped);
      dispatch(updateAdminEmployee({ ...employee, assets: mapped }));
      setErrors({});
      setIsEditing(false);
      dispatch(addNotification({ type: "success", message: "Asset details saved successfully." }));
    } catch (error) {
      dispatch(
        addNotification({
          type: "error",
          message: extractAssetApiError(error, "Failed to save asset details."),
        }),
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setAssets(baseline);
    setErrors({});
    setIsEditing(false);
  };

  const updateAsset = (idx: number, patch: Partial<AssetEntry>) => {
    setAssets((rows) => rows.map((r, i) => (i === idx ? { ...r, ...patch } : r)));
    setErrors((prev) => {
      if (!prev[idx]) return prev;
      const next = { ...prev };
      delete next[idx];
      return next;
    });
  };

  const displayAssets = isEditing ? assets : baseline;
  const mastersReady = categoryOptions.length > 0;

  return (
    <div className="space-y-5 pb-24">
      <div>
        <h2 className="text-lg font-bold text-foreground">Asset Management</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Manage company assets assigned to {employee.name}
        </p>
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 rounded-md border border-border bg-card px-4 py-3 text-sm text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          Loading assets…
        </div>
      )}

      {loadError && !isLoading && (
        <div className="flex items-center justify-between gap-3 rounded-md border border-border bg-card px-4 py-3 text-sm">
          <p className="text-muted-foreground">{loadError}</p>
          <button
            type="button"
            onClick={() => void loadAssets()}
            className="rounded-md border border-border px-3 py-1.5 text-xs font-semibold hover:bg-secondary"
          >
            Retry
          </button>
        </div>
      )}

      <EditableSectionCard
        title="Asset Management"
        icon={Monitor}
        isEditing={isEditing}
        onCancel={handleCancel}
        onSave={() => void handleSave()}
        onEdit={showActions ? startEdit : undefined}
        editLabel={baseline.length ? "Edit" : "Add"}
      >
        {isEditing && !mastersReady ? (
          <p className="text-sm text-muted-foreground">
            Loading asset category and condition options…
          </p>
        ) : null}

        {!displayAssets.length && !isEditing ? (
          <EmptyStateCard
            icon={Monitor}
            title="No assets assigned"
            description="No assets recorded. Contact admin to add assets."
          />
        ) : (
          <div className="space-y-6">
            {displayAssets.map((a, idx) => (
              <div key={a.id} className="rounded-2xl border border-border bg-secondary/10 p-6 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  <ProfileInfoField
                    label="Asset Name"
                    value={a.assetName}
                    editing={isEditing}
                    error={errors[idx]?.assetName}
                    onChange={(v) => updateAsset(idx, { assetName: v })}
                  />
                  <ProfileInfoField
                    label="Asset ID"
                    value={a.assetId}
                    editing={isEditing}
                    error={errors[idx]?.assetId}
                    onChange={(v) => updateAsset(idx, { assetId: v })}
                  />
                  <ProfileInfoField
                    label="Asset Category"
                    value={isEditing ? a.assetCategory : resolveCategoryDisplay(a, categoryOptions)}
                    editing={isEditing}
                    options={categoryOptions}
                    error={errors[idx]?.assetCategory}
                    onChange={(v) => updateAsset(idx, { assetCategory: v, assetCategoryLabel: "" })}
                  />
                  <ProfileInfoField
                    label="Serial Number"
                    value={a.serialNumber}
                    editing={isEditing}
                    onChange={(v) => updateAsset(idx, { serialNumber: v })}
                  />
                  <ProfileInfoField
                    label="Assign Date"
                    value={a.assignedDate}
                    editing={isEditing}
                    type="date"
                    min={today}
                    error={errors[idx]?.assignedDate}
                    onChange={(v) => updateAsset(idx, { assignedDate: v })}
                  />
                  <ProfileInfoField
                    label="Return Date"
                    value={a.returnDate || ""}
                    editing={isEditing}
                    type="date"
                    min={minReturnDate(a.assignedDate, today)}
                    error={errors[idx]?.returnDate}
                    onChange={(v) => updateAsset(idx, { returnDate: v })}
                  />
                  <ProfileInfoField
                    label="Asset Condition"
                    value={
                      isEditing
                        ? a.assetCondition
                        : resolveConditionDisplay(a, conditionOptions)
                    }
                    editing={isEditing}
                    options={conditionOptions}
                    error={errors[idx]?.assetCondition}
                    onChange={(v) =>
                      updateAsset(idx, { assetCondition: v, assetConditionLabel: "" })
                    }
                  />
                  <ProfileInfoField
                    label="Status"
                    value={a.status}
                    editing={isEditing}
                    options={STATUS_OPTIONS}
                    error={errors[idx]?.status}
                    onChange={(v) => updateAsset(idx, { status: v })}
                  />
                  <div className="hidden lg:block" aria-hidden />
                  <div className="sm:col-span-2 lg:col-span-3">
                    <ProfileInfoField
                      label="Remarks"
                      value={a.remarks || ""}
                      editing={isEditing}
                      type="textarea"
                      onChange={(v) => updateAsset(idx, { remarks: v })}
                    />
                  </div>
                </div>
                {isEditing ? (
                  <button
                    type="button"
                    className="text-xs font-semibold text-destructive hover:underline"
                    onClick={() => void removeAsset(idx)}
                  >
                    Remove asset
                  </button>
                ) : null}
              </div>
            ))}
            {isEditing ? (
              <button
                type="button"
                onClick={addAsset}
                disabled={!mastersReady}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-border text-xs font-bold hover:bg-secondary disabled:opacity-50"
              >
                Add another asset
              </button>
            ) : null}
          </div>
        )}
        {isSaving ? (
          <p className="mt-4 text-xs font-medium text-muted-foreground">Saving asset details…</p>
        ) : null}
      </EditableSectionCard>
    </div>
  );
}
