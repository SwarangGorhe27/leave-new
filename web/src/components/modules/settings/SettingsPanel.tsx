import { useState } from 'react';
import { Plus, Pencil, Trash2, Check, X } from 'lucide-react';
import { cn } from '@utils/utils';
import {
  useDepartments, useDesignations, useEmploymentTypes,
  useCompanyLocations, useLeaveTypesMaster, useShiftTypes,
  useBranches, useCostCenters, useShifts, usePayComponents, useSalaryStructures,
  type MasterItem,
} from '@hooks/useMasters';

// ─── Inline editable master table ────────────────────────────────────

interface MasterTableProps {
  label: string;
  items: MasterItem[];
  isLoading: boolean;
  onCreate: (name: string, code?: string) => void;
  onUpdate: (id: number | string, name: string, code?: string) => void;
  onDelete: (id: number | string) => void;
  isPending?: boolean;
  showCode?: boolean;
}

function MasterTable({ label, items, isLoading, onCreate, onUpdate, onDelete, isPending, showCode }: MasterTableProps) {
  const [addName, setAddName] = useState('');
  const [addCode, setAddCode] = useState('');
  const [editId, setEditId] = useState<number | string | null>(null);
  const [editName, setEditName] = useState('');
  const [editCode, setEditCode] = useState('');
  const [confirmDelete, setConfirmDelete] = useState<number | string | null>(null);

  const inputCls = 'w-full rounded-lg border border-surface-200 bg-surface-0 px-2.5 py-1.5 text-sm text-surface-900 placeholder-surface-400 focus:border-brand-400 focus:outline-none dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder-white/30';

  function startEdit(item: MasterItem) {
    setEditId(item.id);
    setEditName(item.name);
    setEditCode(String(item.code ?? ''));
  }

  function saveEdit() {
    if (editId !== null && editName.trim()) {
      onUpdate(editId, editName.trim(), editCode.trim() || undefined);
      setEditId(null);
    }
  }

  function handleAdd() {
    if (!addName.trim()) return;
    onCreate(addName.trim(), addCode.trim() || undefined);
    setAddName('');
    setAddCode('');
  }

  return (
    <div className="rounded-2xl border border-surface-200/70 bg-surface-0 shadow-xs dark:border-white/10 dark:bg-white/5">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-surface-100 px-4 py-3 dark:border-white/5">
        <h3 className="text-sm font-semibold text-surface-900 dark:text-white">{label}</h3>
        <span className="rounded-full bg-surface-100 px-2 py-0.5 text-xs text-surface-500 dark:bg-white/10 dark:text-white/40">
          {items.length}
        </span>
      </div>

      {/* Add row */}
      <div className="flex items-center gap-2 border-b border-surface-100 px-4 py-2.5 dark:border-white/5">
        <input
          type="text"
          placeholder="Name *"
          value={addName}
          onChange={(e) => setAddName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
          className={cn(inputCls, 'flex-1')}
        />
        {showCode && (
          <input
            type="text"
            placeholder="Code"
            value={addCode}
            onChange={(e) => setAddCode(e.target.value)}
            className={cn(inputCls, 'w-20')}
          />
        )}
        <button
          type="button"
          onClick={handleAdd}
          disabled={!addName.trim() || isPending}
          className="flex items-center gap-1 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          <Plus className="h-3.5 w-3.5" /> Add
        </button>
      </div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-2 p-3">
          {[1, 2, 3].map((i) => <div key={i} className="h-9 animate-pulse rounded-lg bg-surface-100 dark:bg-white/10" />)}
        </div>
      ) : items.length === 0 ? (
        <p className="py-8 text-center text-sm text-surface-400 dark:text-white/30">No {label.toLowerCase()} yet.</p>
      ) : (
        <ul className="divide-y divide-surface-50 dark:divide-white/5">
          {items.map((item) => (
            <li key={item.id} className="flex items-center gap-2 px-4 py-2.5">
              {editId === item.id ? (
                <>
                  <input
                    autoFocus
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && saveEdit()}
                    className={cn(inputCls, 'flex-1')}
                  />
                  {showCode && (
                    <input
                      value={editCode}
                      onChange={(e) => setEditCode(e.target.value)}
                      className={cn(inputCls, 'w-20')}
                    />
                  )}
                  <button onClick={saveEdit} className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-600 text-white hover:bg-emerald-700">
                    <Check className="h-3.5 w-3.5" />
                  </button>
                  <button onClick={() => setEditId(null)} className="flex h-7 w-7 items-center justify-center rounded-lg border border-surface-200 text-surface-500 hover:bg-surface-100 dark:border-white/10 dark:text-white/50">
                    <X className="h-3.5 w-3.5" />
                  </button>
                </>
              ) : (
                <>
                  <span className="flex-1 text-sm text-surface-800 dark:text-white/80">{item.name}</span>
                  {showCode && item.code && (
                    <span className="rounded bg-surface-100 px-1.5 py-0.5 font-mono text-xs text-surface-500 dark:bg-white/10 dark:text-white/40">
                      {String(item.code)}
                    </span>
                  )}
                  <span className={cn('h-2 w-2 rounded-full', item.is_active ? 'bg-emerald-500' : 'bg-surface-300 dark:bg-white/20')} />
                  <button onClick={() => startEdit(item)} className="flex h-7 w-7 items-center justify-center rounded-lg text-surface-400 hover:bg-surface-100 hover:text-surface-700 dark:hover:bg-white/10 dark:hover:text-white/70">
                    <Pencil className="h-3.5 w-3.5" />
                  </button>
                  {confirmDelete === item.id ? (
                    <div className="flex items-center gap-1">
                      <button onClick={() => { onDelete(item.id); setConfirmDelete(null); }} className="rounded-lg bg-red-600 px-2 py-1 text-xs font-medium text-white hover:bg-red-700">Delete</button>
                      <button onClick={() => setConfirmDelete(null)} className="rounded-lg border border-surface-200 px-2 py-1 text-xs dark:border-white/10">Cancel</button>
                    </div>
                  ) : (
                    <button onClick={() => setConfirmDelete(item.id)} className="flex h-7 w-7 items-center justify-center rounded-lg text-surface-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20 dark:hover:text-red-400">
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  )}
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ─── Master section wrapper ────────────────────────────────────────

function useMasterSection(hooks: typeof useDepartments) {
  const list = hooks.useList();
  const create = hooks.useCreate();
  const update = hooks.useUpdate();
  const del = hooks.useDelete();
  return { list, create, update, del };
}

// ─── Settings Panel ────────────────────────────────────────────────

type SettingsTab =
  | 'departments'
  | 'designations'
  | 'employment-types'
  | 'locations'
  | 'leave-types'
  | 'shift-types'
  | 'branches'
  | 'cost-centers'
  | 'shifts'
  | 'pay-components'
  | 'salary-structures';

const TABS: { key: SettingsTab; label: string }[] = [
  { key: 'departments', label: 'Departments' },
  { key: 'designations', label: 'Designations' },
  { key: 'employment-types', label: 'Employment Types' },
  { key: 'locations', label: 'Locations' },
  { key: 'branches', label: 'Branches' },
  { key: 'cost-centers', label: 'Cost Centers' },
  { key: 'leave-types', label: 'Leave Types' },
  { key: 'shift-types', label: 'Shift Types' },
  { key: 'shifts', label: 'Shift Master' },
  { key: 'pay-components', label: 'Pay Components' },
  { key: 'salary-structures', label: 'Salary Structures' },
];

export function SettingsPanel() {
  const [tab, setTab] = useState<SettingsTab>('departments');

  const dept = useMasterSection(useDepartments);
  const desig = useMasterSection(useDesignations);
  const empType = useMasterSection(useEmploymentTypes);
  const loc = useMasterSection(useCompanyLocations);
  const leaveType = useMasterSection(useLeaveTypesMaster);
  const shiftType = useMasterSection(useShiftTypes);
  const branch = useMasterSection(useBranches);
  const costCenter = useMasterSection(useCostCenters);
  const shift = useMasterSection(useShifts);
  const payComponent = useMasterSection(usePayComponents);
  const salaryStructure = useMasterSection(useSalaryStructures);

  type SectionMap = Record<SettingsTab, {
    label: string;
    items: MasterItem[];
    isLoading: boolean;
    onCreate: (n: string, c?: string) => void;
    onUpdate: (id: number | string, n: string, c?: string) => void;
    onDelete: (id: number | string) => void;
    isPending?: boolean;
    showCode?: boolean;
  }>;

  const sections: SectionMap = {
    departments: {
      label: 'Departments',
      items: (dept.list.data ?? []) as MasterItem[],
      isLoading: dept.list.isLoading,
      onCreate: (n, c) => dept.create.mutate({ name: n, code: c, is_active: true }),
      onUpdate: (id, n, c) => dept.update.mutate({ id, name: n, code: c }),
      onDelete: (id) => dept.del.mutate(id),
      isPending: dept.create.isPending,
      showCode: true,
    },
    designations: {
      label: 'Designations',
      items: (desig.list.data ?? []) as MasterItem[],
      isLoading: desig.list.isLoading,
      onCreate: (n, c) => desig.create.mutate({ name: n, code: c, is_active: true }),
      onUpdate: (id, n, c) => desig.update.mutate({ id, name: n, code: c }),
      onDelete: (id) => desig.del.mutate(id),
      isPending: desig.create.isPending,
      showCode: true,
    },
    'employment-types': {
      label: 'Employment Types',
      items: (empType.list.data ?? []) as MasterItem[],
      isLoading: empType.list.isLoading,
      onCreate: (n, c) => empType.create.mutate({ name: n, code: c, is_active: true }),
      onUpdate: (id, n, c) => empType.update.mutate({ id, name: n, code: c }),
      onDelete: (id) => empType.del.mutate(id),
      isPending: empType.create.isPending,
    },
    locations: {
      label: 'Company Locations',
      items: (loc.list.data ?? []) as MasterItem[],
      isLoading: loc.list.isLoading,
      onCreate: (n, c) => loc.create.mutate({ name: n, code: c, is_active: true }),
      onUpdate: (id, n, c) => loc.update.mutate({ id, name: n, code: c }),
      onDelete: (id) => loc.del.mutate(id),
      isPending: loc.create.isPending,
    },
    branches: {
      label: 'Branches',
      items: (branch.list.data ?? []) as MasterItem[],
      isLoading: branch.list.isLoading,
      onCreate: (n, c) => branch.create.mutate({ name: n, code: c, is_active: true }),
      onUpdate: (id, n, c) => branch.update.mutate({ id, name: n, code: c }),
      onDelete: (id) => branch.del.mutate(id),
      isPending: branch.create.isPending,
      showCode: true,
    },
    'cost-centers': {
      label: 'Cost Centers',
      items: (costCenter.list.data ?? []) as MasterItem[],
      isLoading: costCenter.list.isLoading,
      onCreate: (n, c) => costCenter.create.mutate({ name: n, code: c, is_active: true }),
      onUpdate: (id, n, c) => costCenter.update.mutate({ id, name: n, code: c }),
      onDelete: (id) => costCenter.del.mutate(id),
      isPending: costCenter.create.isPending,
      showCode: true,
    },
    'leave-types': {
      label: 'Leave Types',
      items: (leaveType.list.data ?? []) as MasterItem[],
      isLoading: leaveType.list.isLoading,
      onCreate: (n, c) => leaveType.create.mutate({ name: n, code: c, is_active: true }),
      onUpdate: (id, n, c) => leaveType.update.mutate({ id, name: n, code: c }),
      onDelete: (id) => leaveType.del.mutate(id),
      isPending: leaveType.create.isPending,
      showCode: true,
    },
    'shift-types': {
      label: 'Shift Types',
      items: (shiftType.list.data ?? []) as MasterItem[],
      isLoading: shiftType.list.isLoading,
      onCreate: (n, c) => shiftType.create.mutate({ name: n, code: c, is_active: true }),
      onUpdate: (id, n, c) => shiftType.update.mutate({ id, name: n, code: c }),
      onDelete: (id) => shiftType.del.mutate(id),
      isPending: shiftType.create.isPending,
    },
    shifts: {
      label: 'Shift Master',
      items: (shift.list.data ?? []) as MasterItem[],
      isLoading: shift.list.isLoading,
      onCreate: (n, c) => shift.create.mutate({ name: n, code: c, is_active: true }),
      onUpdate: (id, n, c) => shift.update.mutate({ id, name: n, code: c }),
      onDelete: (id) => shift.del.mutate(id),
      isPending: shift.create.isPending,
      showCode: true,
    },
    'pay-components': {
      label: 'Pay Components',
      items: (payComponent.list.data ?? []) as MasterItem[],
      isLoading: payComponent.list.isLoading,
      onCreate: (n, c) => payComponent.create.mutate({ name: n, code: c, is_active: true }),
      onUpdate: (id, n, c) => payComponent.update.mutate({ id, name: n, code: c }),
      onDelete: (id) => payComponent.del.mutate(id),
      isPending: payComponent.create.isPending,
      showCode: true,
    },
    'salary-structures': {
      label: 'Salary Structures',
      items: (salaryStructure.list.data ?? []) as MasterItem[],
      isLoading: salaryStructure.list.isLoading,
      onCreate: (n, c) => salaryStructure.create.mutate({ name: n, code: c, is_active: true }),
      onUpdate: (id, n, c) => salaryStructure.update.mutate({ id, name: n, code: c }),
      onDelete: (id) => salaryStructure.del.mutate(id),
      isPending: salaryStructure.create.isPending,
      showCode: true,
    },
  };

  const current = sections[tab];

  return (
    <div className="flex flex-col gap-4 p-1">
      {/* Tab strip */}
      <div className="flex flex-wrap gap-1 rounded-xl border border-surface-200/70 bg-surface-50 p-1 dark:border-white/10 dark:bg-white/5">
        {TABS.map((t) => (
          <button
            key={t.key}
            type="button"
            onClick={() => setTab(t.key)}
            className={cn(
              'rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
              tab === t.key
                ? 'bg-surface-0 text-surface-900 shadow-sm dark:bg-white/10 dark:text-white'
                : 'text-surface-500 hover:text-surface-800 dark:text-white/40 dark:hover:text-white/70',
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      <MasterTable
        label={current.label}
        items={current.items}
        isLoading={current.isLoading}
        onCreate={current.onCreate}
        onUpdate={current.onUpdate}
        onDelete={current.onDelete}
        isPending={current.isPending}
        showCode={current.showCode}
      />
    </div>
  );
}
