import React from "react";
import { ArrowLeft, FileText, Eye, Plus, Search } from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { LetterTemplate } from "@/store/slices/letterSlice";

interface TemplateGalleryProps {
  onBack: () => void;
  onAddTemplate: (tpl: Partial<LetterTemplate>) => void;
  onPreview: (tpl: LetterTemplate) => void;
}

const GALLERY_TEMPLATES: Array<{ name: string; description: string; category: string }> = [
  { name: "Address Proof Letter", description: "Official verification of employee's current residential address in company records.", category: "General" },
  { name: "Appointment Order", description: "Standard appointment letter specifying terms of employment, role, and salary details.", category: "Offer Letter" },
  { name: "Confirmation Letter", description: "Letter issued to employees who have successfully completed their probationary period.", category: "HR" },
  { name: "Department Transfer Letter", description: "Formal notification of transfer to a different team or department.", category: "General" },
  { name: "Experience Letter", description: "Issued upon exit, detailing employment history, designation, and work performance.", category: "Relieving Letter" },
  { name: "Location Transfer Letter", description: "Relocation letter authorizing transfer of job location to another branch or city.", category: "General" },
  { name: "Offer Letter", description: "Comprehensive offer letter with job specifications, joining details, and salary components.", category: "Offer Letter" },
  { name: "Probation Extension Letter", description: "Formally extends employee probation period with details on target goals.", category: "HR" },
  { name: "Re Designation Letter", description: "Letter confirming promotion or change in role / official designation.", category: "HR" },
  { name: "Relieving Letter", description: "Official discharge letter issued upon successful handover and completion of notice period.", category: "Relieving Letter" },
  { name: "Termination Letter", description: "Formal document terminating employment contract with final settlement guidance.", category: "Termination Letter" },
];

export function TemplateGallery({ onBack, onAddTemplate, onPreview }: TemplateGalleryProps) {
  const [search, setSearch] = React.useState("");

  const filtered = GALLERY_TEMPLATES.filter(
    t => t.name.toLowerCase().includes(search.toLowerCase()) || 
         t.description.toLowerCase().includes(search.toLowerCase())
  );

  const handleAdd = (item: typeof GALLERY_TEMPLATES[0]) => {
    const tpl: Partial<LetterTemplate> = {
      name: item.name,
      category: item.category,
      description: item.description,
      enabled: true,
      owner: ["admin"],
      suppressZeroPayroll: false,
      enforceLetter: "Not Required",
      numberSeries: { type: "Default Serial Number" },
      mailTemplate: "None",
      enableDigitalSignature: false,
      customFields: [],
      workflow: { canRequest: false, autoApproval: false, hrApproval: true, managerApproval: false }
    };
    onAddTemplate(tpl);
  };

  const triggerPreview = (item: typeof GALLERY_TEMPLATES[0]) => {
    const tpl: LetterTemplate = {
      id: `gallery-preview-${Date.now()}`,
      name: item.name,
      category: item.category,
      description: item.description,
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
    onPreview(tpl);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <button 
            onClick={onBack}
            className="flex items-center gap-1.5 text-xs font-black uppercase text-muted-foreground hover:text-foreground transition-colors mb-2"
          >
            <ArrowLeft size={14} /> Back to My Templates
          </button>
          <h2 className="text-xl font-black text-foreground uppercase tracking-tight">Template Gallery</h2>
          <p className="text-xs text-muted-foreground font-semibold">Choose from professional templates to quickly create your letter template.</p>
        </div>
        <div className="relative w-full sm:w-72">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input 
            type="text"
            placeholder="Search gallery templates..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs font-semibold bg-card border border-border rounded-xl outline-none focus:border-foreground/30 transition-all"
          />
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((item, idx) => (
          <div 
            key={idx} 
            className="bg-card border border-border rounded-[24px] p-6 hover:shadow-xl hover:border-foreground/20 transition-all duration-300 group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 rounded-2xl bg-secondary flex items-center justify-center group-hover:bg-foreground group-hover:text-primary-foreground transition-all duration-350 shadow-sm">
                   <FileText size={22} />
                </div>
                <button 
                  onClick={() => triggerPreview(item)}
                  className="w-8 h-8 rounded-full border border-border flex items-center justify-center text-muted-foreground hover:bg-secondary hover:text-foreground transition-all"
                  title="Preview template design"
                >
                   <Eye size={14} />
                </button>
              </div>
              
              <div className="space-y-2">
                 <h4 className="text-[13px] font-black text-foreground uppercase tracking-tight">{item.name}</h4>
                 <p className="text-[11px] text-muted-foreground leading-relaxed min-h-[50px]">{item.description}</p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-border/50">
               <Button 
                 onClick={() => handleAdd(item)}
                 className="w-full h-9 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest gap-2 hover:bg-foreground/90 transition-all"
               >
                  <Plus size={12} strokeWidth={3} />
                  Add to My Templates
               </Button>
            </div>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="col-span-full text-center py-12 border-2 border-dashed border-border rounded-[32px] bg-secondary/5">
            <p className="text-xs font-bold text-muted-foreground">No matching templates found in our gallery.</p>
          </div>
        )}
      </div>
    </div>
  );
}
