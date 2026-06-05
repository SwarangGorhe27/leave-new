import React, { useState, useMemo, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "@/store/index";
import { 
  addFilter, updateFilter, deleteFilter, 
  EmployeeFilter, CustomFilterGroup, CustomFilterRule, QuickFilterConfig 
} from "@/store/slices/roleFilterSlice";
import { 
  Filter, Save, Search, Download, Trash2, Edit3, ChevronRight, Share2, Plus, Star, X, Check, Sliders, Users 
} from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { employees } from "../../../../components/employees/mockData";
import { toast } from "sonner";

const QUICK_CATEGORIES = ["Designation", "Department", "Grade", "Location", "Attendance Scheme"];
const QUICK_EMPLOYEE_TYPES = ["All", "Current", "Resigned"];
const QUICK_STATUSES = ["Probation", "Confirmed", "Contract", "Trainee"];

const CUSTOM_FIELDS = [
  "Residential Status", "Years In Service", "Age", "Gender", "Marital Status", 
  "Department", "Grade", "Location", "PAN Status", "PF KYC Status", "Employee Role"
];

const OPERATORS = [
  "IN", "NOT IN", "EQUAL TO", "NOT EQUAL TO", "LIKE", "NOT LIKE", "IS NULL", "IS NOT NULL"
];

export function EmployeeFilterPage() {
  const dispatch = useDispatch();

  // State from store
  const filters = useSelector((state: RootState) => state.roleFilter.filters);

  // Search & List Filters
  const [search, setSearch] = useState("");
  const [selectedFilterId, setSelectedFilterId] = useState<string | null>(null);

  // Editor Modal States
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingFilter, setEditingFilter] = useState<EmployeeFilter | null>(null);

  // Filter creation state inside modal
  const [modalTitle, setModalTitle] = useState("");
  const [modalIsShared, setModalIsShared] = useState(false);
  const [modalTab, setModalTab] = useState<'quick' | 'custom'>('quick');
  const [modalQuickConfig, setModalQuickConfig] = useState<QuickFilterConfig>({
    categoryType: "Department",
    employeeType: "Current",
    employeeStatus: "Confirmed"
  });
  const [modalCustomGroups, setModalCustomGroups] = useState<CustomFilterGroup[]>([]);

  // Apply search filtering on listing
  const filteredFiltersList = useMemo(() => {
    return filters.filter(f => f.title.toLowerCase().includes(search.toLowerCase()));
  }, [filters, search]);

  // Execute active filter selection on employee mock data
  const matchingEmployees = useMemo(() => {
    if (!selectedFilterId) return [];
    const activeFilter = filters.find(f => f.id === selectedFilterId);
    if (!activeFilter) return [];

    if (activeFilter.type === 'quick') {
      const { employeeType, employeeStatus } = activeFilter.quickFilter;
      return employees.filter(emp => {
        // filter resigned vs current
        const isResigned = emp.status === "Terminated" || emp.status === "Suspended";
        if (employeeType === 'Current' && isResigned) return false;
        if (employeeType === 'Resigned' && !isResigned) return false;

        // filter probation, confirmed, contract, trainee
        if (employeeStatus === 'Probation' && emp.status !== 'Probation') return false;
        if (employeeStatus === 'Confirmed' && emp.status !== 'Active') return false;
        return true;
      });
    } else {
      // Custom filter execution
      let baseEmployees = [...employees];
      activeFilter.customFilterGroups.forEach(grp => {
        baseEmployees = baseEmployees.filter(emp => {
          const rowResults = grp.rows.map(row => {
            if (!row.field || !row.value) return true;
            
            let val = "";
            if (row.field === 'Location') val = emp.location || "Bangalore";
            if (row.field === 'Department') val = emp.department || "";
            if (row.field === 'Years In Service') val = String(emp.tenure || "2");
            if (row.field === 'Gender') val = emp.gender || "";
            if (row.field === 'Employee Role') val = emp.designation || "";
            
            const fieldVal = val.toLowerCase();
            const targetVal = row.value.toLowerCase();

            switch (row.operator) {
              case 'EQUAL TO': return fieldVal === targetVal;
              case 'NOT EQUAL TO': return fieldVal !== targetVal;
              case 'LIKE': return fieldVal.includes(targetVal);
              case 'NOT LIKE': return !fieldVal.includes(targetVal);
              case 'IS NULL': return !val;
              case 'IS NOT NULL': return !!val;
              default: return true;
            }
          });

          if (grp.conjunction === 'AND') {
            return rowResults.every(r => r === true);
          } else {
            return rowResults.some(r => r === true);
          }
        });
      });
      return baseEmployees;
    }
  }, [filters, selectedFilterId]);

  const handleOpenCreate = () => {
    setEditingFilter(null);
    setModalTitle("");
    setModalIsShared(false);
    setModalTab("quick");
    setModalQuickConfig({
      categoryType: "Department",
      employeeType: "Current",
      employeeStatus: "Confirmed"
    });
    setModalCustomGroups([{ id: `g-${Date.now()}`, conjunction: "AND", rows: [] }]);
    setIsEditorOpen(true);
  };

  const handleOpenEdit = (filter: EmployeeFilter) => {
    setEditingFilter(filter);
    setModalTitle(filter.title);
    setModalIsShared(filter.isShared);
    setModalTab(filter.type);
    setModalQuickConfig(filter.quickFilter);
    setModalCustomGroups(filter.customFilterGroups.length > 0 ? filter.customFilterGroups : [{ id: `g-${Date.now()}`, conjunction: "AND", rows: [] }]);
    setIsEditorOpen(true);
  };

  const handleDelete = (id: string, title: string) => {
    if (window.confirm(`Are you sure you want to delete filter "${title}"?`)) {
      dispatch(deleteFilter(id));
      if (selectedFilterId === id) setSelectedFilterId(null);
      toast.success("Filter deleted successfully");
    }
  };

  const handleSaveFilter = () => {
    if (!modalTitle.trim()) {
      toast.error("Filter Title is required");
      return;
    }

    const cleanedCustomGroups = modalCustomGroups.map(grp => ({
      ...grp,
      rows: grp.rows.filter(r => r.field && r.value)
    })).filter(grp => grp.rows.length > 0);

    const payload: EmployeeFilter = {
      id: editingFilter?.id || `f-${Date.now()}`,
      title: modalTitle.trim(),
      isShared: modalIsShared,
      type: modalTab,
      quickFilter: modalQuickConfig,
      customFilterGroups: modalTab === 'custom' ? cleanedCustomGroups : []
    };

    if (editingFilter) {
      dispatch(updateFilter(payload));
      toast.success("Filter updated successfully");
    } else {
      dispatch(addFilter(payload));
      toast.success("Filter created successfully");
    }
    setIsEditorOpen(false);
  };

  // Group builders manipulation
  const handleAddGroup = () => {
    setModalCustomGroups(prev => [
      ...prev,
      { id: `g-${Date.now()}`, conjunction: "AND", rows: [] }
    ]);
  };

  const handleRemoveGroup = (gid: string) => {
    setModalCustomGroups(prev => prev.filter(g => g.id !== gid));
  };

  const handleAddRow = (gid: string) => {
    setModalCustomGroups(prev => prev.map(g => {
      if (g.id === gid) {
        return {
          ...g,
          rows: [...g.rows, { id: `r-${Date.now()}`, field: CUSTOM_FIELDS[0], operator: OPERATORS[2], value: "" }]
        };
      }
      return g;
    }));
  };

  const handleRemoveRow = (gid: string, rid: string) => {
    setModalCustomGroups(prev => prev.map(g => {
      if (g.id === gid) {
        return { ...g, rows: g.rows.filter(r => r.id !== rid) };
      }
      return g;
    }));
  };

  const handleUpdateRow = (gid: string, rid: string, key: keyof CustomFilterRule, val: string) => {
    setModalCustomGroups(prev => prev.map(g => {
      if (g.id === gid) {
        return {
          ...g,
          rows: g.rows.map(r => r.id === rid ? { ...r, [key]: val } : r)
        };
      }
      return g;
    }));
  };

  const handleUpdateConjunction = (gid: string, conj: 'AND' | 'OR') => {
    setModalCustomGroups(prev => prev.map(g => {
      if (g.id === gid) return { ...g, conjunction: conj };
      return g;
    }));
  };

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-300">
      
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-card/40 border border-border/50 p-6 rounded-[24px]">
        {/* <div className="space-y-1">
          <h2 className="text-xl font-black text-foreground uppercase tracking-tight flex items-center gap-2">
            <Filter className="w-5 h-5 text-blue-500" />
            Custom Employee Filters
          </h2>
          <p className="text-xs text-muted-foreground font-semibold">Configure and save complex filters to map criteria to workforce segmentations dynamically.</p>
        </div> */}
        <Button 
          onClick={handleOpenCreate}
          className="h-10 px-5 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest gap-2 hover:opacity-90"
        >
          <Plus size={14} strokeWidth={3} /> Add New Filter
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Side: Filter Masters Listing */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-card border border-border rounded-[24px] p-6 shadow-sm space-y-4">
            
            <div className="flex justify-between items-center pb-2 border-b border-border/40">
              <h3 className="text-xs font-black uppercase tracking-widest text-foreground">Saved Filters</h3>
            </div>

            <div className="relative">
              <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input 
                type="text" 
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search filter name..."
                className="w-full pl-9 pr-4 py-2 text-xs font-semibold bg-card border border-border rounded-xl focus:border-foreground/30 outline-none"
              />
            </div>

            <div className="space-y-1.5 max-h-[360px] overflow-y-auto pr-1">
              {filteredFiltersList.map(item => {
                const isSelected = selectedFilterId === item.id;
                return (
                  <div 
                    key={item.id}
                    onClick={() => setSelectedFilterId(item.id)}
                    className={`flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all border ${
                      isSelected 
                        ? "bg-primary/5 border-primary/25 shadow-inner" 
                        : "bg-card border-border/50 hover:bg-secondary/15 hover:border-border"
                    }`}
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <Star size={12} className={item.isShared ? "text-amber-500 fill-current" : "text-muted-foreground"} />
                      <span className="text-xs font-black text-foreground uppercase tracking-tight truncate">{item.title}</span>
                    </div>

                    <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                      <button 
                        onClick={() => handleOpenEdit(item)}
                        className="w-7 h-7 rounded-lg border border-border hover:bg-secondary text-muted-foreground hover:text-foreground transition-all flex items-center justify-center"
                        title="Edit Filter"
                      >
                        <Edit3 size={11} />
                      </button>
                      <button 
                        onClick={() => handleDelete(item.id, item.title)}
                        className="w-7 h-7 rounded-lg border border-border text-red-400 hover:text-red-500 hover:bg-red-50 hover:border-red-100 transition-all flex items-center justify-center"
                        title="Delete Filter"
                      >
                        <Trash2 size={11} />
                      </button>
                    </div>
                  </div>
                );
              })}
              {filteredFiltersList.length === 0 && (
                <p className="text-xs text-muted-foreground text-center py-6">No saved filters found.</p>
              )}
            </div>

          </div>
        </div>

        {/* Right Side: Execution & Filter Preview results list */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-card border border-border rounded-[24px] p-6 shadow-sm min-h-[300px] flex flex-col justify-between">
            {selectedFilterId ? (
              <div className="space-y-4">
                <div className="flex justify-between items-center border-b border-border/60 pb-3">
                  <div>
                    <span className="text-[8px] font-black text-muted-foreground uppercase tracking-widest">Active Execution results</span>
                    <h3 className="text-sm font-black text-foreground uppercase tracking-tight mt-0.5">
                      {filters.find(f => f.id === selectedFilterId)?.title}
                    </h3>
                  </div>
                  <span className="text-xs font-bold text-primary bg-primary/10 px-3 py-1 rounded-full border border-primary/20">
                    {matchingEmployees.length} Matching Employees
                  </span>
                </div>

                <div className="divide-y divide-border/60 max-h-[380px] overflow-y-auto">
                  {matchingEmployees.map(emp => (
                    <div key={emp.id} className="py-3 flex justify-between items-center hover:bg-secondary/5 px-2 rounded-lg transition-colors">
                      <div>
                        <span className="text-xs font-bold text-foreground block">{emp.name}</span>
                        <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">
                          {emp.employeeId} · {emp.department}
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-xs font-semibold text-foreground block">{emp.designation}</span>
                        <span className="text-[9px] text-muted-foreground uppercase tracking-widest font-bold">
                          {emp.location || "Bangalore"}
                        </span>
                      </div>
                    </div>
                  ))}
                  {matchingEmployees.length === 0 && (
                    <p className="text-xs text-muted-foreground text-center py-8">No employees match this filter category.</p>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-20 text-center text-muted-foreground space-y-3">
                <div className="w-12 h-12 rounded-full bg-secondary flex items-center justify-center">
                  <Users className="w-6 h-6 opacity-35" />
                </div>
                <div>
                  <p className="text-xs font-bold text-foreground">Select a Saved Filter</p>
                  <p className="text-[10px] text-muted-foreground max-w-[240px] mx-auto mt-1">Select a filter configuration from the sidebar list to execute query rules and preview matches.</p>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* FILTER BUILDER / EDITOR MODAL */}
      {isEditorOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-card w-full max-w-2xl max-h-[90vh] rounded-[24px] border border-border shadow-2xl flex flex-col overflow-hidden text-foreground">
            
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-border bg-secondary/15 flex items-center justify-between">
              <div>
                <h4 className="text-xs font-black uppercase tracking-tight">
                  {editingFilter ? "Edit Employee Filter" : "Create Employee Filter"}
                </h4>
                <p className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">Configure saved logical master templates</p>
              </div>
              <button onClick={() => setIsEditorOpen(false)} className="w-8 h-8 rounded-full border border-border flex items-center justify-center hover:bg-secondary">
                <X size={15} />
              </button>
            </div>

            {/* Filter Details (Title, Shared Checkbox) */}
            <div className="px-6 py-4 bg-secondary/5 border-b border-border grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">Filter Title *</label>
                <input 
                  type="text" 
                  value={modalTitle}
                  onChange={(e) => setModalTitle(e.target.value)}
                  placeholder="e.g. Bangalore Support Trainees"
                  className="flat-input h-9 w-full text-xs px-3 border border-border bg-card rounded-lg outline-none"
                />
              </div>
              <div className="flex items-center gap-2 pt-5">
                <input 
                  type="checkbox"
                  id="modal-shared"
                  checked={modalIsShared}
                  onChange={(e) => setModalIsShared(e.target.checked)}
                  className="rounded border-border focus:ring-0 w-3.5 h-3.5"
                />
                <label htmlFor="modal-shared" className="text-xs font-bold text-foreground cursor-pointer select-none">
                  Shared Filter (Available globally to all admins)
                </label>
              </div>
            </div>

            {/* Tab switchers */}
            <div className="flex border-b border-border px-6 pt-2 bg-secondary/5 gap-4">
              <button 
                onClick={() => setModalTab('quick')}
                className={`pb-2 text-[10px] font-black uppercase tracking-widest border-b-2 px-1 ${
                  modalTab === 'quick' ? "border-foreground text-foreground font-black" : "border-transparent text-muted-foreground"
                }`}
              >
                Quick Filter Configuration
              </button>
              <button 
                onClick={() => setModalTab('custom')}
                className={`pb-2 text-[10px] font-black uppercase tracking-widest border-b-2 px-1 ${
                  modalTab === 'custom' ? "border-foreground text-foreground font-black" : "border-transparent text-muted-foreground"
                }`}
              >
                Custom logic Builder
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 no-scrollbar">
              {modalTab === 'quick' ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in duration-300">
                  <div className="space-y-1.5">
                    <label className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">Category Type</label>
                    <select
                      value={modalQuickConfig.categoryType}
                      onChange={(e) => setModalQuickConfig(prev => ({ ...prev, categoryType: e.target.value }))}
                      className="flat-input h-9 w-full text-xs px-2 border border-border bg-card rounded-lg outline-none cursor-pointer"
                    >
                      {QUICK_CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">Employee Type</label>
                    <select
                      value={modalQuickConfig.employeeType}
                      onChange={(e) => setModalQuickConfig(prev => ({ ...prev, employeeType: e.target.value as any }))}
                      className="flat-input h-9 w-full text-xs px-2 border border-border bg-card rounded-lg outline-none cursor-pointer"
                    >
                      {QUICK_EMPLOYEE_TYPES.map(e => <option key={e} value={e}>{e}</option>)}
                    </select>
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">Employee Status</label>
                    <select
                      value={modalQuickConfig.employeeStatus}
                      onChange={(e) => setModalQuickConfig(prev => ({ ...prev, employeeStatus: e.target.value as any }))}
                      className="flat-input h-9 w-full text-xs px-2 border border-border bg-card rounded-lg outline-none cursor-pointer"
                    >
                      {QUICK_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                </div>
              ) : (
                /* Custom Logic Builder */
                <div className="space-y-6 animate-in fade-in duration-300">
                  <div className="flex items-center justify-between border-b border-border/40 pb-2">
                    <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Custom Logical Rules</span>
                    <button 
                      onClick={handleAddGroup}
                      className="text-[9px] font-black text-primary uppercase hover:underline"
                    >
                      + Add logic Group
                    </button>
                  </div>

                  <div className="space-y-4">
                    {modalCustomGroups.map((grp, gidx) => (
                      <div key={grp.id} className="p-4 border border-border rounded-xl bg-card space-y-4 relative shadow-sm">
                        
                        <button 
                          onClick={() => handleRemoveGroup(grp.id)}
                          className="absolute top-4 right-4 text-muted-foreground hover:text-red-500 transition-colors"
                        >
                          <Trash2 size={13} />
                        </button>

                        <div className="flex items-center gap-3">
                          <span className="text-[9px] font-black uppercase text-muted-foreground">Logical operator</span>
                          <select
                            value={grp.conjunction}
                            onChange={(e) => handleUpdateConjunction(grp.id, e.target.value as any)}
                            className="text-[10px] font-bold py-1 px-2 border border-border rounded bg-secondary uppercase outline-none"
                          >
                            <option>AND</option>
                            <option>OR</option>
                          </select>
                          <button 
                            type="button"
                            onClick={() => handleAddRow(grp.id)}
                            className="text-[9px] font-black text-primary uppercase hover:underline"
                          >
                            + Add rule
                          </button>
                        </div>

                        <div className="space-y-2">
                          {grp.rows.map(row => (
                            <div key={row.id} className="grid grid-cols-1 sm:grid-cols-12 gap-2 items-center bg-secondary/10 p-2 rounded-lg border border-border/45">
                              
                              <div className="sm:col-span-4">
                                <select
                                  value={row.field}
                                  onChange={(e) => handleUpdateRow(grp.id, row.id, 'field', e.target.value)}
                                  className="w-full text-xs font-semibold py-1 px-2 border border-border rounded bg-card"
                                >
                                  {CUSTOM_FIELDS.map(f => <option key={f} value={f}>{f}</option>)}
                                </select>
                              </div>

                              <div className="sm:col-span-3">
                                <select
                                  value={row.operator}
                                  onChange={(e) => handleUpdateRow(grp.id, row.id, 'operator', e.target.value)}
                                  className="w-full text-xs font-mono py-1 px-2 border border-border rounded bg-card"
                                >
                                  {OPERATORS.map(op => <option key={op} value={op}>{op}</option>)}
                                </select>
                              </div>

                              <div className="sm:col-span-4">
                                <input 
                                  type="text"
                                  value={row.value}
                                  onChange={(e) => handleUpdateRow(grp.id, row.id, 'value', e.target.value)}
                                  placeholder="Rule match value..."
                                  className="w-full text-xs font-semibold py-1 px-2 border border-border rounded bg-card outline-none"
                                />
                              </div>

                              <div className="sm:col-span-1 text-right">
                                <button 
                                  type="button"
                                  onClick={() => handleRemoveRow(grp.id, row.id)}
                                  className="text-muted-foreground hover:text-red-500"
                                >
                                  <X size={12} />
                                </button>
                              </div>

                            </div>
                          ))}
                          {grp.rows.length === 0 && (
                            <p className="text-[10px] text-muted-foreground italic">No filters added in this group yet.</p>
                          )}
                        </div>

                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-border bg-secondary/15 flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsEditorOpen(false)} className="h-10 px-5 rounded-xl text-[10px] font-black uppercase tracking-widest">
                Cancel
              </Button>
              <Button onClick={handleSaveFilter} className="h-10 px-6 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest hover:opacity-90">
                Save Changes
              </Button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
