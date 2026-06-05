import React, { useState, useMemo, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "@/store/index";
import { 
  addSegment, updateSegment, deleteSegment, 
  duplicateSegment, archiveSegment, addSharedFilter,
  Segment, SharedFilter, CriteriaGroup, FilterRow 
} from "@/store/slices/segmentSlice";
import { 
  Users, Plus, Search, Filter, Trash2, Edit, Copy, Archive, 
  ChevronRight, BarChart3, X, HelpCircle, Save, Check, Settings, Eye, Sliders 
} from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { employees } from "../../../../components/employees/mockData";
import { toast } from "sonner";

// Predefined Filter Masters
const PREDEFINED_QUICK_FILTERS = [
  "All Employees",
  "Above 5 years",
  "All Current Employees",
  "All Past Employees",
  "Bangalore Employees",
  "Between 3 – 5 years",
  "Confirmed Employees",
  "Contract Emp",
  "Partially Vaccinated Employees",
  "Probation Emp",
  "Sales Department",
  "Trainee Employees",
  "Upto 3 years service"
];

// Custom fields list from prompt
const CUSTOM_FIELDS = [
  "Residential Status", "Title", "Manager Email Id", "Date Of Birth", "Birthday", "Years In Service Range",
  "Age Range", "Employee Personal Email", "Marriage Date", "Spouse Name", "Previous Employee No",
  "Has Blocked Record Status?", "Nick Name", "Employee Name", "Employee Number", "Remarks About Employee",
  "Joined On", "Employee Document", "Family PF Number", "Employee Birthplace", "Employee Relation",
  "Background Verification Status", "Employee Timeline", "PF Number", "ESI Number", "Manager Employee No",
  "Last Logged In On", "Phone", "Allowed IP For Login", "First Hire Date", "Employee Reference Number",
  "UAN", "PF KYC Status", "Login User Name", "Background Verification Completed On", "Background Verified Agency Name",
  "Background Verification Remarks", "Extension", "Has ESS Login?", "EPF Excess Contribution", "Blood Group",
  "If PF KYC Done", "If EPS Member", "Initials", "Employee Middle Name", "Employee Last Name", "PAN Number",
  "Managers Manager Employee No", "Retirement Date", "Managers Manager Name", "Emergency Contact Name",
  "Employee First Name", "Onboarding Status", "Mother's Name", "Country Of Origin", "Religion", "Is Director?",
  "Allow Excess PF", "Allow Excess EPS", "Has Left The Organization?", "Is PF Eligible", "Is ESI Eligible",
  "Is International Employee?", "Marital Status", "Nationality", "Disability Type", "Email", "PF Join Date",
  "PF Linked Date", "Employee Role", "Actual Birthday", "Reporting To", "Employee Age", "PRAN Number",
  "Emergency Contact Number", "Manager Employee Name", "Father's Name", "Mode of Employee Onboarding",
  "Gender", "PAN Status", "Height", "Weight", "Identification Mark", "Background Verification Indicator",
  "Gender Code", "Wish DOB", "Hobby", "Caste", "Employment Status", "Is LWF Eligible", "Excluded for payroll processing?",
  "EPS Excess Contribution", "Is Photo Available", "Years In Service", "Is physically challenged?",
  "Years In Service (year / month)"
];

const CATEGORIES = [
  "Basic Information",
  "Designation",
  "Department",
  "Grade",
  "Location",
  "Attendance Scheme"
];

const OPERATORS = [
  "EQUAL TO", "NOT EQUAL TO", "GREATER THAN", "LESS THAN",
  "IN", "NOT IN", "BETWEEN", "LIKE", "NOT LIKE",
  "IS NULL", "IS NOT NULL"
];

export function EmployeeSegmentPage() {
  const dispatch = useDispatch();
  const segments = useSelector((state: RootState) => state.segment.segments);

  const [search, setSearch] = useState("");
  const [sourceFilter, setSourceFilter] = useState("All");

  // Editor Modal States
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [editingSegment, setEditingSegment] = useState<Segment | null>(null);

  // View employees modal
  const [viewingSegment, setViewingSegment] = useState<Segment | null>(null);

  const handleCreate = () => {
    setEditingSegment(null);
    setIsEditorOpen(true);
  };

  const handleEdit = (seg: Segment) => {
    setEditingSegment(seg);
    setIsEditorOpen(true);
  };

  const handleDelete = (id: string, name: string) => {
    if (window.confirm(`Are you sure you want to delete segment "${name}"?`)) {
      dispatch(deleteSegment(id));
      toast.success("Segment deleted successfully");
    }
  };

  const handleDuplicate = (id: string) => {
    dispatch(duplicateSegment(id));
    toast.success("Segment duplicated successfully");
  };

  const handleArchive = (id: string, isArchived: boolean) => {
    dispatch(archiveSegment(id));
    toast.success(isArchived ? "Segment restored" : "Segment archived");
  };

  // Filter & Search segments
  const filteredSegments = segments.filter(seg => {
    const matchesSearch = seg.name.toLowerCase().includes(search.toLowerCase()) ||
                          seg.createdBy.toLowerCase().includes(search.toLowerCase());
    const matchesSource = sourceFilter === "All" || seg.source === sourceFilter;
    return matchesSearch && matchesSource;
  });

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-300">
      
      {/* Title Header */}
      <div className="flex justify-end bg-card/40 border border-border/50 p-6 rounded-[24px]">
  <Button
    onClick={handleCreate}
    className="h-10 px-5 rounded-xl !bg-violet-600 !text-white text-[10px] font-black uppercase tracking-widest gap-2 !hover:bg-violet-700 !hover:text-white transition-all shadow-md"
  >
    <Plus size={14} strokeWidth={3} />
    Create Segment
  </Button>
</div>

      {/* Filters Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2 border-t border-border/50">
        <div className="relative flex-1 max-w-sm">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Search segments..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 text-xs font-semibold bg-card border border-border rounded-xl focus:border-foreground/30 outline-none transition-all"
          />
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Source:</span>
          <select
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            className="text-xs font-bold uppercase py-1.5 px-3 border border-border bg-card rounded-xl outline-none cursor-pointer"
          >
            <option value="All">All Sources</option>
            <option value="Based on employee filter criteria">Criteria Based</option>
            <option value="Manual, ad hoc list of employees">Manual list</option>
          </select>
        </div>
      </div>

      {/* Grid List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredSegments.map(seg => (
          <div 
            key={seg.id} 
            className={`bg-card border rounded-[24px] p-6 hover:shadow-xl hover:border-foreground/20 transition-all duration-350 flex flex-col justify-between relative overflow-hidden group ${
              seg.isArchived ? "opacity-60 border-dashed border-border" : "border-border"
            }`}
          >
            {/* Count Badge */}
            <div className="absolute top-6 right-6">
              <div className="w-12 h-12 rounded-2xl bg-secondary/80 flex flex-col items-center justify-center border border-border/50 shadow-inner">
                <span className="text-sm font-black text-foreground leading-none">{seg.totalEmployees}</span>
                <span className="text-[7px] text-muted-foreground font-bold uppercase mt-0.5">Staff</span>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-1 pr-14">
                <h4 className="text-xs font-black text-foreground uppercase tracking-tight flex items-center gap-1.5">
                  {seg.name}
                  {seg.isArchived && <span className="text-[7px] bg-red-100 text-red-600 border border-red-200 px-1.5 py-0.2 rounded-full uppercase font-black">Archived</span>}
                </h4>
                <p className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest">
                  By {seg.createdBy} · {seg.createdDate}
                </p>
              </div>

              {/* Badges / description */}
              <div className="space-y-1.5 pt-2 border-t border-border/40">
                <p className="text-[8px] font-black text-muted-foreground uppercase tracking-widest">Source Mode</p>
                <p className="text-[10px] font-semibold text-foreground truncate">{seg.source}</p>
              </div>

              {seg.quickFilters && seg.quickFilters.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {seg.quickFilters.map(f => (
                    <span key={f} className="text-[8px] font-bold bg-secondary px-2 py-0.5 rounded-full border border-border/50 text-muted-foreground">{f}</span>
                  ))}
                </div>
              )}
            </div>

            {/* Actions Bar */}
            <div className="mt-8 pt-4 border-t border-border/45 flex items-center justify-between">
              <button 
                onClick={() => setViewingSegment(seg)}
                className="text-[10px] font-black text-primary uppercase tracking-widest hover:underline flex items-center gap-1"
              >
                View Employees
                <ChevronRight size={12} />
              </button>

              <div className="flex items-center gap-1">
                <button 
                  onClick={() => handleEdit(seg)}
                  className="w-8 h-8 rounded-lg border border-border flex items-center justify-center text-muted-foreground hover:bg-secondary hover:text-foreground transition-all"
                  title="Edit segment rules"
                >
                  <Edit size={13} />
                </button>
                <button 
                  onClick={() => handleDuplicate(seg.id)}
                  className="w-8 h-8 rounded-lg border border-border flex items-center justify-center text-muted-foreground hover:bg-secondary hover:text-foreground transition-all"
                  title="Duplicate segment"
                >
                  <Copy size={13} />
                </button>
                <button 
                  onClick={() => handleArchive(seg.id, !!seg.isArchived)}
                  className={`w-8 h-8 rounded-lg border flex items-center justify-center transition-all ${
                    seg.isArchived ? "bg-amber-50 text-amber-500 border-amber-200" : "border-border text-muted-foreground hover:bg-secondary"
                  }`}
                  title={seg.isArchived ? "Restore segment" : "Archive segment"}
                >
                  <Archive size={13} />
                </button>
                <button 
                  onClick={() => handleDelete(seg.id, seg.name)}
                  className="w-8 h-8 rounded-lg border border-border flex items-center justify-center text-red-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 hover:border-red-100 transition-all"
                  title="Delete segment"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            </div>
          </div>
        ))}
        {filteredSegments.length === 0 && (
          <div className="col-span-full text-center py-16 border-2 border-dashed border-border rounded-[32px] bg-secondary/5">
            <Users className="w-10 h-10 text-muted-foreground/30 mx-auto mb-3" />
            <p className="text-xs font-bold text-muted-foreground">No segments found matching the criteria.</p>
          </div>
        )}
      </div>

      {/* SEGMENT CREATOR / EDITOR MODAL */}
      <SegmentEditorModal 
        isOpen={isEditorOpen}
        onClose={() => setIsEditorOpen(false)}
        editingSegment={editingSegment}
      />

      {/* VIEW EMPLOYEES POPUP */}
      <ViewEmployeesModal 
        segment={viewingSegment}
        onClose={() => setViewingSegment(null)}
      />

    </div>
  );
}

/* SEGMENT CREATOR / EDITOR MODAL */
interface SegmentEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  editingSegment: Segment | null;
}

function SegmentEditorModal({ isOpen, onClose, editingSegment }: SegmentEditorModalProps) {
  const dispatch = useDispatch();

  const [title, setTitle] = useState("");
  const [source, setSource] = useState<'Based on employee filter criteria' | 'Manual, ad hoc list of employees'>('Based on employee filter criteria');
  const [manualEmployees, setManualEmployees] = useState<string[]>([]);
  const [criteriaGroups, setCriteriaGroups] = useState<CriteriaGroup[]>([]);
  const [quickFilters, setQuickFilters] = useState<string[]>([]);

  // Search employee search inside manual selection
  const [empSearch, setEmpSearch] = useState("");

  // Filter Builder popup state
  const [isBuilderOpen, setIsBuilderOpen] = useState(false);

  useEffect(() => {
    if (isOpen) {
      if (editingSegment) {
        setTitle(editingSegment.name);
        setSource(editingSegment.source);
        setManualEmployees(editingSegment.employeeIds || []);
        setCriteriaGroups(editingSegment.criteriaGroups || []);
        setQuickFilters(editingSegment.quickFilters || []);
      } else {
        setTitle("");
        setSource('Based on employee filter criteria');
        setManualEmployees([]);
        setCriteriaGroups([]);
        setQuickFilters([]);
      }
    }
  }, [isOpen, editingSegment]);

  const filteredEmployeesList = useMemo(() => {
    return employees.filter(emp => 
      emp.name.toLowerCase().includes(empSearch.toLowerCase()) || 
      emp.employeeId.toLowerCase().includes(empSearch.toLowerCase()) ||
      emp.department.toLowerCase().includes(empSearch.toLowerCase())
    );
  }, [empSearch]);

  // Live Count Calculator (Simulated dynamically)
  const computedCount = useMemo(() => {
    if (source === 'Manual, ad hoc list of employees') {
      return manualEmployees.length;
    }
    
    // Simulate count based on quick filters and custom rules
    let baseCount = employees.length;

    // Apply quick filters simulation
    quickFilters.forEach(qf => {
      if (qf === "Above 5 years") baseCount = Math.floor(baseCount * 0.4);
      if (qf === "Probation Emp") baseCount = Math.floor(baseCount * 0.15);
      if (qf === "Sales Department") baseCount = Math.floor(baseCount * 0.25);
      if (qf === "Bangalore Employees") baseCount = Math.floor(baseCount * 0.5);
    });

    // Apply custom criteria rules simulation
    criteriaGroups.forEach(grp => {
      grp.rows.forEach(row => {
        if (row.field && row.value) {
          baseCount = Math.max(2, Math.floor(baseCount * 0.7));
        }
      });
    });

    return Math.min(employees.length, Math.max(0, baseCount));
  }, [source, manualEmployees, quickFilters, criteriaGroups]);

  if (!isOpen) return null;

  const handleToggleManualEmp = (id: string) => {
    setManualEmployees(prev => 
      prev.includes(id) ? prev.filter(e => e !== id) : [...prev, id]
    );
  };

  const handleSave = () => {
    if (!title.trim()) {
      toast.error("Segment Title is required");
      return;
    }

    const payload: Segment = {
      id: editingSegment?.id || `seg-${Date.now()}`,
      name: title.trim(),
      createdBy: editingSegment?.createdBy || "admin",
      createdDate: editingSegment?.createdDate || new Date().toISOString().split('T')[0],
      totalEmployees: computedCount,
      source,
      employeeIds: source === 'Manual, ad hoc list of employees' ? manualEmployees : [],
      criteriaGroups: source === 'Based on employee filter criteria' ? criteriaGroups : [],
      quickFilters: source === 'Based on employee filter criteria' ? quickFilters : []
    };

    if (editingSegment) {
      dispatch(updateSegment(payload));
      toast.success("Segment updated successfully");
    } else {
      dispatch(addSegment(payload));
      toast.success("Segment created successfully");
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-card w-full max-w-3xl max-h-[92vh] rounded-[32px] border border-border shadow-2xl flex flex-col overflow-hidden text-foreground">
        
        {/* Header */}
        <div className="px-8 py-5 border-b border-border flex items-center justify-between bg-secondary/10">
          <div>
            <h3 className="text-sm font-black uppercase tracking-tight">
              {editingSegment ? "Edit Employee Segment" : "Create Employee Segment"}
            </h3>
            <p className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">Configure target segment rules</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full border border-border flex items-center justify-center hover:bg-secondary transition-all">
            <X size={15} />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-8 space-y-6 no-scrollbar">
          
          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Segment Title *</label>
              <input 
                type="text" 
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Bangalore Sales Executives"
                className="flat-input h-10 w-full text-xs px-3 border border-border bg-card rounded-xl outline-none"
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Segment Source</label>
              <select
                value={source}
                onChange={(e) => setSource(e.target.value as any)}
                className="flat-input h-10 w-full text-xs px-3 border border-border bg-card rounded-xl outline-none cursor-pointer"
              >
                <option value="Based on employee filter criteria">Based on employee filter criteria</option>
                <option value="Manual, ad hoc list of employees">Manual, ad hoc list of employees</option>
              </select>
            </div>
          </div>

          {/* Dynamic Sections based on Source Selection */}
          {source === 'Based on employee filter criteria' ? (
            <div className="space-y-6 animate-in fade-in duration-300">
               
               <div className="flex items-center justify-between p-5 border border-border rounded-2xl bg-secondary/5">
                 <div>
                   <h4 className="text-xs font-black uppercase tracking-tight">Segment Rule Builder</h4>
                   <p className="text-[10px] text-muted-foreground font-semibold">Apply custom filter parameters, groups, and logic expressions.</p>
                 </div>
                 <Button 
                   onClick={() => setIsBuilderOpen(true)}
                   className="h-9 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest gap-1.5 bg-foreground text-primary-foreground hover:bg-foreground/90 shadow-sm"
                 >
                   <Sliders size={13} /> Add / Edit Filters
                 </Button>
               </div>

               {/* Applied Rules Summary */}
               {(quickFilters.length > 0 || criteriaGroups.length > 0) && (
                 <div className="border border-border rounded-2xl p-5 space-y-4">
                   <p className="text-[9px] font-black text-muted-foreground uppercase tracking-widest border-b border-border pb-1.5">Applied Criteria</p>
                   
                   {quickFilters.length > 0 && (
                     <div className="space-y-1">
                       <span className="text-[9px] font-black text-muted-foreground uppercase">Quick Filters:</span>
                       <div className="flex flex-wrap gap-1.5">
                         {quickFilters.map(qf => (
                           <span key={qf} className="text-[9px] font-bold text-foreground bg-secondary px-2.5 py-0.5 rounded-full border border-border/60">
                             {qf}
                           </span>
                         ))}
                       </div>
                     </div>
                   )}

                   {criteriaGroups.length > 0 && (
                     <div className="space-y-2 pt-2 border-t border-border/30">
                       <span className="text-[9px] font-black text-muted-foreground uppercase block">Custom Criteria:</span>
                       {criteriaGroups.map((grp, i) => (
                         <div key={grp.id} className="p-3 bg-secondary/15 rounded-xl border border-border/80 text-[11px] space-y-1.5">
                           <div className="flex items-center justify-between text-[9px] font-black uppercase tracking-widest text-primary">
                             <span>Group {i + 1} ({grp.conjunction})</span>
                           </div>
                           <div className="space-y-1">
                             {grp.rows.map(row => (
                               <div key={row.id} className="flex items-center gap-1.5 text-muted-foreground">
                                 <span className="font-bold text-foreground uppercase">{row.field || "?"}</span>
                                 <span className="font-mono text-[9px] bg-secondary/80 px-1 rounded">{row.operator}</span>
                                 <span className="font-bold text-foreground">"{row.value || "?"}"</span>
                               </div>
                             ))}
                           </div>
                         </div>
                       ))}
                     </div>
                   )}
                 </div>
               )}
            </div>
          ) : (
            /* Manual Selection UI */
            <div className="space-y-4 animate-in fade-in duration-300">
              <div className="flex items-center justify-between">
                <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Select Employees Manually</label>
                <span className="text-[9px] font-black text-primary uppercase">({manualEmployees.length} Selected)</span>
              </div>
              
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <input 
                  type="text" 
                  placeholder="Search employees by name, number, or department..."
                  value={empSearch}
                  onChange={(e) => setEmpSearch(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 text-xs font-semibold bg-card border border-border rounded-xl focus:border-foreground/30 outline-none"
                />
              </div>

              <div className="border border-border rounded-2xl overflow-hidden max-h-[220px] overflow-y-auto bg-card shadow-inner divide-y divide-border">
                {filteredEmployeesList.map(emp => {
                  const isChecked = manualEmployees.includes(emp.id);
                  return (
                    <div 
                      key={emp.id}
                      onClick={() => handleToggleManualEmp(emp.id)}
                      className={`flex items-center justify-between py-2 px-4 cursor-pointer hover:bg-secondary/15 transition-colors ${
                        isChecked ? "bg-primary/5" : ""
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <input 
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => {}} // click on parent handles toggle
                          className="rounded border-border focus:ring-0 w-3.5 h-3.5"
                        />
                        <div>
                          <span className="text-xs font-bold text-foreground block">{emp.name}</span>
                          <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">
                            {emp.employeeId} · {emp.department}
                          </span>
                        </div>
                      </div>
                      <span className="text-[10px] text-muted-foreground font-semibold">{emp.location || "Bangalore"}</span>
                    </div>
                  );
                })}
                {filteredEmployeesList.length === 0 && (
                  <p className="text-xs text-muted-foreground text-center py-6">No matching employees found.</p>
                )}
              </div>
            </div>
          )}

          {/* Dynamic employee count preview box */}
          <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-[20px] flex items-center justify-between shadow-sm">
            <div className="space-y-0.5">
              <p className="text-[9px] font-black text-emerald-600 uppercase tracking-widest">Live Employee Count Preview</p>
              <p className="text-2xl font-black text-emerald-600 tracking-tight">{computedCount} Staff Members</p>
            </div>
            <BarChart3 className="w-8 h-8 text-emerald-600/35" />
          </div>

        </div>

        {/* Footer */}
        <div className="px-8 py-5 border-t border-border bg-secondary/15 flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={onClose} className="h-10 px-5 rounded-xl text-[10px] font-black uppercase tracking-widest">
            Cancel
          </Button>
          <Button type="button" onClick={handleSave} className="h-10 px-6 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest hover:bg-foreground/90">
            Save Segment
          </Button>
        </div>

      </div>

      {/* FILTER BUILDER MODAL POPUP */}
      <FilterBuilderModal 
        isOpen={isBuilderOpen}
        onClose={() => setIsBuilderOpen(false)}
        quickFilters={quickFilters}
        setQuickFilters={setQuickFilters}
        criteriaGroups={criteriaGroups}
        setCriteriaGroups={setCriteriaGroups}
        computedCount={computedCount}
      />

    </div>
  );
}

/* FILTER BUILDER POPUP (Add New Filter - Popup) */
interface FilterBuilderModalProps {
  isOpen: boolean;
  onClose: () => void;
  quickFilters: string[];
  setQuickFilters: (q: string[]) => void;
  criteriaGroups: CriteriaGroup[];
  setCriteriaGroups: (c: CriteriaGroup[]) => void;
  computedCount: number;
}

function FilterBuilderModal({ 
  isOpen, onClose, 
  quickFilters, setQuickFilters, 
  criteriaGroups, setCriteriaGroups,
  computedCount
}: FilterBuilderModalProps) {
  const dispatch = useDispatch();

  // Tab: 'quick' | 'custom'
  const [activeTab, setActiveTab] = useState<'quick' | 'custom'>('quick');

  const [filterTitle, setFilterTitle] = useState("");
  const [sharedFilter, setSharedFilter] = useState(false);

  // Custom Category selected
  const [categoryType, setCategoryType] = useState("Basic Information");
  const [searchField, setSearchField] = useState("");

  // Local state replicas
  const [localQuickFilters, setLocalQuickFilters] = useState<string[]>([]);
  const [localGroups, setLocalGroups] = useState<CriteriaGroup[]>([]);

  useEffect(() => {
    if (isOpen) {
      setLocalQuickFilters(quickFilters);
      setLocalGroups(criteriaGroups.length > 0 ? criteriaGroups : [{ id: 'g-1', conjunction: 'AND', rows: [] }]);
      setFilterTitle("");
      setSharedFilter(false);
    }
  }, [isOpen, quickFilters, criteriaGroups]);

  // Search fields
  const filteredCustomFields = useMemo(() => {
    return CUSTOM_FIELDS.filter(f => f.toLowerCase().includes(searchField.toLowerCase()));
  }, [searchField]);

  if (!isOpen) return null;

  const handleToggleQuick = (f: string) => {
    setLocalQuickFilters(prev => 
      prev.includes(f) ? prev.filter(item => item !== f) : [...prev, f]
    );
  };

  const handleApply = () => {
    setQuickFilters(localQuickFilters);
    // filter empty rows/groups
    const cleanedGroups = localGroups.map(grp => ({
      ...grp,
      rows: grp.rows.filter(r => r.field && r.value)
    })).filter(grp => grp.rows.length > 0);
    
    setCriteriaGroups(cleanedGroups);

    if (sharedFilter && filterTitle.trim()) {
      // Save globally
      dispatch(addSharedFilter({
        id: `sf-${Date.now()}`,
        title: filterTitle.trim(),
        criteriaGroups: cleanedGroups,
        quickFilters: localQuickFilters
      }));
      toast.success(`Filter "${filterTitle}" saved as Shared Filter`);
    }

    onClose();
  };

  const handleAddGroup = () => {
    setLocalGroups(prev => [
      ...prev,
      { id: `g-${Date.now()}`, conjunction: 'AND', rows: [] }
    ]);
  };

  const handleRemoveGroup = (gid: string) => {
    setLocalGroups(prev => prev.filter(g => g.id !== gid));
  };

  const handleAddRow = (gid: string) => {
    setLocalGroups(prev => prev.map(g => {
      if (g.id === gid) {
        return {
          ...g,
          rows: [...g.rows, { id: `r-${Date.now()}`, field: CUSTOM_FIELDS[0], operator: OPERATORS[0], value: "" }]
        };
      }
      return g;
    }));
  };

  const handleRemoveRow = (gid: string, rid: string) => {
    setLocalGroups(prev => prev.map(g => {
      if (g.id === gid) {
        return {
          ...g,
          rows: g.rows.filter(r => r.id !== rid)
        };
      }
      return g;
    }));
  };

  const handleUpdateRow = (gid: string, rid: string, key: keyof FilterRow, val: string) => {
    setLocalGroups(prev => prev.map(g => {
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
    setLocalGroups(prev => prev.map(g => {
      if (g.id === gid) {
        return { ...g, conjunction: conj };
      }
      return g;
    }));
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-card w-full max-w-2xl max-h-[85vh] rounded-[24px] border border-border shadow-2xl flex flex-col overflow-hidden text-foreground">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-border bg-secondary/10 flex items-center justify-between">
          <div>
            <h4 className="text-xs font-black uppercase tracking-tight">Add New Filter Criteria</h4>
            <p className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">Customize query logic parameters</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full border border-border flex items-center justify-center hover:bg-secondary">
            <X size={15} />
          </button>
        </div>

        {/* Form elements */}
        <div className="px-6 py-3 border-b border-border bg-secondary/5 grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1">
            <span className="text-[8px] font-black text-muted-foreground uppercase">Filter Name</span>
            <input 
              type="text" 
              placeholder="e.g. Bangalore Sales Staff Filter"
              value={filterTitle}
              onChange={(e) => setFilterTitle(e.target.value)}
              className="flat-input h-8 w-full text-xs px-2 border border-border bg-card rounded-lg"
            />
          </div>
          <div className="flex items-center gap-2 pt-4">
            <input 
              type="checkbox"
              id="shared-filter"
              checked={sharedFilter}
              onChange={(e) => setSharedFilter(e.target.checked)}
              className="rounded border-border focus:ring-0 w-3.5 h-3.5 cursor-pointer"
            />
            <label htmlFor="shared-filter" className="text-xs font-bold text-foreground cursor-pointer select-none">
              Save shared filter globally for reuse
            </label>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-border/60 px-6 pt-2 bg-secondary/5 gap-4">
          <button 
            onClick={() => setActiveTab('quick')}
            className={`pb-2 text-[10px] font-black uppercase tracking-widest border-b-2 px-1 ${
              activeTab === 'quick' ? "border-foreground text-foreground" : "border-transparent text-muted-foreground"
            }`}
          >
            Quick Predefined Filters
          </button>
          <button 
            onClick={() => setActiveTab('custom')}
            className={`pb-2 text-[10px] font-black uppercase tracking-widest border-b-2 px-1 ${
              activeTab === 'custom' ? "border-foreground text-foreground" : "border-transparent text-muted-foreground"
            }`}
          >
            Custom Rule Builder
          </button>
        </div>

        {/* Popup Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 no-scrollbar">
          
          {activeTab === 'quick' ? (
            /* Quick Filter list view */
            <div className="space-y-3">
              <p className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">Select target employee categories</p>
              <div className="flex flex-wrap gap-2">
                {PREDEFINED_QUICK_FILTERS.map(f => {
                  const isSel = localQuickFilters.includes(f);
                  return (
                    <button
                      key={f}
                      onClick={() => handleToggleQuick(f)}
                      className={`px-3 py-1.5 rounded-xl text-[9px] font-bold uppercase tracking-wider border transition-all ${
                        isSel 
                          ? "bg-foreground text-primary-foreground border-foreground shadow-sm font-black" 
                          : "bg-card border-border text-muted-foreground hover:border-muted-foreground/35"
                      }`}
                    >
                      {f}
                    </button>
                  );
                })}
              </div>
            </div>
          ) : (
            /* Custom Filter Builder view */
            <div className="space-y-6">
              
              <div className="flex items-center justify-between gap-4 p-4 border border-border rounded-xl bg-secondary/5">
                <div className="flex items-center gap-2">
                  <span className="text-[9px] font-black text-muted-foreground uppercase">Category Type:</span>
                  <select 
                    value={categoryType}
                    onChange={(e) => setCategoryType(e.target.value)}
                    className="text-xs font-bold uppercase py-1 px-3 border border-border bg-card rounded-lg outline-none cursor-pointer"
                  >
                    {CATEGORIES.map(cat => <option key={cat}>{cat}</option>)}
                  </select>
                </div>
                <button 
                  onClick={handleAddGroup}
                  className="text-[9px] font-black text-primary uppercase hover:underline"
                >
                  + Add Logic Group
                </button>
              </div>

              {/* Nested groups */}
              <div className="space-y-4">
                {localGroups.map((grp, gidx) => (
                  <div key={grp.id} className="p-5 border border-border rounded-[20px] bg-card space-y-4 relative shadow-sm">
                    
                    <button 
                      onClick={() => handleRemoveGroup(grp.id)}
                      className="absolute top-4 right-4 text-muted-foreground hover:text-red-500 transition-colors"
                    >
                      <Trash2 size={13} />
                    </button>

                    <div className="flex items-center gap-4">
                      <span className="text-[9px] font-black uppercase tracking-wider text-muted-foreground">Logical Conjunction</span>
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
                        + Add Rule
                      </button>
                    </div>

                    <div className="space-y-2">
                      {grp.rows.map((row, ridx) => (
                        <div key={row.id} className="grid grid-cols-1 sm:grid-cols-12 gap-2 items-center bg-secondary/10 p-2.5 rounded-lg border border-border/45">
                          
                          {/* Searchable Fields list */}
                          <div className="sm:col-span-4">
                            <select
                              value={row.field}
                              onChange={(e) => handleUpdateRow(grp.id, row.id, 'field', e.target.value)}
                              className="w-full text-xs font-semibold py-1 px-2 border border-border rounded bg-card"
                            >
                              {CUSTOM_FIELDS.map(f => <option key={f} value={f}>{f}</option>)}
                            </select>
                          </div>

                          {/* Operator */}
                          <div className="sm:col-span-3">
                            <select
                              value={row.operator}
                              onChange={(e) => handleUpdateRow(grp.id, row.id, 'operator', e.target.value)}
                              className="w-full text-xs font-mono py-1 px-2 border border-border rounded bg-card"
                            >
                              {OPERATORS.map(op => <option key={op} value={op}>{op}</option>)}
                            </select>
                          </div>

                          {/* Value */}
                          <div className="sm:col-span-4">
                            <input 
                              type="text"
                              value={row.value}
                              onChange={(e) => handleUpdateRow(grp.id, row.id, 'value', e.target.value)}
                              placeholder="Type filter value..."
                              className="w-full text-xs font-semibold py-1 px-2 border border-border rounded bg-card outline-none"
                            />
                          </div>

                          {/* Delete Row button */}
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
                        <p className="text-[10px] text-muted-foreground italic">No filters added in this group yet. Click "+ Add Rule" to start.</p>
                      )}
                    </div>

                  </div>
                ))}
              </div>

            </div>
          )}

        </div>

        {/* Footer popup */}
        <div className="px-6 py-4 border-t border-border bg-secondary/10 flex items-center justify-between">
          <div className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">
            Count Preview: <span className="font-black text-foreground">{computedCount} Matches</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={onClose} className="h-9 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest">
              Cancel
            </Button>
            <Button onClick={handleApply} className="h-9 px-4 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest hover:bg-foreground/90">
              Apply Changes
            </Button>
          </div>
        </div>

      </div>
    </div>
  );
}

/* VIEW EMPLOYEES MODAL */
interface ViewEmployeesModalProps {
  segment: Segment | null;
  onClose: () => void;
}

function ViewEmployeesModal({ segment, onClose }: ViewEmployeesModalProps) {
  if (!segment) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-card w-full max-w-xl max-h-[80vh] rounded-[24px] border border-border shadow-2xl flex flex-col overflow-hidden text-foreground">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-border flex items-center justify-between bg-secondary/15">
          <div>
            <h4 className="text-xs font-black uppercase tracking-tight">{segment.name}</h4>
            <p className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">Staff Segment Members</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full border border-border flex items-center justify-center hover:bg-secondary">
            <X size={15} />
          </button>
        </div>

        {/* Body list of matching employees */}
        <div className="flex-1 overflow-y-auto p-6 divide-y divide-border/60 no-scrollbar">
          {employees.slice(0, segment.totalEmployees).map(emp => (
            <div key={emp.id} className="py-2.5 flex justify-between items-center">
              <div>
                <span className="text-xs font-bold text-foreground block">{emp.name}</span>
                <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">
                  {emp.employeeId} · {emp.department}
                </span>
              </div>
              <span className="text-[10px] font-bold text-foreground bg-secondary px-2.5 py-1 rounded-full border border-border/80">
                {emp.designation}
              </span>
            </div>
          ))}
          {segment.totalEmployees === 0 && (
            <p className="text-xs text-muted-foreground text-center py-8">No employees currently in this segment.</p>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-border bg-secondary/15 flex justify-end">
          <Button variant="outline" onClick={onClose} className="h-9 px-5 rounded-xl text-[10px] font-black uppercase tracking-widest">
            Close
          </Button>
        </div>

      </div>
    </div>
  );
}
