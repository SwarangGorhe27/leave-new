import { useState } from "react";
import { Download, Eye, Wallet, X } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { employees } from "../../components/employees/mockData";
import { payrollRecords } from "../../components/employees/mockAdminData";

const fmt = (n: number) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);

/* ── Payslip Detail Modal ──────────────────────────────────── */
function PayslipModal({
  slip, onClose,
}: {
  slip: { month: string; year: string } & Partial<typeof payrollRecords[0]>;
  onClose: () => void;
}) {
  const rec = slip as any;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-[#212529]/50" onClick={onClose} />
      <div className="relative w-full max-w-md bg-card border border-border rounded-xl shadow-xl overflow-hidden">

        {/* Header */}
        <div className="bg-foreground text-primary-foreground p-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-[11px] font-semibold text-primary-foreground/60 uppercase tracking-widest">Payslip</p>
              <p className="text-lg font-bold mt-0.5">{rec.month} {rec.year}</p>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 bg-primary-foreground/10 hover:bg-primary-foreground/20 rounded-lg flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Earnings & Deductions */}
        <div className="p-6 space-y-4">
          <div className="bg-background border border-border rounded-lg p-4">
            <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-widest mb-3">Earnings</p>
            <div className="space-y-2">
              {[
                { label: "Basic Salary",   value: rec.basicSalary       },
                { label: "HRA",            value: rec.hra               },
                { label: "Conveyance",     value: rec.conveyance        },
                { label: "Medical",        value: rec.medicalAllowance  },
                { label: "Special",        value: rec.specialAllowance  },
              ].map(({ label, value }) => (
                <div key={label} className="flex justify-between text-sm">
                  <span className="text-muted-foreground">{label}</span>
                  <span className="font-medium text-foreground">{fmt(value || 0)}</span>
                </div>
              ))}
              <div className="flex justify-between text-sm border-t border-border pt-2">
                <span className="font-semibold text-foreground">Gross</span>
                <span className="font-bold text-foreground">{fmt(rec.grossSalary || 0)}</span>
              </div>
            </div>
          </div>

          <div className="bg-background border border-border rounded-lg p-4">
            <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-widest mb-3">Deductions</p>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">PF</span>
                <span className="text-[#6C757D] font-medium">– {fmt(rec.pf || 0)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">TDS</span>
                <span className="text-[#6C757D] font-medium">– {fmt(rec.tds || 0)}</span>
              </div>
            </div>
          </div>

          <div className="bg-foreground text-primary-foreground rounded-lg p-4 flex justify-between items-center">
            <span className="text-sm font-semibold">Net Pay</span>
            <span className="text-xl font-bold">{fmt(rec.netSalary || 0)}</span>
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

/* ── Main Page ─────────────────────────────────────────────── */
export function ManagerPayslipsPage() {
  const { user } = useAuth();
  const [selectedSlip, setSelectedSlip] = useState<any>(null);

  const emp       = employees.find((e) => e.id === user?.employeeId) || employees[0];
  const myPayroll = payrollRecords.find((p) => p.employeeId === emp.employeeId);

  const payslips = [
    { id: "APR26", month: "April",    year: "2026", ...myPayroll },
    { id: "MAR26", month: "March",    year: "2026", ...myPayroll },
    { id: "FEB26", month: "February", year: "2026", ...myPayroll },
    { id: "JAN26", month: "January",  year: "2026", ...myPayroll },
  ];

  return (
    <>
      <div className="portal-page admin-dashboard">

        {/* ── Header & Latest Salary ───────────────────── */}
        <div className="flat-card bg-card p-6">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-secondary border border-border flex items-center justify-center flex-shrink-0">
                <Wallet className="w-6 h-6 text-foreground" />
              </div>
              <div>
                <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">Latest Net Pay</p>
                <p className="text-3xl font-bold text-foreground mt-0.5">
                  {myPayroll ? fmt(myPayroll.netSalary) : "—"}
                </p>
              </div>
            </div>

            <div className="md:ml-auto text-left md:text-right">
              <p className="text-sm font-semibold text-foreground">April 2026</p>
              <div className="flex items-center gap-2 mt-1.5">
                <div className="w-2 h-2 rounded-full bg-[#212529]" />
                <span className="text-xs text-muted-foreground font-medium">Credited to HDFC Bank ****1234</span>
              </div>
            </div>
          </div>
        </div>

        {/* ── Payslip List ─────────────────────────────── */}
        <div className="flat-card bg-card overflow-hidden">
          <div className="px-6 py-4 border-b border-border">
            <h2 className="text-sm font-semibold text-foreground">Payslip History</h2>
            <p className="text-xs text-muted-foreground mt-0.5">Download and view your monthly salary slips</p>
          </div>

          <div className="divide-y divide-border">
            {payslips.map((slip) => (
              <div
                key={slip.id}
                className="px-6 py-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4
                  hover:bg-secondary transition-colors duration-150"
              >
                <div className="flex items-center gap-4">
                  {/* Month badge */}
                  <div className="w-14 h-14 rounded-xl bg-secondary border border-border flex flex-col items-center justify-center flex-shrink-0">
                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                      {slip.month.slice(0, 3)}
                    </span>
                    <span className="text-xs font-bold text-foreground">{slip.year.slice(2)}</span>
                  </div>
                  <div>
                    <p className="text-base font-bold text-foreground">{slip.month} {slip.year}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Gross: <span className="text-foreground font-medium">{fmt(slip.grossSalary || 0)}</span>
                      {" · "}Deductions: <span className="text-[#6C757D] font-medium">– {fmt((slip.pf || 0) + (slip.tds || 0))}</span>
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-6 sm:ml-auto">
                  <div className="text-left sm:text-right">
                    <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-0.5">Net Salary</p>
                    <p className="text-lg font-bold text-foreground">{fmt(slip.netSalary || 0)}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setSelectedSlip(slip)}
                      className="p-2 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-border transition-colors"
                      title="View payslip"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      className="p-2 rounded-lg border border-border text-muted-foreground hover:text-foreground hover:bg-border transition-colors"
                      title="Download PDF"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {selectedSlip && <PayslipModal slip={selectedSlip} onClose={() => setSelectedSlip(null)} />}
    </>
  );
}
