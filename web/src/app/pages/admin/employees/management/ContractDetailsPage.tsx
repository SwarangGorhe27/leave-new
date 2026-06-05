import React, { useState, useMemo, useEffect } from "react";

import {

  Handshake,

  Calendar,

  AlertTriangle,

  FileSignature,

  Filter,

  Plus,

  Search,

  RotateCcw,

  Edit2,

  Trash2,

  Settings2,

  X,

  Check,

  AlertCircle,

  Eye,

  Building2,

  Users,

  Briefcase,

  Info

} from "lucide-react";

import { employees as allMockEmployees } from "../../../../components/employees/mockData";



// Interfaces

interface EmployeeMap {

  id: string; // Employee ID (e.g. EMP-001)

  name: string;

  department: string;

  designation: string;

}



interface Contract {

  id: string;

  code: string;

  name: string;

  company: string;

  counterParty: string;

  establishment: string;

  natureOfWork: string;

  employeesRequired: number;

  startDate: string;

  endDate: string;

  status: "Active" | "Cancelled" | "Closed" | "Expired" | "Pending";

  mappedEmployees: EmployeeMap[];

}



export function ContractDetailsPage() {

  // --- Masters State (Dynamic & Manageable) ---

  const [companies, setCompanies] = useState<string[]>([

    "ABC Ltd",

    "Jai Maruthi Enterprise"

  ]);

  const [counterParties, setCounterParties] = useState<string[]>([

    "LLP Services",

    "Lea",

    "Guru Services"

  ]);

  const [establishments, setEstablishments] = useState<string[]>([

    "Main Campus",

    "Tech Park Office",

    "Corporate HQ"

  ]);



  // --- Masters Manager Modal State ---

  const [isMastersOpen, setIsMastersOpen] = useState(false);

  const [activeMasterTab, setActiveMasterTab] = useState<"companies" | "counterParties" | "establishments">("companies");

  const [newMasterInput, setNewMasterInput] = useState("");



  // --- Contracts State ---

  const [contracts, setContracts] = useState<Contract[]>([

    {

      id: "c1",

      code: "CONT-2026-001",

      name: "IT Infrastructure Support",

      company: "ABC Ltd",

      counterParty: "LLP Services",

      establishment: "Corporate HQ",

      natureOfWork: "L1 Support & Maintenance",

      employeesRequired: 5,

      startDate: "2026-01-01",

      endDate: "2026-12-31",

      status: "Active",

      mappedEmployees: [

        { id: "EMP-001", name: "Arjun Sharma", department: "Engineering", designation: "Senior Developer" },

        { id: "EMP-002", name: "Priya Nair", department: "Human Resources", designation: "HR Manager" }

      ]

    },

    {

      id: "c2",

      code: "CONT-2026-002",

      name: "Facility Management",

      company: "Jai Maruthi Enterprise",

      counterParty: "Lea",

      establishment: "Tech Park Office",

      natureOfWork: "Housekeeping & Security",

      employeesRequired: 3,

      startDate: "2025-06-01",

      endDate: "2026-05-01", // Past date, resolves to Expired automatically

      status: "Active",

      mappedEmployees: []

    },

    {

      id: "c3",

      code: "CONT-2026-003",

      name: "Helpdesk Operations",

      company: "ABC Ltd",

      counterParty: "Guru Services",

      establishment: "Main Campus",

      natureOfWork: "Customer Helpdesk Support",

      employeesRequired: 10,

      startDate: "2026-04-15",

      endDate: "2026-10-15",

      status: "Pending",

      mappedEmployees: []

    }

  ]);



  // --- View Mode State ---

  // "list" | "add" | "edit" | "view"

  const [viewMode, setViewMode] = useState<"list" | "add" | "edit" | "view">("list");

  const [selectedContractId, setSelectedContractId] = useState<string | null>(null);



  // --- Filter State ---

  const [filterCounterParty, setFilterCounterParty] = useState("All");

  const [filterStatus, setFilterStatus] = useState("All");

  const [filterFromDate, setFilterFromDate] = useState("");

  const [filterToDate, setFilterToDate] = useState("");

  const [searchQuery, setSearchQuery] = useState("");



  // Working state for active filters (applied only on Search click)

  const [appliedFilters, setAppliedFilters] = useState({

    counterParty: "All",

    status: "All",

    fromDate: "",

    toDate: "",

    search: ""

  });



  // --- Form State ---

  const [formCode, setFormCode] = useState("");

  const [formName, setFormName] = useState("");

  const [formCompany, setFormCompany] = useState("");

  const [formCounterParty, setFormCounterParty] = useState("");

  const [formEstablishment, setFormEstablishment] = useState("");

  const [formNatureOfWork, setFormNatureOfWork] = useState("");

  const [formEmployeesRequired, setFormEmployeesRequired] = useState<number>(0);

  const [formStartDate, setFormStartDate] = useState("");

  const [formEndDate, setFormEndDate] = useState("");

  const [formStatus, setFormStatus] = useState<Contract["status"]>("Pending");

  const [formMappedEmployees, setFormMappedEmployees] = useState<EmployeeMap[]>([]);



  // --- Employee Assignment Search State ---

  const [empSearchQuery, setEmpSearchQuery] = useState("");

  const [isEmpSearchDropdownOpen, setIsEmpSearchDropdownOpen] = useState(false);



  // Determine if a contract is expired based on current date

  const isExpired = (endDateStr: string) => {

    if (!endDateStr) return false;

    const today = new Date();

    today.setHours(0, 0, 0, 0);

    const end = new Date(endDateStr);

    end.setHours(0, 0, 0, 0);

    return end < today;

  };



  // Resolve contract status dynamically

  const getResolvedStatus = (contract: Contract): Contract["status"] => {

    if (contract.status === "Closed" || contract.status === "Cancelled") {

      return contract.status;

    }

    if (isExpired(contract.endDate)) {

      return "Expired";

    }

    return contract.status;

  };



  // Resolve all contracts with automatic expiration checks

  const resolvedContracts = useMemo(() => {

    return contracts.map(c => ({

      ...c,

      status: getResolvedStatus(c)

    }));

  }, [contracts]);



  // Handle dynamic filtering

  const filteredContracts = useMemo(() => {

    return resolvedContracts.filter((c) => {

      const matchCounterParty =

        appliedFilters.counterParty === "All" || c.counterParty === appliedFilters.counterParty;



      const matchStatus =

        appliedFilters.status === "All" || c.status === appliedFilters.status;



      let matchPeriod = true;

      if (appliedFilters.fromDate) {

        matchPeriod = matchPeriod && new Date(c.startDate) >= new Date(appliedFilters.fromDate);

      }

      if (appliedFilters.toDate) {

        matchPeriod = matchPeriod && new Date(c.endDate) <= new Date(appliedFilters.toDate);

      }



      let matchSearch = true;

      if (appliedFilters.search) {

        const query = appliedFilters.search.toLowerCase();

        matchSearch =

          c.name.toLowerCase().includes(query) ||

          c.code.toLowerCase().includes(query) ||

          c.natureOfWork.toLowerCase().includes(query) ||

          c.company.toLowerCase().includes(query) ||

          c.counterParty.toLowerCase().includes(query) ||

          c.establishment.toLowerCase().includes(query);

      }



      return matchCounterParty && matchStatus && matchPeriod && matchSearch;

    });

  }, [resolvedContracts, appliedFilters]);



  // Apply filters on Search click

  const handleApplyFilters = () => {

    setAppliedFilters({

      counterParty: filterCounterParty,

      status: filterStatus,

      fromDate: filterFromDate,

      toDate: filterToDate,

      search: searchQuery

    });

  };



  // Reset Filters

  const handleResetFilters = () => {

    setFilterCounterParty("All");

    setFilterStatus("All");

    setFilterFromDate("");

    setFilterToDate("");

    setSearchQuery("");

    setAppliedFilters({

      counterParty: "All",

      status: "All",

      fromDate: "",

      toDate: "",

      search: ""

    });

  };



  // Open Form for Add

  const handleOpenAdd = () => {

    setFormCode(`CONT-${new Date().getFullYear()}-${String(contracts.length + 1).padStart(3, "0")}`);

    setFormName("");

    setFormCompany(companies[0] || "");

    setFormCounterParty(counterParties[0] || "");

    setFormEstablishment(establishments[0] || "");

    setFormNatureOfWork("");

    setFormEmployeesRequired(0);

    setFormStartDate("");

    setFormEndDate("");

    setFormStatus("Pending");

    setFormMappedEmployees([]);

    setViewMode("add");

  };



  // Open Form for Edit or View

  const handleOpenEditOrView = (contractId: string, mode: "edit" | "view") => {

    const c = contracts.find((x) => x.id === contractId);

    if (!c) return;



    setSelectedContractId(contractId);

    setFormCode(c.code);

    setFormName(c.name);

    setFormCompany(c.company);

    setFormCounterParty(c.counterParty);

    setFormEstablishment(c.establishment);

    setFormNatureOfWork(c.natureOfWork);

    setFormEmployeesRequired(c.employeesRequired);

    setFormStartDate(c.startDate);

    setFormEndDate(c.endDate);

    setFormStatus(c.status);

    setFormMappedEmployees(c.mappedEmployees);

    setViewMode(mode);

  };



  // Save or Update Contract

  const handleSave = () => {

    if (!formCode || !formName || !formCompany || !formCounterParty || !formEstablishment || !formStartDate || !formEndDate) {

      alert("Please fill in all mandatory fields.");

      return;

    }



    // Determine target status

    let finalStatus = formStatus;

    if (isExpired(formEndDate)) {

      finalStatus = "Expired";

    }



    if (viewMode === "add") {

      const newContract: Contract = {

        id: `c_${Date.now()}`,

        code: formCode,

        name: formName,

        company: formCompany,

        counterParty: formCounterParty,

        establishment: formEstablishment,

        natureOfWork: formNatureOfWork,

        employeesRequired: formEmployeesRequired,

        startDate: formStartDate,

        endDate: formEndDate,

        status: finalStatus,

        mappedEmployees: formMappedEmployees

      };

      setContracts((prev) => [...prev, newContract]);

    } else if (viewMode === "edit" && selectedContractId) {

      setContracts((prev) =>

        prev.map((c) =>

          c.id === selectedContractId

            ? {

                ...c,

                code: formCode,

                name: formName,

                company: formCompany,

                counterParty: formCounterParty,

                establishment: formEstablishment,

                natureOfWork: formNatureOfWork,

                employeesRequired: formEmployeesRequired,

                startDate: formStartDate,

                endDate: formEndDate,

                status: finalStatus,

                mappedEmployees: formMappedEmployees

              }

            : c

        )

      );

    }

    setViewMode("list");

  };



  // Employee Selection Options (exclude already mapped ones)

  const availableEmployeesToMap = useMemo(() => {

    return allMockEmployees.filter((emp) => {

      const isAlreadyMapped = formMappedEmployees.some((m) => m.id === emp.employeeId);

      const matchesSearch =

        emp.name.toLowerCase().includes(empSearchQuery.toLowerCase()) ||

        emp.employeeId.toLowerCase().includes(empSearchQuery.toLowerCase());

      return !isAlreadyMapped && matchesSearch;

    });

  }, [allMockEmployees, formMappedEmployees, empSearchQuery]);



  // Add Employee to Mapping List

  const handleAddEmployeeMapping = (emp: typeof allMockEmployees[0]) => {

    const mapping: EmployeeMap = {

      id: emp.employeeId,

      name: emp.name,

      department: emp.department,

      designation: emp.designation

    };

    setFormMappedEmployees((prev) => [...prev, mapping]);

    setEmpSearchQuery("");

    setIsEmpSearchDropdownOpen(false);

  };



  // Remove Employee Mapping

  const handleRemoveEmployeeMapping = (empId: string) => {

    setFormMappedEmployees((prev) => prev.filter((e) => e.id !== empId));

  };



  // Dynamic Validation / Statistics

  const assignedCount = formMappedEmployees.length;

  const pendingCount = Math.max(0, formEmployeesRequired - assignedCount);

  const isCountExceeded = assignedCount > formEmployeesRequired;



  // Master Management logic

  const handleAddMaster = () => {

    if (!newMasterInput.trim()) return;

    const value = newMasterInput.trim();



    if (activeMasterTab === "companies") {

      if (!companies.includes(value)) setCompanies([...companies, value]);

    } else if (activeMasterTab === "counterParties") {

      if (!counterParties.includes(value)) setCounterParties([...counterParties, value]);

    } else if (activeMasterTab === "establishments") {

      if (!establishments.includes(value)) setEstablishments([...establishments, value]);

    }



    setNewMasterInput("");

  };



  const handleDeleteMaster = (valueToDelete: string) => {

    if (activeMasterTab === "companies") {

      setCompanies(companies.filter((x) => x !== valueToDelete));

    } else if (activeMasterTab === "counterParties") {

      setCounterParties(counterParties.filter((x) => x !== valueToDelete));

    } else if (activeMasterTab === "establishments") {

      setEstablishments(establishments.filter((x) => x !== valueToDelete));

    }

  };



  // Expired or Closed or Cancelled forms should be read-only

  const isFormReadOnly = viewMode === "view" || formStatus === "Closed" || formStatus === "Cancelled";



  return (

    <div className="portal-page admin-dashboard">

      {/* Title Header */}

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">

        {/* <div className="space-y-1">

          <h2 className="text-2xl font-black tracking-tight text-foreground flex items-center gap-2.5">

            <Handshake className="w-6 h-6 text-amber-500" />

            Contract Details

          </h2>

          <p className="text-sm text-muted-foreground">

            Manage operational contracts, mappings, status compliance, and counter parties dynamic records.

          </p>

        </div> */}

        {viewMode === "list" && (

          <div className="flex items-center gap-3">

            <button

              onClick={() => setIsMastersOpen(true)}

              className="flex items-center gap-2 px-4 py-2 border border-border bg-background hover:bg-secondary/50 text-sm font-bold rounded-xl transition-all"

            >

              <Settings2 className="w-4 h-4" />

              Manage Masters

            </button>

            <button

              onClick={handleOpenAdd}

              className="flex items-center gap-2 px-4 py-2 bg-primary text-white text-sm font-black rounded-xl hover:opacity-90 shadow-lg shadow-primary/20 transition-all"

            >

              <Plus className="w-4 h-4" />

              Add Contract

            </button>

          </div>

        )}

      </div>



      {viewMode === "list" ? (

        <>

          {/* Filters Card */}

          <div className="bg-card border border-border p-5 rounded-2xl shadow-sm space-y-4">

            {/* <div className="flex items-center gap-2 text-xs font-black uppercase text-muted-foreground tracking-widest border-b border-border pb-2.5">

              <Filter className="w-4 h-4" />

              Search & Filters

            </div> */}

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">

              {/* Counter Party Filter */}

              <div className="space-y-1.5">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Counter Party</label>

                <select

                  value={filterCounterParty}

                  onChange={(e) => setFilterCounterParty(e.target.value)}

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/20 p-2.5 outline-none focus:border-primary transition-all"

                >

                  <option value="All">All Counter Parties</option>

                  {counterParties.map((cp) => (

                    <option key={cp} value={cp}>{cp}</option>

                  ))}

                </select>

              </div>



              {/* Status Filter */}

              <div className="space-y-1.5">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Status</label>

                <select

                  value={filterStatus}

                  onChange={(e) => setFilterStatus(e.target.value)}

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/20 p-2.5 outline-none focus:border-primary transition-all"

                >

                  <option value="All">All Statuses</option>

                  <option value="Active">Active</option>

                  <option value="Cancelled">Cancelled</option>

                  <option value="Closed">Closed</option>

                  <option value="Expired">Expired</option>

                  <option value="Pending">Pending</option>

                </select>

              </div>



              {/* Date From */}

              <div className="space-y-1.5">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">From Date</label>

                <input

                  type="date"

                  value={filterFromDate}

                  onChange={(e) => setFilterFromDate(e.target.value)}

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/20 p-2 outline-none focus:border-primary transition-all"

                />

              </div>



              {/* Date To */}

              <div className="space-y-1.5">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">To Date</label>

                <input

                  type="date"

                  value={filterToDate}

                  onChange={(e) => setFilterToDate(e.target.value)}

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/20 p-2 outline-none focus:border-primary transition-all"

                />

              </div>



              {/* Search String */}

              <div className="space-y-1.5">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Search text</label>

                <div className="relative">

                  <input

                    type="text"

                    placeholder="Search query..."

                    value={searchQuery}

                    onChange={(e) => setSearchQuery(e.target.value)}

                    className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/20 py-2.5 pl-8 pr-3 outline-none focus:border-primary transition-all"

                  />

                  <Search className="w-3.5 h-3.5 absolute left-3 top-3.5 text-muted-foreground" />

                </div>

              </div>

            </div>



            {/* Filter Action Buttons */}

            <div className="flex items-center justify-end gap-3 pt-2">

              <button

                onClick={handleResetFilters}

                className="flex items-center gap-1.5 text-xs font-bold text-muted-foreground hover:text-foreground px-4 py-2 rounded-lg transition-all"

              >

                <RotateCcw className="w-3.5 h-3.5" />

                Reset Filters

              </button>

              {/* <button

                onClick={handleApplyFilters}

                className="flex items-center gap-2 px-5 py-2.5 bg-foreground text-background text-xs font-black rounded-lg hover:opacity-90 shadow-md transition-all"

              >

                <Search className="w-3.5 h-3.5" />

                Search

              </button> */}

            </div>

          </div>



          {/* Grid/Table Card */}

          <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">

            <div className="overflow-x-auto">

              <table className="w-full text-left border-collapse">

                <thead>

                  <tr className="bg-secondary/40 border-b border-border">

                    <th className="p-4 text-[10px] font-black uppercase text-muted-foreground tracking-widest">Contract Code</th>

                    <th className="p-4 text-[10px] font-black uppercase text-muted-foreground tracking-widest">Contract Name</th>

                    <th className="p-4 text-[10px] font-black uppercase text-muted-foreground tracking-widest">Company</th>

                    <th className="p-4 text-[10px] font-black uppercase text-muted-foreground tracking-widest">Counter Party</th>

                    <th className="p-4 text-[10px] font-black uppercase text-muted-foreground tracking-widest">Establishment</th>

                    <th className="p-4 text-[10px] font-black uppercase text-muted-foreground tracking-widest">Nature of Work</th>

                    <th className="p-4 text-[10px] font-black uppercase text-muted-foreground tracking-widest">Contract Period</th>

                    <th className="p-4 text-[10px] font-black uppercase text-muted-foreground tracking-widest">Req / Mapped / Pend</th>

                    <th className="p-4 text-[10px] font-black uppercase text-muted-foreground tracking-widest">Status</th>

                    <th className="p-4 text-[10px] font-black uppercase text-muted-foreground tracking-widest text-center">Actions</th>

                  </tr>

                </thead>

                <tbody className="divide-y divide-border">

                  {filteredContracts.length === 0 ? (

                    <tr>

                      <td colSpan={10} className="p-8 text-center text-sm font-medium text-muted-foreground">

                        No contracts found matching the active filter criteria.

                      </td>

                    </tr>

                  ) : (

                    filteredContracts.map((c) => {

                      const req = c.employeesRequired;

                      const mapped = c.mappedEmployees.length;

                      const pending = Math.max(0, req - mapped);

                      const isOver = mapped > req;



                      return (

                        <tr key={c.id} className="hover:bg-secondary/20 transition-all">

                          <td className="p-4 text-xs font-bold font-mono text-primary">{c.code}</td>

                          <td className="p-4 text-xs font-black">{c.name}</td>

                          <td className="p-4 text-xs font-semibold text-muted-foreground">{c.company}</td>

                          <td className="p-4 text-xs font-semibold text-muted-foreground">{c.counterParty}</td>

                          <td className="p-4 text-xs font-semibold text-muted-foreground">{c.establishment}</td>

                          <td className="p-4 text-xs font-semibold text-muted-foreground truncate max-w-[150px]">{c.natureOfWork || "—"}</td>

                          <td className="p-4 text-xs font-semibold text-muted-foreground">

                            <div className="flex flex-col gap-0.5">

                              <span className="text-[10px] font-medium text-muted-foreground/80">From: {c.startDate}</span>

                              <span className="text-[10px] font-medium text-muted-foreground/80">To: {c.endDate}</span>

                            </div>

                          </td>

                          <td className="p-4 text-xs font-bold">

                            <span className="text-foreground">{req}</span>

                            <span className="text-muted-foreground/50 mx-1">/</span>

                            <span className={isOver ? "text-rose-500 font-extrabold" : "text-emerald-500"}>{mapped}</span>

                            <span className="text-muted-foreground/50 mx-1">/</span>

                            <span className={pending > 0 ? "text-amber-500" : "text-muted-foreground"}>{pending}</span>

                          </td>

                          <td className="p-4 text-xs">

                            <span

                              className={`px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-wider ${

                                c.status === "Active"

                                  ? "bg-emerald-500/10 text-emerald-500"

                                  : c.status === "Cancelled"

                                  ? "bg-rose-500/10 text-rose-500"

                                  : c.status === "Closed"

                                  ? "bg-slate-500/10 text-slate-500"

                                  : c.status === "Expired"

                                  ? "bg-amber-500/10 text-amber-500"

                                  : "bg-blue-500/10 text-blue-500"

                              }`}

                            >

                              {c.status}

                            </span>

                          </td>

                          <td className="p-4 text-xs text-center">

                            <div className="flex items-center justify-center gap-2">

                              <button

                                onClick={() => handleOpenEditOrView(c.id, "view")}

                                className="p-1.5 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-lg transition-all"

                                title="View Details"

                              >

                                <Eye className="w-4 h-4" />

                              </button>

                              <button

                                onClick={() => handleOpenEditOrView(c.id, "edit")}

                                className="p-1.5 text-muted-foreground hover:text-primary hover:bg-secondary rounded-lg transition-all"

                                title={c.status === "Closed" || c.status === "Cancelled" ? "View Read-Only" : "Edit Contract"}

                              >

                                <Edit2 className="w-4 h-4" />

                              </button>

                            </div>

                          </td>

                        </tr>

                      );

                    })

                  )}

                </tbody>

              </table>

            </div>

          </div>

        </>

      ) : (

        /* Form View (Add / Edit / View) */

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Left Column: Contract Details form */}

          <div className="lg:col-span-2 space-y-6 bg-card border border-border p-6 rounded-2xl shadow-sm">

            <div className="flex items-center justify-between border-b border-border pb-3">

              <h3 className="text-sm font-black uppercase tracking-wider text-muted-foreground flex items-center gap-2">

                <FileSignature className="w-4 h-4 text-primary" />

                Contract Details

              </h3>

              {isFormReadOnly && (

                <span className="flex items-center gap-1.5 text-xs font-black text-rose-500 bg-rose-500/10 px-3 py-1 rounded-full">

                  <Info className="w-3.5 h-3.5" />

                  READ ONLY MODE

                </span>

              )}

            </div>



            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

              {/* Contract Code */}

              <div className="space-y-1">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Contract Code</label>

                <input

                  type="text"

                  disabled={true} // Always auto-generated/locked

                  value={formCode}

                  className="w-full text-xs font-bold font-mono rounded-lg border border-border bg-secondary/40 p-2.5 outline-none cursor-not-allowed"

                />

              </div>



              {/* Name of Contract */}

              <div className="space-y-1">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Name of Contract *</label>

                <input

                  type="text"

                  disabled={isFormReadOnly}

                  value={formName}

                  onChange={(e) => setFormName(e.target.value)}

                  placeholder="Enter contract name"

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/10 p-2.5 outline-none focus:border-primary transition-all disabled:opacity-60 disabled:cursor-not-allowed"

                />

              </div>



              {/* Company (Dropdown) */}

              <div className="space-y-1">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Company *</label>

                <select

                  disabled={isFormReadOnly}

                  value={formCompany}

                  onChange={(e) => setFormCompany(e.target.value)}

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/10 p-2.5 outline-none focus:border-primary transition-all disabled:opacity-60 disabled:cursor-not-allowed"

                >

                  {companies.map((co) => (

                    <option key={co} value={co}>{co}</option>

                  ))}

                </select>

              </div>



              {/* Counter Party (Dropdown) */}

              <div className="space-y-1">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Counter Party *</label>

                <select

                  disabled={isFormReadOnly}

                  value={formCounterParty}

                  onChange={(e) => setFormCounterParty(e.target.value)}

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/10 p-2.5 outline-none focus:border-primary transition-all disabled:opacity-60 disabled:cursor-not-allowed"

                >

                  {counterParties.map((cp) => (

                    <option key={cp} value={cp}>{cp}</option>

                  ))}

                </select>

              </div>



              {/* Establishment (Dropdown) */}

              <div className="space-y-1">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Establishment *</label>

                <select

                  disabled={isFormReadOnly}

                  value={formEstablishment}

                  onChange={(e) => setFormEstablishment(e.target.value)}

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/10 p-2.5 outline-none focus:border-primary transition-all disabled:opacity-60 disabled:cursor-not-allowed"

                >

                  {establishments.map((est) => (

                    <option key={est} value={est}>{est}</option>

                  ))}

                </select>

              </div>



              {/* Status (Dropdown) */}

              <div className="space-y-1">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Status</label>

                <select

                  disabled={isFormReadOnly}

                  value={formStatus}

                  onChange={(e) => setFormStatus(e.target.value as Contract["status"])}

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/10 p-2.5 outline-none focus:border-primary transition-all disabled:opacity-60 disabled:cursor-not-allowed"

                >

                  <option value="Active">Active</option>

                  <option value="Cancelled">Cancelled</option>

                  <option value="Closed">Closed</option>

                  <option value="Expired">Expired</option>

                  <option value="Pending">Pending</option>

                </select>

              </div>



              {/* Start Date */}

              <div className="space-y-1">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Start Date *</label>

                <input

                  type="date"

                  disabled={isFormReadOnly}

                  value={formStartDate}

                  onChange={(e) => setFormStartDate(e.target.value)}

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/10 p-2 outline-none focus:border-primary transition-all disabled:opacity-60 disabled:cursor-not-allowed"

                />

              </div>



              {/* End Date */}

              <div className="space-y-1">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">End Date *</label>

                <input

                  type="date"

                  disabled={isFormReadOnly}

                  value={formEndDate}

                  onChange={(e) => setFormEndDate(e.target.value)}

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/10 p-2 outline-none focus:border-primary transition-all disabled:opacity-60 disabled:cursor-not-allowed"

                />

              </div>



              {/* No of Employees Required */}

              <div className="space-y-1">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Employees Required</label>

                <input

                  type="number"

                  disabled={isFormReadOnly}

                  value={formEmployeesRequired}

                  onChange={(e) => setFormEmployeesRequired(Number(e.target.value))}

                  placeholder="0"

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/10 p-2.5 outline-none focus:border-primary transition-all disabled:opacity-60 disabled:cursor-not-allowed"

                />

              </div>



              {/* Nature of Work */}

              <div className="space-y-1 sm:col-span-2">

                <label className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Nature of Work</label>

                <textarea

                  rows={2}

                  disabled={isFormReadOnly}

                  value={formNatureOfWork}

                  onChange={(e) => setFormNatureOfWork(e.target.value)}

                  placeholder="Describe scope / nature of work..."

                  className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/10 p-2.5 outline-none focus:border-primary transition-all disabled:opacity-60 disabled:cursor-not-allowed"

                />

              </div>

            </div>



            {/* Action Buttons */}

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-border mt-6">

              <button

                onClick={() => setViewMode("list")}

                className="px-4 py-2 border border-border hover:bg-secondary/40 text-xs font-bold rounded-lg transition-all"

              >

                Cancel

              </button>

              {!isFormReadOnly && (

                <button

                  onClick={handleSave}

                  className="px-6 py-2.5 bg-primary text-white text-xs font-black rounded-lg hover:opacity-90 shadow-md shadow-primary/10 transition-all"

                >

                  {viewMode === "add" ? "Save" : "Update"}

                </button>

              )}

            </div>

          </div>



          {/* Right Column: Employees Mapping Section */}

          <div className="space-y-6">

            {/* Stats widget for Mapping */}

            <div className="bg-card border border-border p-5 rounded-2xl shadow-sm space-y-4">

              <h3 className="text-xs font-black uppercase tracking-wider text-muted-foreground flex items-center gap-2">

                <Users className="w-4 h-4 text-emerald-500" />

                Assigned Statistics

              </h3>

              <div className="grid grid-cols-3 gap-3 text-center">

                <div className="bg-secondary/30 p-3 rounded-xl border border-border">

                  <p className="text-[10px] font-black uppercase text-muted-foreground tracking-wider">Required</p>

                  <p className="text-xl font-black text-foreground mt-1">{formEmployeesRequired}</p>

                </div>

                <div className="bg-secondary/30 p-3 rounded-xl border border-border">

                  <p className="text-[10px] font-black uppercase text-muted-foreground tracking-wider">Assigned</p>

                  <p className={`text-xl font-black mt-1 ${isCountExceeded ? "text-rose-500" : "text-emerald-500"}`}>

                    {assignedCount}

                  </p>

                </div>

                <div className="bg-secondary/30 p-3 rounded-xl border border-border">

                  <p className="text-[10px] font-black uppercase text-muted-foreground tracking-wider">Pending</p>

                  <p className="text-xl font-black text-amber-500 mt-1">{pendingCount}</p>

                </div>

              </div>



              {/* Employee Count Validation Message */}

              {isCountExceeded && (

                <div className="flex items-start gap-2 bg-rose-500/10 border border-rose-500/20 text-rose-500 p-3 rounded-xl text-xs font-semibold leading-relaxed">

                  <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />

                  <div>

                    Validation Alert: Mapped employees ({assignedCount}) exceed the required count ({formEmployeesRequired}).

                  </div>

                </div>

              )}

            </div>



            {/* Mapped Employees list */}

            <div className="bg-card border border-border p-5 rounded-2xl shadow-sm space-y-4">

              <div className="flex items-center justify-between">

                <h3 className="text-xs font-black uppercase tracking-wider text-muted-foreground">Mapped Employees</h3>

                {!isFormReadOnly && (

                  <span className="text-[10px] font-medium text-muted-foreground">

                    Assign from search dropdown below

                  </span>

                )}

              </div>



              {/* Search dropdown trigger */}

              {!isFormReadOnly && (

                <div className="relative">

                  <div className="relative">

                    <input

                      type="text"

                      placeholder="Search employee by Name or ID..."

                      value={empSearchQuery}

                      onFocus={() => setIsEmpSearchDropdownOpen(true)}

                      onChange={(e) => {

                        setEmpSearchQuery(e.target.value);

                        setIsEmpSearchDropdownOpen(true);

                      }}

                      className="w-full text-xs font-semibold rounded-lg border border-border bg-secondary/15 py-2.5 pl-8 pr-3 outline-none focus:border-primary transition-all"

                    />

                    <Search className="w-3.5 h-3.5 absolute left-3 top-3.5 text-muted-foreground" />

                    {empSearchQuery && (

                      <button

                        onClick={() => {

                          setEmpSearchQuery("");

                          setIsEmpSearchDropdownOpen(false);

                        }}

                        className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"

                      >

                        <X className="w-3.5 h-3.5" />

                      </button>

                    )}

                  </div>



                  {/* Dropdown Options */}

                  {isEmpSearchDropdownOpen && (

                    <div className="absolute left-0 right-0 mt-1 max-h-48 overflow-y-auto bg-card border border-border shadow-xl rounded-xl z-20 divide-y divide-border">

                      {availableEmployeesToMap.length === 0 ? (

                        <div className="p-3 text-xs font-medium text-muted-foreground text-center">

                          No available employees matching search criteria

                        </div>

                      ) : (

                        availableEmployeesToMap.map((emp) => (

                          <div

                            key={emp.employeeId}

                            onClick={() => handleAddEmployeeMapping(emp)}

                            className="p-2.5 hover:bg-secondary/40 transition-colors cursor-pointer text-left space-y-0.5"

                          >

                            <p className="text-xs font-black text-foreground">{emp.name}</p>

                            <div className="flex items-center justify-between text-[10px] text-muted-foreground">

                              <span>ID: {emp.employeeId}</span>

                              <span>Dept: {emp.department}</span>

                            </div>

                          </div>

                        ))

                      )}

                    </div>

                  )}

                </div>

              )}



              {/* Mapped employees scroll area */}

              <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">

                {formMappedEmployees.length === 0 ? (

                  <div className="text-center py-8 text-xs font-medium text-muted-foreground border-2 border-dashed border-border rounded-xl">

                    No employees mapped to this contract yet.

                  </div>

                ) : (

                  formMappedEmployees.map((emp) => (

                    <div

                      key={emp.id}

                      className="flex items-center justify-between p-3 bg-secondary/20 border border-border rounded-xl hover:bg-secondary/35 transition-colors"

                    >

                      <div className="space-y-0.5">

                        <div className="flex items-center gap-2">

                          <span className="text-xs font-black">{emp.name}</span>

                          <span className="text-[9px] font-bold font-mono bg-secondary border border-border px-1 py-0.5 rounded text-muted-foreground">

                            {emp.id}

                          </span>

                        </div>

                        <div className="flex items-center gap-2 text-[10px] text-muted-foreground">

                          <span className="flex items-center gap-0.5">

                            <Building2 className="w-3 h-3" />

                            {emp.department}

                          </span>

                          <span className="text-muted-foreground/30">•</span>

                          <span className="flex items-center gap-0.5">

                            <Briefcase className="w-3 h-3" />

                            {emp.designation}

                          </span>

                        </div>

                      </div>



                      {!isFormReadOnly && (

                        <button

                          onClick={() => handleRemoveEmployeeMapping(emp.id)}

                          className="p-1 text-muted-foreground hover:text-rose-500 hover:bg-rose-500/10 rounded-lg transition-all"

                          title="Remove Assignment"

                        >

                          <X className="w-4 h-4" />

                        </button>

                      )}

                    </div>

                  ))

                )}

              </div>

            </div>

          </div>

        </div>

      )}



      {/* Dynamic Masters Modal Popup */}

      {isMastersOpen && (

        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">

          <div className="bg-card border border-border rounded-2xl max-w-md w-full shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">

            {/* Header */}

            <div className="px-5 py-4 border-b border-border flex items-center justify-between bg-muted/20">

              <h3 className="text-sm font-black uppercase tracking-wider text-muted-foreground flex items-center gap-2">

                <Settings2 className="w-4 h-4 text-primary" />

                Manage Dynamic Masters

              </h3>

              <button

                onClick={() => setIsMastersOpen(false)}

                className="p-1 rounded-lg hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground"

              >

                <X className="w-4 h-4" />

              </button>

            </div>



            {/* Tabs */}

            <div className="flex border-b border-border bg-secondary/20">

              {[

                { id: "companies", label: "Companies" },

                { id: "counterParties", label: "Counter Parties" },

                { id: "establishments", label: "Establishments" }

              ].map((tab) => (

                <button

                  key={tab.id}

                  onClick={() => {

                    setActiveMasterTab(tab.id as any);

                    setNewMasterInput("");

                  }}

                  className={`flex-1 py-3 text-xs font-bold border-b-2 transition-all ${

                    activeMasterTab === tab.id

                      ? "border-primary text-foreground bg-card"

                      : "border-transparent text-muted-foreground hover:text-foreground"

                  }`}

                >

                  {tab.label}

                </button>

              ))}

            </div>



            {/* Tab Panel */}

            <div className="p-5 space-y-4">

              {/* Add Master Input */}

              <div className="flex gap-2">

                <input

                  type="text"

                  placeholder={`Add new ${

                    activeMasterTab === "companies"

                      ? "company"

                      : activeMasterTab === "counterParties"

                      ? "counter party"

                      : "establishment"

                  }...`}

                  value={newMasterInput}

                  onChange={(e) => setNewMasterInput(e.target.value)}

                  className="flex-1 text-xs font-semibold rounded-lg border border-border bg-secondary/15 p-2 outline-none focus:border-primary transition-all"

                />

                <button

                  onClick={handleAddMaster}

                  className="px-3.5 py-2 bg-foreground text-background text-xs font-black rounded-lg hover:opacity-90 transition-all"

                >

                  Add

                </button>

              </div>



              {/* Master Options List */}

              <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">

                {(activeMasterTab === "companies"

                  ? companies

                  : activeMasterTab === "counterParties"

                  ? counterParties

                  : establishments

                ).map((val) => (

                  <div

                    key={val}

                    className="flex items-center justify-between p-2.5 bg-secondary/10 border border-border/80 rounded-lg"

                  >

                    <span className="text-xs font-bold text-foreground">{val}</span>

                    <button

                      onClick={() => handleDeleteMaster(val)}

                      className="text-muted-foreground hover:text-rose-500 p-0.5 rounded transition-colors"

                      title="Delete Option"

                    >

                      <Trash2 className="w-3.5 h-3.5" />

                    </button>

                  </div>

                ))}

              </div>

            </div>



            {/* Footer */}

            <div className="px-5 py-3 border-t border-border flex justify-end bg-muted/20">

              <button

                onClick={() => setIsMastersOpen(false)}

                className="px-4 py-1.5 bg-primary text-white text-xs font-bold rounded-lg hover:opacity-95"

              >

                Close

              </button>

            </div>

          </div>

        </div>

      )}

    </div>

  );

}

