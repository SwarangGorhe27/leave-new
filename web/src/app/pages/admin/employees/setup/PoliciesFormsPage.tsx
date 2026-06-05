import React, { useState, useRef, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "@/store/index";
import { 
  addPolicy, updatePolicy, deletePolicy,
  addForm, updateForm, deleteForm,
  addPolicyCategory, deletePolicyCategory,
  addFormCategory, deleteFormCategory,
  Policy, Form, Category
} from "@/store/slices/policySlice";
import { addNotification } from "@/store/slices/notificationSlice";
import { 
  ShieldCheck, Upload, Search, File, FolderPlus, Plus,
  Trash2, Edit, Eye, Download, Info, Check, 
  X, ChevronLeft, ChevronRight, Filter, Settings, FileSpreadsheet
} from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { toast } from "sonner";

const EMPLOYEE_FILTER_MASTERS = [
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

export function PoliciesFormsPage() {
  const dispatch = useDispatch();
  const { policies, forms, policyCategories, formCategories } = useSelector((state: RootState) => state.policy);

  // Tabs: 'policies' | 'forms'
  const [activeTab, setActiveTab] = useState<'policies' | 'forms'>('policies');

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");

  // Pagination & Sorting state
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;
  const [sortField, setSortField] = useState<string>("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  // Modals state
  const [isPolicyModalOpen, setIsPolicyModalOpen] = useState(false);
  const [editingPolicy, setEditingPolicy] = useState<Policy | null>(null);
  
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [editingForm, setEditingForm] = useState<Form | null>(null);

  // Master Categories Manager modal state
  const [isCategoryManagerOpen, setIsCategoryManagerOpen] = useState(false);
  const [newCatName, setNewCatName] = useState("");

  // Document details preview modal state
  const [previewFileUrl, setPreviewFileUrl] = useState<string | null>(null);
  const [previewFileName, setPreviewFileName] = useState("");

  // Header "Upload Document" click handler
  const handleHeaderUploadClick = () => {
    if (activeTab === 'policies') {
      setEditingPolicy(null);
      setIsPolicyModalOpen(true);
    } else {
      setEditingForm(null);
      setIsFormModalOpen(true);
    }
  };

  const handleOpenEditPolicy = (p: Policy) => {
    setEditingPolicy(p);
    setIsPolicyModalOpen(true);
  };

  const handleOpenEditForm = (f: Form) => {
    setEditingForm(f);
    setIsFormModalOpen(true);
  };

  const handleDeletePolicy = (id: string, name: string) => {
    if (window.confirm(`Are you sure you want to permanently delete policy: "${name}"?`)) {
      dispatch(deletePolicy(id));
      toast.success("Policy deleted successfully");
    }
  };

  const handleDeleteForm = (id: string, name: string) => {
    if (window.confirm(`Are you sure you want to permanently delete form: "${name}"?`)) {
      dispatch(deleteForm(id));
      toast.success("Form template deleted successfully");
    }
  };

  // Reset page when switching tabs or categories
  const handleTabChange = (tab: 'policies' | 'forms') => {
    setActiveTab(tab);
    setSearchQuery("");
    setCategoryFilter("All");
    setCurrentPage(1);
  };

  // Listings filter & sort
  const activeCategories = activeTab === 'policies' ? policyCategories : formCategories;
  
  const filteredItems = (activeTab === 'policies' ? policies : forms).filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.serialNo.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === "All" || item.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const sortedItems = [...filteredItems].sort((a, b) => {
    let valA = (a as any)[sortField] || "";
    let valB = (b as any)[sortField] || "";
    if (typeof valA === "string" && typeof valB === "string") {
      return sortOrder === "asc" ? valA.localeCompare(valB) : valB.localeCompare(valA);
    }
    return 0;
  });

  const totalPages = Math.ceil(sortedItems.length / itemsPerPage);
  const paginatedItems = sortedItems.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const toggleSort = (field: string) => {
    if (sortField === field) {
      setSortOrder(o => o === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("asc");
    }
  };

  const handleAddCategory = () => {
    if (!newCatName.trim()) return;
    if (activeTab === 'policies') {
      dispatch(addPolicyCategory(newCatName.trim()));
    } else {
      dispatch(addFormCategory(newCatName.trim()));
    }
    setNewCatName("");
    toast.success("Category added successfully");
  };

  const handleDeleteCategory = (id: string) => {
    if (window.confirm("Delete this category? Items in this category will remain unchanged.")) {
      if (activeTab === 'policies') {
        dispatch(deletePolicyCategory(id));
      } else {
        dispatch(deleteFormCategory(id));
      }
      toast.success("Category deleted");
    }
  };

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-300">
      
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-card/40 border border-border/50 p-6 rounded-[24px]">
        {/* <div className="space-y-1">
          <h2 className="text-xl font-black text-foreground uppercase tracking-tight flex items-center gap-2.5">
            <ShieldCheck className="w-5 h-5 text-indigo-500" />
            Company Policies & Forms
          </h2>
          <p className="text-xs text-muted-foreground font-semibold">Manage, configure, and distribute internal compliance guidelines and HR request forms.</p>
        </div> */}
        <div className="flex items-center gap-3">
          <Button 
            onClick={() => setIsCategoryManagerOpen(true)}
            variant="outline" 
            className="h-10 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest gap-2 hover:bg-secondary transition-all"
          >
            <Settings size={14} /> Categories Master
          </Button>
          <button 
            onClick={handleHeaderUploadClick}
            className="flex items-center gap-2 px-5 py-2.5 bg-foreground text-background text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-foreground/90 transition-all shadow-md"
          >
            <Upload className="w-4 h-4" />
            Upload Document
          </button>
        </div>
      </div>

      {/* Tabs Selector */}
      <div className="flex border-b border-border/60 pb-px gap-6">
        <button
          onClick={() => handleTabChange('policies')}
          className={`pb-3 text-xs font-black uppercase tracking-widest transition-all border-b-2 px-2 -mb-px ${
            activeTab === 'policies' 
              ? "border-foreground text-foreground" 
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Company Policies
        </button>
        <button
          onClick={() => handleTabChange('forms')}
          className={`pb-3 text-xs font-black uppercase tracking-widest transition-all border-b-2 px-2 -mb-px ${
            activeTab === 'forms' 
              ? "border-foreground text-foreground" 
              : "border-transparent text-muted-foreground hover:text-foreground"
          }`}
        >
          Forms & Templates
        </button>
      </div>

      {/* Main Layout Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Sidebar Directories */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-card border border-border rounded-[24px] p-5 shadow-sm">
            <h3 className="text-[10px] font-black text-muted-foreground uppercase tracking-widest mb-4">Categories</h3>
            <div className="space-y-1">
              <button 
                onClick={() => { setCategoryFilter("All"); setCurrentPage(1); }}
                className={`w-full flex items-center justify-between px-3 py-2 text-xs font-semibold rounded-xl transition-all ${
                  categoryFilter === "All" ? "bg-secondary text-foreground font-bold shadow-sm" : "text-muted-foreground hover:bg-secondary/40 hover:text-foreground"
                }`}
              >
                <span>All Categories</span>
                <span className="text-[10px] font-mono opacity-60">{(activeTab === 'policies' ? policies : forms).length}</span>
              </button>
              {activeCategories.map(cat => {
                const count = (activeTab === 'policies' ? policies : forms).filter(item => item.category === cat.name).length;
                return (
                  <button 
                    key={cat.id}
                    onClick={() => { setCategoryFilter(cat.name); setCurrentPage(1); }}
                    className={`w-full flex items-center justify-between px-3 py-2 text-xs font-semibold rounded-xl transition-all ${
                      categoryFilter === cat.name ? "bg-secondary text-foreground font-bold shadow-sm" : "text-muted-foreground hover:bg-secondary/40 hover:text-foreground"
                    }`}
                  >
                    <span className="truncate">{cat.name}</span>
                    <span className="text-[10px] font-mono opacity-60">{count}</span>
                  </button>
                );
              })}
            </div>
          </div>
          
          <div className="p-5 bg-amber-500/5 border border-amber-500/10 rounded-[20px] space-y-2">
            <h4 className="text-[10px] font-black text-amber-600 uppercase tracking-wider flex items-center gap-2">
              <Info className="w-4 h-4" />
              Dynamic Sync
            </h4>
            <p className="text-[11px] text-muted-foreground font-semibold leading-relaxed">
              Updates to policies and forms take effect on employee dashboards immediately.
            </p>
          </div>
        </div>

        {/* Content Listing Area */}
        <div className="lg:col-span-3 space-y-4">
          
          {/* Sub Search Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input 
                type="text" 
                placeholder={`Search by name or serial...`}
                value={searchQuery}
                onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
                className="w-full pl-9 pr-4 py-2 text-xs font-semibold bg-card border border-border rounded-xl focus:border-foreground/30 outline-none transition-all shadow-sm"
              />
            </div>
            
            <Button
              onClick={() => activeTab === 'policies' ? handleOpenEditPolicy(null as any) : handleOpenEditForm(null as any)}
              className="h-9 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest gap-1.5 bg-foreground text-primary-foreground hover:bg-foreground/90"
            >
              <Plus size={12} strokeWidth={3} /> Add New {activeTab === 'policies' ? 'Policy' : 'Form'}
            </Button>
          </div>

          {/* Table Container */}
          <div className="bg-card border border-border rounded-[24px] overflow-hidden shadow-inner">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-secondary/15 border-b border-border">
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-muted-foreground cursor-pointer select-none" onClick={() => toggleSort("serialNo")}>
                      Serial No {sortField === "serialNo" && (sortOrder === "asc" ? "▲" : "▼")}
                    </th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-muted-foreground cursor-pointer select-none" onClick={() => toggleSort("name")}>
                      Document Name {sortField === "name" && (sortOrder === "asc" ? "▲" : "▼")}
                    </th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-muted-foreground cursor-pointer select-none" onClick={() => toggleSort("category")}>
                      Category {sortField === "category" && (sortOrder === "asc" ? "▲" : "▼")}
                    </th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-muted-foreground">
                      Status / Details
                    </th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-muted-foreground text-right">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {paginatedItems.map((item) => (
                    <tr key={item.id} className="hover:bg-secondary/10 transition-colors group cursor-pointer" onClick={() => {
                      if (item.file?.url && item.file.url !== '#') {
                        setPreviewFileUrl(item.file.url);
                        setPreviewFileName(item.file.name);
                      } else {
                        toast.info("No file uploaded for preview.");
                      }
                    }}>
                      <td className="px-6 py-4 text-xs font-mono font-bold text-muted-foreground">
                        {item.serialNo}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-red-50 dark:bg-red-950/20 text-red-600 flex items-center justify-center">
                            <File className="w-4 h-4" />
                          </div>
                          <div>
                            <span className="text-xs font-bold text-foreground block">{item.name}</span>
                            <span className="text-[10px] text-muted-foreground block truncate max-w-[280px]">{item.description}</span>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-[9px] font-black uppercase tracking-wider bg-secondary px-2.5 py-1 rounded-full border border-border">
                          {item.category}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {activeTab === 'policies' ? (
                          <div className="flex flex-col gap-1">
                            <span className={`text-[9px] font-black uppercase tracking-wider w-fit px-2 py-0.5 rounded-full ${
                              (item as Policy).releaseToEss ? "bg-green-100 text-green-700 border border-green-200" : "bg-slate-100 text-slate-700 border border-slate-200"
                            }`}>
                              {(item as Policy).releaseToEss ? "ESS Released" : "Internal Only"}
                            </span>
                            {(item as Policy).employeeFilters?.length > 0 && (
                              <span className="text-[8px] text-muted-foreground font-semibold truncate max-w-[150px]">
                                Filters: {(item as Policy).employeeFilters.join(', ')}
                              </span>
                            )}
                          </div>
                        ) : (
                          <span className="text-xs text-muted-foreground font-medium">
                            {item.file ? "Template Attached" : "No Attachment"}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-1">
                          {item.file && (
                            <a 
                              href={item.file.url} 
                              download={item.file.name}
                              className="w-8 h-8 rounded-lg border border-border flex items-center justify-center text-muted-foreground hover:bg-secondary hover:text-foreground transition-all"
                              title="Download File"
                            >
                              <Download size={13} />
                            </a>
                          )}
                          <button 
                            onClick={() => activeTab === 'policies' ? handleOpenEditPolicy(item as Policy) : handleOpenEditForm(item as Form)}
                            className="w-8 h-8 rounded-lg border border-border flex items-center justify-center text-muted-foreground hover:bg-secondary hover:text-foreground transition-all"
                            title="Edit"
                          >
                            <Edit size={13} />
                          </button>
                          <button 
                            onClick={() => activeTab === 'policies' ? handleDeletePolicy(item.id, item.name) : handleDeleteForm(item.id, item.name)}
                            className="w-8 h-8 rounded-lg border border-border flex items-center justify-center text-red-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 hover:border-red-100 transition-all"
                            title="Delete"
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {paginatedItems.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-xs font-bold text-muted-foreground">
                        No {activeTab === 'policies' ? 'policies' : 'forms'} matching the filters found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="px-6 py-4 bg-secondary/15 border-t border-border flex items-center justify-between">
                <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
                  Page {currentPage} of {totalPages} ({filteredItems.length} total entries)
                </span>
                <div className="flex items-center gap-2">
                  <Button 
                    variant="outline" 
                    onClick={() => setCurrentPage(c => Math.max(c - 1, 1))} 
                    disabled={currentPage === 1}
                    className="h-8 w-8 p-0 rounded-lg"
                  >
                    <ChevronLeft size={14} />
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => setCurrentPage(c => Math.min(c + 1, totalPages))} 
                    disabled={currentPage === totalPages}
                    className="h-8 w-8 p-0 rounded-lg"
                  >
                    <ChevronRight size={14} />
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* POLICY MODAL */}
      <PolicyModal 
        isOpen={isPolicyModalOpen}
        onClose={() => setIsPolicyModalOpen(false)}
        editingPolicy={editingPolicy}
        categories={policyCategories}
      />

      {/* FORM MODAL */}
      <FormModal 
        isOpen={isFormModalOpen}
        onClose={() => setIsFormModalOpen(false)}
        editingForm={editingForm}
        categories={formCategories}
      />

      {/* CATEGORY MASTER MANAGER */}
      {isCategoryManagerOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-card w-full max-w-md rounded-[24px] border border-border p-6 shadow-2xl space-y-6">
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <h3 className="text-xs font-black uppercase tracking-widest text-foreground">Manage {activeTab === 'policies' ? 'Policy' : 'Form'} Categories</h3>
              <button onClick={() => setIsCategoryManagerOpen(false)} className="w-8 h-8 rounded-full hover:bg-secondary flex items-center justify-center">
                <X size={15} />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="flex gap-2">
                <input 
                  type="text" 
                  placeholder="New category name..."
                  value={newCatName}
                  onChange={(e) => setNewCatName(e.target.value)}
                  className="flex-1 text-xs font-semibold px-3 py-2 bg-card border border-border rounded-xl outline-none focus:border-foreground/30"
                />
                <Button onClick={handleAddCategory} className="h-9 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest">
                  Add
                </Button>
              </div>

              <div className="border border-border rounded-xl p-3 max-h-[180px] overflow-y-auto space-y-1.5 bg-secondary/10">
                {activeCategories.map(cat => (
                  <div key={cat.id} className="flex items-center justify-between py-1.5 px-3 bg-card border border-border/60 rounded-lg">
                    <span className="text-xs font-semibold text-foreground truncate">{cat.name}</span>
                    <button 
                      onClick={() => handleDeleteCategory(cat.id)}
                      className="text-red-400 hover:text-red-500 transition-colors"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                ))}
                {activeCategories.length === 0 && (
                  <p className="text-[10px] text-muted-foreground text-center py-4">No categories configured.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* DOCUMENT PREVIEW MODAL */}
      {previewFileUrl && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-card w-full max-w-4xl h-[85vh] rounded-[24px] border border-border shadow-2xl flex flex-col overflow-hidden">
            <div className="px-6 py-4 border-b border-border flex items-center justify-between bg-secondary/15">
              <div>
                <h4 className="text-xs font-black uppercase tracking-tight">{previewFileName}</h4>
                <p className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">Attachment Preview</p>
              </div>
              <div className="flex items-center gap-3">
                <a 
                  href={previewFileUrl}
                  download={previewFileName}
                  className="h-8 px-3 rounded-lg bg-foreground text-background text-[10px] font-black uppercase tracking-widest flex items-center gap-1 hover:opacity-90"
                >
                  <Download size={12} /> Download
                </a>
                <button 
                  onClick={() => setPreviewFileUrl(null)} 
                  className="w-8 h-8 rounded-full border border-border flex items-center justify-center hover:bg-secondary"
                >
                  <X size={15} />
                </button>
              </div>
            </div>
            <div className="flex-1 bg-secondary/30 flex items-center justify-center p-8">
              {/* Fallback mock visual representation for document preview */}
              <div className="max-w-md w-full bg-card border border-border rounded-[20px] p-8 text-center space-y-6 shadow-lg">
                <div className="w-16 h-16 rounded-2xl bg-red-100 dark:bg-red-950/20 text-red-600 flex items-center justify-center mx-auto shadow-sm">
                  <File size={32} />
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-black text-foreground uppercase tracking-tight">{previewFileName}</p>
                  <p className="text-[10px] text-muted-foreground font-semibold">Portable Document File Format (PDF)</p>
                </div>
                <div className="h-px bg-border w-24 mx-auto" />
                <p className="text-xs text-muted-foreground leading-relaxed">
                  This mock preview represents the digital rendering of the attachment. You can download the physical copy directly.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

/* POLICY FORM MODAL COMPONENT */
interface PolicyModalProps {
  isOpen: boolean;
  onClose: () => void;
  editingPolicy: Policy | null;
  categories: Category[];
}

function PolicyModal({ isOpen, onClose, editingPolicy, categories }: PolicyModalProps) {
  const dispatch = useDispatch();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [serialNo, setSerialNo] = useState("");
  const [category, setCategory] = useState("General");
  const [releaseToEss, setReleaseToEss] = useState(false);
  const [employeeFilters, setEmployeeFilters] = useState<string[]>([]);
  const [enforcePolicy, setEnforcePolicy] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<{ name: string; size: number; url: string } | null>(null);

  // Initialize fields on open
  React.useEffect(() => {
    if (isOpen) {
      if (editingPolicy) {
        setName(editingPolicy.name);
        setDescription(editingPolicy.description);
        setSerialNo(editingPolicy.serialNo);
        setCategory(editingPolicy.category);
        setReleaseToEss(editingPolicy.releaseToEss);
        setEmployeeFilters(editingPolicy.employeeFilters || []);
        setEnforcePolicy(editingPolicy.enforcePolicy);
        setUploadedFile(editingPolicy.file || null);
      } else {
        setName("");
        setDescription("");
        setSerialNo(`POL-${Math.floor(100 + Math.random() * 900)}`);
        setCategory(categories[0]?.name || "General");
        setReleaseToEss(false);
        setEmployeeFilters([]);
        setEnforcePolicy(false);
        setUploadedFile(null);
      }
    }
  }, [isOpen, editingPolicy, categories]);

  if (!isOpen) return null;

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Invalid format. Policies only support PDF upload.");
      return;
    }

    setUploadedFile({
      name: file.name,
      size: file.size,
      url: URL.createObjectURL(file)
    });
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleToggleFilter = (filter: string) => {
    setEmployeeFilters(prev => 
      prev.includes(filter) ? prev.filter(f => f !== filter) : [...prev, filter]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !serialNo.trim()) {
      toast.error("Policy Name and Serial Number are required");
      return;
    }

    const payload: Policy = {
      id: editingPolicy?.id || `p-${Date.now()}`,
      name: name.trim(),
      description: description.trim(),
      serialNo: serialNo.trim(),
      category,
      releaseToEss,
      employeeFilters,
      enforcePolicy,
      file: uploadedFile || undefined,
      lastUpdated: new Date().toISOString().split('T')[0]
    };

    if (editingPolicy) {
      dispatch(updatePolicy(payload));
      toast.success("Policy updated successfully");
    } else {
      dispatch(addPolicy(payload));
      toast.success("New Policy created successfully");
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-card w-full max-w-2xl max-h-[92vh] rounded-[32px] border border-border shadow-2xl flex flex-col overflow-hidden text-foreground">
        
        {/* Header */}
        <div className="px-8 py-5 border-b border-border flex items-center justify-between bg-secondary/10">
          <div>
            <h3 className="text-sm font-black uppercase tracking-tight">{editingPolicy ? "Edit Company Policy" : "Create New Policy"}</h3>
            <p className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">Policy Information Details</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full border border-border flex items-center justify-center hover:bg-secondary transition-all">
            <X size={15} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-8 space-y-6 no-scrollbar">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Policy Name *</label>
              <input 
                type="text" 
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Code of Conduct"
                className="flat-input h-10 w-full text-xs px-3 border border-border bg-card rounded-xl outline-none"
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Serial No *</label>
              <input 
                type="text" 
                value={serialNo}
                onChange={(e) => setSerialNo(e.target.value)}
                placeholder="POL-001"
                className="flat-input h-10 w-full text-xs px-3 border border-border bg-card rounded-xl outline-none font-mono"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Company Policy Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="flat-input h-10 w-full text-xs px-3 border border-border bg-card rounded-xl outline-none cursor-pointer"
            >
              {categories.map(cat => <option key={cat.id} value={cat.name}>{cat.name}</option>)}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Policy Description</label>
            <textarea 
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Provide a brief summary of the policy guidelines..."
              className="flat-input w-full min-h-[70px] text-xs p-3 border border-border bg-card rounded-xl outline-none"
            />
          </div>

          {/* Upload Section */}
          <div className="space-y-2">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Policy Document Upload (.PDF Only)</label>
            <input 
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              className="hidden"
            />
            {!uploadedFile ? (
              <div 
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-border rounded-2xl p-6 text-center cursor-pointer hover:bg-secondary/20 hover:border-muted-foreground/35 transition-all"
              >
                <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-xs font-bold uppercase text-foreground">Click to browse or Drag & Drop policy PDF</p>
                <p className="text-[9px] text-muted-foreground mt-1">Supported Formats: PDF (Max 5MB)</p>
              </div>
            ) : (
              <div className="p-4 bg-card border border-border rounded-xl flex items-center justify-between shadow-sm animate-in zoom-in-95">
                <div className="flex items-center gap-3">
                  <File className="w-8 h-8 text-red-500" />
                  <div>
                    <p className="text-xs font-bold text-foreground truncate max-w-[280px]">{uploadedFile.name}</p>
                    <p className="text-[9px] text-green-500 font-bold uppercase tracking-widest">Ready · {(uploadedFile.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <div className="flex items-center gap-1.5">
                  {uploadedFile.url !== '#' && (
                    <a 
                      href={uploadedFile.url}
                      download={uploadedFile.name}
                      className="w-8 h-8 rounded-lg border border-border hover:bg-secondary flex items-center justify-center text-muted-foreground"
                      title="Download PDF"
                    >
                      <Download size={13} />
                    </a>
                  )}
                  <button 
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="h-8 px-3 rounded-lg bg-secondary text-[9px] font-black uppercase tracking-wider hover:bg-border transition-all"
                  >
                    Replace
                  </button>
                  <button 
                    type="button"
                    onClick={handleRemoveFile}
                    className="w-8 h-8 rounded-lg border border-red-100 hover:bg-red-50 hover:text-red-500 flex items-center justify-center text-muted-foreground"
                    title="Remove File"
                  >
                    <X size={14} />
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Release & Enforce Toggles */}
          <div className="p-4 bg-secondary/10 border border-border rounded-2xl grid grid-cols-1 sm:grid-cols-2 gap-4">
            <label className="flex items-start gap-3 cursor-pointer select-none">
              <input 
                type="checkbox"
                checked={releaseToEss}
                onChange={(e) => setReleaseToEss(e.target.checked)}
                className="rounded border-border focus:ring-0 w-4 h-4 cursor-pointer mt-0.5"
              />
              <div>
                <span className="text-xs font-bold text-foreground block">Release to Employee Self Service</span>
                <span className="text-[9px] text-muted-foreground block leading-normal mt-0.5">Let employees download/view this policy.</span>
              </div>
            </label>
            
            <label className="flex items-start gap-3 cursor-pointer select-none">
              <input 
                type="checkbox"
                checked={enforcePolicy}
                onChange={(e) => setEnforcePolicy(e.target.checked)}
                className="rounded border-border focus:ring-0 w-4 h-4 cursor-pointer mt-0.5"
              />
              <div>
                <span className="text-xs font-bold text-foreground block">Enforce Policy</span>
                <span className="text-[9px] text-muted-foreground block leading-normal mt-0.5">Require mandatory acknowledgement from targets.</span>
              </div>
            </label>
          </div>

          {/* Employee filter (masters) */}
          <div className="space-y-3">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest flex justify-between">
              <span>Employee Target Filter *</span>
              <span className="text-[8px] text-primary">Multi-select Dynamic Selection</span>
            </label>
            <div className="flex flex-wrap gap-2">
              {EMPLOYEE_FILTER_MASTERS.map(f => {
                const isSelected = employeeFilters.includes(f);
                return (
                  <button
                    key={f}
                    type="button"
                    onClick={() => handleToggleFilter(f)}
                    className={`px-3 py-1.5 rounded-xl text-[9px] font-bold uppercase tracking-wider border transition-all ${
                      isSelected 
                        ? "bg-foreground text-primary-foreground border-foreground shadow-sm font-black" 
                        : "bg-card border-border text-muted-foreground hover:border-muted-foreground/35"
                    }`}
                  >
                    {f}
                  </button>
                );
              })}
            </div>
            {employeeFilters.length > 0 && (
              <p className="text-[9px] text-muted-foreground font-medium italic mt-1.5">
                Targeting: {employeeFilters.join(', ')}
              </p>
            )}
          </div>

        </form>

        {/* Footer */}
        <div className="px-8 py-5 border-t border-border bg-secondary/15 flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={onClose} className="h-10 px-5 rounded-xl text-[10px] font-black uppercase tracking-widest">
            Cancel
          </Button>
          <Button type="submit" onClick={handleSubmit} className="h-10 px-6 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest hover:bg-foreground/90">
            Submit
          </Button>
        </div>

      </div>
    </div>
  );
}

/* FORM MODAL COMPONENT */
interface FormModalProps {
  isOpen: boolean;
  onClose: () => void;
  editingForm: Form | null;
  categories: Category[];
}

function FormModal({ isOpen, onClose, editingForm, categories }: FormModalProps) {
  const dispatch = useDispatch();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [serialNo, setSerialNo] = useState("");
  const [category, setCategory] = useState("General");
  const [uploadedFile, setUploadedFile] = useState<{ name: string; size: number; url: string } | null>(null);

  // Initialize fields on open
  React.useEffect(() => {
    if (isOpen) {
      if (editingForm) {
        setName(editingForm.name);
        setDescription(editingForm.description);
        setSerialNo(editingForm.serialNo);
        setCategory(editingForm.category);
        setUploadedFile(editingForm.file || null);
      } else {
        setName("");
        setDescription("");
        setSerialNo(`FRM-${Math.floor(100 + Math.random() * 900)}`);
        setCategory(categories[0]?.name || "General");
        setUploadedFile(null);
      }
    }
  }, [isOpen, editingForm, categories]);

  if (!isOpen) return null;

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'pdf' && ext !== 'doc' && ext !== 'docx') {
      alert("Invalid format. Forms templates support PDF, DOC, or DOCX formats.");
      return;
    }

    setUploadedFile({
      name: file.name,
      size: file.size,
      url: URL.createObjectURL(file)
    });
  };

  const handleRemoveFile = () => {
    setUploadedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !serialNo.trim()) {
      toast.error("Form Name and Serial Number are required");
      return;
    }

    const payload: Form = {
      id: editingForm?.id || `f-${Date.now()}`,
      name: name.trim(),
      description: description.trim(),
      serialNo: serialNo.trim(),
      category,
      file: uploadedFile || undefined,
      lastUpdated: new Date().toISOString().split('T')[0]
    };

    if (editingForm) {
      dispatch(updateForm(payload));
      toast.success("Form updated successfully");
    } else {
      dispatch(addForm(payload));
      toast.success("New Form Template uploaded successfully");
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-card w-full max-w-xl max-h-[88vh] rounded-[32px] border border-border shadow-2xl flex flex-col overflow-hidden text-foreground">
        
        {/* Header */}
        <div className="px-8 py-5 border-b border-border flex items-center justify-between bg-secondary/10">
          <div>
            <h3 className="text-sm font-black uppercase tracking-tight">{editingForm ? "Edit Form Template" : "Upload New Form"}</h3>
            <p className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">Form Configuration Fields</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full border border-border flex items-center justify-center hover:bg-secondary transition-all">
            <X size={15} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-8 space-y-6 no-scrollbar">
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Form Name *</label>
              <input 
                type="text" 
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Leave Application Form"
                className="flat-input h-10 w-full text-xs px-3 border border-border bg-card rounded-xl outline-none"
              />
            </div>
            
            <div className="space-y-2">
              <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Serial No *</label>
              <input 
                type="text" 
                value={serialNo}
                onChange={(e) => setSerialNo(e.target.value)}
                placeholder="FRM-001"
                className="flat-input h-10 w-full text-xs px-3 border border-border bg-card rounded-xl outline-none font-mono"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Form Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="flat-input h-10 w-full text-xs px-3 border border-border bg-card rounded-xl outline-none cursor-pointer"
            >
              {categories.map(cat => <option key={cat.id} value={cat.name}>{cat.name}</option>)}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Form Description</label>
            <textarea 
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Provide guidelines on who should submit this form and key details needed..."
              className="flat-input w-full min-h-[70px] text-xs p-3 border border-border bg-card rounded-xl outline-none"
            />
          </div>

          {/* Attachment upload */}
          <div className="space-y-2">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Upload Form Template File (.PDF, .DOC, .DOCX)</label>
            <input 
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleFileUpload}
              className="hidden"
            />
            {!uploadedFile ? (
              <div 
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-border rounded-2xl p-6 text-center cursor-pointer hover:bg-secondary/20 hover:border-muted-foreground/35 transition-all"
              >
                <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-xs font-bold uppercase text-foreground">Click to browse or Drag & Drop form template</p>
                <p className="text-[9px] text-muted-foreground mt-1">Supported: PDF, DOC, DOCX (Max 5MB)</p>
              </div>
            ) : (
              <div className="p-4 bg-card border border-border rounded-xl flex items-center justify-between shadow-sm animate-in zoom-in-95">
                <div className="flex items-center gap-3">
                  <File className="w-8 h-8 text-indigo-500" />
                  <div>
                    <p className="text-xs font-bold text-foreground truncate max-w-[220px]">{uploadedFile.name}</p>
                    <p className="text-[9px] text-green-500 font-bold uppercase tracking-widest">Ready · {(uploadedFile.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  {uploadedFile.url !== '#' && (
                    <a 
                      href={uploadedFile.url}
                      download={uploadedFile.name}
                      className="w-8 h-8 rounded-lg border border-border hover:bg-secondary flex items-center justify-center text-muted-foreground"
                      title="Download Template File"
                    >
                      <Download size={13} />
                    </a>
                  )}
                  <button 
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="h-8 px-3 rounded-lg bg-secondary text-[9px] font-black uppercase tracking-wider hover:bg-border transition-all"
                  >
                    Replace
                  </button>
                  <button 
                    type="button"
                    onClick={handleRemoveFile}
                    className="w-8 h-8 rounded-lg border border-red-100 hover:bg-red-50 hover:text-red-500 flex items-center justify-center text-muted-foreground"
                    title="Delete Template"
                  >
                    <X size={14} />
                  </button>
                </div>
              </div>
            )}
          </div>

        </form>

        {/* Footer */}
        <div className="px-8 py-5 border-t border-border bg-secondary/15 flex justify-end gap-3">
          <Button type="button" variant="outline" onClick={onClose} className="h-10 px-5 rounded-xl text-[10px] font-black uppercase tracking-widest">
            Cancel
          </Button>
          <Button type="submit" onClick={handleSubmit} className="h-10 px-6 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest hover:bg-foreground/90">
            Submit
          </Button>
        </div>

      </div>
    </div>
  );
}
