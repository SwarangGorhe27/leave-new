import React, { useState, useEffect } from "react";
import { 
  ShieldCheck, 
  Fingerprint, 
  CreditCard, 
  Landmark, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Search, 
  Eye, 
  Download, 
  Trash2, 
  ChevronDown, 
  FileText 
} from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/app/context/AuthContext";
import { SearchableSelect } from "@/app/components/ui/SearchableSelect";

interface VerificationItem {
  id: string;
  employeeId: string;
  name: string;
  type: string;
  submittedOn: string;
  status: "Verified" | "Pending" | "Rejected" | "Not Available";
  // Filterable metadata
  employeeType: string;
  serviceYears: number;
  isCurrent: boolean;
  vaccinated: "Fully" | "Partially" | "No";
  department: string;
  location: string;
  scheme: string;
}

const INITIAL_MOCK_DATA: VerificationItem[] = [
  {
    id: "1",
    employeeId: "EMP001",
    name: "Rahul Sharma",
    type: "Aadhaar",
    submittedOn: "2026-05-10",
    status: "Pending",
    employeeType: "Confirmed",
    serviceYears: 2,
    isCurrent: true,
    vaccinated: "Partially",
    department: "Sales",
    location: "Bangalore",
    scheme: "General scheme filter"
  },
  {
    id: "2",
    employeeId: "EMP002",
    name: "Priya Patel",
    type: "Permanent Account Number",
    submittedOn: "2026-05-09",
    status: "Verified",
    employeeType: "Confirmed",
    serviceYears: 4,
    isCurrent: true,
    vaccinated: "Fully",
    department: "Engineering",
    location: "Mumbai",
    scheme: "General scheme filter"
  },
  {
    id: "3",
    employeeId: "EMP003",
    name: "Amit Kumar",
    type: "Passport",
    submittedOn: "2026-05-08",
    status: "Rejected",
    employeeType: "Probation",
    serviceYears: 1,
    isCurrent: true,
    vaccinated: "No",
    department: "Marketing",
    location: "Delhi",
    scheme: "My Filter"
  },
  {
    id: "4",
    employeeId: "EMP004",
    name: "Sneha Reddy",
    type: "Ration Card",
    submittedOn: "2026-05-07",
    status: "Verified",
    employeeType: "Contract",
    serviceYears: 6,
    isCurrent: true,
    vaccinated: "Fully",
    department: "Sales",
    location: "Bangalore",
    scheme: "General scheme filter"
  },
  {
    id: "5",
    employeeId: "EMP005",
    name: "Vikram Singh",
    type: "Driving License",
    submittedOn: "2026-05-06",
    status: "Pending",
    employeeType: "Trainee",
    serviceYears: 0.5,
    isCurrent: true,
    vaccinated: "Partially",
    department: "Operations",
    location: "Pune",
    scheme: "General scheme filter"
  },
  {
    id: "6",
    employeeId: "EMP006",
    name: "Ananya Iyer",
    type: "Election Card",
    submittedOn: "—",
    status: "Not Available",
    employeeType: "Probation",
    serviceYears: 1.5,
    isCurrent: true,
    vaccinated: "Fully",
    department: "HR",
    location: "Chennai",
    scheme: "General scheme filter"
  },
  {
    id: "7",
    employeeId: "EMP007",
    name: "Rajesh Gupta",
    type: "Permanent Retirement Account Number",
    submittedOn: "2026-05-05",
    status: "Verified",
    employeeType: "Confirmed",
    serviceYears: 8,
    isCurrent: false,
    vaccinated: "Fully",
    department: "Finance",
    location: "Bangalore",
    scheme: "My Filter"
  },
  {
    id: "8",
    employeeId: "EMP008",
    name: "Pooja Mehta",
    type: "Labour Welfare Fund Number",
    submittedOn: "2026-05-04",
    status: "Pending",
    employeeType: "Contract",
    serviceYears: 3,
    isCurrent: true,
    vaccinated: "Partially",
    department: "Sales",
    location: "Mumbai",
    scheme: "General scheme filter"
  },
  {
    id: "9",
    employeeId: "EMP009",
    name: "Karan Johar",
    type: "IFSC Code",
    submittedOn: "2026-05-03",
    status: "Verified",
    employeeType: "Probation",
    serviceYears: 0.8,
    isCurrent: true,
    vaccinated: "Partially",
    department: "Marketing",
    location: "Bangalore",
    scheme: "My Filter"
  },
  {
    id: "10",
    employeeId: "EMP010",
    name: "Neha Sharma",
    type: "National Population Register",
    submittedOn: "2026-05-02",
    status: "Rejected",
    employeeType: "Confirmed",
    serviceYears: 5,
    isCurrent: true,
    vaccinated: "Partially",
    department: "Sales",
    location: "Kolkata",
    scheme: "General scheme filter"
  },
  {
    id: "11",
    employeeId: "EMP011",
    name: "Aditya Birla",
    type: "Marital Status",
    submittedOn: "—",
    status: "Not Available",
    employeeType: "Confirmed",
    serviceYears: 10,
    isCurrent: false,
    vaccinated: "Fully",
    department: "Legal",
    location: "Mumbai",
    scheme: "My Filter"
  },
  {
    id: "12",
    employeeId: "EMP012",
    name: "Divya Dutta",
    type: "Bank Details for Identification",
    submittedOn: "2026-05-01",
    status: "Verified",
    employeeType: "Confirmed",
    serviceYears: 3.5,
    isCurrent: true,
    vaccinated: "Partially",
    department: "IT",
    location: "Bangalore",
    scheme: "General scheme filter"
  }
];

export function IdentityVerificationPage() {
  const { user } = useAuth();
  const [data, setData] = useState<VerificationItem[]>(INITIAL_MOCK_DATA);
  const [search, setSearch] = useState("");

  // States for advanced filters with sessionStorage persistence
  const [personalIdStatusFilter, setPersonalIdStatusFilter] = useState(() => {
    return sessionStorage.getItem("hrms_id_verify_personalIdStatusFilter") || "All";
  });
  const [documentTypeFilter, setDocumentTypeFilter] = useState(() => {
    return sessionStorage.getItem("hrms_id_verify_documentTypeFilter") || "All";
  });
  const [employeeSearchFilter, setEmployeeSearchFilter] = useState(() => {
    return sessionStorage.getItem("hrms_id_verify_employeeSearchFilter") || "All";
  });
  const [employeeFilter, setEmployeeFilter] = useState(() => {
    return sessionStorage.getItem("hrms_id_verify_employeeFilter") || "All";
  });

  useEffect(() => {
    sessionStorage.setItem("hrms_id_verify_personalIdStatusFilter", personalIdStatusFilter);
  }, [personalIdStatusFilter]);
  useEffect(() => {
    sessionStorage.setItem("hrms_id_verify_documentTypeFilter", documentTypeFilter);
  }, [documentTypeFilter]);
  useEffect(() => {
    sessionStorage.setItem("hrms_id_verify_employeeSearchFilter", employeeSearchFilter);
  }, [employeeSearchFilter]);
  useEffect(() => {
    sessionStorage.setItem("hrms_id_verify_employeeFilter", employeeFilter);
  }, [employeeFilter]);

  const handleDelete = (id: string) => {
    if (confirm("Are you sure you want to delete this identity verification record?")) {
      setData(prev => prev.filter(item => item.id !== id));
      toast.success("Identity verification record deleted.");
    }
  };

  const handleDownload = (item: VerificationItem) => {
    const element = document.createElement("a");
    const file = new Blob([`Identity Verification Document\nEmployee: ${item.name}\nType: ${item.type}\nSubmitted On: ${item.submittedOn}\nStatus: ${item.status}`], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `${item.name.replace(/\s+/g, "_")}_${item.type}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    toast.success("Identity proof downloaded successfully!");
  };

  const handleView = (item: VerificationItem) => {
    const win = window.open("", "_blank");
    if (win) {
      win.document.write(`
        <html>
          <head>
            <title>Verification Proof - ${item.name}</title>
            <style>
              body { font-family: sans-serif; padding: 40px; background: #f8f9fa; color: #333; }
              .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); max-width: 500px; margin: auto; text-align: center; }
              h1 { color: #111; font-size: 22px; border-bottom: 2px solid #eee; padding-bottom: 12px; }
              .badge { display: inline-block; padding: 6px 12px; border-radius: 12px; font-weight: bold; font-size: 12px; margin-top: 10px; }
              .verified { background: #e6fcf5; color: #0ca678; }
              .pending { background: #fff9db; color: #f59f00; }
              .rejected { background: #fff5f5; color: #fa5252; }
            </style>
          </head>
          <body>
            <div class="card">
              <h1>📄 ID Verification Proof</h1>
              <p><strong>Employee:</strong> ${item.name}</p>
              <p><strong>Identity Document Type:</strong> ${item.type}</p>
              <p><strong>Submitted Date:</strong> ${item.submittedOn}</p>
              <div>
                <strong>Status:</strong> 
                <span class="badge ${item.status.toLowerCase().replace(/\s+/g, "")}">${item.status}</span>
              </div>
              <div style="margin-top: 30px; border: 2px dashed #ccc; padding: 50px; border-radius: 8px; color: #888;">
                [ MOCK IMAGE PREVIEW FOR ${item.type.toUpperCase()} ]
              </div>
            </div>
          </body>
        </html>
      `);
      win.document.close();
    }
  };

  const handleStatusChange = (id: string, newStatus: "Verified" | "Pending" | "Rejected") => {
    const item = data.find(i => i.id === id);
    if (!item) return;
    
    if (confirm(`Are you sure you want to change the status of ${item.name} to ${newStatus}?`)) {
      setData(prev => prev.map(i => i.id === id ? { ...i, status: newStatus } : i));
      toast.success(`Verification status updated to ${newStatus}.`);
    }
  };

  const handleResetFilters = () => {
    setPersonalIdStatusFilter("All");
    setDocumentTypeFilter("All");
    setEmployeeSearchFilter("All");
    setEmployeeFilter("All");
    setSearch("");
    toast.success("Filters reset successfully");
  };

  // Determine if editable for HR/Admin users
  const isEditable = !user || user.role === "admin" || user.role?.toLowerCase() === "hr";

  const documentTypeOptions = [
    { value: "All", label: "All" },
    { value: "Ration Card", label: "Ration Card" },
    { value: "IFSC Code", label: "IFSC Code" },
    { value: "Marital Status", label: "Marital Status" },
    { value: "Blood Group", label: "Blood Group" },
    { value: "Date Of Birth", label: "Date Of Birth" },
    { value: "Email", label: "Email" },
    { value: "Mobile Number", label: "Mobile Number" },
    { value: "AADHAAR", label: "AADHAAR" },
    { value: "Weight", label: "Weight" },
    { value: "Height", label: "Height" },
    { value: "Bank Details for Identification", label: "Bank Details for Identification" },
    { value: "Driving License", label: "Driving License" },
    { value: "Election Card", label: "Election Card" },
    { value: "National Population Register", label: "National Population Register" },
    { value: "Permanent Retirement Account Number", label: "Permanent Retirement Account Number" },
    { value: "Permanent Account Number", label: "Permanent Account Number" },
    { value: "Labour Welfare Fund Number", label: "Labour Welfare Fund Number" },
    { value: "Passport", label: "Passport" },
  ];

  const employeeSearchOptions = [
    { value: "All", label: "All Employees" },
    ...Array.from(new Map(data.map(item => [item.employeeId, item])).values()).map(emp => ({
      value: emp.employeeId,
      label: `${emp.name} (${emp.employeeId})`
    }))
  ];

  const employeeFilterOptions = [
    { value: "All", label: "All" },
    { value: "General scheme filter", label: "General scheme filter" },
    { value: "Confirmed Employees", label: "Confirmed Employees" },
    { value: "Probation Employees", label: "Probation Employees" },
    { value: "Probation EMP", label: "Probation EMP" },
    { value: "Probation Emp", label: "Probation Emp" },
    { value: "Trainee Employees", label: "Trainee Employees" },
    { value: "Contract Employees", label: "Contract Employees" },
    { value: "Contract Emp", label: "Contract Emp" },
    { value: "Upto 3 years service", label: "Upto 3 years service" },
    { value: "Between 3 - 5 years", label: "Between 3 - 5 years" },
    { value: "All Current Employees", label: "All Current Employees" },
    { value: "All Past Employees", label: "All Past Employees" },
    { value: "Above 5 years", label: "Above 5 years" },
    { value: "Partially Vaccinated Employees", label: "Partially Vaccinated Employees" },
    { value: "Sales Department", label: "Sales Department" },
    { value: "Bangalore Employees", label: "Bangalore Employees" },
    { value: "My Filter", label: "My Filter" },
  ];

  const filtered = data.filter((item) => {
    // 1. Personal ID Status Filter
    if (personalIdStatusFilter !== "All") {
      if (personalIdStatusFilter === "Not Available" && item.status !== "Not Available") return false;
      if (personalIdStatusFilter === "Available" && item.status === "Not Available") return false;
      if (personalIdStatusFilter === "Not Verified" && item.status !== "Pending" && item.status !== "Rejected") return false;
      if (personalIdStatusFilter === "Verified" && item.status !== "Verified") return false;
    }

    // 2. Document Type Filter
    if (documentTypeFilter !== "All") {
      const normFilter = documentTypeFilter.toLowerCase().replace(/\s+/g, "");
      const normItemType = item.type.toLowerCase().replace(/\s+/g, "");
      
      const isAadhaarMatch = normFilter === "aadhaar" && normItemType === "aadhaar";
      const isPanMatch = (normFilter === "permanentaccountnumber" || normFilter === "pan") && 
                         (normItemType === "pan" || normItemType === "permanentaccountnumber");
      const isPassportMatch = normFilter === "passport" && normItemType === "passport";
      const isGeneralMatch = normItemType === normFilter;
      
      if (!isAadhaarMatch && !isPanMatch && !isPassportMatch && !isGeneralMatch) {
        return false;
      }
    }

    // 3. Employee Search
    if (employeeSearchFilter !== "All") {
      if (item.employeeId !== employeeSearchFilter) {
        return false;
      }
    }

    // 4. Employee Filter
    if (employeeFilter !== "All") {
      switch (employeeFilter) {
        case "General scheme filter":
          if (item.scheme !== "General scheme filter") return false;
          break;
        case "Confirmed Employees":
          if (item.employeeType !== "Confirmed") return false;
          break;
        case "Probation Employees":
        case "Probation EMP":
        case "Probation Emp":
          if (item.employeeType !== "Probation") return false;
          break;
        case "Trainee Employees":
          if (item.employeeType !== "Trainee") return false;
          break;
        case "Contract Employees":
        case "Contract Emp":
          if (item.employeeType !== "Contract") return false;
          break;
        case "Upto 3 years service":
          if (item.serviceYears > 3) return false;
          break;
        case "Between 3 - 5 years":
          if (item.serviceYears <= 3 || item.serviceYears > 5) return false;
          break;
        case "Above 5 years":
          if (item.serviceYears <= 5) return false;
          break;
        case "All Current Employees":
          if (!item.isCurrent) return false;
          break;
        case "All Past Employees":
          if (item.isCurrent) return false;
          break;
        case "Partially Vaccinated Employees":
          if (item.vaccinated !== "Partially") return false;
          break;
        case "Sales Department":
          if (item.department !== "Sales") return false;
          break;
        case "Bangalore Employees":
          if (item.location !== "Bangalore") return false;
          break;
        case "My Filter":
          if (item.scheme !== "My Filter") return false;
          break;
        default:
          break;
      }
    }

    // 5. Search text (original search bar)
    if (search.trim() !== "") {
      const s = search.toLowerCase();
      const matchesSearchText =
        item.name.toLowerCase().includes(s) ||
        item.employeeId.toLowerCase().includes(s) ||
        item.type.toLowerCase().includes(s) ||
        item.status.toLowerCase().includes(s);
      if (!matchesSearchText) return false;
    }

    return true;
  });

  const stats = {
    verified: filtered.filter(i => i.status === "Verified").length,
    pending: filtered.filter(i => i.status === "Pending").length,
    rejected: filtered.filter(i => i.status === "Rejected").length,
  };

  return (
    <div className="portal-page admin-dashboard">
      {/* Header section */}
      <div>
        {/* <div className="space-y-1">
          <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-500" />
            Identity Verification
          </h2>
          <p className="text-sm text-muted-foreground">Review and verify employee government identity documents.</p>
        </div> */}
      </div>

      {/* Advanced Filters Section */}
      <div className="bg-card border border-border rounded-xl p-5 space-y-4 shadow-sm">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <Search className="w-4 h-4 text-muted-foreground" />
            Advanced Filters
          </h3>
          <button
            onClick={handleResetFilters}
            className="text-xs font-bold text-primary hover:text-primary/85 flex items-center gap-1 transition-colors outline-none"
          >
            Reset Filters
          </button>
        </div>
        
        <div className="space-y-3">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search employee..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:ring-2 focus:ring-primary/20 outline-none w-full"
            />
          </div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div className="space-y-1">
            <label className="text-xs font-bold text-muted-foreground">Personal ID Status</label>
            <SearchableSelect
              value={personalIdStatusFilter}
              onChange={setPersonalIdStatusFilter}
              options={[
                { value: "All", label: "All" },
                { value: "Not Available", label: "Not Available" },
                { value: "Available", label: "Available" },
                { value: "Not Verified", label: "Not Verified" },
                { value: "Verified", label: "Verified" },
              ]}
              searchable={false}
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-xs font-bold text-muted-foreground">Document Type</label>
            <SearchableSelect
              value={documentTypeFilter}
              onChange={setDocumentTypeFilter}
              options={documentTypeOptions}
              searchable={true}
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-xs font-bold text-muted-foreground">Employee Search</label>
            <SearchableSelect
              value={employeeSearchFilter}
              onChange={setEmployeeSearchFilter}
              options={employeeSearchOptions}
              placeholder="Search by Name/ID..."
              searchable={true}
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-xs font-bold text-muted-foreground">Employee Filter</label>
            <SearchableSelect
              value={employeeFilter}
              onChange={setEmployeeFilter}
              options={employeeFilterOptions}
              searchable={true}
            />
          </div>
        </div>
      </div>

      {/* Table Section */}
      <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-muted/30 border-b border-border">
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Employee</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">ID Type</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Submitted On</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Status</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((item) => (
                <tr key={item.id} className="hover:bg-secondary/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center font-bold text-xs">
                        {item.name.charAt(0)}
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm font-semibold">{item.name}</span>
                        <span className="text-[10px] text-muted-foreground font-mono">{item.employeeId}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {item.type === "Aadhaar" && <Fingerprint className="w-4 h-4 text-blue-500" />}
                      {(item.type === "Permanent Account Number" || item.type === "PAN") && <CreditCard className="w-4 h-4 text-orange-500" />}
                      {item.type === "Passport" && <Landmark className="w-4 h-4 text-indigo-500" />}
                      {(item.type === "Bank Details for Identification" || item.type === "IFSC Code") && <Landmark className="w-4 h-4 text-emerald-500" />}
                      {(item.type === "Driving License" || item.type === "Election Card") && <CreditCard className="w-4 h-4 text-purple-500" />}
                      {!["Aadhaar", "Permanent Account Number", "PAN", "Passport", "Bank Details for Identification", "IFSC Code", "Driving License", "Election Card"].includes(item.type) && <FileText className="w-4 h-4 text-slate-400" />}
                      <span className="text-sm">{item.type}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{item.submittedOn}</td>
                  <td className="px-6 py-4">
                    {isEditable && item.status !== "Not Available" ? (
                      <div className="relative inline-flex w-32">
                        <select
                          value={item.status}
                          onChange={(e) => handleStatusChange(item.id, e.target.value as any)}
                          className={`appearance-none w-full cursor-pointer pr-8 pl-3 py-1.5 rounded-full text-[11px] font-bold outline-none border-none focus:ring-2 focus:ring-primary/20 ${
                            item.status === "Verified" ? "bg-emerald-500/10 text-emerald-600" :
                            item.status === "Pending" ? "bg-amber-500/10 text-amber-600" :
                            "bg-rose-500/10 text-rose-600"
                          }`}
                        >
                          <option value="Pending" className="bg-card text-foreground font-bold">Pending</option>
                          <option value="Verified" className="bg-card text-foreground font-bold">Verified</option>
                          <option value="Rejected" className="bg-card text-foreground font-bold">Rejected</option>
                        </select>
                        <ChevronDown className={`w-3 h-3 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none ${
                          item.status === "Verified" ? "text-emerald-600" :
                          item.status === "Pending" ? "text-amber-600" :
                          "text-rose-600"
                        }`} />
                      </div>
                    ) : (
                      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold ${
                        item.status === "Verified" ? "bg-emerald-500/10 text-emerald-600" :
                        item.status === "Pending" ? "bg-amber-500/10 text-amber-600" :
                        item.status === "Rejected" ? "bg-rose-500/10 text-rose-600" :
                        "bg-slate-500/10 text-slate-600"
                      }`}>
                        {item.status === "Verified" && <CheckCircle2 className="w-3 h-3" />}
                        {item.status === "Pending" && <Clock className="w-3 h-3" />}
                        {item.status === "Rejected" && <XCircle className="w-3 h-3" />}
                        {item.status === "Not Available" && <Clock className="w-3 h-3 text-slate-400" />}
                        {item.status}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button 
                        onClick={() => handleView(item)}
                        disabled={item.status === "Not Available"}
                        className="p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-border transition-colors disabled:opacity-30 disabled:pointer-events-none"
                        title={item.status === "Not Available" ? "No proof submitted" : "View Proof"}
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleDownload(item)}
                        disabled={item.status === "Not Available"}
                        className="p-1.5 rounded-md text-muted-foreground hover:text-foreground hover:bg-border transition-colors disabled:opacity-30 disabled:pointer-events-none"
                        title={item.status === "Not Available" ? "No proof submitted" : "Download Proof"}
                      >
                        <Download className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleDelete(item.id)}
                        disabled={item.status === "Not Available"}
                        className="p-1.5 rounded-md text-muted-foreground hover:text-rose-600 hover:bg-rose-50 transition-colors disabled:opacity-30 disabled:pointer-events-none"
                        title={item.status === "Not Available" ? "No proof submitted" : "Delete Record"}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground text-sm font-medium">
                    No verification records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Stats Cards Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-3">
          <div className="w-10 h-10 bg-emerald-500/10 text-emerald-600 rounded-lg flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <p className="text-2xl font-bold">{stats.verified}</p>
          <p className="text-sm text-muted-foreground">Successfully Verified</p>
        </div>
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-3">
          <div className="w-10 h-10 bg-amber-500/10 text-amber-600 rounded-lg flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
          <p className="text-2xl font-bold">{stats.pending}</p>
          <p className="text-sm text-muted-foreground">Pending Review</p>
        </div>
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-3">
          <div className="w-10 h-10 bg-rose-500/10 text-rose-600 rounded-lg flex items-center justify-center">
            <XCircle className="w-5 h-5" />
          </div>
          <p className="text-2xl font-bold">{stats.rejected}</p>
          <p className="text-sm text-muted-foreground">Rejected Proofs</p>
        </div>
      </div>
    </div>
  );
}
