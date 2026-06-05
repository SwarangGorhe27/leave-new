import { useState } from "react";
import { Plus, X, Trash2, GripVertical, ChevronDown, ChevronUp, Settings2, GitBranch } from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

type ApprovalLevel = {
  id: string;
  role: string;
  approverName: string;
  reminderAfter: string;
  reminderUnit: "Hours" | "Days";
  escalateAfter: string;
  escalateUnit: "Hours" | "Days";
  escalateTo: string;
  canDelegate: boolean;
};

type Workflow = {
  id: string;
  name: string;
  appliesTo: string;
  active: boolean;
  sla: string;
  slaUnit: "Hours" | "Days";
  levels: ApprovalLevel[];
};

// ─── Seed data ────────────────────────────────────────────────────────────────

const SEED_WORKFLOWS: Workflow[] = [
  {
    id: "wf-1",
    name: "Standard Leave Approval",
    appliesTo: "LEAVE",
    active: true,
    sla: "5",
    slaUnit: "Days",
    levels: [
      {
        id: "l1",
        role: "Manager",
        approverName: "",
        reminderAfter: "24",
        reminderUnit: "Hours",
        escalateAfter: "3",
        escalateUnit: "Days",
        escalateTo: "HR",
        canDelegate: true,
      },
      {
        id: "l2",
        role: "HR",
        approverName: "",
        reminderAfter: "24",
        reminderUnit: "Hours",
        escalateAfter: "2",
        escalateUnit: "Days",
        escalateTo: "Admin",
        canDelegate: false,
      },
      {
        id: "l3",
        role: "Admin",
        approverName: "",
        reminderAfter: "12",
        reminderUnit: "Hours",
        escalateAfter: "1",
        escalateUnit: "Days",
        escalateTo: "Superadmin",
        canDelegate: false,
      },
    ],
  },
];

const LEAVE_TYPES = [
  "LEAVE",
  "COMP_OFF",
  "SHORT_LEAVE",
  "OUT_DUTY",
  "WFH",
  "GATE_PASS",
  "OVERTIME",
];

const ROLES = ["Manager", "HR", "Admin", "Superadmin", "Team Lead", "Director"];

// ─── Helpers ──────────────────────────────────────────────────────────────────

function uid() {
  return Math.random().toString(36).slice(2, 9);
}

function emptyLevel(): ApprovalLevel {
  return {
    id: uid(),
    role: "Manager",
    approverName: "",
    reminderAfter: "24",
    reminderUnit: "Hours",
    escalateAfter: "3",
    escalateUnit: "Days",
    escalateTo: "HR",
    canDelegate: false,
  };
}

function emptyWorkflow(): Workflow {
  return {
    id: uid(),
    name: "",
    appliesTo: "LEAVE",
    active: true,
    sla: "5",
    slaUnit: "Days",
    levels: [emptyLevel()],
  };
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function LevelRow({
  level,
  index,
  total,
  onChange,
  onRemove,
}: {
  level: ApprovalLevel;
  index: number;
  total: number;
  onChange: (updated: ApprovalLevel) => void;
  onRemove: () => void;
}) {
  const [open, setOpen] = useState(true);

  const set = <K extends keyof ApprovalLevel>(k: K, v: ApprovalLevel[K]) =>
    onChange({ ...level, [k]: v });

  return (
    <div className="rounded-xl border border-border bg-background overflow-hidden">
      {/* Level header */}
      <div className="flex items-center gap-3 px-4 py-3 bg-secondary/40 border-b border-border">
        <GripVertical className="w-4 h-4 text-muted-foreground flex-shrink-0" />

        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Level {index + 1}
          </span>
          <span className="text-xs text-muted-foreground">—</span>
          <span className="text-sm font-semibold text-foreground truncate">
            {level.role || "Unset"}
          </span>
        </div>

        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            className="w-7 h-7 flex items-center justify-center rounded-md hover:bg-secondary transition-colors text-muted-foreground"
          >
            {open ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>

          {total > 1 && (
            <button
              type="button"
              onClick={onRemove}
              className="w-7 h-7 flex items-center justify-center rounded-md hover:bg-red-50 hover:text-red-500 transition-colors text-muted-foreground"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {open && (
        <div className="p-4 grid grid-cols-2 gap-3">
          {/* Role */}
          <div>
            <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1.5">
              Approver Role
            </label>
            <select
              value={level.role}
              onChange={(e) => set("role", e.target.value)}
              className="flat-input h-9 px-3 text-sm w-full"
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>

          {/* Approver name (optional) */}
          <div>
            <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1.5">
              Specific Approver{" "}
              <span className="normal-case font-normal">(optional)</span>
            </label>
            <input
              value={level.approverName}
              onChange={(e) => set("approverName", e.target.value)}
              placeholder="e.g. John Doe"
              className="flat-input h-9 px-3 text-sm w-full"
            />
          </div>

          {/* Reminder after */}
          <div>
            <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1.5">
              Send Reminder After
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                min="1"
                value={level.reminderAfter}
                onChange={(e) => set("reminderAfter", e.target.value)}
                className="flat-input h-9 px-3 text-sm w-20"
              />
              <select
                value={level.reminderUnit}
                onChange={(e) =>
                  set("reminderUnit", e.target.value as "Hours" | "Days")
                }
                className="flat-input h-9 px-3 text-sm flex-1"
              >
                <option value="Hours">Hours</option>
                <option value="Days">Days</option>
              </select>
            </div>
          </div>

          {/* Escalate after */}
          <div>
            <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1.5">
              Escalate After
            </label>
            <div className="flex gap-2">
              <input
                type="number"
                min="1"
                value={level.escalateAfter}
                onChange={(e) => set("escalateAfter", e.target.value)}
                className="flat-input h-9 px-3 text-sm w-20"
              />
              <select
                value={level.escalateUnit}
                onChange={(e) =>
                  set("escalateUnit", e.target.value as "Hours" | "Days")
                }
                className="flat-input h-9 px-3 text-sm flex-1"
              >
                <option value="Hours">Hours</option>
                <option value="Days">Days</option>
              </select>
            </div>
          </div>

          {/* Escalate to */}
          <div>
            <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1.5">
              Escalate To
            </label>
            <select
              value={level.escalateTo}
              onChange={(e) => set("escalateTo", e.target.value)}
              className="flat-input h-9 px-3 text-sm w-full"
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>

          {/* Can delegate */}
          <div className="flex items-end pb-1">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={level.canDelegate}
                onChange={(e) => set("canDelegate", e.target.checked)}
                className="h-4 w-4 rounded border-border"
              />
              <span className="text-sm text-foreground">Allow delegation</span>
            </label>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Create / Edit Modal ──────────────────────────────────────────────────────

function WorkflowModal({
  initial,
  onSave,
  onClose,
}: {
  initial: Workflow;
  onSave: (w: Workflow) => void;
  onClose: () => void;
}) {
  const [wf, setWf] = useState<Workflow>(initial);

  const setField = <K extends keyof Workflow>(k: K, v: Workflow[K]) =>
    setWf((prev) => ({ ...prev, [k]: v }));

  const updateLevel = (index: number, updated: ApprovalLevel) =>
    setWf((prev) => {
      const levels = [...prev.levels];
      levels[index] = updated;
      return { ...prev, levels };
    });

  const removeLevel = (index: number) =>
    setWf((prev) => ({
      ...prev,
      levels: prev.levels.filter((_, i) => i !== index),
    }));

  const addLevel = () =>
    setWf((prev) => ({ ...prev, levels: [...prev.levels, emptyLevel()] }));

  const approvalChain = wf.levels.map((l) => l.role).join(" → ");

  const isValid = wf.name.trim().length > 0 && wf.levels.length > 0;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={onClose}
    >
      <div
        className="relative bg-background border border-border rounded-xl shadow-xl flex flex-col w-[92vw] max-w-2xl max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal header */}
        <div className="border-b border-border bg-card px-5 py-4 flex items-start justify-between gap-3 flex-shrink-0">
          <div>
            <h2 className="text-base font-semibold text-foreground">
              {initial.name ? "Edit Workflow" : "Create Workflow"}
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Define approval levels, escalation rules, and SLA.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-9 h-9 flex items-center justify-center rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors flex-shrink-0"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Scrollable body */}
        <div className="overflow-y-auto flex-1 p-5 space-y-5">

          {/* Basic info */}
          <div className="flat-card bg-card p-4 space-y-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Basic Info
            </p>

            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2">
                <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1.5">
                  Workflow Name
                </label>
                <input
                  value={wf.name}
                  onChange={(e) => setField("name", e.target.value)}
                  placeholder="e.g. Standard Leave Approval"
                  className="flat-input h-10 px-3 text-sm w-full"
                />
              </div>

              <div>
                <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1.5">
                  Applies To
                </label>
                <select
                  value={wf.appliesTo}
                  onChange={(e) => setField("appliesTo", e.target.value)}
                  className="flat-input h-10 px-3 text-sm w-full"
                >
                  {LEAVE_TYPES.map((lt) => (
                    <option key={lt} value={lt}>
                      {lt.replaceAll("_", " ")}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider block mb-1.5">
                  Overall SLA
                </label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    min="1"
                    value={wf.sla}
                    onChange={(e) => setField("sla", e.target.value)}
                    className="flat-input h-10 px-3 text-sm w-20"
                  />
                  <select
                    value={wf.slaUnit}
                    onChange={(e) =>
                      setField("slaUnit", e.target.value as "Hours" | "Days")
                    }
                    className="flat-input h-10 px-3 text-sm flex-1"
                  >
                    <option value="Hours">Hours</option>
                    <option value="Days">Days</option>
                  </select>
                </div>
              </div>

              <div className="col-span-2 flex items-center gap-2">
                <label className="flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={wf.active}
                    onChange={(e) => setField("active", e.target.checked)}
                    className="h-4 w-4 rounded border-border"
                  />
                  <span className="text-sm text-foreground">
                    Active — this workflow will be applied to new requests
                  </span>
                </label>
              </div>
            </div>
          </div>

          {/* Approval chain preview */}
          {wf.levels.length > 0 && (
            <div className="px-4 py-3 rounded-lg border border-border bg-secondary/40 flex items-center gap-2 flex-wrap">
              <GitBranch className="w-4 h-4 text-muted-foreground flex-shrink-0" />
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Chain:
              </p>
              <p className="text-sm text-foreground font-medium">
                {approvalChain}
              </p>
            </div>
          )}

          {/* Approval levels */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-foreground">
                  Approval Levels
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {wf.levels.length} level{wf.levels.length !== 1 ? "s" : ""} configured
                </p>
              </div>
            </div>

            {wf.levels.map((level, i) => (
              <LevelRow
                key={level.id}
                level={level}
                index={i}
                total={wf.levels.length}
                onChange={(updated) => updateLevel(i, updated)}
                onRemove={() => removeLevel(i)}
              />
            ))}

            <button
              type="button"
              onClick={addLevel}
              className="w-full px-4 py-2.5 rounded-lg border border-dashed border-border text-xs font-semibold text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors flex items-center justify-center gap-2"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Approval Level
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-border bg-card px-5 py-4 flex justify-end gap-2 flex-shrink-0">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-border text-sm font-semibold"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={!isValid}
            onClick={() => {
              if (isValid) {
                onSave(wf);
                onClose();
              }
            }}
            className="px-4 py-2 rounded-lg bg-foreground text-primary-foreground text-sm font-semibold disabled:opacity-40"
          >
            {initial.name ? "Save Changes" : "Create Workflow"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Workflow card (list view) ─────────────────────────────────────────────────

function WorkflowCard({
  workflow,
  onEdit,
  onDelete,
  onToggle,
}: {
  workflow: Workflow;
  onEdit: () => void;
  onDelete: () => void;
  onToggle: () => void;
}) {
  const chain = workflow.levels.map((l) => l.role).join(" → ");

  return (
    <div className="rounded-xl border border-border bg-secondary/20 overflow-hidden">
      <div className="px-5 py-4 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="text-sm font-semibold text-foreground">
              {workflow.name}
            </p>
            <span
              className={`text-[10px] font-semibold px-2 py-0.5 rounded-md border ${
                workflow.active
                  ? "bg-green-50 text-green-700 border-green-200"
                  : "bg-secondary text-muted-foreground border-border"
              }`}
            >
              {workflow.active ? "Active" : "Inactive"}
            </span>
          </div>

          <p className="text-xs text-muted-foreground mt-1">
            {workflow.appliesTo.replaceAll("_", " ")} ·{" "}
            {workflow.levels.length} level{workflow.levels.length !== 1 ? "s" : ""} ·
            SLA {workflow.sla} {workflow.slaUnit}
          </p>

          <div className="mt-2 px-3 py-1.5 rounded-md bg-secondary/60 border border-border inline-flex items-center gap-2">
            <GitBranch className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0" />
            <p className="text-xs text-muted-foreground">{chain}</p>
          </div>
        </div>

        <div className="flex items-center gap-1 flex-shrink-0">
          <button
            type="button"
            onClick={onToggle}
            className="px-2.5 py-1.5 rounded-md border border-border text-xs font-semibold hover:bg-secondary transition-colors"
          >
            {workflow.active ? "Disable" : "Enable"}
          </button>
          <button
            type="button"
            onClick={onEdit}
            className="w-8 h-8 flex items-center justify-center rounded-md border border-border hover:bg-secondary transition-colors text-muted-foreground"
          >
            <Settings2 className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={onDelete}
            className="w-8 h-8 flex items-center justify-center rounded-md border border-border hover:bg-red-50 hover:text-red-500 transition-colors text-muted-foreground"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Level pills */}
      <div className="px-5 pb-4 flex flex-wrap gap-2">
        {workflow.levels.map((l, i) => (
          <div
            key={l.id}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-card border border-border text-xs"
          >
            <span className="text-muted-foreground">L{i + 1}</span>
            <span className="font-semibold text-foreground">{l.role}</span>
            <span className="text-muted-foreground">·</span>
            <span className="text-muted-foreground">
              esc. {l.escalateAfter}{l.escalateUnit[0]}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Main page ─────────────────────────────────────────────────────────────────

export function SuperadminWorkflowSettings() {
  const [workflows, setWorkflows] = useState<Workflow[]>(SEED_WORKFLOWS);
  const [modalWorkflow, setModalWorkflow] = useState<Workflow | null>(null);

  const openCreate = () => setModalWorkflow(emptyWorkflow());
  const openEdit = (wf: Workflow) => setModalWorkflow({ ...wf });
  const closeModal = () => setModalWorkflow(null);

  const handleSave = (updated: Workflow) => {
    setWorkflows((prev) => {
      const exists = prev.find((w) => w.id === updated.id);
      if (exists) {
        return prev.map((w) => (w.id === updated.id ? updated : w));
      }
      return [...prev, updated];
    });
  };

  const handleDelete = (id: string) =>
    setWorkflows((prev) => prev.filter((w) => w.id !== id));

  const handleToggle = (id: string) =>
    setWorkflows((prev) =>
      prev.map((w) => (w.id === id ? { ...w, active: !w.active } : w))
    );

  return (
    <>
      <div className="flat-card bg-card p-6 space-y-6">

        {/* Page header */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-sm font-semibold text-foreground">
              Workflow Settings
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Configure approval routing, escalation policies, reminders, and SLAs.
            </p>
          </div>

          <button
            type="button"
            onClick={openCreate}
            className="px-3 py-2 rounded-lg text-xs font-semibold bg-foreground text-primary-foreground inline-flex items-center gap-2 flex-shrink-0"
          >
            <Plus className="w-4 h-4" />
            New Workflow
          </button>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: "Total Workflows", value: workflows.length },
            {
              label: "Active",
              value: workflows.filter((w) => w.active).length,
            },
            {
              label: "Inactive",
              value: workflows.filter((w) => !w.active).length,
            },
          ].map((s) => (
            <div
              key={s.label}
              className="p-4 rounded-xl border border-border bg-secondary/30 text-center"
            >
              <p className="text-2xl font-semibold text-foreground">
                {s.value}
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">
                {s.label}
              </p>
            </div>
          ))}
        </div>

        {/* Workflow list */}
        <div className="space-y-3">
          {workflows.length === 0 ? (
            <div className="py-12 text-center rounded-xl border border-dashed border-border">
              <p className="text-sm font-semibold text-foreground">
                No workflows yet
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Click "New Workflow" to create your first approval flow.
              </p>
            </div>
          ) : (
            workflows.map((wf) => (
              <WorkflowCard
                key={wf.id}
                workflow={wf}
                onEdit={() => openEdit(wf)}
                onDelete={() => handleDelete(wf.id)}
                onToggle={() => handleToggle(wf.id)}
              />
            ))
          )}
        </div>
      </div>

      {/* Modal */}
      {modalWorkflow && (
        <WorkflowModal
          initial={modalWorkflow}
          onSave={handleSave}
          onClose={closeModal}
        />
      )}
    </>
  );
}