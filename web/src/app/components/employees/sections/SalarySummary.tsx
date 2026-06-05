import { useMemo, useState } from "react";
import { Employee, SalaryRecord } from "../mockData";
import { TrendingUp, TrendingDown, Save, X, Plus, Pencil, Trash2, IndianRupee } from "lucide-react";
import { useAdminSync } from "../../admin/useAdminSync";
import { ConfirmationDialog } from "../employee-details/ConfirmationDialog";
import { format } from "date-fns";

interface Props {
  employee: Employee;
  showActions?: boolean;
}

const formatInr = (n: number) =>
  `₹${new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(
    Number.isFinite(n) ? n : 0
  )}`;

const formatDate = (d?: string) => {
  if (!d) return "—";
  try { return format(new Date(d), "dd MMM yyyy"); } catch { return "—"; }
};

const emptySalary = (): SalaryRecord => ({
  id: `sal-new-${Date.now()}`,
  effectiveDate: "",
  basicSalary: 0,
  hra: 0,
  conveyance: 0,
  medicalAllowance: 0,
  specialAllowance: 0,
  grossSalary: 0,
  pf: 0,
  tds: 0,
  netSalary: 0,
});

function InrInput({ value, onChange }: { value: number; onChange: (n: number) => void }) {
  return (
    <div className="relative w-36">
      <span className="absolute left-2 top-1/2 -translate-y-1/2 text-sm font-semibold text-muted-foreground">₹</span>
      <input
        type="number"
        min={0}
        value={value}
        onChange={(e) => onChange(Number(e.target.value) || 0)}
        className="w-full text-sm font-mono font-semibold bg-secondary/50 border border-border rounded-md pl-6 pr-2 py-1 text-right focus:outline-none focus:ring-2 focus:ring-primary/30"
      />
    </div>
  );
}

function SalaryFieldRow({
  label,
  value,
  isEditing,
  onChange,
  type = "normal",
}: {
  label: string;
  value: number;
  isEditing: boolean;
  onChange?: (n: number) => void;
  type?: "normal" | "deduction" | "gross" | "total";
}) {
  return (
    <div
      className={`flex justify-between items-center py-3 ${
        type === "total"
          ? "border-t border-border pt-4 mt-2"
          : "border-b border-border last:border-0"
      }`}
    >
      <span
        className={`text-sm ${
          type === "total" ? "font-bold text-foreground" : "text-muted-foreground font-medium"
        }`}
      >
        {label}
      </span>
      {isEditing && type !== "gross" && type !== "total" && onChange ? (
        <InrInput value={value} onChange={onChange} />
      ) : (
        <span
          className={`text-sm font-mono ${
            type === "total" || type === "gross"
              ? "font-bold text-foreground"
              : type === "deduction"
                ? "font-semibold text-[#6C757D]"
                : "font-semibold text-foreground"
          }`}
        >
          {type === "deduction" ? `– ${formatInr(value)}` : formatInr(value)}
        </span>
      )}
    </div>
  );
}

export function SalarySummary({ employee, showActions = true }: Props) {
  const { handleAdminSave } = useAdminSync();

  const baseline = useMemo(() => employee.salaryHistory || [], [employee.salaryHistory]);
  const [records, setRecords] = useState<SalaryRecord[]>(baseline);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const updateRecord = (id: string, patch: Partial<SalaryRecord>) =>
    setRecords((prev) => prev.map((r) => (r.id === id ? { ...r, ...patch } : r)));

  // Auto-compute gross = sum of earnings, net = gross - deductions
  const recompute = (id: string, patch: Partial<SalaryRecord>) => {
    setRecords((prev) =>
      prev.map((r) => {
        if (r.id !== id) return r;
        const next = { ...r, ...patch };
        const gross =
          (next.basicSalary || 0) +
          (next.hra || 0) +
          (next.conveyance || 0) +
          (next.medicalAllowance || 0) +
          (next.specialAllowance || 0);
        const net = gross - (next.pf || 0) - (next.tds || 0);
        return { ...next, grossSalary: gross, netSalary: net };
      })
    );
  };

  const handleAdd = () => {
    const rec = emptySalary();
    setRecords((prev) => [...prev, rec]);
    setEditingId(rec.id);
  };

  const handleEdit = (id: string) => {
    setRecords(baseline.map((r) => ({ ...r })));
    setEditingId(id);
  };

  const handleSave = async (id: string) => {
    const ok = await handleAdminSave("Salary Details", employee, {
      ...employee,
      salaryHistory: records,
    });
    if (ok) setEditingId(null);
  };

  const handleCancel = (id: string) => {
    const isNew = !baseline.find((r) => r.id === id);
    if (isNew) setRecords(baseline.map((r) => ({ ...r })));
    else setRecords(baseline.map((r) => ({ ...r })));
    setEditingId(null);
  };

  const confirmDelete = async () => {
    if (!deleteId) return;
    const next = records.filter((r) => r.id !== deleteId);
    const ok = await handleAdminSave("Salary Details", employee, {
      ...employee,
      salaryHistory: next,
    });
    if (ok) {
      setRecords(next);
      if (editingId === deleteId) setEditingId(null);
    }
    setDeleteId(null);
  };

  return (
    <div className="space-y-5 pb-24">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-foreground">Employee Salary</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Compensation history for {employee.name} (INR)
          </p>
        </div>
        {showActions && (
          <button
            type="button"
            onClick={handleAdd}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-white rounded-lg text-xs font-bold hover:bg-primary/90 transition-all"
          >
            <Plus size={13} /> Add Salary
          </button>
        )}
      </div>

      {/* Empty state */}
      {records.length === 0 ? (
        <div className="flat-card bg-card border border-dashed border-border p-10 text-center">
          <IndianRupee className="w-8 h-8 text-muted-foreground/40 mx-auto mb-3" />
          <p className="text-sm font-semibold text-muted-foreground">No salary records yet.</p>
          <p className="text-xs text-muted-foreground mt-1">
            Click "Add Salary" to create the first salary entry.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {records.map((rec, index) => {
            const isEditing = editingId === rec.id;
            const totalDeductions = (rec.pf || 0) + (rec.tds || 0);

            return (
              <div key={rec.id} className="flat-card bg-card border border-border p-6 space-y-5">
                {/* Card header */}
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-secondary border border-border flex items-center justify-center flex-shrink-0">
                      <IndianRupee className="w-4 h-4 text-foreground" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-foreground">
                        Salary Record #{index + 1}
                      </p>
                      {rec.effectiveDate && !isEditing && (
                        <p className="text-xs text-muted-foreground mt-0.5">
                          Effective from {formatDate(rec.effectiveDate)}
                        </p>
                      )}
                    </div>
                  </div>

                  {!isEditing && (
                    <p className="text-sm font-mono font-bold text-foreground">
                      {formatInr(rec.grossSalary)} <span className="text-xs font-medium text-muted-foreground">/ month</span>
                    </p>
                  )}

                  {showActions && (
                    <div className="flex items-center gap-2">
                      {isEditing ? (
                        <>
                          <button
                            type="button"
                            onClick={() => handleSave(rec.id)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-bold hover:bg-primary/90 transition-colors"
                          >
                            <Save className="w-3.5 h-3.5" /> Save
                          </button>
                          <button
                            type="button"
                            onClick={() => handleCancel(rec.id)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-bold hover:bg-secondary transition-colors"
                          >
                            <X className="w-3.5 h-3.5" /> Cancel
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            type="button"
                            onClick={() => handleEdit(rec.id)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-bold hover:bg-secondary transition-colors"
                          >
                            <Pencil className="w-3.5 h-3.5" /> Edit
                          </button>
                          <button
                            type="button"
                            onClick={() => setDeleteId(rec.id)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-destructive/40 text-destructive text-xs font-bold hover:bg-destructive/10 transition-colors"
                          >
                            <Trash2 className="w-3.5 h-3.5" /> Delete
                          </button>
                        </>
                      )}
                    </div>
                  )}
                </div>

                {/* Effective date field (editing only) */}
                {isEditing && (
                  <div className="flex items-center gap-4 pb-3 border-b border-border">
                    <label className="text-sm text-muted-foreground font-medium w-40">Effective Date</label>
                    <input
                      type="date"
                      value={rec.effectiveDate || ""}
                      onChange={(e) => updateRecord(rec.id, { effectiveDate: e.target.value })}
                      className="text-sm bg-secondary/50 border border-border rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary/30"
                    />
                  </div>
                )}

                {/* Summary tiles (view mode) */}
                {!isEditing && (
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="flat-card bg-foreground text-primary-foreground p-5">
                      <p className="text-[11px] font-bold uppercase tracking-widest text-primary-foreground/60">Gross Salary</p>
                      <p className="text-2xl mt-2 font-mono font-bold">{formatInr(rec.grossSalary)}</p>
                      <p className="text-xs text-primary-foreground/60 mt-1.5 font-medium">Per Month</p>
                    </div>
                    <div className="flat-card bg-card border border-border p-5">
                      <p className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground">Total Deductions</p>
                      <p className="text-2xl mt-2 font-mono font-bold text-[#6C757D]">{formatInr(totalDeductions)}</p>
                      <p className="text-xs text-muted-foreground mt-1.5 font-medium">PF + TDS</p>
                    </div>
                    <div className="flat-card bg-secondary border border-foreground/20 p-5">
                      <p className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground">Net Salary</p>
                      <p className="text-2xl mt-2 font-mono font-bold">{formatInr(rec.netSalary)}</p>
                      <p className="text-xs text-muted-foreground mt-1.5 font-medium">Take Home</p>
                    </div>
                  </div>
                )}

                {/* Earnings + Deductions */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                  <div className="flat-card bg-card border border-border p-5">
                    <h4 className="text-sm font-bold text-foreground mb-4 flex items-center gap-3">
                      <div className="w-7 h-7 rounded-lg bg-secondary border border-border flex items-center justify-center">
                        <TrendingUp className="w-3.5 h-3.5 text-foreground" />
                      </div>
                      Earnings
                    </h4>
                    <SalaryFieldRow label="Basic Salary" value={rec.basicSalary} isEditing={isEditing} onChange={(n) => recompute(rec.id, { basicSalary: n })} />
                    <SalaryFieldRow label="House Rent Allowance (HRA)" value={rec.hra} isEditing={isEditing} onChange={(n) => recompute(rec.id, { hra: n })} />
                    <SalaryFieldRow label="Conveyance Allowance" value={rec.conveyance} isEditing={isEditing} onChange={(n) => recompute(rec.id, { conveyance: n })} />
                    <SalaryFieldRow label="Medical Allowance" value={rec.medicalAllowance} isEditing={isEditing} onChange={(n) => recompute(rec.id, { medicalAllowance: n })} />
                    <SalaryFieldRow label="Special Allowance" value={rec.specialAllowance} isEditing={isEditing} onChange={(n) => recompute(rec.id, { specialAllowance: n })} />
                    <SalaryFieldRow label="Gross Earnings" value={rec.grossSalary} isEditing={isEditing} type="gross" />
                  </div>

                  <div className="flat-card bg-card border border-border p-5 flex flex-col">
                    <h4 className="text-sm font-bold text-foreground mb-4 flex items-center gap-3">
                      <div className="w-7 h-7 rounded-lg bg-secondary border border-border flex items-center justify-center">
                        <TrendingDown className="w-3.5 h-3.5 text-foreground" />
                      </div>
                      Deductions
                    </h4>
                    <SalaryFieldRow label="Provident Fund (PF)" value={rec.pf} isEditing={isEditing} type="deduction" onChange={(n) => recompute(rec.id, { pf: n })} />
                    <SalaryFieldRow label="Tax Deducted at Source (TDS)" value={rec.tds} isEditing={isEditing} type="deduction" onChange={(n) => recompute(rec.id, { tds: n })} />
                    <SalaryFieldRow label="Total Deductions" value={totalDeductions} isEditing={false} type="total" />

                    <div className="mt-auto pt-5">
                      <div className="bg-foreground text-primary-foreground rounded-lg p-5">
                        <p className="text-[11px] font-bold uppercase tracking-widest text-primary-foreground/60">Net Take Home</p>
                        <p className="text-2xl mt-2 font-mono font-bold">{formatInr(rec.netSalary)}</p>
                        <p className="text-xs text-primary-foreground/60 mt-1.5 font-medium">After all deductions</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Annual CTC */}
                <div className="bg-secondary border border-border rounded-lg p-5 flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-sm font-bold text-foreground">Annual CTC</p>
                    <p className="text-xs text-muted-foreground mt-0.5">Cost to Company per year (INR)</p>
                  </div>
                  <p className="text-xl font-mono font-bold text-foreground">{formatInr(rec.grossSalary * 12)}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <ConfirmationDialog
        open={deleteId !== null}
        onOpenChange={(o) => !o && setDeleteId(null)}
        title="Delete salary record?"
        description="This salary record will be permanently removed. This action cannot be undone."
        confirmLabel="Delete"
        destructive
        onConfirm={confirmDelete}
      />
    </div>
  );
}
