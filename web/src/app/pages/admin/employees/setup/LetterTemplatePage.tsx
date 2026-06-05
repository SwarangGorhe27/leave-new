import { useState } from "react";
import { 
  FileText, 
  Plus, 
  Search, 
  Edit3, 
  Trash2, 
  Eye, 
  Download, 
  ChevronRight, 
  Tags, 
  Copy, 
  History,
  ToggleLeft,
  ToggleRight,
  Shield,
  Clock,
  User,
  ExternalLink,
  Library
} from "lucide-react";
import { KebabMenu } from "../../../../components/ui/KebabMenu";
import { toast } from "sonner";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "@/store";
import { 
  deleteTemplate, 
  duplicateTemplate, 
  toggleTemplateStatus, 
  LetterTemplate,
  addTemplate
} from "@/store/slices/letterSlice";
import { TemplateWizard } from "./components/TemplateWizard";
import { TemplatePreviewModal } from "./components/TemplatePreviewModal";
import { PlaceholderPanel } from "./components/PlaceholderPanel";
import { TemplateGalleryCard } from "./components/TemplateGalleryCard";

const CATEGORIES = ["All", "Onboarding", "Offboarding", "Appraisal", "Statutory", "Other"];

const GALLERY_TEMPLATES = [
  { name: "Appointment Order", description: "Standard appointment letter with terms and conditions." },
  { name: "Experience Letter", description: "Work experience certification for departing employees." },
  { name: "Confirmation Letter", description: "Official confirmation after probation period." },
  { name: "Probation Extension", description: "Extension of probation period with reasons." },
  { name: "Relieving Letter", description: "Official relieving document for exit clearance." },
  { name: "Termination Letter", description: "Notice of termination as per company policy." }
];

export function LetterTemplatePage() {
  const dispatch = useDispatch();
  const templates = useSelector((state: RootState) => state.letter.templates);
  
  const [activeCategory, setActiveCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<LetterTemplate | null>(null);
  const [previewTemplate, setPreviewTemplate] = useState<LetterTemplate | null>(null);
  const [viewMode, setViewMode] = useState<"list" | "gallery">("list");

  const filteredTemplates = templates.filter(tpl => {
    const matchesCat = activeCategory === "All" || tpl.category === activeCategory;
    const matchesSearch = tpl.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         tpl.category.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  const handleCreate = () => {
    setEditingTemplate(null);
    setIsWizardOpen(true);
  };

  const handleEdit = (tpl: LetterTemplate) => {
    setEditingTemplate(tpl);
    setIsWizardOpen(true);
  };

  const handleDelete = (tpl: LetterTemplate) => {
    if (confirm(`Are you sure you want to delete "${tpl.name}"?`)) {
      dispatch(deleteTemplate(tpl.id));
      toast.success("Template deleted successfully");
    }
  };

  const addToMyTemplates = (tplName: string) => {
    const newTpl: LetterTemplate = {
      id: `tpl-${Date.now()}`,
      name: tplName,
      category: "Other",
      description: `Template for ${tplName}`,
      enabled: true,
      lastModified: new Date().toISOString().split('T')[0],
      owner: ["admin"],
      suppressZeroPayroll: false,
      enforceLetter: "Not Required",
      numberSeries: { type: "Default Serial Number" },
      mailTemplate: "None",
      enableDigitalSignature: false,
      customFields: [],
      workflow: { canRequest: false, autoApproval: false, hrApproval: true, managerApproval: false }
    };
    dispatch(addTemplate(newTpl));
    toast.success(`${tplName} added to your templates`);
  };

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-700 pb-20 no-scrollbar overflow-y-auto h-full">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
             <div className="w-12 h-12 rounded-2xl bg-foreground text-primary-foreground flex items-center justify-center shadow-xl shadow-foreground/10">
                <FileText size={24} />
             </div>
             <div>
                <h2 className="text-2xl font-black text-foreground uppercase tracking-tight">
                  Letter Template Setup
                </h2>
                <div className="flex items-center gap-2 text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em]">
                   <span>Employee Setup</span>
                   <ChevronRight size={10} />
                   <span className="text-primary">Templates</span>
                </div>
             </div>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="bg-secondary/50 p-1 rounded-xl border border-border flex">
             <button 
              onClick={() => setViewMode("list")}
              className={`px-4 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${viewMode === "list" ? "bg-card text-foreground shadow-sm border border-border" : "text-muted-foreground hover:text-foreground"}`}
             >
                My Templates
             </button>
             <button 
              onClick={() => setViewMode("gallery")}
              className={`px-4 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${viewMode === "gallery" ? "bg-card text-foreground shadow-sm border border-border" : "text-muted-foreground hover:text-foreground"}`}
             >
                Gallery
             </button>
          </div>
          <button 
            onClick={handleCreate}
            className="flex items-center gap-2 px-6 py-3 bg-foreground text-primary-foreground text-xs font-black uppercase tracking-widest rounded-2xl hover:bg-accent transition-all shadow-xl shadow-foreground/20 active:scale-95"
          >
            <Plus className="w-4 h-4" strokeWidth={3} />
            Create Template
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Sidebar & Placeholders */}
        <div className="lg:col-span-3 space-y-8">
          {/* Categories Card */}
          <div className="bg-card border border-border rounded-3xl p-6 shadow-sm space-y-6">
            <div>
              <h3 className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em] mb-4">Template Categories</h3>
              <div className="space-y-1">
                {CATEGORIES.map(cat => {
                  const count = cat === "All" ? templates.length : templates.filter(t => t.category === cat).length;
                  return (
                    <button
                      key={cat}
                      onClick={() => setActiveCategory(cat)}
                      className={`w-full text-left px-4 py-3 text-xs rounded-2xl transition-all flex items-center justify-between group ${
                        activeCategory === cat ? "bg-foreground text-primary-foreground font-black shadow-lg shadow-foreground/10" : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground font-bold"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Tags size={14} className={activeCategory === cat ? "text-primary" : "text-muted-foreground opacity-50"} />
                        {cat}
                      </div>
                      <span className={`text-[9px] px-2 py-0.5 rounded-full border ${
                        activeCategory === cat ? "bg-primary/20 border-primary/30 text-primary-foreground" : "bg-background border-border"
                      }`}>
                        {count}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Dynamic Placeholders Panel */}
          <PlaceholderPanel />
        </div>

        {/* Right Column: Content Grid */}
        <div className="lg:col-span-9 space-y-6">
          {viewMode === "list" ? (
            <>
              {/* Search & Filter Bar */}
              <div className="flex flex-col sm:flex-row gap-4 items-stretch sm:items-center justify-between">
                <div className="relative flex-1 max-w-lg group">
                  <Search className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" />
                  <input
                    type="text"
                    placeholder="Search your templates by name or category..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 bg-card border border-border rounded-2xl text-sm font-bold focus:ring-4 focus:ring-primary/5 outline-none shadow-inner transition-all"
                  />
                </div>
                
                <div className="flex items-center gap-4 text-[10px] font-black text-muted-foreground uppercase tracking-widest px-4">
                   <Clock size={12} className="text-primary" />
                   Showing {filteredTemplates.length} Templates
                </div>
              </div>

              {/* Templates Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-2 gap-6">
                {filteredTemplates.map((tpl) => (
                  <div 
                    key={tpl.id} 
                    className={`bg-card border border-border rounded-[32px] p-6 hover:shadow-2xl hover:border-foreground/10 transition-all group relative overflow-hidden flex flex-col h-full border-t-4 ${tpl.enabled ? 'border-t-primary' : 'border-t-slate-300'}`}
                  >
                    {/* Decorative Background Icon */}
                    <div className="absolute -right-4 -top-4 opacity-[0.03] group-hover:opacity-[0.08] group-hover:scale-125 transition-all duration-700 pointer-events-none">
                       <FileText size={160} />
                    </div>

                    <div className="flex items-start justify-between relative z-10 mb-6">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                           <span className="text-[9px] font-black text-primary uppercase tracking-[0.2em] bg-primary/10 px-2.5 py-1 rounded-full">
                              {tpl.category}
                           </span>
                           {!tpl.enabled && (
                             <span className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em] bg-slate-100 px-2.5 py-1 rounded-full">
                                Disabled
                             </span>
                           )}
                        </div>
                        <h4 className="text-base font-black text-foreground leading-tight group-hover:text-primary transition-colors pr-8">
                          {tpl.name}
                        </h4>
                      </div>
                      <KebabMenu
                        size="md"
                        items={[
                          { label: "Edit Template", icon: Edit3, onClick: () => handleEdit(tpl) },
                          { label: "Duplicate", icon: Copy, onClick: () => dispatch(duplicateTemplate(tpl.id)) },
                          { label: tpl.enabled ? "Disable" : "Enable", icon: tpl.enabled ? ToggleLeft : ToggleRight, onClick: () => dispatch(toggleTemplateStatus(tpl.id)) },
                          { label: "Version History", icon: History, onClick: () => toast.info("Coming Soon") },
                          {
                            label: "Delete", icon: Trash2, variant: "destructive", separator: true, onClick: () => handleDelete(tpl)
                          },
                        ]}
                      />
                    </div>

                    <div className="flex-1 space-y-4 relative z-10">
                       <p className="text-xs text-muted-foreground line-clamp-2 font-medium">
                          {tpl.description || "No description provided for this template."}
                       </p>
                       
                       <div className="flex flex-wrap gap-4 pt-2">
                          <div className="flex items-center gap-2">
                             <User size={12} className="text-muted-foreground" />
                             <span className="text-[10px] font-bold text-muted-foreground uppercase">{tpl.owner?.[0] || 'admin'}</span>
                          </div>
                          <div className="flex items-center gap-2">
                             <Shield size={12} className={tpl.enableDigitalSignature ? "text-green-500" : "text-muted-foreground"} />
                             <span className="text-[10px] font-bold text-muted-foreground uppercase">{tpl.enableDigitalSignature ? 'Secured' : 'Standard'}</span>
                          </div>
                       </div>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-muted-foreground pt-6 mt-6 border-t border-border/50 relative z-10">
                      <span className="font-bold flex items-center gap-2 uppercase tracking-tighter">
                         <Clock size={10} />
                         Modified {tpl.lastModified}
                      </span>
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => setPreviewTemplate(tpl)}
                          className="flex items-center gap-1.5 hover:text-foreground transition-all font-black uppercase tracking-widest bg-secondary/50 px-3 py-1.5 rounded-xl border border-transparent hover:border-border"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          Preview
                        </button>
                        <button className="flex items-center gap-1.5 hover:text-foreground transition-all font-black uppercase tracking-widest bg-secondary/50 px-3 py-1.5 rounded-xl border border-transparent hover:border-border">
                          <Download className="w-3.5 h-3.5" />
                          Export
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {filteredTemplates.length === 0 && (
                  <div className="col-span-full py-20 flex flex-col items-center justify-center bg-card border-2 border-dashed border-border rounded-[40px] space-y-4">
                     <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center text-muted-foreground">
                        <FileText size={32} opacity={0.2} />
                     </div>
                     <div className="text-center">
                        <p className="text-sm font-black text-foreground uppercase tracking-widest">No templates found</p>
                        <p className="text-[11px] text-muted-foreground mt-1">Try adjusting your filters or create a new template.</p>
                     </div>
                     <Button onClick={handleCreate} variant="outline" className="mt-4 rounded-xl font-black text-[10px] uppercase tracking-[0.2em] h-10 px-6">
                        Create New Template
                     </Button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
               <div className="flex items-center gap-4 bg-primary/5 border border-primary/10 p-6 rounded-[32px]">
                  <div className="w-14 h-14 rounded-2xl bg-primary/10 text-primary flex items-center justify-center">
                     <Library size={28} />
                  </div>
                  <div>
                     <h3 className="text-lg font-black text-foreground uppercase tracking-tight">Template Gallery</h3>
                     <p className="text-xs text-muted-foreground font-medium uppercase tracking-widest">Pre-defined standardized HR document templates ready for use.</p>
                  </div>
               </div>

               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {GALLERY_TEMPLATES.map((tpl, i) => (
                    <TemplateGalleryCard 
                      key={i}
                      name={tpl.name}
                      description={tpl.description}
                      onAdd={() => addToMyTemplates(tpl.name)}
                      onPreview={() => toast.info("Previewing Gallery Template")}
                    />
                  ))}
               </div>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <TemplateWizard 
        isOpen={isWizardOpen} 
        onClose={() => setIsWizardOpen(false)} 
        editingTemplate={editingTemplate}
      />

      <TemplatePreviewModal 
        isOpen={!!previewTemplate}
        onClose={() => setPreviewTemplate(null)}
        template={previewTemplate}
      />
    </div>
  );
}
