import React, { useState, useMemo } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "@/store/index";
import { 
  addFine, updateFine, deleteFine, 
  addDamage, updateDamage, deleteDamage, 
  FineRecord, DamageRecord 
} from "@/store/slices/finesDamagesSlice";
import { 
  AlertCircle, AlertTriangle, Plus, Search, Trash2, Edit3, X, Calendar, DollarSign, Check, Info, FileText 
} from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { employees } from "../../../../components/employees/mockData";
import { toast } from "sonner";

export function FinesDamagesPage() {
  const dispatch = useDispatch();
  
  // Redux lists
  const fines = useSelector((state: RootState) => state.finesDamages.fines);
  const damages = useSelector((state: RootState) => state.finesDamages.damages);

  // Tab State
  const [activeTab, setActiveTab] = useState<'fines' | 'damages'>('fines');

  // Filters State - Fines
  const [fineEmpFilter, setFineEmpFilter] = useState("All");
  const [fineRealizedFilter, setFineRealizedFilter] = useState("");
  const [fineFromDate, setFineFromDate] = useState("");
  const [fineToDate, setFineToDate] = useState("");
  const [fineSearch, setFineSearch] = useState("");

  // Filters State - Damages
  const [damageEmpFilter, setDamageEmpFilter] = useState("All");
  const [damageInstallmentsFilter, setDamageInstallmentsFilter] = useState("");

  // Edit / Add Dialog State
  const [isFineModalOpen, setIsFineModalOpen] = useState(false);
  const [isDamageModalOpen, setIsDamageModalOpen] = useState(false);
  const [editingFine, setEditingFine] = useState<FineRecord | null>(null);
  const [editingDamage, setEditingDamage] = useState<DamageRecord | null>(null);

  // Fine Form State
  const [fineEmployeeId, setFineEmployeeId] = useState("");
  const [fineDateOfOffence, setFineDateOfOffence] = useState("");
  const [fineActOmission, setFineActOmission] = useState("");
  const [fineShowedCause, setFineShowedCause] = useState<'Yes' | 'No'>('No');
  const [fineDateOfShowCause, setFineDateOfShowCause] = useState("");
  const [fineHearingAuthority, setFineHearingAuthority] = useState("");
  const [fineAmount, setFineAmount] = useState("");
  const [fineDateRealized, setFineDateRealized] = useState("");
  const [fineRemarks, setFineRemarks] = useState("");

  // Damage Form State
  const [damageEmployeeId, setDamageEmployeeId] = useState("");
  const [damageDateOfDamage, setDamageDateOfDamage] = useState("");
  const [damageParticulars, setDamageParticulars] = useState("");
  const [damageShowedCause, setDamageShowedCause] = useState<'Yes' | 'No'>('No');
  const [damageDateOfShowCause, setDamageDateOfShowCause] = useState("");
  const [damageHearingAuthority, setDamageHearingAuthority] = useState("");
  const [damageAmount, setDamageAmount] = useState("");
  const [damageInstallments, setDamageInstallments] = useState("1");
  const [damageFirstInstallmentDate, setDamageFirstInstallmentDate] = useState("");
  const [damageLastInstallmentDate, setDamageLastInstallmentDate] = useState("");
  const [damageRemarks, setDamageRemarks] = useState("");

  // Unique lists of employees who have records for filters
  const fineEmployeesWithRecords = useMemo(() => {
    const ids = Array.from(new Set(fines.map(f => f.employeeId)));
    return employees.filter(e => ids.includes(e.id));
  }, [fines]);

  const damageEmployeesWithRecords = useMemo(() => {
    const ids = Array.from(new Set(damages.map(d => d.employeeId)));
    return employees.filter(e => ids.includes(e.id));
  }, [damages]);

  // Dynamic Fines Filtering
  const filteredFines = useMemo(() => {
    return fines.filter(fine => {
      // Employee filter
      if (fineEmpFilter !== "All" && fine.employeeId !== fineEmpFilter) return false;
      
      // Fine Realized On filter
      if (fineRealizedFilter && fine.dateFineRealized !== fineRealizedFilter) return false;

      // From/To Date filter
      if (fineFromDate && fine.dateOfOffence < fineFromDate) return false;
      if (fineToDate && fine.dateOfOffence > fineToDate) return false;

      // General Search
      if (fineSearch) {
        const query = fineSearch.toLowerCase();
        const matchName = fine.employeeName.toLowerCase().includes(query);
        const matchNum = fine.employeeNumber.toLowerCase().includes(query);
        const matchAct = fine.actOmission.toLowerCase().includes(query);
        if (!matchName && !matchNum && !matchAct) return false;
      }

      return true;
    });
  }, [fines, fineEmpFilter, fineRealizedFilter, fineFromDate, fineToDate, fineSearch]);

  // Dynamic Damages Filtering
  const filteredDamages = useMemo(() => {
    return damages.filter(dmg => {
      // Employee Filter
      if (damageEmpFilter !== "All" && dmg.employeeId !== damageEmpFilter) return false;

      // Installments Filter
      if (damageInstallmentsFilter && String(dmg.installments) !== damageInstallmentsFilter) return false;

      return true;
    });
  }, [damages, damageEmpFilter, damageInstallmentsFilter]);

  // Open Fine Modal (Add Mode)
  const openAddFine = () => {
    setEditingFine(null);
    setFineEmployeeId(employees[0]?.id || "");
    setFineDateOfOffence("");
    setFineActOmission("");
    setFineShowedCause("No");
    setFineDateOfShowCause("");
    setFineHearingAuthority("");
    setFineAmount("");
    setFineDateRealized("");
    setFineRemarks("");
    setIsFineModalOpen(true);
  };

  // Open Fine Modal (Edit Mode)
  const openEditFine = (record: FineRecord) => {
    setEditingFine(record);
    setFineEmployeeId(record.employeeId);
    setFineDateOfOffence(record.dateOfOffence);
    setFineActOmission(record.actOmission);
    setFineShowedCause(record.showedCause);
    setFineDateOfShowCause(record.dateOfShowCauseNotice);
    setFineHearingAuthority(record.hearingAuthorityName);
    setFineAmount(String(record.fineAmount));
    setFineDateRealized(record.dateFineRealized);
    setFineRemarks(record.remarks);
    setIsFineModalOpen(true);
  };

  // Save Fine
  const handleSaveFine = () => {
    if (!fineEmployeeId || !fineDateOfOffence || !fineActOmission || !fineAmount) {
      toast.error("Please fill in all required fields marked with *");
      return;
    }

    const selectedEmp = employees.find(e => e.id === fineEmployeeId);
    if (!selectedEmp) return;

    const payload: FineRecord = {
      id: editingFine?.id || `fine-${Date.now()}`,
      employeeId: fineEmployeeId,
      employeeName: selectedEmp.name,
      employeeNumber: selectedEmp.employeeId,
      dateOfOffence: fineDateOfOffence,
      actOmission: fineActOmission,
      showedCause: fineShowedCause,
      dateOfShowCauseNotice: fineDateOfShowCause,
      hearingAuthorityName: fineHearingAuthority,
      fineAmount: Number(fineAmount),
      dateFineRealized: fineDateRealized,
      remarks: fineRemarks
    };

    if (editingFine) {
      dispatch(updateFine(payload));
      toast.success("Fine record updated successfully");
    } else {
      dispatch(addFine(payload));
      toast.success("Fine record added successfully");
    }
    setIsFineModalOpen(false);
  };

  // Delete Fine
  const handleDeleteFine = (id: string) => {
    if (window.confirm("Are you sure you want to delete this fine record?")) {
      dispatch(deleteFine(id));
      toast.success("Fine record deleted");
    }
  };

  // Open Damage Modal (Add Mode)
  const openAddDamage = () => {
    setEditingDamage(null);
    setDamageEmployeeId(employees[0]?.id || "");
    setDamageDateOfDamage("");
    setDamageParticulars("");
    setDamageShowedCause("No");
    setDamageDateOfShowCause("");
    setDamageHearingAuthority("");
    setDamageAmount("");
    setDamageInstallments("1");
    setDamageFirstInstallmentDate("");
    setDamageLastInstallmentDate("");
    setDamageRemarks("");
    setIsDamageModalOpen(true);
  };

  // Open Damage Modal (Edit Mode)
  const openEditDamage = (record: DamageRecord) => {
    setEditingDamage(record);
    setDamageEmployeeId(record.employeeId);
    setDamageDateOfDamage(record.dateOfDamage);
    setDamageParticulars(record.damageParticulars);
    setDamageShowedCause(record.showedCause);
    setDamageDateOfShowCause(record.dateOfShowCauseNotice);
    setDamageHearingAuthority(record.hearingAuthorityName);
    setDamageAmount(String(record.deductionAmount));
    setDamageInstallments(String(record.installments));
    setDamageFirstInstallmentDate(record.firstInstallmentDate);
    setDamageLastInstallmentDate(record.lastInstallmentDate);
    setDamageRemarks(record.remarks);
    setIsDamageModalOpen(true);
  };

  // Save Damage
  const handleSaveDamage = () => {
    if (!damageEmployeeId || !damageDateOfDamage || !damageParticulars || !damageAmount) {
      toast.error("Please fill in all required fields marked with *");
      return;
    }

    const selectedEmp = employees.find(e => e.id === damageEmployeeId);
    if (!selectedEmp) return;

    const payload: DamageRecord = {
      id: editingDamage?.id || `damage-${Date.now()}`,
      employeeId: damageEmployeeId,
      employeeName: selectedEmp.name,
      employeeNumber: selectedEmp.employeeId,
      dateOfDamage: damageDateOfDamage,
      damageParticulars: damageParticulars,
      showedCause: damageShowedCause,
      dateOfShowCauseNotice: damageDateOfShowCause,
      hearingAuthorityName: damageHearingAuthority,
      deductionAmount: Number(damageAmount),
      installments: Number(damageInstallments),
      firstInstallmentDate: damageFirstInstallmentDate,
      lastInstallmentDate: damageLastInstallmentDate,
      remarks: damageRemarks
    };

    if (editingDamage) {
      dispatch(updateDamage(payload));
      toast.success("Damage record updated successfully");
    } else {
      dispatch(addDamage(payload));
      toast.success("Damage record added successfully");
    }
    setIsDamageModalOpen(false);
  };

  // Delete Damage
  const handleDeleteDamage = (id: string) => {
    if (window.confirm("Are you sure you want to delete this damage record?")) {
      dispatch(deleteDamage(id));
      toast.success("Damage record deleted");
    }
  };

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-300">
      
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-card/40 border border-border/50 p-6 rounded-[24px]">
        <div className="space-y-1">
          <h2 className="text-xl font-black text-foreground uppercase tracking-tight flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            Fines & Damages Register
          </h2>
          <p className="text-xs text-muted-foreground font-semibold">Log disciplinary fines and company property damages with compliance approvals and deduction logs.</p>
        </div>
        <Button 
          onClick={activeTab === 'fines' ? openAddFine : openAddDamage}
          className="h-10 px-5 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest gap-2 hover:opacity-90"
        >
          <Plus size={14} strokeWidth={3} /> {activeTab === 'fines' ? 'Record Fine' : 'Record Damage'}
        </Button>
      </div>

      {/* Tabs Switcher */}
      <div className="flex border-b border-border gap-6">
        <button
          onClick={() => setActiveTab('fines')}
          className={`pb-3 text-xs font-black uppercase tracking-widest border-b-2 transition-all ${
            activeTab === 'fines' ? "border-amber-500 text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Fines Log
        </button>
        <button
          onClick={() => setActiveTab('damages')}
          className={`pb-3 text-xs font-black uppercase tracking-widest border-b-2 transition-all ${
            activeTab === 'damages' ? "border-amber-500 text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Property Damages Log
        </button>
      </div>

      {/* ACTIVE SECTION: FINES TAB */}
      {activeTab === 'fines' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          
          {/* Fines Filters */}
          <div className="bg-card border border-border rounded-[24px] p-5 shadow-sm grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4 items-end">
            <div className="space-y-1.5 col-span-1">
              <label className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">Employee</label>
              <select
                value={fineEmpFilter}
                onChange={(e) => setFineEmpFilter(e.target.value)}
                className="w-full text-xs font-semibold py-1.5 px-2.5 border border-border rounded-xl bg-card outline-none"
              >
                <option value="All">All Employees</option>
                {fineEmployeesWithRecords.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            </div>

            <div className="space-y-1.5 col-span-1">
              <label className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">Fine Realized On</label>
              <input 
                type="date"
                value={fineRealizedFilter}
                onChange={(e) => setFineRealizedFilter(e.target.value)}
                className="w-full text-xs font-semibold py-1.5 px-2.5 border border-border rounded-xl bg-card outline-none"
              />
            </div>

            <div className="space-y-1.5 col-span-1">
              <label className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">From Date</label>
              <input 
                type="date"
                value={fineFromDate}
                onChange={(e) => setFineFromDate(e.target.value)}
                className="w-full text-xs font-semibold py-1.5 px-2.5 border border-border rounded-xl bg-card outline-none"
              />
            </div>

            <div className="space-y-1.5 col-span-1">
              <label className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">To Date</label>
              <input 
                type="date"
                value={fineToDate}
                onChange={(e) => setFineToDate(e.target.value)}
                className="w-full text-xs font-semibold py-1.5 px-2.5 border border-border rounded-xl bg-card outline-none"
              />
            </div>

            <div className="space-y-1.5 col-span-1 relative">
              <label className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">Search</label>
              <div className="relative">
                <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <input 
                  type="text" 
                  value={fineSearch}
                  onChange={(e) => setFineSearch(e.target.value)}
                  placeholder="Name, Number..."
                  className="w-full pl-9 pr-3 py-1.5 text-xs font-semibold bg-card border border-border rounded-xl outline-none"
                />
              </div>
            </div>
          </div>

          {/* Fines Table */}
          <div className="bg-card border border-border rounded-[24px] overflow-hidden shadow-sm">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-secondary/15 border-b border-border/80 text-[10px] font-black uppercase tracking-wider text-muted-foreground">
                  <th className="p-4">Date of Offence</th>
                  <th className="p-4">Emp Number</th>
                  <th className="p-4">Employee Name</th>
                  <th className="p-4">Act / Omission</th>
                  <th className="p-4">Fine Amount</th>
                  <th className="p-4">Realized On</th>
                  <th className="p-4">Remarks</th>
                  <th className="p-4 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60 text-xs">
                {filteredFines.map(fine => (
                  <tr key={fine.id} className="hover:bg-secondary/5 transition-colors">
                    <td className="p-4 font-semibold text-foreground whitespace-nowrap">{fine.dateOfOffence}</td>
                    <td className="p-4 font-mono font-bold text-muted-foreground">{fine.employeeNumber}</td>
                    <td className="p-4 font-bold text-foreground">{fine.employeeName}</td>
                    <td className="p-4 max-w-[200px] truncate" title={fine.actOmission}>{fine.actOmission}</td>
                    <td className="p-4 font-black text-red-600">₹{fine.fineAmount}</td>
                    <td className="p-4 whitespace-nowrap">
                      {fine.dateFineRealized ? (
                        <span className="text-[10px] bg-emerald-50 text-emerald-700 px-2.5 py-0.5 rounded-full border border-emerald-100 font-bold">
                          {fine.dateFineRealized}
                        </span>
                      ) : (
                        <span className="text-[10px] bg-red-50 text-red-600 px-2.5 py-0.5 rounded-full border border-red-100 font-bold">
                          Pending
                        </span>
                      )}
                    </td>
                    <td className="p-4 max-w-[150px] truncate text-muted-foreground">{fine.remarks || "-"}</td>
                    <td className="p-4 flex items-center justify-center gap-1.5">
                      <button 
                        onClick={() => openEditFine(fine)}
                        className="w-7 h-7 rounded-lg border border-border hover:bg-secondary text-muted-foreground hover:text-foreground transition-all flex items-center justify-center"
                        title="Edit Fine Record"
                      >
                        <Edit3 size={11} />
                      </button>
                      <button 
                        onClick={() => handleDeleteFine(fine.id)}
                        className="w-7 h-7 rounded-lg border border-border text-red-400 hover:text-red-500 hover:bg-red-50 hover:border-red-100 transition-all flex items-center justify-center"
                        title="Delete Fine Record"
                      >
                        <Trash2 size={11} />
                      </button>
                    </td>
                  </tr>
                ))}
                {filteredFines.length === 0 && (
                  <tr>
                    <td colSpan={8} className="p-8 text-center text-muted-foreground">No fine logs found matching filters.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

        </div>
      )}

      {/* ACTIVE SECTION: DAMAGES TAB */}
      {activeTab === 'damages' && (
        <div className="space-y-6 animate-in fade-in duration-200">
          
          {/* Damages Filters */}
          <div className="bg-card border border-border rounded-[24px] p-5 shadow-sm grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 items-end max-w-2xl">
            <div className="space-y-1.5 col-span-2">
              <label className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">Employee</label>
              <select
                value={damageEmpFilter}
                onChange={(e) => setDamageEmpFilter(e.target.value)}
                className="w-full text-xs font-semibold py-1.5 px-2.5 border border-border rounded-xl bg-card outline-none"
              >
                <option value="All">All Employees</option>
                {damageEmployeesWithRecords.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            </div>

            <div className="space-y-1.5 col-span-2">
              <label className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">Installments Count</label>
              <input 
                type="number"
                placeholder="e.g. 4"
                value={damageInstallmentsFilter}
                onChange={(e) => setDamageInstallmentsFilter(e.target.value)}
                className="w-full py-1.5 px-2.5 border border-border rounded-xl bg-card text-xs outline-none"
              />
            </div>
          </div>

          {/* Damages Table */}
          <div className="bg-card border border-border rounded-[24px] overflow-hidden shadow-sm">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-secondary/15 border-b border-border/80 text-[10px] font-black uppercase tracking-wider text-muted-foreground">
                  <th className="p-4">Date of Damage</th>
                  <th className="p-4">Emp Number</th>
                  <th className="p-4">Employee Name</th>
                  <th className="p-4">Damage / Loss Particulars</th>
                  <th className="p-4">Deduction Amount</th>
                  <th className="p-4">Installments</th>
                  <th className="p-4">First Install Date</th>
                  <th className="p-4">Last Install Date</th>
                  <th className="p-4">Remarks</th>
                  <th className="p-4 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60 text-xs">
                {filteredDamages.map(dmg => (
                  <tr key={dmg.id} className="hover:bg-secondary/5 transition-colors">
                    <td className="p-4 font-semibold text-foreground whitespace-nowrap">{dmg.dateOfDamage}</td>
                    <td className="p-4 font-mono font-bold text-muted-foreground">{dmg.employeeNumber}</td>
                    <td className="p-4 font-bold text-foreground">{dmg.employeeName}</td>
                    <td className="p-4 max-w-[200px] truncate" title={dmg.damageParticulars}>{dmg.damageParticulars}</td>
                    <td className="p-4 font-black text-red-600">₹{dmg.deductionAmount}</td>
                    <td className="p-4 font-bold text-center">{dmg.installments} Parts</td>
                    <td className="p-4 whitespace-nowrap">{dmg.firstInstallmentDate || "-"}</td>
                    <td className="p-4 whitespace-nowrap">{dmg.lastInstallmentDate || "-"}</td>
                    <td className="p-4 max-w-[150px] truncate text-muted-foreground">{dmg.remarks || "-"}</td>
                    <td className="p-4 flex items-center justify-center gap-1.5">
                      <button 
                        onClick={() => openEditDamage(dmg)}
                        className="w-7 h-7 rounded-lg border border-border hover:bg-secondary text-muted-foreground hover:text-foreground transition-all flex items-center justify-center"
                        title="Edit Damage Record"
                      >
                        <Edit3 size={11} />
                      </button>
                      <button 
                        onClick={() => handleDeleteDamage(dmg.id)}
                        className="w-7 h-7 rounded-lg border border-border text-red-400 hover:text-red-500 hover:bg-red-50 hover:border-red-100 transition-all flex items-center justify-center"
                        title="Delete Damage Record"
                      >
                        <Trash2 size={11} />
                      </button>
                    </td>
                  </tr>
                ))}
                {filteredDamages.length === 0 && (
                  <tr>
                    <td colSpan={10} className="p-8 text-center text-muted-foreground">No damage logs found matching filters.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

        </div>
      )}

      {/* FINES RECORD MODAL */}
      {isFineModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-card w-full max-w-lg rounded-[24px] border border-border shadow-2xl overflow-hidden p-6 text-foreground space-y-4">
            
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h4 className="text-xs font-black uppercase tracking-tight">
                {editingFine ? "Edit Fine Record" : "Record Fine Incident"}
              </h4>
              <button onClick={() => setIsFineModalOpen(false)} className="w-8 h-8 rounded-full border border-border flex items-center justify-center hover:bg-secondary">
                <X size={13} />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              
              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Employee *</label>
                <select
                  value={fineEmployeeId}
                  onChange={(e) => setFineEmployeeId(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg outline-none cursor-pointer"
                >
                  {employees.map(e => <option key={e.id} value={e.id}>{e.name} ({e.employeeId})</option>)}
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Date of Offence *</label>
                <input 
                  type="date"
                  value={fineDateOfOffence}
                  onChange={(e) => setFineDateOfOffence(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg"
                />
              </div>

              <div className="space-y-1 sm:col-span-2">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Act / Omission Particulars *</label>
                <textarea 
                  value={fineActOmission}
                  onChange={(e) => setFineActOmission(e.target.value)}
                  rows={2}
                  placeholder="Details of infraction committed..."
                  className="w-full text-xs py-1.5 px-2.5 border border-border bg-card rounded-lg outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Workman Showed Cause</label>
                <select
                  value={fineShowedCause}
                  onChange={(e) => setFineShowedCause(e.target.value as any)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg outline-none cursor-pointer"
                >
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Date of Show Cause Notice</label>
                <input 
                  type="date"
                  value={fineDateOfShowCause}
                  disabled={fineShowedCause === 'No'}
                  onChange={(e) => setFineDateOfShowCause(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg disabled:opacity-40"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Hearing Authority Name</label>
                <input 
                  type="text"
                  placeholder="Name of presiding officer"
                  value={fineHearingAuthority}
                  disabled={fineShowedCause === 'No'}
                  onChange={(e) => setFineHearingAuthority(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg disabled:opacity-40"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Fine Amount *</label>
                <input 
                  type="number"
                  placeholder="₹"
                  value={fineAmount}
                  onChange={(e) => setFineAmount(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Date Fine Realized</label>
                <input 
                  type="date"
                  value={fineDateRealized}
                  onChange={(e) => setFineDateRealized(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg"
                />
              </div>

              <div className="space-y-1 sm:col-span-2">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Remarks</label>
                <input 
                  type="text"
                  placeholder="Additional context warnings notes..."
                  value={fineRemarks}
                  onChange={(e) => setFineRemarks(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg"
                />
              </div>

            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="outline" onClick={() => setIsFineModalOpen(false)} className="h-9 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest">
                Cancel
              </Button>
              <Button onClick={handleSaveFine} className="h-9 px-5 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest hover:opacity-90">
                Save Record
              </Button>
            </div>

          </div>
        </div>
      )}

      {/* DAMAGES RECORD MODAL */}
      {isDamageModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-card w-full max-w-lg rounded-[24px] border border-border shadow-2xl overflow-hidden p-6 text-foreground space-y-4">
            
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h4 className="text-xs font-black uppercase tracking-tight">
                {editingDamage ? "Edit Damage Log" : "Record Property Damage"}
              </h4>
              <button onClick={() => setIsDamageModalOpen(false)} className="w-8 h-8 rounded-full border border-border flex items-center justify-center hover:bg-secondary">
                <X size={13} />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              
              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Employee *</label>
                <select
                  value={damageEmployeeId}
                  onChange={(e) => setDamageEmployeeId(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg outline-none cursor-pointer"
                >
                  {employees.map(e => <option key={e.id} value={e.id}>{e.name} ({e.employeeId})</option>)}
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Date of Damage / Loss *</label>
                <input 
                  type="date"
                  value={damageDateOfDamage}
                  onChange={(e) => setDamageDateOfDamage(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg"
                />
              </div>

              <div className="space-y-1 sm:col-span-2">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Damage / Loss Particulars *</label>
                <textarea 
                  value={damageParticulars}
                  onChange={(e) => setDamageParticulars(e.target.value)}
                  rows={2}
                  placeholder="Asset description and breakage cause..."
                  className="w-full text-xs py-1.5 px-2.5 border border-border bg-card rounded-lg outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Workman Showed Cause</label>
                <select
                  value={damageShowedCause}
                  onChange={(e) => setDamageShowedCause(e.target.value as any)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg outline-none cursor-pointer"
                >
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Date of Show Cause Notice</label>
                <input 
                  type="date"
                  value={damageDateOfShowCause}
                  disabled={damageShowedCause === 'No'}
                  onChange={(e) => setDamageDateOfShowCause(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg disabled:opacity-40"
                />
              </div>

              <div className="space-y-1 text-foreground sm:col-span-2 grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[9px] font-black text-muted-foreground uppercase">Hearing Authority Name</label>
                  <input 
                    type="text"
                    placeholder="Presiding authority"
                    value={damageHearingAuthority}
                    disabled={damageShowedCause === 'No'}
                    onChange={(e) => setDamageHearingAuthority(e.target.value)}
                    className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg disabled:opacity-40"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[9px] font-black text-muted-foreground uppercase">Deduction Amount *</label>
                  <input 
                    type="number"
                    placeholder="₹"
                    value={damageAmount}
                    onChange={(e) => setDamageAmount(e.target.value)}
                    className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Number of Installments</label>
                <input 
                  type="number"
                  placeholder="e.g. 3"
                  value={damageInstallments}
                  onChange={(e) => setDamageInstallments(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">First Installment Date</label>
                <input 
                  type="date"
                  value={damageFirstInstallmentDate}
                  onChange={(e) => setDamageFirstInstallmentDate(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Last Installment Date</label>
                <input 
                  type="date"
                  value={damageLastInstallmentDate}
                  onChange={(e) => setDamageLastInstallmentDate(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg"
                />
              </div>

              <div className="space-y-1 sm:col-span-2">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Remarks</label>
                <input 
                  type="text"
                  placeholder="Recovery policy agreement details..."
                  value={damageRemarks}
                  onChange={(e) => setDamageRemarks(e.target.value)}
                  className="w-full text-xs py-1.5 px-2 border border-border bg-card rounded-lg"
                />
              </div>

            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-border">
              <Button variant="outline" onClick={() => setIsDamageModalOpen(false)} className="h-9 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest">
                Cancel
              </Button>
              <Button onClick={handleSaveDamage} className="h-9 px-5 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest hover:opacity-90">
                Save Record
              </Button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
