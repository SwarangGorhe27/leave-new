import React, { useState, useMemo } from "react";
import { 
  Search, 
  Filter, 
  Download, 
  MoreHorizontal, 
  Mail, 
  Phone, 
  Hash,
  Calendar,
  ChevronLeft,
  ChevronRight,
  FilterX
} from "lucide-react";
import { employees as mockEmployees } from "../../../components/employees/mockData";

export function EmployeeDirectoryPage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [employmentStatus, setEmploymentStatus] = useState("All");
  const [employeeFilter, setEmployeeFilter] = useState("All");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const filteredEmployees = useMemo(() => {
    return mockEmployees.filter(emp => {
      const matchesSearch = 
        emp.name.toLowerCase().includes(search.toLowerCase()) ||
        emp.employeeId.toLowerCase().includes(search.toLowerCase()) ||
        emp.email.toLowerCase().includes(search.toLowerCase());
      
      const matchesStatus = employmentStatus === "All" || emp.employmentStatus === employmentStatus;
      
      // Filter logic for "Current" vs "Past"
      const matchesFilter = employeeFilter === "All" || 
        (employeeFilter === "Current Employees" && emp.status === "Active") ||
        (employeeFilter === "Past Employees" && emp.status === "Inactive");

      return matchesSearch && matchesStatus && matchesFilter;
    });
  }, [search, employmentStatus, employeeFilter]);

  const totalPages = Math.ceil(filteredEmployees.length / itemsPerPage);
  const paginatedEmployees = filteredEmployees.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const resetFilters = () => {
    setSearch("");
    setCategory("All");
    setEmploymentStatus("All");
    setEmployeeFilter("All");
    setCurrentPage(1);
  };

  return (
    <div className="flex flex-col h-full bg-background/50">
      {/* Header & Stats */}
      <div className="px-6 py-6 bg-card border-b border-border shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-black text-foreground tracking-tight">Employee Directory</h1>
            <p className="text-sm font-medium text-muted-foreground mt-1 uppercase tracking-widest flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
              Viewing {filteredEmployees.length} total personnel records
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border bg-background text-sm font-bold text-foreground hover:bg-secondary transition-all">
              <Download size={16} />
              Export CSV
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-5 gap-4 mt-8">
          <div className="relative group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-indigo-500 transition-colors" size={16} />
            <input 
              type="text" 
              placeholder="Search name, ID or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-2xl bg-secondary/50 border border-border focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 outline-none text-sm transition-all"
            />
          </div>

          <select 
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="px-4 py-2.5 rounded-2xl bg-secondary/50 border border-border outline-none text-sm font-bold focus:border-indigo-500 transition-all cursor-pointer"
          >
            <option value="All">All Categories</option>
            <option value="Staff">Staff</option>
            <option value="Management">Management</option>
          </select>

          <select 
            value={employmentStatus}
            onChange={(e) => setEmploymentStatus(e.target.value)}
            className="px-4 py-2.5 rounded-2xl bg-secondary/50 border border-border outline-none text-sm font-bold focus:border-indigo-500 transition-all cursor-pointer"
          >
            <option value="All">All Employment Status</option>
            <option value="Confirmed">Confirmed</option>
            <option value="Probation">Probation</option>
            <option value="Contract">Contract</option>
            <option value="Trainee">Trainee</option>
          </select>

          <select 
            value={employeeFilter}
            onChange={(e) => setEmployeeFilter(e.target.value)}
            className="px-4 py-2.5 rounded-2xl bg-secondary/50 border border-border outline-none text-sm font-bold focus:border-indigo-500 transition-all cursor-pointer"
          >
            <option value="All">All Employees</option>
            <option value="Current Employees">Current Employees</option>
            <option value="Past Employees">Past Employees</option>
          </select>

          <button 
            onClick={resetFilters}
            className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-2xl border border-border bg-background text-sm font-bold text-muted-foreground hover:text-red-500 hover:bg-red-500/5 transition-all"
          >
            <FilterX size={16} />
            Reset
          </button>
        </div>
      </div>

      {/* Table Section */}
      <div className="flex-1 overflow-auto p-6">
        <div className="bg-card border border-border rounded-[2rem] overflow-hidden shadow-xl shadow-foreground/5">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-secondary/30 border-b border-border">
                <th className="px-6 py-4 text-[11px] font-black text-muted-foreground uppercase tracking-[0.2em]">Employee No</th>
                <th className="px-6 py-4 text-[11px] font-black text-muted-foreground uppercase tracking-[0.2em]">Employee Name</th>
                <th className="px-6 py-4 text-[11px] font-black text-muted-foreground uppercase tracking-[0.2em]">Join Date</th>
                <th className="px-6 py-4 text-[11px] font-black text-muted-foreground uppercase tracking-[0.2em]">Status</th>
                <th className="px-6 py-4 text-[11px] font-black text-muted-foreground uppercase tracking-[0.2em]">Contact Details</th>
                <th className="px-6 py-4 text-[11px] font-black text-muted-foreground uppercase tracking-[0.2em]">Ext. No</th>
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {paginatedEmployees.map((emp) => (
                <tr key={emp.id} className="hover:bg-secondary/20 transition-colors group">
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-2">
                      <Hash size={14} className="text-muted-foreground/50" />
                      <span className="text-sm font-black text-foreground font-mono">{emp.employeeId}</span>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-500 font-black text-sm border border-indigo-500/20 group-hover:scale-110 transition-transform">
                        {emp.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <p className="text-sm font-black text-foreground leading-none">{emp.name}</p>
                        <p className="text-[10px] font-bold text-muted-foreground mt-1 uppercase tracking-widest">{emp.designation}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Calendar size={14} />
                      <span className="text-xs font-bold">{new Date(emp.joiningDate).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}</span>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${
                      emp.status === "Active" ? "bg-emerald-500/10 text-emerald-600 border-emerald-500/20" :
                      emp.status === "On Leave" ? "bg-amber-500/10 text-amber-600 border-amber-500/20" :
                      "bg-slate-500/10 text-slate-600 border-slate-500/20"
                    }`}>
                      {emp.status}
                    </span>
                  </td>
                  <td className="px-6 py-5">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-xs font-bold text-foreground">
                        <Phone size={12} className="text-muted-foreground" />
                        {emp.phone}
                      </div>
                      <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
                        <Mail size={12} className="text-muted-foreground" />
                        {emp.email}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <span className="text-xs font-black text-muted-foreground/80">#{(Math.floor(Math.random() * 900) + 100)}</span>
                  </td>
                  <td className="px-6 py-5 text-right">
                    <button className="p-2 rounded-lg hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground">
                      <MoreHorizontal size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {paginatedEmployees.length === 0 && (
            <div className="py-20 text-center">
              <div className="w-16 h-16 rounded-3xl bg-secondary flex items-center justify-center mx-auto mb-4">
                <Search size={32} className="text-muted-foreground/30" />
              </div>
              <h3 className="text-lg font-black text-foreground">No employees found</h3>
              <p className="text-sm text-muted-foreground mt-1">Try adjusting your filters or search query.</p>
              <button onClick={resetFilters} className="mt-6 text-indigo-500 font-black text-xs uppercase tracking-widest hover:underline">Clear all filters</button>
            </div>
          )}
        </div>
      </div>

      {/* Pagination */}
      <div className="px-8 py-4 bg-card border-t border-border flex items-center justify-between">
        <p className="text-xs font-bold text-muted-foreground">
          Showing <span className="text-foreground">{(currentPage - 1) * itemsPerPage + 1}</span> to <span className="text-foreground">{Math.min(currentPage * itemsPerPage, filteredEmployees.length)}</span> of <span className="text-foreground">{filteredEmployees.length}</span> results
        </p>
        <div className="flex items-center gap-2">
          <button 
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(p => p - 1)}
            className="p-2 rounded-xl border border-border hover:bg-secondary transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ChevronLeft size={16} />
          </button>
          {[...Array(totalPages)].map((_, i) => (
            <button 
              key={i}
              onClick={() => setCurrentPage(i + 1)}
              className={`w-8 h-8 rounded-xl text-xs font-black transition-all ${
                currentPage === i + 1 ? "bg-foreground text-primary-foreground shadow-lg" : "hover:bg-secondary text-muted-foreground"
              }`}
            >
              {i + 1}
            </button>
          ))}
          <button 
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(p => p + 1)}
            className="p-2 rounded-xl border border-border hover:bg-secondary transition-all disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
