import { useState } from "react";
import {
  Plus, Filter, ChevronDown,
  Trash2, RotateCcw,
} from "lucide-react";
 
// ─── Types ────────────────────────────────────────────────────────────────────
 
type GranterView = "grant" | "view";
type Periodicity = "monthly" | "quarterly" | "halfyearly" | "yearly";
type GrantType = "all" | "new";
 
interface GrantRecord {
  id: string;
  employeeNo: string;
  employeeName: string;
  leaveType: string;
  period: string;
  frequency: string;
  scheme: string;
  status: "Confirmed" | "Pending";
  joiningDate: string;
  days: number;
}
 
// ─── Mock Data ────────────────────────────────────────────────────────────────
 
const MOCK_GRANTS: GrantRecord[] = [
  { id: "g1", employeeNo: "T0031", employeeName: "Rajeev Dixit",     leaveType: "Privilege Leave", period: "Dec 2025", frequency: "Monthly", scheme: "General Scheme",   status: "Confirmed", joiningDate: "18 Apr 2016", days: 1 },
  { id: "g2", employeeNo: "T0046", employeeName: "Dinesh Babu",      leaveType: "Privilege Leave", period: "Dec 2025", frequency: "Monthly", scheme: "General Scheme",   status: "Confirmed", joiningDate: "10 Feb 2025", days: 1 },
  { id: "g3", employeeNo: "T0033", employeeName: "Manoj Biradari",   leaveType: "Annual Leave",    period: "Dec 2025", frequency: "Monthly", scheme: "General Scheme",   status: "Confirmed", joiningDate: "01 Aug 2025", days: 1 },
  { id: "g4", employeeNo: "T0022", employeeName: "P Hari Hara Rao",  leaveType: "Annual Leave",    period: "Dec 2025", frequency: "Monthly", scheme: "General Scheme",   status: "Confirmed", joiningDate: "13 Aug 2024", days: 1 },
  { id: "g5", employeeNo: "T0041", employeeName: "Daisy George",     leaveType: "Sick Leave",      period: "Dec 2025", frequency: "Monthly", scheme: "General Scheme",   status: "Confirmed", joiningDate: "09 Jun 2024", days: 1 },
];
 
const ALL_LEAVE_TYPES = [
  "Annual Leave", "Casual Leave", "Compensatory Off", "Earned Leave",
  "Loss of Pay", "Maternity Leave", "On Duty", "PWC", "Paternity Leave",
  "Plant Shut Down", "Privilege Leave", "Restricted Holiday", "Sick Leave", "Work From Home",
];
 
const LEAVE_SCHEMES = ["General Scheme", "Probation Scheme", "Trainee Scheme"];
 
const MOCK_EMPLOYEES = [
  { no: "T0031", name: "Rajeev Dixit",    status: "Confirmed" as const, joiningDate: "18 Apr 2016" },
  { no: "T0046", name: "Dinesh Babu",     status: "Confirmed" as const, joiningDate: "10 Feb 2025" },
  { no: "T0033", name: "Manoj Biradari",  status: "Confirmed" as const, joiningDate: "01 Aug 2025" },
  { no: "T0022", name: "P Hari Hara Rao", status: "Confirmed" as const, joiningDate: "13 Aug 2024" },
  { no: "T0041", name: "Daisy George",    status: "Confirmed" as const, joiningDate: "09 Jun 2024" },
];
 
// ─── Component ────────────────────────────────────────────────────────────────
 
export function AdminLeaveAllocations() {
  const [granterView, setGranterView] = useState<GranterView>("grant");
  const [grantType, setGrantType] = useState<GrantType>("all");
  const [periodicity, setPeriodicity] = useState<Periodicity | "">("");
  const [period, setPeriod] = useState("");
  const [scheme, setScheme] = useState("");
  const [selectedLeaveTypes, setSelectedLeaveTypes] = useState<string[]>([]);
  const [showLeaveTypeDropdown, setShowLeaveTypeDropdown] = useState(false);
  const [showHelp, setShowHelp] = useState(true);
 
  // View grants filters
  const [filterGrantType, setFilterGrantType] = useState("all");
  const [filterLeaveType, setFilterLeaveType] = useState("all");
  const [filterEmployee, setFilterEmployee] = useState("all");
 
  // Grants list (mutable for delete)
  const [grants, setGrants] = useState<GrantRecord[]>(MOCK_GRANTS);
 
  const allSelected = selectedLeaveTypes.length === ALL_LEAVE_TYPES.length;
  const someSelected = selectedLeaveTypes.length > 0 && !allSelected;
 
  const toggleLeaveType = (lt: string) => {
    setSelectedLeaveTypes((prev) =>
      prev.includes(lt) ? prev.filter((x) => x !== lt) : [...prev, lt]
    );
  };
 
  const toggleAll = () => {
    setSelectedLeaveTypes(allSelected ? [] : [...ALL_LEAVE_TYPES]);
  };
 
  const handleGrant = () => {
    if (!scheme || selectedLeaveTypes.length === 0) return;
    setGranterView("view");
  };
 
  const handleReset = () => {
    setPeriodicity("");
    setPeriod("");
    setScheme("");
    setSelectedLeaveTypes([]);
  };
 
  const handleDeleteGrant = (id: string) => {
    setGrants((prev) => prev.filter((g) => g.id !== id));
  };
 
  const filteredGrants = grants.filter((g) => {
    if (filterLeaveType !== "all" && g.leaveType !== filterLeaveType) return false;
    if (filterEmployee !== "all" && g.employeeNo !== filterEmployee) return false;
    return true;
  });
 
  const showPreviewTable = scheme && selectedLeaveTypes.length > 0;
 
  return (
    <div className="space-y-4">
      {/* Help Banner */}
      {showHelp && (
        <div className="flat-card bg-card px-5 py-3 text-xs text-muted-foreground leading-relaxed relative">
          {granterView === "grant" ? (
            <>
              The <span className="font-semibold text-foreground">Leave Granter</span> page enables you to grant manually (credit) leaves to employees. You can grant leaves to all employees (typically done at the beginning of the Leave year) or newly joined employees (done periodically). Select the <span className="font-semibold text-foreground">Scheme</span> and the <span className="font-semibold text-foreground">Leave Types</span> within the Scheme and click <span className="font-semibold text-foreground">Grant</span> to complete the process.
            </>
          ) : (
            <>
              This page displays a summary of all leaves credited (granted) to employees for the current leave year. Click the icons adjacent to each row to manage data. Leave is usually granted automatically as per schedule. You can also grant leave manually by clicking the <span className="font-semibold text-foreground">Grant Leave</span> button.
            </>
          )}
          <button
            onClick={() => setShowHelp(false)}
            className="absolute right-4 top-3 text-[10px] text-blue-600 dark:text-blue-400 hover:underline"
          >
            Hide Help
          </button>
        </div>
      )}
 
      {/* Sub-tab bar + period badge */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-1 p-1 bg-muted/50 rounded-lg">
          {(["grant", "view"] as GranterView[]).map((v) => (
            <button
              key={v}
              onClick={() => setGranterView(v)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                granterView === v
                  ? "bg-foreground text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {v === "grant" ? "Grant Leave" : "View Grants"}
            </button>
          ))}
        </div>
        <span className="text-xs px-3 py-1.5 rounded-lg border border-border text-muted-foreground bg-card">
          Jan 2025 – Dec 2025
        </span>
      </div>
 
      {/* ── GRANT FORM ── */}
      {granterView === "grant" && (
        <div className="space-y-5">
          <div className="flat-card bg-card overflow-visible">
            <div className="px-6 py-4 border-b border-border">
              <h3 className="text-sm font-semibold text-foreground">Grant Configuration</h3>
            </div>
 
            <div className="px-6 py-5 space-y-5">
              {/* Grant type radio */}
              <div className="flex items-center gap-6">
                {([["all", "Grant for all employees"], ["new", "Grant for newly joined employees"]] as [GrantType, string][]).map(([val, label]) => (
                  <label key={val} className="flex items-center gap-2 cursor-pointer text-xs text-foreground">
                    <input
                      type="radio"
                      name="grantType"
                      value={val}
                      checked={grantType === val}
                      onChange={() => setGrantType(val)}
                      className="accent-foreground"
                    />
                    {label}
                  </label>
                ))}
              </div>
 
              {/* Form fields grid */}
              <div className="grid grid-cols-[140px_1fr] gap-x-6 gap-y-4 max-w-xl items-start">
                {/* Periodicity */}
                <label className="text-xs text-muted-foreground pt-2">
                  Periodicity <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <select
                    value={periodicity}
                    onChange={(e) => setPeriodicity(e.target.value as Periodicity | "")}
                    className="w-full pl-3 pr-8 py-1.5 rounded-lg border border-border bg-background text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring appearance-none cursor-pointer"
                  >
                    <option value="">— Select —</option>
                    <option value="monthly">Monthly</option>
                    <option value="quarterly">Quarterly</option>
                    <option value="halfyearly">Half Yearly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                  <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-muted-foreground pointer-events-none" />
                </div>
 
                {/* Period */}
                <label className="text-xs text-muted-foreground pt-2">
                  Period <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <select
                    value={period}
                    onChange={(e) => setPeriod(e.target.value)}
                    className="w-full pl-3 pr-8 py-1.5 rounded-lg border border-border bg-background text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring appearance-none cursor-pointer"
                  >
                    <option value="">— Select —</option>
                    <option value="dec2025">Dec 2025</option>
                    <option value="nov2025">Nov 2025</option>
                    <option value="oct2025">Oct 2025</option>
                    <option value="sep2025">Sep 2025</option>
                  </select>
                  <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-muted-foreground pointer-events-none" />
                </div>
 
                {/* Scheme */}
                <label className="text-xs text-muted-foreground pt-2">
                  Leave Scheme <span className="text-rose-500">*</span>
                </label>
                <div className="relative">
                  <select
                    value={scheme}
                    onChange={(e) => setScheme(e.target.value)}
                    className="w-full pl-3 pr-8 py-1.5 rounded-lg border border-border bg-background text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring appearance-none cursor-pointer"
                  >
                    <option value="">— Select Scheme —</option>
                    {LEAVE_SCHEMES.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-muted-foreground pointer-events-none" />
                </div>
 
                {/* Leave Types Dropdown */}
<label className="text-xs text-muted-foreground pt-2">
  Leave Types
</label>
 
<div className="relative">
  <button
    type="button"
    onClick={() => setShowLeaveTypeDropdown(!showLeaveTypeDropdown)}
    className="w-full flex items-center justify-between px-3 py-2 rounded-lg border border-border bg-background text-xs text-left"
  >
    <span>
      {selectedLeaveTypes.length === 0
        ? "Select Leave Types"
        : allSelected
        ? "All Leave Types Selected"
        : selectedLeaveTypes.length === 1
        ? selectedLeaveTypes[0]
        : `${selectedLeaveTypes.length} Leave Types Selected`}
    </span>
 
    <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
  </button>
 
  {showLeaveTypeDropdown && (
    <div className="absolute z-50 mt-1 w-full rounded-lg border border-border bg-card shadow-lg overflow-hidden">
      {/* Select All */}
      <label className="flex items-center gap-2 px-3 py-2 bg-muted/40 border-b border-border cursor-pointer">
        <input
          type="checkbox"
          checked={allSelected}
          ref={(el) => {
            if (el) el.indeterminate = someSelected;
          }}
          onChange={toggleAll}
        />
        <span className="text-xs font-medium">
          Select All
        </span>
      </label>
 
      {/* Leave Types */}
      <div className="max-h-60 overflow-y-auto">
        {ALL_LEAVE_TYPES.map((lt) => (
          <label
            key={lt}
            className="flex items-center gap-2 px-3 py-2 hover:bg-muted/30 cursor-pointer"
          >
            <input
              type="checkbox"
              checked={selectedLeaveTypes.includes(lt)}
              onChange={() => toggleLeaveType(lt)}
            />
 
            <span className="text-xs">
              {lt}
            </span>
          </label>
        ))}
      </div>
    </div>
  )}
</div>
              </div>
            </div>
          </div>
 
          {/* Preview Table */}
          {showPreviewTable && (
            <div className="flat-card bg-card overflow-hidden">
              <div className="px-5 py-3 border-b border-border bg-muted/40 flex flex-wrap gap-4 text-xs text-muted-foreground">
                <span>Period: <span className="font-semibold text-foreground">Dec 2025</span></span>
                <span>Frequency: <span className="font-semibold text-foreground capitalize">{periodicity || "—"}</span></span>
                <span>Leave Type: <span className="font-semibold text-foreground">
                  {selectedLeaveTypes.length === 1 ? selectedLeaveTypes[0] : `${selectedLeaveTypes.length} types`}
                </span></span>
                <span>Scheme: <span className="font-semibold text-foreground">{scheme}</span></span>
                <span>Headcount: <span className="font-semibold text-foreground">{MOCK_EMPLOYEES.length}</span></span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-border bg-muted/20">
                      {["#", "Employee No", "Employee Name", "Status", "Joining Date", "Days", ""].map((h) => (
                        <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground whitespace-nowrap">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {MOCK_EMPLOYEES.map((emp, i) => (
                      <tr key={emp.no} className="hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3 text-muted-foreground">{i + 1}</td>
                        <td className="px-4 py-3 text-muted-foreground">{emp.no}</td>
                        <td className="px-4 py-3 font-medium text-foreground">{emp.name}</td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                            {emp.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-muted-foreground">{emp.joiningDate}</td>
                        <td className="px-4 py-3 text-center font-semibold text-foreground">1</td>
                        <td className="px-4 py-3">
                          <button className="p-1 rounded hover:bg-muted transition-colors text-muted-foreground hover:text-rose-500">
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
 
          {/* Action buttons */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleGrant}
              disabled={!scheme || selectedLeaveTypes.length === 0}
              className="px-5 py-2 rounded-lg text-xs font-semibold bg-foreground text-primary-foreground hover:bg-accent transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Grant
            </button>
            <button
              onClick={handleReset}
              className="px-5 py-2 rounded-lg text-xs font-medium border border-border text-muted-foreground hover:bg-muted transition-colors inline-flex items-center gap-1.5"
            >
              <RotateCcw className="w-3 h-3" />
              Reset
            </button>
          </div>
        </div>
      )}
 
      {/* ── VIEW GRANTS ── */}
      {granterView === "view" && (
        <div className="flat-card bg-card overflow-hidden">
          {/* Toolbar */}
          <div className="px-5 py-3 border-b border-border flex flex-wrap items-center gap-2">
            {/* Grant type filter */}
            <div className="relative">
              <Filter className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
              <select
                value={filterGrantType}
                onChange={(e) => setFilterGrantType(e.target.value)}
                className="pl-8 pr-7 py-1.5 rounded-lg border border-border bg-background text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring appearance-none cursor-pointer"
              >
                <option value="all">Grant Type: All</option>
                <option value="leave">Leave Grant</option>
                <option value="rollback">Rollback Grant</option>
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-muted-foreground pointer-events-none" />
            </div>
            {/* Leave type filter */}
            <div className="relative">
              <select
                value={filterLeaveType}
                onChange={(e) => setFilterLeaveType(e.target.value)}
                className="pl-3 pr-7 py-1.5 rounded-lg border border-border bg-background text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring appearance-none cursor-pointer"
              >
                <option value="all">Leave Type: All</option>
                {ALL_LEAVE_TYPES.map((lt) => (
                  <option key={lt} value={lt}>{lt}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-muted-foreground pointer-events-none" />
            </div>
            {/* Employee filter */}
            <div className="relative">
              <select
                value={filterEmployee}
                onChange={(e) => setFilterEmployee(e.target.value)}
                className="pl-3 pr-7 py-1.5 rounded-lg border border-border bg-background text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-ring appearance-none cursor-pointer"
              >
                <option value="all">Employee: All</option>
                {MOCK_EMPLOYEES.map((e) => (
                  <option key={e.no} value={e.no}>{e.name}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-muted-foreground pointer-events-none" />
            </div>
            <button
              onClick={() => setGranterView("grant")}
              className="ml-auto px-3 py-1.5 rounded-lg text-xs font-semibold bg-foreground text-primary-foreground hover:bg-accent transition-colors inline-flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              Grant Leave
            </button>
          </div>
 
          {/* Grants Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border bg-muted/40">
                  {["#", "Employee No", "Employee Name", "Leave Type · Scheme", "Period · Freq.", "Status", "Joining Date", "Days", ""].map((h) => (
                    <th key={h} className="px-4 py-3 text-left font-semibold text-muted-foreground whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredGrants.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="px-4 py-10 text-center text-muted-foreground">No grant records found.</td>
                  </tr>
                ) : (
                  filteredGrants.map((g, i) => (
                    <tr key={g.id} className="hover:bg-muted/30 transition-colors">
                      <td className="px-4 py-3 text-muted-foreground">{i + 1}</td>
                      <td className="px-4 py-3 text-muted-foreground">{g.employeeNo}</td>
                      <td className="px-4 py-3 font-medium text-foreground">{g.employeeName}</td>
                      <td className="px-4 py-3">
                        <p className="font-medium text-foreground">{g.leaveType}</p>
                        <p className="text-[10px] text-muted-foreground">{g.scheme}</p>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <p className="text-foreground">{g.period}</p>
                        <p className="text-[10px] text-muted-foreground">{g.frequency}</p>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          g.status === "Confirmed"
                            ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
                            : "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300"
                        }`}>
                          {g.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground whitespace-nowrap">{g.joiningDate}</td>
                      <td className="px-4 py-3 text-center font-semibold text-foreground">{g.days}</td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => handleDeleteGrant(g.id)}
                          className="p-1 rounded hover:bg-muted transition-colors text-muted-foreground hover:text-rose-500"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
 
          <div className="px-5 py-3 border-t border-border flex items-center justify-between text-xs text-muted-foreground">
            <span>Showing {filteredGrants.length} of {grants.length} grants</span>
            <div className="flex items-center gap-1">
              <button className="px-2 py-1 rounded hover:bg-muted transition-colors disabled:opacity-40" disabled>← Prev</button>
              <span className="px-2 py-1 rounded bg-foreground text-primary-foreground font-semibold">1</span>
              <button className="px-2 py-1 rounded hover:bg-muted transition-colors disabled:opacity-40" disabled>Next →</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
 