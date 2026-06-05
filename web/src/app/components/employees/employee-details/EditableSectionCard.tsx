import { LucideIcon, Save, X, Pencil, Plus, Send } from "lucide-react";
import { cn } from "../../ui/utils";
import { useEmployeeFormContext } from "./EmployeeFormContext";

interface EditableSectionCardProps {
  title: string;
  icon?: LucideIcon;
  children: React.ReactNode;
  isEditing: boolean;
  onEdit?: () => void;
  /** Separate Add action (employee/manager); shown beside Edit, not when Edit is clicked */
  onAdd?: () => void;
  addLabel?: string;
  onSave: () => void;
  onCancel: () => void;
  /** Extra actions shown next to Save/Cancel while editing (admin-only extras) */
  headerExtra?: React.ReactNode;
  className?: string;
  editLabel?: string;
  // Selective Editing for ESS
  sectionId?: string;
  canEmployeeEdit?: boolean;
  onToggleEmployeeEdit?: (checked: boolean) => void;
  requestStatus?: 'None' | 'Pending' | 'Updated';
  /** When true, hides the admin-only "Allow Employee to Edit" checkbox (used on ESS side) */
  hideAdminControls?: boolean;
  /** When true the profile/section is locked for direct edits */
  profileLocked?: boolean;
  /** When true, Edit is disabled (e.g. no existing records to edit) */
  editDisabled?: boolean;
  /** When true, show Add/Edit on ESS even if profile is read-only (e.g. Bank / PF / ESI) */
  allowEssDirectEdit?: boolean;
}

export function EditableSectionCard({
  title,
  icon: Icon,
  children,
  isEditing,
  onEdit,
  onAdd,
  addLabel = "Add",
  onSave,
  onCancel,
  headerExtra,
  className,
  editLabel,
  sectionId,
  canEmployeeEdit,
  requestStatus,
  profileLocked,
  editDisabled = false,
  allowEssDirectEdit = false,
}: EditableSectionCardProps) {
  const getStatusLabel = () => {
    if (requestStatus === 'Pending') return { l: 'Pending Employee Update', c: 'bg-amber-500/10 text-amber-600 border-amber-200' };
    if (requestStatus === 'Updated') return { l: 'Updated by Employee', c: 'bg-emerald-500/10 text-emerald-600 border-emerald-200' };
    if (canEmployeeEdit) return { l: 'Editable by Employee', c: 'bg-indigo-500/10 text-indigo-600 border-indigo-200' };
    return { l: '', c: '' };
  };

  const status = getStatusLabel();
  const ctx = useEmployeeFormContext();
  const finalSubmitted = ctx?.finalSubmitted;
  const essReadOnly = ctx?.essReadOnly;
  const effectiveProfileLocked = profileLocked || !!finalSubmitted || !!essReadOnly;

  const requestChange = () => {
    if (!sectionId) return;
    window.dispatchEvent(new CustomEvent("ess:request_change", { detail: { sectionId } }));
  };

  return (
    <div className={cn("flat-card bg-card border border-border p-6", className)}>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-bold text-foreground flex items-center gap-2.5">
            {Icon ? (
              <span className="w-8 h-8 rounded-lg bg-secondary border border-border flex items-center justify-center flex-shrink-0">
                <Icon className="w-4 h-4 text-foreground" />
              </span>
            ) : null}
            {title}
          </h3>
          {sectionId && status.l ? (
             <span className={cn("text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded border transition-all", status.c)}>
               {status.l}
             </span>
          ) : null}
        </div>
        <div className="flex items-center gap-4 flex-shrink-0">
          <div className="flex items-center gap-2">
            {!effectiveProfileLocked && headerExtra}
            {isEditing ? (
              <>
                <button
                  type="button"
                  onClick={onSave}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-bold hover:bg-primary/90 transition-colors"
                >
                  <Save className="w-3.5 h-3.5" />
                  Save
                </button>
                <button
                  type="button"
                  onClick={onCancel}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-bold hover:bg-secondary transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                  Cancel
                </button>
              </>
            ) : essReadOnly && sectionId && !allowEssDirectEdit ? (
              <button
                type="button"
                onClick={requestChange}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-bold hover:bg-secondary transition-colors"
              >
                <Send className="w-3.5 h-3.5" />
                Request Change
              </button>
            ) : (
              <>
                {onAdd && !effectiveProfileLocked ? (
                  <button
                    type="button"
                    onClick={onAdd}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-bold transition-colors hover:bg-secondary"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    {addLabel}
                  </button>
                ) : null}
                {onEdit ? (
                  <button
                    type="button"
                    onClick={onEdit}
                    disabled={editDisabled}
                    title={editDisabled ? "Add a record first, then use Edit" : undefined}
                    className={cn(
                      "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-bold transition-colors",
                      editDisabled
                        ? "opacity-50 cursor-not-allowed"
                        : "hover:bg-secondary",
                    )}
                  >
                    {editLabel === "Add" ? (
                      <Plus className="w-3.5 h-3.5" />
                    ) : (
                      <Pencil className="w-3.5 h-3.5" />
                    )}
                    {editLabel || "Edit"}
                  </button>
                ) : null}
              </>
            )}
          </div>
        </div>
      </div>
      {children}
    </div>
  );
}
