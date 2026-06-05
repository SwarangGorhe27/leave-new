import { useMemo, useState } from "react";
import { Download, Eye, FileDown, FileSpreadsheet, List, RefreshCw, Search, Users } from "lucide-react";
import { MyAttendanceModule } from "../../components/attendance/my-attendance/MyAttendanceModule";
import { DailyAttendance } from "../../modules/attendance/types";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import { cn } from "../../components/ui/utils";
import { Modal } from "../../../components/ui/Modal";
import {
  useManagerTeamAttendance,
  useTeamMemberAttendanceHistory,
} from "../../hooks/useManagerTeamAttendance";
import { teamStatusLabel } from "../../modules/manager-attendance/mappers";

type TeamView = "card" | "list";

function formatHours(hours?: number) {
  return typeof hours === "number" && hours > 0 ? `${hours.toFixed(1)}h` : "-";
}

function downloadBlob(content: BlobPart, fileName: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

function statusClass(status?: string) {
  switch (status) {
    case "Present":
      return "bg-emerald-100 text-emerald-700 border border-emerald-200 dark:bg-emerald-500/20 dark:text-emerald-400 dark:border-emerald-500/30";
    case "Absent":
      return "bg-rose-100 text-rose-700 border border-rose-200 dark:bg-rose-500/20 dark:text-rose-400 dark:border-rose-500/30";
    case "Leave":
      return "bg-blue-100 text-blue-700 border border-blue-200 dark:bg-blue-500/20 dark:text-blue-400 dark:border-blue-500/30";
    case "Half Day":
    case "Late":
      return "bg-amber-100 text-amber-700 border border-amber-200 dark:bg-amber-500/20 dark:text-amber-400 dark:border-amber-500/30";
    case "Holiday":
      return "bg-purple-100 text-purple-700 border border-purple-200 dark:bg-purple-500/20 dark:text-purple-400 dark:border-purple-500/30";
    case "Week Off":
      return "bg-slate-100 text-slate-700 border border-slate-200 dark:bg-slate-500/20 dark:text-slate-400 dark:border-slate-500/30";
    default:
      return "bg-secondary text-muted-foreground border border-border";
  }
}

export function ManagerTeamAttendancePage() {
  const [query, setQuery] = useState("");
  const [department, setDepartment] = useState("ALL");
  const [status, setStatus] = useState("ALL");
  const [view, setView] = useState<TeamView>("card");
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string | null>(null);
  const [isAttendanceModalOpen, setIsAttendanceModalOpen] = useState(false);
  const [modalPeriodDate, setModalPeriodDate] = useState(() => new Date());

  const { members: teamMembers, loading: teamLoading, error: teamError, reload } = useManagerTeamAttendance();

  const selectedEmployee = teamMembers.find((employee) => employee.id === selectedEmployeeId) ?? null;

  const { records: selectedRecords, loading: historyLoading, error: historyError } =
    useTeamMemberAttendanceHistory(
      selectedEmployeeId,
      modalPeriodDate,
      {
        name: selectedEmployee?.name ?? "",
        department: selectedEmployee?.department ?? "",
        designation: selectedEmployee?.designation ?? "",
      },
    );

  const departments = useMemo(
    () => ["ALL", ...Array.from(new Set(teamMembers.map((employee) => employee.department))).sort()],
    [teamMembers],
  );

  const statuses = useMemo(
    () => [
      "ALL",
      ...Array.from(
        new Set(teamMembers.map((employee) => teamStatusLabel(employee.raw.status))),
      ).sort(),
    ],
    [teamMembers],
  );

  const filteredEmployees = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return teamMembers.filter((employee) => {
      const matchesQuery =
        !normalizedQuery ||
        employee.name.toLowerCase().includes(normalizedQuery) ||
        employee.displayId.toLowerCase().includes(normalizedQuery) ||
        employee.id.toLowerCase().includes(normalizedQuery);
      const matchesDepartment = department === "ALL" || employee.department === department;
      const employeeStatus = teamStatusLabel(employee.raw.status);
      const matchesStatus = status === "ALL" || employeeStatus === status;

      return matchesQuery && matchesDepartment && matchesStatus;
    });
  }, [teamMembers, query, department, status]);

  const exportRows = selectedRecords.map((record: DailyAttendance) => ({
    Date: record.date,
    Status: record.status,
    "Shift Timing": record.shiftName,
    "Punch In": record.firstIn || "No Punch In",
    "Punch Out": record.lastOut || "No Punch Out",
    "Working Hours": record.workHours,
    "Late By": record.lateMins,
    "Early By": record.earlyExitMins,
    "Work Mode": record.workMode,
    "Regularization Status": record.approvalPending ? "Pending" : "None",
    Remarks: record.exception ? "Exception recorded" : "",
  }));

  const exportCsv = () => {
    if (!selectedEmployee) return;
    const headers = Object.keys(exportRows[0] ?? {});
    const csv = [
      headers.join(","),
      ...exportRows.map((row) => headers.map((header) => JSON.stringify(row[header as keyof typeof row] ?? "")).join(",")),
    ].join("\n");
    downloadBlob(csv, `${selectedEmployee.displayId}-attendance.csv`, "text/csv;charset=utf-8");
  };

  const exportExcel = () => {
    if (!selectedEmployee) return;
    const worksheet = XLSX.utils.json_to_sheet(exportRows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Attendance");
    XLSX.writeFile(workbook, `${selectedEmployee.displayId}-attendance.xlsx`);
  };

  const exportPdf = () => {
    if (!selectedEmployee) return;
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text(`${selectedEmployee.name} Attendance Report`, 14, 18);
    doc.setFontSize(10);
    doc.text(`${selectedEmployee.displayId} | ${selectedEmployee.department} | ${selectedEmployee.designation}`, 14, 26);

    selectedRecords.slice(0, 28).forEach((record, index) => {
      const y = 38 + index * 8;
      doc.text(
        `${record.date}  ${record.status}  In: ${record.firstIn || "No Punch In"}  Out: ${record.lastOut || "No Punch Out"}  Hours: ${formatHours(record.workHours)}`,
        14,
        y,
      );
    });

    doc.save(`${selectedEmployee.displayId}-attendance.pdf`);
  };

  const openAttendanceModal = (employeeId: string) => {
    setSelectedEmployeeId(employeeId);
    setModalPeriodDate(new Date());
    setIsAttendanceModalOpen(true);
  };

  const todayRecord = selectedEmployee?.today;

  return (
    <div className="attendance-liquid team-attendance-page space-y-7 p-4 md:p-6">
      <div className="attendance-hero p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => void reload()}
              className="attendance-export-button inline-flex h-9 items-center gap-2 px-3 text-sm font-semibold text-white"
            >
              <RefreshCw className={cn("h-4 w-4", teamLoading && "animate-spin")} /> Refresh
            </button>
            {selectedEmployee ? (
              <>
                <button onClick={exportExcel} className="attendance-export-button inline-flex h-9 items-center gap-2 px-3 text-sm font-semibold text-white">
                  <FileSpreadsheet className="h-4 w-4" /> Excel
                </button>
                <button onClick={exportPdf} className="attendance-export-button inline-flex h-9 items-center gap-2 px-3 text-sm font-semibold text-white">
                  <FileDown className="h-4 w-4" /> PDF
                </button>
                <button onClick={exportCsv} className="attendance-export-button inline-flex h-9 items-center gap-2 px-3 text-sm font-semibold text-white">
                  <Download className="h-4 w-4" /> CSV
                </button>
              </>
            ) : null}
          </div>
        </div>

        {teamError ? (
          <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-300">
            {teamError}
          </div>
        ) : null}

        <div className="attendance-team-toolbar mt-5 grid gap-3 lg:grid-cols-[minmax(220px,1fr)_180px_160px_auto]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="        Search by employee name or ID"
              className="attendance-form-control h-10 w-full pl-9 pr-3 text-sm text-foreground outline-none"
            />
          </div>

          <select
            value={department}
            onChange={(event) => setDepartment(event.target.value)}
            className="attendance-form-control h-10 px-3 text-sm text-foreground outline-none"
          >
            {departments.map((option) => (
              <option key={option} value={option} className="bg-card text-foreground">
                {option === "ALL" ? "Department" : option}
              </option>
            ))}
          </select>

          <select
            value={status}
            onChange={(event) => setStatus(event.target.value)}
            className="attendance-form-control h-10 px-3 text-sm text-foreground outline-none"
          >
            {statuses.map((option) => (
              <option key={option} value={option} className="bg-card text-foreground">
                {option === "ALL" ? "Status" : option}
              </option>
            ))}
          </select>

          <div className="attendance-segment inline-flex p-1">
            <button
              onClick={() => setView("card")}
              className={cn("attendance-segment-button inline-flex h-8 items-center gap-2 px-3 text-sm font-semibold", view === "card" ? "is-active" : "text-muted-foreground hover:text-foreground")}
            >
              <Users className="h-4 w-4" /> Card View
            </button>
            <button
              onClick={() => setView("list")}
              className={cn("attendance-segment-button inline-flex h-8 items-center gap-2 px-3 text-sm font-semibold", view === "list" ? "is-active" : "text-muted-foreground hover:text-foreground")}
            >
              <List className="h-4 w-4" /> List View
            </button>
          </div>
        </div>
      </div>

      {teamLoading ? (
        <div className="attendance-empty flex min-h-[260px] items-center justify-center p-8 text-center text-muted-foreground">
          Loading team attendance…
        </div>
      ) : null}

      {!teamLoading && view === "card" ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filteredEmployees.map((employee) => {
            const selected = employee.id === selectedEmployeeId;
            const statusLabel = teamStatusLabel(employee.raw.status);
            return (
              <div
                key={employee.id}
                role="button"
                tabIndex={0}
                onClick={() => openAttendanceModal(employee.id)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") openAttendanceModal(employee.id);
                }}
                className={cn(
                  "attendance-team-card cursor-pointer p-5 text-left transition-all",
                  selected && "border-primary bg-primary/10 ring-2 ring-primary/30",
                )}
              >
                <div className="flex items-start gap-4">
                  <img src={employee.avatar} alt={employee.name} className="h-12 w-12 rounded-full border border-border bg-secondary object-cover" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <h2 className="truncate text-sm font-bold text-foreground">{employee.name}</h2>
                        <p className="text-xs text-muted-foreground">{employee.displayId}</p>
                      </div>
                      <span className={cn("rounded-md px-2 py-1 text-[10px] font-bold uppercase", statusClass(statusLabel))}>
                        {statusLabel}
                      </span>
                    </div>
                    <p className="mt-3 text-xs font-medium text-foreground">{employee.designation}</p>
                    <p className="text-xs text-muted-foreground">{employee.department}</p>
                  </div>
                </div>

                <div className="attendance-mini-metrics mt-4 grid grid-cols-3 gap-2 p-3">
                  <MiniMetric label="Punch In" value={employee.today?.firstIn || "No Punch In"} />
                  <MiniMetric label="Punch Out" value={employee.today?.lastOut || "No Punch Out"} />
                  <MiniMetric label="Hours" value={formatHours(employee.today?.workHours)} />
                </div>

                <div className="mt-4 flex gap-2">
                  <button type="button" onClick={(event) => { event.stopPropagation(); openAttendanceModal(employee.id); }} className="attendance-submit-button inline-flex h-8 flex-1 items-center justify-center gap-2 text-sm font-semibold text-primary-foreground">
                    <Eye className="h-4 w-4" /> View Attendance
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      ) : null}

      {!teamLoading && view === "list" ? (
        <div className="attendance-list-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr>
                  <th className="px-4 py-3">Employee</th>
                  <th className="px-4 py-3">Department</th>
                  <th className="px-4 py-3">Designation</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Punch In</th>
                  <th className="px-4 py-3">Punch Out</th>
                  <th className="px-4 py-3">Working Hours</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredEmployees.map((employee) => {
                  const statusLabel = teamStatusLabel(employee.raw.status);
                  return (
                  <tr
                    key={employee.id}
                    onClick={() => openAttendanceModal(employee.id)}
                    className={cn("attendance-list-row cursor-pointer", employee.id === selectedEmployeeId && "bg-primary/10")}
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <img src={employee.avatar} alt={employee.name} className="h-9 w-9 rounded-full border border-border bg-secondary object-cover" />
                        <div>
                          <p className="text-sm font-semibold text-foreground">{employee.name}</p>
                          <p className="text-xs text-muted-foreground">{employee.displayId}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">{employee.department}</td>
                    <td className="px-4 py-3 text-sm">{employee.designation}</td>
                    <td className="px-4 py-3">
                      <span className={cn("rounded-md px-2 py-1 text-[10px] font-bold uppercase", statusClass(statusLabel))}>
                        {statusLabel}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">{employee.today?.firstIn || "No Punch In"}</td>
                    <td className="px-4 py-3 text-sm">{employee.today?.lastOut || "No Punch Out"}</td>
                    <td className="px-4 py-3 text-sm">{formatHours(employee.today?.workHours)}</td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <button className="attendance-submit-button px-3 py-1.5 text-xs font-semibold text-primary-foreground" onClick={(event) => { event.stopPropagation(); openAttendanceModal(employee.id); }}>View Attendance</button>
                      </div>
                    </td>
                  </tr>
                );})}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      {!teamLoading && filteredEmployees.length === 0 ? (
        <div className="attendance-empty flex min-h-[200px] items-center justify-center text-muted-foreground">
          No team members match your filters.
        </div>
      ) : null}

      {!selectedEmployee ? (
        <div className="attendance-empty flex min-h-[260px] items-center justify-center p-8 text-center">
          <div>
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-secondary text-muted-foreground">
              <Users className="h-6 w-6" />
            </div>
            <h2 className="mt-4 text-lg font-semibold text-foreground">Select a team member to open attendance details.</h2>
            <p className="text-sm text-muted-foreground mt-2">Attendance details will appear in a popup so you can stay on this page.</p>
          </div>
        </div>
      ) : null}

      {selectedEmployee && (
        <Modal
          open={isAttendanceModalOpen}
          onOpenChange={setIsAttendanceModalOpen}
          title="Attendance Details"
          className="max-w-[100vw] w-full md:max-w-[90vw] xl:max-w-[85vw]"
        >
          <div className="attendance-modal-profile flex flex-col xl:flex-row gap-6 mb-8 p-6">
            <div className="flex items-center gap-5 xl:w-1/3">
              <img src={selectedEmployee.avatar} alt={selectedEmployee.name} className="h-20 w-20 rounded-full border-4 border-card shadow-sm object-cover" />
              <div>
                <h2 className="text-xl font-bold text-foreground">{selectedEmployee.name}</h2>
                <p className="text-sm font-medium text-muted-foreground mb-1">{selectedEmployee.displayId}</p>
                <div className="flex flex-col gap-0.5">
                  <span className="text-sm text-foreground">{selectedEmployee.designation}</span>
                  <span className="text-xs text-muted-foreground">{selectedEmployee.department}</span>
                </div>
                <div className="mt-2">
                  <span className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold shadow-sm", statusClass(teamStatusLabel(selectedEmployee.raw.status)))}>
                    {teamStatusLabel(selectedEmployee.raw.status)}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3 flex-1">
              <div className="attendance-mini-panel p-4 flex flex-col justify-center">
                <p className="text-[10px] font-bold uppercase text-muted-foreground mb-1">Punch In</p>
                <p className="text-sm font-semibold text-foreground">{todayRecord?.firstIn || "--:--"}</p>
              </div>
              <div className="attendance-mini-panel p-4 flex flex-col justify-center">
                <p className="text-[10px] font-bold uppercase text-muted-foreground mb-1">Punch Out</p>
                <p className="text-sm font-semibold text-foreground">{todayRecord?.lastOut || "--:--"}</p>
              </div>
              <div className="attendance-mini-panel p-4 flex flex-col justify-center">
                <p className="text-[10px] font-bold uppercase text-muted-foreground mb-1">Working Hours</p>
                <p className="text-sm font-semibold text-foreground">{formatHours(todayRecord?.workHours)}</p>
              </div>
              <div className="attendance-mini-panel p-4 flex flex-col justify-center">
                <p className="text-[10px] font-bold uppercase text-muted-foreground mb-1">Late By</p>
                <p className="text-sm font-semibold text-amber-600 dark:text-amber-400">{todayRecord?.lateMins ? `${todayRecord.lateMins}m` : "-"}</p>
              </div>
              <div className="attendance-mini-panel p-4 flex flex-col justify-center">
                <p className="text-[10px] font-bold uppercase text-muted-foreground mb-1">Early Out</p>
                <p className="text-sm font-semibold text-rose-600 dark:text-rose-400">{todayRecord?.earlyExitMins ? `${todayRecord.earlyExitMins}m` : "-"}</p>
              </div>
              <div className="attendance-mini-panel p-4 flex flex-col justify-center">
                <p className="text-[10px] font-bold uppercase text-muted-foreground mb-1">Overtime</p>
                <p className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">{todayRecord?.otMins ? `${todayRecord.otMins}m` : "-"}</p>
              </div>
            </div>
          </div>

          <div className="min-h-[60vh]">
            <MyAttendanceModule
              employeeId={selectedEmployee.id}
              readOnly
              showTitle={false}
              externalRecords={selectedRecords}
              externalLoading={historyLoading}
              externalError={historyError}
              onPeriodChange={setModalPeriodDate}
            />
          </div>
        </Modal>
      )}
    </div>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[10px] font-semibold uppercase text-muted-foreground">{label}</p>
      <p className="mt-1 truncate text-xs font-bold text-foreground">{value}</p>
    </div>
  );
}
