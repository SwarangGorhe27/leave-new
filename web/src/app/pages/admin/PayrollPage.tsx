import { useState } from "react";
import { Wallet, X, Download, TrendingUp, Users } from "lucide-react";
import { payrollRecords, PayrollRecord, PayrollStatus } from "../../components/employees/mockAdminData";

const STATUS_BADGE: Record<PayrollStatus, string> = {
  Processed: "bg-[#212529] text-[#F8F9FA]",
  Pending:   "bg-[#6C757D] text-white",
  "On Hold": "bg-[#CED4DA] text-[#212529]",
};

const fmt = (n: number) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);

const MONTHS = ["April 2026", "March 2026", "February 2026", "January 2026"];

/* ── Payslip Modal ──────────────────────────────────────────── */
function PayslipModal({ record, onClose }: { record: PayrollRecord; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-[#212529]/50" onClick={onClose} />
      <div className="relative w-full max-w-lg bg-card border border-border rounded-xl shadow-xl overflow-hidden">

        {/* Header */}
        <div className="bg-foreground text-primary-foreground p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-[11px] font-semibold text-primary-foreground/60 uppercase tracking-widest">Payslip</p>
              <p className="text-lg font-bold mt-0.5">April 2026</p>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 bg-primary-foreground/10 hover:bg-primary-foreground/20 rounded-lg flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="flex items-center gap-4">
            <div
              className="w-11 h-11 rounded-lg flex items-center justify-center text-sm font-bold border border-primary-foreground/20"
              style={{ backgroundColor: record.avatarColor }}
            >
              {record.initials}
            </div>
            <div>
              <p className="font-semibold">{record.employeeName}</p>
              <p className="text-sm text-primary-foreground/70 mt-0.5">{record.designation} · {record.department}</p>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="portal-page admin-dashboard">
          {/* Earnings */}
          <div className="bg-background border border-border rounded-lg p-4">
            <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-widest mb-3">Earnings</p>
            <div className="space-y-2.5">
              {[
                { label: "Basic Salary",              value: record.basicSalary       },
                { label: "House Rent Allowance (HRA)", value: record.hra              },
                { label: "Conveyance Allowance",       value: record.conveyance       },
                { label: "Medical Allowance",          value: record.medicalAllowance },
                { label: "Special Allowance",          value: record.specialAllowance },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between text-sm">
                  <span className="text-muted-foreground">{label}</span>
                  <span className="font-medium text-foreground">{fmt(value)}</span>
                </div>
              ))}
              <div className="flex justify-between text-sm border-t border-border pt-2.5 mt-2.5">
                <span className="font-semibold text-foreground">Gross Salary</span>
                <span className="font-bold text-foreground">{fmt(record.grossSalary)}</span>
              </div>
            </div>
          </div>

          {/* Deductions */}
          <div className="bg-background border border-border rounded-lg p-4">
            <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-widest mb-3">Deductions</p>
            <div className="space-y-2.5">
              {[
                { label: "Provident Fund (PF)", value: record.pf  },
                { label: "TDS",                  value: record.tds },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between text-sm">
                  <span className="text-muted-foreground">{label}</span>
                  <span className="font-medium text-[#6C757D]">– {fmt(value)}</span>
                </div>
              ))}
              <div className="flex justify-between text-sm border-t border-border pt-2.5 mt-2.5">
                <span className="font-semibold text-foreground">Total Deductions</span>
                <span className="font-bold text-[#6C757D]">– {fmt(record.pf + record.tds)}</span>
              </div>
            </div>
          </div>

          {/* Net pay */}
          <div className="bg-foreground text-primary-foreground rounded-lg p-4 flex justify-between items-center">
            <span className="text-sm font-semibold">Net Pay (Take Home)</span>
            <span className="text-xl font-bold">{fmt(record.netSalary)}</span>
          </div>
        </div>

        <div className="px-6 pb-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium border border-border text-foreground rounded-lg hover:bg-secondary transition-colors"
          >
            Close
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-foreground text-primary-foreground text-sm font-medium rounded-lg hover:bg-accent transition-colors">
            <Download className="w-4 h-4" /> Download PDF
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── Main Page ──────────────────────────────────────────────── */
export function PayrollPage() {
  const [month, setMonth]                 = useState(MONTHS[0]);
  const [selectedRecord, setSelectedRecord] = useState<PayrollRecord | null>(null);
  const [filterStatus, setFilterStatus]   = useState<PayrollStatus | "All">("All");

  const filtered    = payrollRecords.filter((r) => filterStatus === "All" || r.status === filterStatus);
  const totalGross  = payrollRecords.reduce((s, r) => s + r.grossSalary, 0);
  const totalNet    = payrollRecords.reduce((s, r) => s + r.netSalary, 0);
  const totalDeduct = payrollRecords.reduce((s, r) => s + r.pf + r.tds, 0);

  return (
    <>
      <div className="portal-page admin-dashboard">

        {/* ── Stat Cards ────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { icon: Users,      label: "Total Employees",    value: payrollRecords.length, sub: "On payroll"       },
            { icon: Wallet,     label: "Total Gross Payout", value: fmt(totalGross),       sub: "Before deductions"},
            { icon: TrendingUp, label: "Total Net Payout",   value: fmt(totalNet),         sub: "After deductions" },
          ].map(({ icon: Icon, label, value, sub }) => (
            <div key={label} className="flat-card flat-card-hover bg-card p-5 flex items-start gap-4">
              <div className="w-10 h-10 rounded-lg bg-secondary border border-border flex items-center justify-center flex-shrink-0">
                <Icon className="w-5 h-5 text-foreground" />
              </div>
              <div>
                <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">{label}</p>
                <p className="text-xl font-bold text-foreground mt-0.5">{value}</p>
                <p className="text-xs text-muted-foreground mt-1">{sub}</p>
              </div>
            </div>
          ))}
        </div>

        {/* ── Table Card ────────────────────────────────── */}
        <div className="flat-card bg-card overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-4 border-b border-border">
            <h2 className="text-sm font-semibold text-foreground">Salary Register</h2>
            <div className="flex flex-wrap items-center gap-2">
              <select
                value={month}
                onChange={(e) => setMonth(e.target.value)}
                className="flat-input text-sm px-3 py-2 cursor-pointer appearance-none font-medium"
              >
                {MONTHS.map((m) => <option key={m}>{m}</option>)}
              </select>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as PayrollStatus | "All")}
                className="flat-input text-sm px-3 py-2 cursor-pointer appearance-none font-medium"
              >
                <option value="All">All Status</option>
                <option>Processed</option>
                <option>Pending</option>
                <option>On Hold</option>
              </select>
              <button className="flex items-center gap-2 px-3 py-2 text-sm font-medium border border-border rounded-lg
                text-foreground hover:bg-secondary transition-colors">
                <Download className="w-4 h-4" /> Export
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-secondary border-b border-border">
                  {["Employee", "Department", "Gross Salary", "Deductions", "Net Salary", "Status", "Payslip"].map((h) => (
                    <th key={h} className="text-left px-6 py-3 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider whitespace-nowrap">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map((rec) => (
                  <tr key={rec.employeeId} className="hover:bg-secondary transition-colors duration-150">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                          style={{ backgroundColor: rec.avatarColor }}
                        >
                          {rec.initials}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-foreground">{rec.employeeName}</p>
                          <p className="text-xs text-muted-foreground">{rec.employeeId}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">{rec.department}</td>
                    <td className="px-6 py-4 text-sm font-medium text-foreground">{fmt(rec.grossSalary)}</td>
                    <td className="px-6 py-4 text-sm font-medium text-[#6C757D]">– {fmt(rec.pf + rec.tds)}</td>
                    <td className="px-6 py-4 text-sm font-bold text-foreground">{fmt(rec.netSalary)}</td>
                    <td className="px-6 py-4">
                      <span className={`text-xs px-2.5 py-1 rounded-md font-medium ${STATUS_BADGE[rec.status]}`}>
                        {rec.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => setSelectedRecord(rec)}
                        className="text-xs font-medium text-foreground border border-border px-3 py-1.5 rounded-md
                          hover:bg-secondary transition-colors"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="px-6 py-3 border-t border-border bg-secondary text-xs text-muted-foreground font-medium flex justify-between">
            <span>{filtered.length} employees</span>
            <span>Total deductions: {fmt(totalDeduct)}</span>
          </div>
        </div>
      </div>

      {selectedRecord && (
        <PayslipModal record={selectedRecord} onClose={() => setSelectedRecord(null)} />
      )}
    </>
  );
}
