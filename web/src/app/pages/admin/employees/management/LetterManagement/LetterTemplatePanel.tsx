import { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "@/store/index";
import { 
  deleteTemplate, 
  toggleTemplateStatus, 
  duplicateTemplate, 
  addTemplate,
  LetterTemplate 
} from "@/store/slices/letterSlice";
import { addNotification } from "@/store/slices/notificationSlice";
import { 
  Search, 
  Plus, 
  Grid, 
  Trash2, 
  Edit, 
  Copy, 
  Eye, 
  FileText, 
  Filter, 
  ChevronLeft, 
  ChevronRight,
  ShieldAlert,
  ShieldCheck,
  Library
} from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { TemplateWizard } from "./TemplateWizard";
import { TemplateGallery } from "./TemplateGallery";
import { TemplatePreviewModal } from "./TemplatePreviewModal";

export function LetterTemplatePanel() {
  const dispatch = useDispatch();
  const templates = useSelector((state: RootState) => state.letter.templates);

  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");
  
  // View states: 'list' | 'gallery'
  const [viewMode, setViewMode] = useState<'list' | 'gallery'>('list');
  
  // Wizard state
  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<LetterTemplate | null>(null);

  // Preview state
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [previewTemplate, setPreviewTemplate] = useState<LetterTemplate | null>(null);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  // Sorting
  const [sortField, setSortField] = useState<keyof LetterTemplate>("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  // Get distinct categories
  const categories = ["All", ...Array.from(new Set(templates.map(t => t.category)))];

  const handleToggleStatus = (id: string) => {
    dispatch(toggleTemplateStatus(id));
    dispatch(addNotification({ type: "info", message: "Template status updated" }));
  };

  const handleDelete = (id: string, name: string) => {
    if (window.confirm(`Are you sure you want to delete template "${name}"?`)) {
      dispatch(deleteTemplate(id));
      dispatch(addNotification({ type: "success", message: "Template deleted successfully" }));
    }
  };

  const handleDuplicate = (id: string) => {
    dispatch(duplicateTemplate(id));
    dispatch(addNotification({ type: "success", message: "Template duplicated successfully" }));
  };

  const handleEdit = (tpl: LetterTemplate) => {
    setEditingTemplate(tpl);
    setIsWizardOpen(true);
  };

  const handleCreateNew = () => {
    setEditingTemplate(null);
    setIsWizardOpen(true);
  };

  const handlePreview = (tpl: LetterTemplate) => {
    setPreviewTemplate(tpl);
    setIsPreviewOpen(true);
  };

  const handleAddFromGallery = (tplData: Partial<LetterTemplate>) => {
    const finalTpl: LetterTemplate = {
      ...(tplData as LetterTemplate),
      id: `tpl-${Date.now()}`,
      lastModified: new Date().toISOString().split('T')[0]
    };
    dispatch(addTemplate(finalTpl));
    dispatch(addNotification({ type: "success", message: `Added "${finalTpl.name}" to My Templates` }));
    setViewMode('list');
  };

  // Filter & Sort
  const filtered = templates.filter(t => {
    const matchesSearch = t.name.toLowerCase().includes(search.toLowerCase()) || 
                          t.description.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = categoryFilter === "All" || t.category === categoryFilter;
    const matchesStatus = statusFilter === "All" || 
                          (statusFilter === "Enabled" && t.enabled) || 
                          (statusFilter === "Disabled" && !t.enabled);
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const sorted = [...filtered].sort((a, b) => {
    let valA = a[sortField];
    let valB = b[sortField];

    if (typeof valA === "string" && typeof valB === "string") {
      return sortOrder === "asc" 
        ? valA.localeCompare(valB) 
        : valB.localeCompare(valA);
    }
    if (typeof valA === "boolean" && typeof valB === "boolean") {
      return sortOrder === "asc" 
        ? (valA === valB ? 0 : valA ? 1 : -1) 
        : (valA === valB ? 0 : valB ? 1 : -1);
    }
    return 0;
  });

  // Paginate
  const totalPages = Math.ceil(sorted.length / itemsPerPage);
  const paginated = sorted.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const toggleSort = (field: keyof LetterTemplate) => {
    if (sortField === field) {
      setSortOrder(o => o === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("asc");
    }
  };

  if (viewMode === 'gallery') {
    return (
      <div className="p-6 bg-card border border-border rounded-[32px] shadow-sm animate-in fade-in duration-300">
        <TemplateGallery 
          onBack={() => setViewMode('list')} 
          onAddTemplate={handleAddFromGallery}
          onPreview={handlePreview}
        />
        <TemplatePreviewModal 
          isOpen={isPreviewOpen} 
          onClose={() => setIsPreviewOpen(false)} 
          template={previewTemplate}
        />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-card border border-border rounded-[32px] shadow-sm animate-in fade-in duration-300">
      
      {/* Title Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* <div>
          <h2 className="text-xl font-black text-foreground uppercase tracking-tight">Letter Template Management</h2>
          <p className="text-xs text-muted-foreground font-semibold">Configure letter layouts, signature options, custom parameters, and approvals.</p>
        </div> */}
        <div className="flex items-center gap-3">
          <Button 
            onClick={() => setViewMode('gallery')}
            variant="outline" 
            className="h-10 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest gap-2 hover:bg-secondary transition-all"
          >
            <Library size={14} /> Open Template Gallery
          </Button>
          <Button 
            onClick={handleCreateNew}
            className="h-10 px-5 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest gap-2 hover:bg-foreground/90 transition-all shadow-md"
          >
            <Plus size={14} strokeWidth={3} /> Create New Template
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2 border-t border-border/50">
        <div className="relative flex-1 max-w-md">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Search templates by name..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setCurrentPage(1); }}
            className="w-full pl-9 pr-4 py-2.5 text-xs font-semibold bg-card border border-border rounded-xl focus:border-foreground/30 outline-none transition-all"
          />
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Category:</span>
            <select
              value={categoryFilter}
              onChange={(e) => { setCategoryFilter(e.target.value); setCurrentPage(1); }}
              className="text-xs font-bold uppercase py-1.5 px-3 border border-border bg-card rounded-xl outline-none cursor-pointer"
            >
              {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setCurrentPage(1); }}
              className="text-xs font-bold uppercase py-1.5 px-3 border border-border bg-card rounded-xl outline-none cursor-pointer"
            >
              <option value="All">All Statuses</option>
              <option value="Enabled">Enabled Only</option>
              <option value="Disabled">Disabled Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Listing Table */}
      <div className="border border-border rounded-2xl overflow-hidden bg-card/50 shadow-inner">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="border-b border-border bg-secondary/15">
                <th className="p-4 text-[10px] font-black uppercase tracking-widest text-muted-foreground cursor-pointer select-none" onClick={() => toggleSort("name")}>
                  Template Name {sortField === "name" && (sortOrder === "asc" ? "▲" : "▼")}
                </th>
                <th className="p-4 text-[10px] font-black uppercase tracking-widest text-muted-foreground cursor-pointer select-none" onClick={() => toggleSort("category")}>
                  Category {sortField === "category" && (sortOrder === "asc" ? "▲" : "▼")}
                </th>
                <th className="p-4 text-[10px] font-black uppercase tracking-widest text-muted-foreground">
                  Signature PFX
                </th>
                <th className="p-4 text-[10px] font-black uppercase tracking-widest text-muted-foreground cursor-pointer select-none" onClick={() => toggleSort("lastModified")}>
                  Last Modified {sortField === "lastModified" && (sortOrder === "asc" ? "▲" : "▼")}
                </th>
                <th className="p-4 text-[10px] font-black uppercase tracking-widest text-muted-foreground cursor-pointer select-none" onClick={() => toggleSort("enabled")}>
                  Enabled Status {sortField === "enabled" && (sortOrder === "asc" ? "▲" : "▼")}
                </th>
                <th className="p-4 text-[10px] font-black uppercase tracking-widest text-muted-foreground text-right">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {paginated.map(tpl => (
                <tr key={tpl.id} className="hover:bg-secondary/10 transition-colors">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-secondary flex items-center justify-center text-foreground">
                        <FileText size={16} />
                      </div>
                      <div>
                        <p className="text-xs font-bold text-foreground">{tpl.name}</p>
                        <p className="text-[10px] text-muted-foreground truncate max-w-[240px]">{tpl.description || "No description provided."}</p>
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-[9px] font-black uppercase tracking-wider bg-secondary px-2.5 py-1 rounded-full border border-border">
                      {tpl.category}
                    </span>
                  </td>
                  <td className="p-4">
                    {tpl.enableDigitalSignature ? (
                      <span className="text-[9px] font-bold text-emerald-600 uppercase flex items-center gap-1">
                        <ShieldCheck size={12} /> Yes (PFX)
                      </span>
                    ) : (
                      <span className="text-[9px] font-bold text-muted-foreground uppercase flex items-center gap-1">
                        <ShieldAlert size={12} /> No
                      </span>
                    )}
                  </td>
                  <td className="p-4 text-xs font-semibold text-muted-foreground">
                    {tpl.lastModified}
                  </td>
                  <td className="p-4">
                    <button 
                      onClick={() => handleToggleStatus(tpl.id)}
                      className={`h-6 px-3 rounded-full text-[9px] font-black uppercase tracking-widest transition-all ${
                        tpl.enabled 
                          ? "bg-green-100 text-green-700 border border-green-200" 
                          : "bg-red-100 text-red-700 border border-red-200"
                      }`}
                    >
                      {tpl.enabled ? "Active" : "Disabled"}
                    </button>
                  </td>
                  <td className="p-4 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <button 
                        onClick={() => handlePreview(tpl)}
                        className="w-8 h-8 rounded-lg border border-border flex items-center justify-center text-muted-foreground hover:bg-secondary hover:text-foreground transition-all"
                        title="Preview template rendering"
                      >
                        <Eye size={13} />
                      </button>
                      <button 
                        onClick={() => handleEdit(tpl)}
                        className="w-8 h-8 rounded-lg border border-border flex items-center justify-center text-muted-foreground hover:bg-secondary hover:text-foreground transition-all"
                        title="Edit Template"
                      >
                        <Edit size={13} />
                      </button>
                      <button 
                        onClick={() => handleDuplicate(tpl.id)}
                        className="w-8 h-8 rounded-lg border border-border flex items-center justify-center text-muted-foreground hover:bg-secondary hover:text-foreground transition-all"
                        title="Duplicate Template"
                      >
                        <Copy size={13} />
                      </button>
                      <button 
                        onClick={() => handleDelete(tpl.id, tpl.name)}
                        className="w-8 h-8 rounded-lg border border-border flex items-center justify-center text-red-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 hover:border-red-100 transition-all"
                        title="Delete Template"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {paginated.length === 0 && (
                <tr>
                  <td colSpan={6} className="p-12 text-center text-xs font-bold text-muted-foreground">
                    No letter templates found. Click "Create New Template" or "Open Template Gallery" to get started.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        {totalPages > 1 && (
          <div className="px-6 py-4 bg-secondary/15 border-t border-border flex items-center justify-between">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
              Page {currentPage} of {totalPages} ({filtered.length} total templates)
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

      {/* Modals and Overlays */}
      <TemplateWizard 
        isOpen={isWizardOpen} 
        onClose={() => { setIsWizardOpen(false); setEditingTemplate(null); }}
        editingTemplate={editingTemplate}
      />
      <TemplatePreviewModal 
        isOpen={isPreviewOpen} 
        onClose={() => { setIsPreviewOpen(false); setPreviewTemplate(null); }}
        template={previewTemplate}
      />
    </div>
  );
}
