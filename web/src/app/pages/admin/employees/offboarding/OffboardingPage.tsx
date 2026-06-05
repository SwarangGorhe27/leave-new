import { useState, useMemo } from "react";
import { 
  Search, 
  Plus, 
  Download, 
  Filter, 
  ChevronRight,
  MoreVertical,
  UserX,
  Clock,
  ClipboardCheck,
  CheckCircle2,
  Wallet,
  Monitor,
  Eye,
  Edit,
  Check,
  FileText,
  Trash2
} from "lucide-react";
import { employees, Employee } from "../../../../components/employees/mockData";
import { AddOffboardingForm } from "./AddOffboardingForm";
import { OffboardingDetailsPage } from "./OffboardingDetailsPage";
import { useOffboardingRecords } from "./useOffboardingDetails";
import { OffboardingRecord } from "./types";

type OffboardingStatus = "Active" | "Pending" | "Approved" | "In Notice Period" | "Clearance Pending" | "Completed" | "Archived";

// Removed static initialOffboardingData - now using dynamic data from localStorage via hook

function SummaryCard({ title, count, icon: Icon, trend }: { title: string, count: number, icon: any, trend?: string }) {
  return (
    <div className="bg-card border border-border p-5 rounded-2xl flex flex-col gap-3 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center">
          <Icon className="w-5 h-5 text-foreground" />
        </div>
        {trend && (
          <span className="text-[10px] font-bold text-primary-foreground bg-foreground px-2 py-0.5 rounded-full uppercase tracking-wider">
            {trend}
          </span>
        )}
      </div>
      <div>
        <p className="text-sm font-bold text-muted-foreground">{title}</p>
        <h3 className="text-2xl font-black mt-1 tracking-tight">{count}</h3>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: OffboardingStatus }) {
  const styles: Record<OffboardingStatus, string> = {
    "Active": "bg-blue-500/10 text-blue-500 border-blue-500/20",
    "Pending": "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
    "Approved": "bg-green-500/10 text-green-500 border-green-500/20",
    "In Notice Period": "bg-purple-500/10 text-purple-500 border-purple-500/20",
    "Clearance Pending": "bg-orange-500/10 text-orange-500 border-orange-500/20",
    "Completed": "bg-slate-500/10 text-slate-500 border-slate-500/20",
    "Archived": "bg-zinc-500/10 text-zinc-500 border-zinc-500/20",
  };

  return (
    <span className={`text-[10px] px-2.5 py-1 rounded-md uppercase tracking-wider font-bold border ${styles[status]}`}>
      {status}
    </span>
  );
}

export function OffboardingPage() {
  const [activeTab, setActiveTab] = useState("Active Offboarding");
  const [search, setSearch] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<OffboardingRecord | null>(null);
  const [selectedDepartment, setSelectedDepartment] = useState("All Departments");

  // Use the hook to manage offboarding records
  const { records: offboardingData, addRecord, deleteRecord } = useOffboardingRecords();

  const departments = ["All Departments", ...Array.from(new Set(offboardingData.map(item => item.department)))];

  const stats = useMemo(() => {
    return {
      active: offboardingData.filter(i => ["Pending", "Approved", "Active", "In Notice Period"].includes(i.exitStatus)).length,
      notice: offboardingData.filter(i => i.exitStatus === "In Notice Period").length,
      clearance: offboardingData.filter(i => i.clearanceStatus === "Pending" || i.clearanceStatus === "Partially Completed").length,
      completed: offboardingData.filter(i => i.exitStatus === "Completed").length,
      ff: offboardingData.filter(i => i.clearanceStatus !== "Completed").length,
      assets: offboardingData.filter(i => i.clearanceStatus === "Pending").length,
    };
  }, [offboardingData]);

  const filteredData = useMemo(() => {
    return offboardingData.filter((item) => {
      // Tab Filtering
      const matchesTab = (() => {
        switch (activeTab) {
          case "Active Offboarding":
            return ["Pending", "Approved", "Active", "In Notice Period"].includes(item.exitStatus);
          case "Notice Period":
            return item.exitStatus === "In Notice Period";
          case "Pending Clearance":
            return item.exitStatus === "Clearance Pending";
          case "Completed Exits":
            return item.exitStatus === "Completed";
          case "Archived Employees":
            return item.exitStatus === "Archived";
          default:
            return true;
        }
      })();

      // Search Filtering
      const s = search.toLowerCase();
      const matchesSearch = 
        item.name.toLowerCase().includes(s) || 
        item.employeeId.toLowerCase().includes(s) || 
        item.department.toLowerCase().includes(s) ||
        item.id.toLowerCase().includes(s);

      // Department Filtering
      const matchesDept = selectedDepartment === "All Departments" || item.department === selectedDepartment;

      return matchesTab && matchesSearch && matchesDept;
    });
  }, [activeTab, search, offboardingData, selectedDepartment]);

  const handleExport = () => {
    const headers = ["Employee ID", "Name", "Department", "Designation", "Resignation Date", "LWD", "Status"];
    const csvData = filteredData.map(item => [
      item.employeeId,
      item.name,
      item.department,
      item.designation,
      item.resignationDate,
      item.lastWorkingDay,
      item.exitStatus
    ]);

    const csvContent = [headers, ...csvData].map(e => e.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `offboarding_report_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleAddOffboarding = (data: any) => {
    // Convert OffboardingData to OffboardingRecord for list
    const newRecord: OffboardingRecord = {
      id: data.offboardingId,
      employeeId: data.employeeId,
      name: data.name,
      initials: data.initials,
      avatarColor: data.avatarColor,
      department: data.department,
      designation: data.designation,
      reportingManager: data.reportingManager,
      resignationDate: data.resignationDate,
      lastWorkingDay: data.lastWorkingDay,
      noticeStatus: data.noticeDetails ? calculateNoticeStatus(data.noticeDetails.noticeEndDate) : "In Notice",
      exitStatus: deriveExitStatus(data),
      clearanceStatus: data.clearanceChecklist.clearanceProgress === 100 ? "Completed" : 
                       data.clearanceChecklist.clearanceProgress > 0 ? "Partially Completed" : "Pending",
    };
    addRecord(newRecord);
    setShowAddForm(false);
  };

  const calculateNoticeStatus = (endDate: string): "In Notice" | "Completed" | "Waived" => {
    try {
      const end = new Date(endDate);
      const today = new Date();
      return today > end ? "Completed" : "In Notice";
    } catch {
      return "In Notice";
    }
  };

  // Derive high-level exit status used for list filtering/cards
  const deriveExitStatus = (data: any): OffboardingStatus => {
    // If explicit status set on data (from form), normalize to known values
    const explicit = (data.status || "").toString();
    if (explicit === "Completed") return "Completed";
    if (explicit === "Approved") return "Approved";

    // If notice details exist, consider notice period state
    if (data.noticeDetails && data.noticeDetails.noticeEndDate) {
      const end = new Date(data.noticeDetails.noticeEndDate);
      if (new Date() > end) return "Completed";
      return "In Notice Period";
    }

    // If any clearance progress exists, mark accordingly
    if (data.clearanceChecklist && data.clearanceChecklist.clearanceProgress > 0) return "Clearance Pending";

    // Default to Pending
    return "Pending";
  };

  const tabs = [
    "Active Offboarding",
    "Notice Period",
    "Pending Clearance",
    "Completed Exits",
    "Archived Employees"
  ];

  return (
    <div className="flex flex-col h-full bg-background overflow-y-auto">
      {/* Header Section */}
      <div className="px-6 py-6 space-y-6">
        <div className="flex flex-col gap-1">
          {/* <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground uppercase tracking-widest">
            <span>Employees</span>
            <ChevronRight className="w-3 h-3" />
            <span className="text-foreground">Employee Offboarding</span>
          </div> */}
          <div className="flex items-center justify-between">
            {/* <h1 className="text-3xl font-black tracking-tight mt-1">Employee Offboarding</h1> */}
            <div className="flex items-center gap-3">
              <button 
                onClick={() => setShowAddForm(true)}
                className="flex items-center gap-2 px-4 py-2.5 text-sm font-bold text-white bg-primary rounded-xl shadow-lg shadow-primary/20 hover:scale-[1.02] transition-all active:scale-[0.98]"
              >
                <Plus className="w-4 h-4" />
                Add Offboarding
              </button>
              <button 
                onClick={handleExport}
                className="flex items-center gap-2 px-4 py-2.5 text-sm font-bold text-foreground bg-card border border-border rounded-xl hover:bg-secondary transition-all"
              >
                <Download className="w-4 h-4" />
                Export Data
              </button>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <SummaryCard title="Active Resignations" count={stats.active} icon={UserX} trend="+2 new" />
          <SummaryCard title="In Notice Period" count={stats.notice} icon={Clock} trend="Critical" />
          <SummaryCard title="Pending Clearances" count={stats.clearance} icon={ClipboardCheck} />
          <SummaryCard title="Completed Offboarding" count={stats.completed} icon={CheckCircle2} />
          <SummaryCard title="Full & Final Pending" count={stats.ff} icon={Wallet} />
          <SummaryCard title="Assets Pending Return" count={stats.assets} icon={Monitor} trend="Due Soon" />
        </div>

        {/* Tabs and Controls */}
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-px">
            <div className="flex items-center gap-8">
              {tabs.map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`relative py-4 text-sm font-bold transition-all ${
                    activeTab === tab 
                      ? "text-primary" 
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {tab}
                  {activeTab === tab && (
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
                  )}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <div className="relative flex-1 max-w-lg">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search by Employee Name, ID, Department..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="flat-input dark:bg-slate-900 dark:text-white dark:border-slate-700 dark:placeholder:text-slate-400 w-full pl-12 pr-4 py-2.5 text-sm font-bold"
              />
            </div>
            <div className="flex items-center gap-2">
              <select 
                value={selectedDepartment}
                onChange={(e) => setSelectedDepartment(e.target.value)}
                className="flat-input px-4 py-2.5 text-sm font-bold bg-card border border-border rounded-xl hover:bg-secondary transition-all cursor-pointer outline-none"
              >
                {departments.map(dept => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
              
            </div>
          </div>
        </div>

        {/* Table Section */}
        <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-secondary/50 border-b border-border">
                  {[
                    "Employee ID",
                    "Employee Name",
                    "Department & Designation",
                    "Manager",
                    "Resignation / LWD",
                    "Notice Status",
                    "Clearance",
                    "Status",
                    "Actions"
                  ].map((h) => (
                    <th key={h} className="px-6 py-4 text-[10px] font-black text-muted-foreground uppercase tracking-widest">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredData.map((record) => (
                  <tr key={record.id} className="hover:bg-secondary/30 transition-colors group">
                    <td className="px-6 py-4">
                      <span className="text-sm font-black tracking-tight">{record.employeeId}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div 
                          className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-black text-sm border border-white/10"
                          style={{ backgroundColor: record.avatarColor }}
                        >
                          {record.initials}
                        </div>
                        <div>
                          <p className="text-sm font-black tracking-tight">{record.name}</p>
                          <p className="text-[10px] font-bold text-muted-foreground uppercase">{record.id}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm font-bold">{record.department}</p>
                      <p className="text-[11px] font-medium text-muted-foreground">{record.designation}</p>
                    </td>
                    <td className="px-6 py-4 text-sm font-medium">
                      {record.reportingManager}
                    </td>
                    <td className="px-6 py-4" onClick={() => setSelectedRecord(record)}>
                      <div className="space-y-1">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-muted-foreground">
                          <span className="w-1 h-1 rounded-full bg-blue-500" />
                          Reg: {record.resignationDate}
                        </div>
                        <div className="flex items-center gap-1.5 text-xs font-bold text-foreground">
                          <span className="w-1 h-1 rounded-full bg-red-500" />
                          LWD: {record.lastWorkingDay}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-xs font-bold text-muted-foreground italic">
                        {record.noticeStatus}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-1.5 min-w-[120px]">
                        <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider">
                          <span className="text-muted-foreground">Progress</span>
                          <span className={record.clearanceStatus === "Completed" ? "text-green-500" : "text-primary"}>
                            {record.clearanceStatus === "Completed" ? "100%" : "40%"}
                          </span>
                        </div>
                        <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${record.clearanceStatus === "Completed" ? "bg-green-500" : "bg-primary"}`}
                            style={{ width: record.clearanceStatus === "Completed" ? "100%" : "40%" }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={record.exitStatus} />
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => setSelectedRecord(record)}
                          className="p-2 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground" 
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => {
                            const element = document.createElement("a");
                            const contentText = `HRMS OFFBOARDING RECORD\n\nEmployee: \${record.name}\nDesignation: \${record.designation}\nDepartment: \${record.department}\nResignation Date: \${record.resignationDate}\nLast Working Day: \${record.lastWorkingDay}\nNotice Status: \${record.noticeStatus}\nExit Status: \${record.exitStatus}`;
                            const file = new Blob([contentText], { type: 'text/plain' });
                            element.href = URL.createObjectURL(file);
                            element.download = `\${record.name.replace(/\\s+/g, "_")}_offboarding.txt`;
                            document.body.appendChild(element);
                            element.click();
                            document.body.removeChild(element);
                          }}
                          className="p-2 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground" 
                          title="Download Documents"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => {
                            if(window.confirm(`Approve offboarding for \${record.name}?`)) {
                              setOffboardingData(prev => prev.map(item => 
                                item.id === record.id ? { ...item, exitStatus: "Approved" } : item
                              ));
                            }
                          }}
                          className="p-2 hover:bg-secondary rounded-lg transition-colors text-muted-foreground hover:text-foreground" 
                          title="Approve"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                        <button 
                          onClick={() => {
                            if (window.confirm(`Are you sure you want to delete the offboarding record for ${record.name}?`)) {
                              deleteRecord(record.id);
                            }
                          }}
                          className="p-2 hover:bg-rose-50 rounded-lg transition-colors text-rose-500 hover:text-rose-600" 
                          title="Delete Record"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filteredData.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="w-20 h-20 bg-secondary rounded-full flex items-center justify-center mb-4">
                <UserX className="w-10 h-10 text-muted-foreground opacity-20" />
              </div>
              <h3 className="text-lg font-black tracking-tight">No Offboarding Records Found</h3>
              <p className="text-sm text-muted-foreground font-medium mt-1 mb-6">Start by adding a new offboarding process.</p>
              <button 
                onClick={() => setShowAddForm(true)}
                className="flex items-center gap-2 px-6 py-3 text-sm font-bold text-white bg-primary rounded-xl shadow-lg shadow-primary/20 hover:scale-[1.02] transition-all active:scale-[0.98]"
              >
                <Plus className="w-4 h-4" />
                Add Offboarding
              </button>
            </div>
          )}
        </div>
      </div>

      {showAddForm && (
        <AddOffboardingForm 
          onClose={() => setShowAddForm(false)}
          onSave={handleAddOffboarding}
        />
      )}

      {selectedRecord && (
        <OffboardingDetailsPage 
          record={selectedRecord}
          onClose={() => setSelectedRecord(null)}
        />
      )}
    </div>
  );
}
