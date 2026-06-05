import { useEffect, useMemo, useState } from "react";
import { Check, Copy, Edit3, Plus, RotateCcw, Search, Trash2 } from "lucide-react";
import { useAuth } from "../../../../context/AuthContext";
import { Input } from "../../../../components/ui/input";
import { Switch } from "../../../../components/ui/switch";
import { Textarea } from "../../../../components/ui/textarea";
import { cn } from "../../../../components/ui/utils";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../../../../components/ui/dialog";
import { SETTINGS_SECTIONS, useLeaveSettingsStore } from "../../../../modules/adminLeave/settings";
import type {
  LeaveSettingsRecord,
  LeaveSettingsSectionKey,
  SettingsFieldSchema,
} from "../../../../modules/adminLeave/settings";

function DynamicField({
  field,
  value,
  onChange,
}: {
  field: SettingsFieldSchema;
  value: unknown;
  onChange: (v: unknown) => void;
}) {
  if (field.type === "boolean") {
    return (
      <div className="flex items-center justify-between rounded-2xl border border-border bg-secondary/40 px-4 py-4 shadow-sm transition-all">
        <div className="space-y-0.5">
          <p className="text-sm font-semibold text-foreground">{field.label}</p>

          <p className="text-[11px] text-muted-foreground">
            {Boolean(value) ? "Enabled" : "Disabled"}
          </p>
        </div>

        <Switch
          checked={Boolean(value)}
          onCheckedChange={onChange as (checked: boolean) => void}
          className="
            data-[state=checked]:bg-black
            data-[state=unchecked]:bg-zinc-300
            border
            border-zinc-400
            h-7
            w-12
            shadow-inner
          "
        />
      </div>
    );
  }
  if (field.type === "textarea" || field.type === "json") {
    return (
      <div className="space-y-1">
        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {field.label}
        </label>
        <Textarea
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
          className="min-h-20"
        />
      </div>
    );
  }
  if (field.type === "select") {
    return (
      <div className="space-y-1">
        <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {field.label}
        </label>
        <select
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
          className="flat-input w-full px-3 py-2 text-sm"
        >
          <option value="">Select</option>
          {(field.options ?? []).map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
      </div>
    );
  }
  return (
    <div className="space-y-1">
      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
        {field.label}
      </label>
      <Input
        type={field.type === "number" ? "number" : field.type === "color" ? "color" : "text"}
        value={String(value ?? "")}
        onChange={(e) => onChange(field.type === "number" ? Number(e.target.value) : e.target.value)}
      />
    </div>
  );
}

export function LeaveSettingsCenter({
  targetSection,
  createSignal,
  onCreateHandled,
}: {
  targetSection?: LeaveSettingsSectionKey;
  createSignal?: number;
  onCreateHandled?: () => void;
}) {
  const { user } = useAuth();
  const actor = user?.name ?? "Admin User";
  const store = useLeaveSettingsStore();
  const [activeSection, setActiveSection] = useState<LeaveSettingsSectionKey>("general");
  const [query, setQuery] = useState("");
  const [showArchived, setShowArchived] = useState(false);
  const [editorOpen, setEditorOpen] = useState(false);
  const [editing, setEditing] = useState<LeaveSettingsRecord | null>(null);
  const [draft, setDraft] = useState<Record<string, unknown>>({});

  const section = SETTINGS_SECTIONS.find((s) => s.key === activeSection) ?? SETTINGS_SECTIONS[0];
  const rows = store.data[activeSection] ?? [];

  const filteredRows = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows.filter((r) => {
      if (!showArchived && r.archived_at) return false;
      if (!q) return true;
      return r.name.toLowerCase().includes(q) || r.code.toLowerCase().includes(q);
    });
  }, [query, rows, showArchived]);

  const openNew = () => {
    setEditing(null);
    setDraft({
      id: `cfg-${Date.now()}`,
      name: "",
      code: "",
      is_active: true,
      ...Object.fromEntries(section.schema.map((f) => [f.key, f.type === "boolean" ? false : ""])),
    });
    setEditorOpen(true);
  };

  const openEdit = (row: LeaveSettingsRecord) => {
    setEditing(row);
    setDraft({ id: row.id, name: row.name, code: row.code, is_active: row.is_active, ...row.config });
    setEditorOpen(true);
  };

  const save = () => {
    const id = String(draft.id ?? `cfg-${Date.now()}`);
    const next: LeaveSettingsRecord = {
      id,
      name: String(draft.name ?? "").trim(),
      code: String(draft.code ?? "").trim(),
      is_active: Boolean(draft.is_active),
      archived_at: editing?.archived_at ?? null,
      updated_at: new Date().toISOString(),
      config: Object.fromEntries(
        Object.entries(draft).filter(([k]) => !["id", "name", "code", "is_active"].includes(k)),
      ),
    };
    if (!next.name || !next.code) return;
    store.upsert(activeSection, next, actor, !editing);
    setEditorOpen(false);
  };

  useEffect(() => {
    if (!targetSection) return;
    setActiveSection(targetSection);
  }, [targetSection]);

  useEffect(() => {
    if (!createSignal) return;
    openNew();
    onCreateHandled?.();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [createSignal]);

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[260px_minmax(0,1fr)] gap-5 items-start">
      <aside className="flat-card bg-card p-3 sticky top-4 max-h-[calc(100vh-130px)] overflow-y-auto">
        <p className="px-3 pb-3 text-[10px] uppercase tracking-widest text-muted-foreground font-semibold">
          Leave Settings
        </p>
        <nav className="space-y-0.5">
          {SETTINGS_SECTIONS.map((s) => {
            const isActive = s.key === activeSection;
            return (
              <button
                key={s.key}
                onClick={() => setActiveSection(s.key)}
                className={cn(
                  "w-full px-3 py-2.5 text-left rounded-lg text-sm transition-colors",
                  isActive
                    ? "bg-secondary text-foreground font-semibold"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                )}
              >
                {s.label}
              </button>
            );
          })}
        </nav>
      </aside>

      <div className="space-y-5">
        <div className="flat-card bg-card p-5">
          <h2 className="text-base font-semibold text-foreground">{section.label}</h2>
          <p className="text-xs text-muted-foreground mt-1">{section.description}</p>
          <div className="mt-4 flex flex-col md:flex-row gap-2 md:items-center md:justify-between">
            <div className="relative w-full md:max-w-md">
              <Search className="w-4 h-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-9"
                placeholder="Search settings by name/code"
              />
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowArchived((v) => !v)}
                className="px-3 py-2 rounded-lg text-xs font-semibold bg-secondary border border-border"
              >
                {showArchived ? "Hide Archived" : "Show Archived"}
              </button>
              <button
                onClick={openNew}
                className="px-3 py-2 rounded-lg text-xs font-semibold bg-foreground text-primary-foreground inline-flex items-center gap-2"
              >
                <Plus className="w-4 h-4" /> New
              </button>
            </div>
          </div>
        </div>

        <div className="flat-card bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-secondary border-b border-border sticky top-0">
                <tr>
                  {["Name", "Code", "Status", "Updated", "Actions"].map((h) => (
                    <th
                      key={h}
                      className={cn(
                        "px-4 py-3 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider",
                        h === "Actions" && "sticky right-0 bg-secondary",
                      )}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredRows.map((r) => (
                  <tr key={r.id} className="hover:bg-secondary/40">
                    <td className="px-4 py-3 text-sm font-medium text-foreground">{r.name}</td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">{r.code}</td>
                    <td className="px-4 py-3">
                      <span className="text-[11px] font-semibold px-2 py-0.5 rounded-md border bg-secondary text-muted-foreground border-border">
                        {r.archived_at ? "Archived" : r.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {new Date(r.updated_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 sticky right-0 bg-card">
                      <div className="flex gap-1">
                        <button
                          onClick={() => openEdit(r)}
                          className="px-2 py-1 rounded border border-border text-[11px]"
                        >
                          <Edit3 className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => store.clone(activeSection, r.id, actor)}
                          className="px-2 py-1 rounded border border-border text-[11px]"
                        >
                          <Copy className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => store.setActive(activeSection, r.id, !r.is_active, actor)}
                          className="px-2 py-1 rounded border border-border text-[11px]"
                        >
                          <Check className="w-3 h-3" />
                        </button>
                        {!r.archived_at ? (
                          <button
                            onClick={() => store.archive(activeSection, r.id, actor)}
                            className="px-2 py-1 rounded border border-border text-[11px]"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        ) : (
                          <button
                            onClick={() => store.restore(activeSection, r.id, actor)}
                            className="px-2 py-1 rounded border border-border text-[11px]"
                          >
                            <RotateCcw className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {filteredRows.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-4 py-10 text-center text-sm text-muted-foreground">
                      No records found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="flat-card bg-card p-5">
          <h3 className="text-sm font-semibold text-foreground">Recent Audit</h3>
          <div className="mt-3 space-y-2 max-h-64 overflow-y-auto">
            {store.audit
              .filter((a) => a.section === activeSection)
              .slice(0, 12)
              .map((a) => (
                <div key={a.id} className="p-3 rounded-lg border border-border bg-secondary/30">
                  <p className="text-sm font-medium text-foreground">
                    {a.action} · {a.target_id}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(a.at).toLocaleString()} · {a.actor}
                  </p>
                </div>
              ))}
          </div>
        </div>
      </div>

      <Dialog open={editorOpen} onOpenChange={setEditorOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>{editing ? "Edit Setting" : "Create Setting"}</DialogTitle>
            <DialogDescription>
              Schema-driven form for {section.label}. You can add custom fields in JSON.
            </DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[60vh] overflow-y-auto pr-1">
            {section.schema.map((field) => (
              <DynamicField
                key={field.key}
                field={field}
                value={draft[field.key]}
                onChange={(v) => setDraft((prev) => ({ ...prev, [field.key]: v }))}
              />
            ))}
          </div>
          <DialogFooter>
            <button
              onClick={() => setEditorOpen(false)}
              className="px-3 py-2 rounded-lg text-xs font-semibold bg-secondary border border-border"
            >
              Cancel
            </button>
            <button
              onClick={save}
              className="px-3 py-2 rounded-lg text-xs font-semibold bg-foreground text-primary-foreground"
            >
              Save
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
