import { useState, useRef, useEffect } from "react";
import { 
  X, 
  ChevronRight, 
  ChevronLeft, 
  Upload, 
  Plus, 
  Trash2, 
  Check, 
  FileText, 
  Download,
  Info,
  Settings,
  Layers,
  Eye,
  CheckCircle2
} from "lucide-react";
import { useDispatch } from "react-redux";
import { addTemplate, updateTemplate, LetterTemplate, CustomField } from "@/store/slices/letterSlice";
import { addNotification } from "@/store/slices/notificationSlice";
import { Button } from "@/app/components/ui/button";

interface TemplateWizardProps {
  isOpen: boolean;
  onClose: () => void;
  editingTemplate?: LetterTemplate | null;
}

const STEPS = [
  { id: 1, label: "General Information", icon: Info },
  { id: 2, label: "Upload Template", icon: Upload },
  { id: 3, label: "Workflow Setup", icon: Settings },
];

const ENFORCE_OPTIONS = ["Not Required", "Accept Only", "Acknowledge Only", "Accept or Reject"];
const MAIL_TEMPLATES = ["None", "Letter Default"];
const OWNER_OPTIONS = ["Payroll Admin", "Recruit", "Test", "admin", "recruit1", "recruit2"];
const VISIBILITY_SEGMENTS = ["All Employees", "Confirmed Employees Only", "Sales Team Only", "Bangalore Branch Only"];

export function TemplateWizard({ isOpen, onClose, editingTemplate }: TemplateWizardProps) {
  const dispatch = useDispatch();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<Partial<LetterTemplate>>({
    name: "",
    category: "General",
    description: "",
    enabled: true,
    owner: [],
    suppressZeroPayroll: false,
    enforceLetter: "Not Required",
    numberSeries: { type: "Default Serial Number", prefix: "REF", startNumber: "1001", suffix: "2026" },
    mailTemplate: "None",
    enableDigitalSignature: false,
    customFields: [],
    workflow: { canRequest: false, autoApproval: false, hrApproval: true, managerApproval: false }
  });

  useEffect(() => {
    if (editingTemplate) {
      setFormData(editingTemplate);
    }
  }, [editingTemplate]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const next = () => setStep(s => Math.min(s + 1, 3));
  const prev = () => setStep(s => Math.max(s - 1, 1));

  const updateField = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const updateNestedField = (parent: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [parent]: { ...(prev as any)[parent], [field]: value }
    }));
  };

  const handleSave = (status: 'draft' | 'published' | 'save') => {
    if (!formData.name) {
      dispatch(addNotification({ type: "error", message: "Template title is required" }));
      return;
    }

    const finalEnabled = status === 'published' ? true : status === 'draft' ? false : !!formData.enabled;

    const template: LetterTemplate = {
      ...(formData as LetterTemplate),
      id: formData.id || `tpl-${Date.now()}`,
      enabled: finalEnabled,
      lastModified: new Date().toISOString().split('T')[0]
    };

    if (editingTemplate) {
      dispatch(updateTemplate(template));
      dispatch(addNotification({ type: "success", message: `Template "${template.name}" updated successfully` }));
    } else {
      dispatch(addTemplate(template));
      dispatch(addNotification({ type: "success", message: `Template "${template.name}" created successfully` }));
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-card w-full max-w-4xl max-h-[92vh] rounded-[32px] border border-border shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-300 text-foreground">
        
        {/* Header */}
        <div className="px-8 py-5 border-b border-border flex items-center justify-between bg-secondary/10">
          <div>
            <h2 className="text-lg font-black uppercase tracking-tight">
              {editingTemplate ? "Edit Letter Template" : "Create New Template"}
            </h2>
            <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">Wizard Step {step} of 3</p>
          </div>
          <button onClick={onClose} className="w-9 h-9 rounded-full border border-border flex items-center justify-center hover:bg-secondary transition-all">
            <X size={16} />
          </button>
        </div>

        {/* Stepper */}
        <div className="px-8 py-4 bg-secondary/5 border-b border-border flex items-center justify-between">
          {STEPS.map((s, i) => (
            <div key={s.id} className="flex items-center flex-1 last:flex-none">
              <div className={`flex items-center gap-3 transition-all ${step >= s.id ? "text-foreground" : "text-muted-foreground"}`}>
                <div className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs border-2 transition-all ${
                  step === s.id ? "bg-foreground text-primary-foreground border-foreground shadow-lg" : 
                  step > s.id ? "bg-green-500 border-green-500 text-white" : "border-border bg-card"
                }`}>
                  {step > s.id ? <Check size={14} strokeWidth={3} /> : s.id}
                </div>
                <span className="text-[10px] font-black uppercase tracking-widest">{s.label}</span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={`h-0.5 flex-1 mx-6 rounded-full ${step > s.id ? "bg-green-500" : "bg-border"}`} />
              )}
            </div>
          ))}
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-8 space-y-8 no-scrollbar">
          {step === 1 && <Step1 formData={formData} updateField={updateField} updateNestedField={updateNestedField} />}
          {step === 2 && <Step2 formData={formData} updateField={updateField} fileInputRef={fileInputRef} />}
          {step === 3 && <Step3 formData={formData} updateNestedField={updateNestedField} />}
        </div>

        {/* Footer */}
        <div className="px-8 py-5 border-t border-border bg-secondary/10 flex items-center justify-between">
          <Button variant="outline" onClick={step === 1 ? onClose : prev} className="h-10 px-5 rounded-xl font-bold text-[10px] uppercase tracking-widest gap-2">
            <ChevronLeft size={14} />
            {step === 1 ? "Cancel" : "Previous"}
          </Button>
          
          <div className="flex items-center gap-3">
            <Button variant="ghost" onClick={() => handleSave('draft')} className="h-10 px-4 rounded-xl font-bold text-[10px] uppercase tracking-widest border border-border hover:bg-secondary">
              Save as Draft
            </Button>
            
            <Button variant="outline" onClick={() => handleSave('save')} className="h-10 px-4 rounded-xl font-bold text-[10px] uppercase tracking-widest border border-border hover:bg-secondary">
              Save Template
            </Button>

            {step < 3 ? (
              <Button onClick={next} className="h-10 px-6 rounded-xl font-bold text-[10px] uppercase tracking-widest gap-2 bg-foreground text-primary-foreground hover:bg-foreground/90">
                Next Step
                <ChevronRight size={14} />
              </Button>
            ) : (
              <Button onClick={() => handleSave('published')} className="h-10 px-6 rounded-xl font-bold text-[10px] uppercase tracking-widest gap-2 bg-foreground text-primary-foreground hover:bg-foreground/90 shadow-xl">
                Publish Template
                <Check size={14} strokeWidth={3} />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function Step1({ formData, updateField, updateNestedField }: any) {
  const numberSeriesType = formData.numberSeries?.type || "Default Serial Number";
  
  // Format preview helper
  const prefix = formData.numberSeries?.prefix || "";
  const startNumber = formData.numberSeries?.startNumber || "";
  const suffix = formData.numberSeries?.suffix || "";
  const previewFormat = numberSeriesType === "Custom Series" 
    ? `${prefix}/${startNumber}/${suffix}`
    : "SL-0001";

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-in slide-in-from-right-4 duration-400">
      <div className="space-y-6">
        <div className="space-y-2">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Template Title *</label>
          <input 
            type="text" 
            value={formData.name}
            onChange={(e) => updateField('name', e.target.value)}
            className="flat-input h-10 w-full text-xs px-4 border border-border rounded-xl bg-card" 
            placeholder="e.g. Standard Offer Letter" 
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Enforce Letter</label>
            <select 
              value={formData.enforceLetter}
              onChange={(e) => updateField('enforceLetter', e.target.value)}
              className="flat-input h-10 w-full text-xs px-3 border border-border rounded-xl bg-card outline-none cursor-pointer"
            >
              {ENFORCE_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Mail Template</label>
            <select 
              value={formData.mailTemplate}
              onChange={(e) => updateField('mailTemplate', e.target.value)}
              className="flat-input h-10 w-full text-xs px-3 border border-border rounded-xl bg-card outline-none cursor-pointer"
            >
              {MAIL_TEMPLATES.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Letter Number Series</label>
          <select
            value={numberSeriesType}
            onChange={(e) => updateNestedField('numberSeries', 'type', e.target.value)}
            className="flat-input h-10 w-full text-xs px-3 border border-border rounded-xl bg-card outline-none cursor-pointer"
          >
            <option value="Default Serial Number">Default Serial Number</option>
            <option value="Custom Series">Custom Series</option>
          </select>
        </div>

        {numberSeriesType === "Custom Series" && (
          <div className="p-4 bg-secondary/20 border border-border rounded-2xl space-y-4 animate-in slide-in-from-top-2 duration-300">
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1">
                <span className="text-[8px] font-black text-muted-foreground uppercase">Prefix</span>
                <input 
                  type="text" 
                  value={formData.numberSeries?.prefix || ""}
                  onChange={(e) => updateNestedField('numberSeries', 'prefix', e.target.value)}
                  className="flat-input h-8 w-full text-xs px-2 border border-border bg-card rounded-lg" 
                  placeholder="REF"
                />
              </div>
              <div className="space-y-1">
                <span className="text-[8px] font-black text-muted-foreground uppercase">Start No.</span>
                <input 
                  type="text" 
                  value={formData.numberSeries?.startNumber || ""}
                  onChange={(e) => updateNestedField('numberSeries', 'startNumber', e.target.value)}
                  className="flat-input h-8 w-full text-xs px-2 border border-border bg-card rounded-lg" 
                  placeholder="001"
                />
              </div>
              <div className="space-y-1">
                <span className="text-[8px] font-black text-muted-foreground uppercase">Suffix</span>
                <input 
                  type="text" 
                  value={formData.numberSeries?.suffix || ""}
                  onChange={(e) => updateNestedField('numberSeries', 'suffix', e.target.value)}
                  className="flat-input h-8 w-full text-xs px-2 border border-border bg-card rounded-lg" 
                  placeholder="2026"
                />
              </div>
            </div>
            <div className="text-[10px] text-muted-foreground font-semibold flex items-center justify-between border-t border-border pt-2">
              <span>Preview Format:</span>
              <span className="font-mono text-foreground font-bold">{previewFormat}</span>
            </div>
          </div>
        )}

        <div className="space-y-2">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Template Description</label>
          <textarea 
            value={formData.description}
            onChange={(e) => updateField('description', e.target.value)}
            className="flat-input min-h-[80px] w-full text-xs px-4 py-2 border border-border rounded-xl bg-card" 
            placeholder="Introduce letter guidelines or terms..." 
          />
        </div>
      </div>

      <div className="space-y-6">
        <div className="space-y-3">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest flex items-center justify-between">
            <span>Select Owner(s) *</span>
            <span className="text-[8px] text-primary">Multi-select Master</span>
          </label>
          <div className="flex flex-wrap gap-2">
            {OWNER_OPTIONS.map(owner => {
              const isSelected = formData.owner?.includes(owner);
              return (
                <button
                  key={owner}
                  type="button"
                  onClick={() => {
                    const next = isSelected 
                      ? formData.owner.filter((o: string) => o !== owner)
                      : [...(formData.owner || []), owner];
                    updateField('owner', next);
                  }}
                  className={`px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase tracking-wider border transition-all ${
                    isSelected ? "bg-foreground text-primary-foreground border-foreground shadow-md" : "bg-card border-border text-muted-foreground hover:border-muted-foreground/30"
                  }`}
                >
                  {owner}
                </button>
              );
            })}
          </div>
        </div>

        <div className="p-5 border border-border rounded-2xl bg-secondary/10 space-y-4">
          <div className="flex items-center gap-3">
             <input 
              type="checkbox" 
              checked={formData.enabled}
              onChange={(e) => updateField('enabled', e.target.checked)}
              id="enabled"
              className="rounded border-border focus:ring-0 w-4 h-4 cursor-pointer"
             />
             <label htmlFor="enabled" className="text-xs font-bold text-foreground cursor-pointer select-none">Enabled Status</label>
          </div>
          
          <div className="flex items-center gap-3">
             <input 
              type="checkbox" 
              checked={formData.suppressZeroPayroll}
              onChange={(e) => updateField('suppressZeroPayroll', e.target.checked)}
              id="suppress"
              className="rounded border-border focus:ring-0 w-4 h-4 cursor-pointer"
             />
             <label htmlFor="suppress" className="text-xs font-bold text-foreground cursor-pointer select-none">Suppress Table Rows with Zero Payroll Values</label>
          </div>

          <div className="flex items-center gap-3 pt-1 border-t border-border">
             <input 
              type="checkbox" 
              checked={formData.enableDigitalSignature}
              onChange={(e) => updateField('enableDigitalSignature', e.target.checked)}
              id="digisign"
              className="rounded border-border focus:ring-0 w-4 h-4 cursor-pointer"
             />
             <label htmlFor="digisign" className="text-xs font-bold text-foreground cursor-pointer select-none">Enable Digital Signature (PFX Certificate Based)</label>
          </div>
        </div>
      </div>

      {/* Dynamic Custom Fields Section */}
      <div className="md:col-span-2 pt-6 border-t border-border mt-4">
        <CustomFieldBuilder 
          fields={formData.customFields || []} 
          onUpdate={(f: any) => updateField('customFields', f)} 
        />
      </div>
    </div>
  );
}

function Step2({ formData, updateField, fileInputRef }: any) {
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = (f: File) => {
    const ext = f.name.split('.').pop()?.toLowerCase();
    if (ext !== 'doc' && ext !== 'docx') {
      alert("Invalid format. Please upload DOC or DOCX.");
      return;
    }
    updateField('templateFile', {
      name: f.name,
      size: f.size,
      url: URL.createObjectURL(f)
    });
  };

  const triggerDownload = () => {
    if (formData.templateFile?.url) {
      const a = document.createElement('a');
      a.href = formData.templateFile.url;
      a.download = formData.templateFile.name;
      a.click();
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in slide-in-from-right-4 duration-400">
      <div className="text-center space-y-2">
        <h3 className="text-lg font-black uppercase tracking-tight">Upload Document Template</h3>
        <p className="text-xs text-muted-foreground max-w-md mx-auto leading-relaxed">
          Upload your standardized letter template in Microsoft Word format (.doc or .docx). 
          Ensure all dynamic custom fields like <code>{"{{reason}}"}</code> match exactly.
        </p>
      </div>

      {!formData.templateFile ? (
        <div 
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => { e.preventDefault(); setIsDragging(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
          className={`border-[3px] border-dashed rounded-[24px] p-12 text-center cursor-pointer transition-all ${
            isDragging ? "border-foreground bg-secondary/50 scale-[0.98]" : "border-border hover:border-muted-foreground/30 hover:bg-secondary/10"
          }`}
        >
          <input 
            ref={fileInputRef}
            type="file" 
            className="hidden" 
            accept=".doc,.docx"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
          />
          <div className="w-16 h-16 rounded-2xl bg-secondary flex items-center justify-center mx-auto mb-5 shadow-sm">
            <Upload size={28} className="text-muted-foreground" />
          </div>
          <p className="text-sm font-black uppercase tracking-wide">Drag & Drop Template here</p>
          <p className="text-[10px] text-muted-foreground mt-1.5">Or click to browse from local drive</p>
          <div className="mt-6 flex items-center justify-center gap-4">
             <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest bg-secondary px-3 py-1 rounded-full border border-border flex items-center gap-2">
               <FileText size={12} /> .DOC / .DOCX
             </span>
             <span className="text-[9px] font-black text-muted-foreground uppercase tracking-widest bg-secondary px-3 py-1 rounded-full border border-border flex items-center gap-2">
               <CheckCircle2 size={12} className="text-green-500" /> MAX 5MB
             </span>
          </div>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-[24px] p-6 flex items-center justify-between shadow-xl animate-in zoom-in-95 duration-350">
          <div className="flex items-center gap-5">
            <div className="w-14 h-14 rounded-2xl bg-foreground text-primary-foreground flex items-center justify-center shadow-lg shadow-foreground/20">
              <FileText size={24} />
            </div>
            <div>
              <p className="text-xs font-black truncate max-w-[280px]">{formData.templateFile.name}</p>
              <p className="text-[9px] font-bold text-green-500 uppercase tracking-widest flex items-center gap-1 mt-1">
                <Check size={12} strokeWidth={3} />
                {(formData.templateFile.size / 1024).toFixed(1)} KB · Ready to Publish
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={triggerDownload}
              className="w-10 h-10 rounded-xl border border-border flex items-center justify-center hover:bg-secondary text-foreground transition-all"
              title="Download Uploaded Template"
            >
              <Download size={15} />
            </button>
            <button 
              onClick={() => updateField('templateFile', null)}
              className="w-10 h-10 rounded-xl border border-border flex items-center justify-center hover:bg-red-50 hover:text-red-500 hover:border-red-200 transition-all text-muted-foreground"
              title="Remove template"
            >
              <Trash2 size={15} />
            </button>
            <button 
              onClick={() => fileInputRef.current?.click()}
              className="h-10 px-4 rounded-xl bg-secondary text-foreground text-[10px] font-black uppercase tracking-widest hover:bg-border transition-all"
            >
               Replace Template
            </button>
            <input 
              ref={fileInputRef}
              type="file" 
              className="hidden" 
              accept=".doc,.docx"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
            />
          </div>
        </div>
      )}

      {/* Guide Info */}
      <div className="bg-blue-50/50 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/50 rounded-2xl p-4 flex gap-4">
        <Info className="text-blue-500 shrink-0 mt-0.5" size={16} />
        <div className="space-y-1">
          <h4 className="text-xs font-bold text-blue-900 dark:text-blue-200 uppercase tracking-wider">File Formatting Instructions</h4>
          <p className="text-[11px] text-blue-800/80 dark:text-blue-300/80 leading-relaxed">
            Ensure your Word document is clean and macro-free. All dynamic custom placeholders should be enclosed in double curly braces (e.g. <code>{"{{reason}}"}</code> or <code>{"{{effective_date}}"}</code>) and match the custom input fields defined in Step 1.
          </p>
        </div>
      </div>
    </div>
  );
}

function Step3({ formData, updateNestedField }: any) {
  const canRequest = formData.workflow?.canRequest ?? false;
  const autoApproval = formData.workflow?.autoApproval ?? false;

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in slide-in-from-right-4 duration-400">
      <div className="text-center space-y-2">
        <h3 className="text-lg font-black uppercase tracking-tight">Workflow & Approval Setup</h3>
        <p className="text-xs text-muted-foreground leading-relaxed">Configure if employees can request this document through the ESS portal and customize the review cycle.</p>
      </div>

      <div className="space-y-6">
        <div className="flex items-center justify-between p-6 rounded-[24px] border border-border bg-secondary/15">
          <div className="space-y-0.5">
             <h4 className="text-xs font-black uppercase tracking-tight">Can Employees Request for Letter?</h4>
             <p className="text-[10px] text-muted-foreground font-semibold uppercase tracking-wider">Toggle ESS portal accessibility</p>
          </div>
          <select 
            value={canRequest ? "Yes" : "No"}
            onChange={(e) => updateNestedField('workflow', 'canRequest', e.target.value === "Yes")}
            className="flat-input h-10 w-24 text-xs px-3 border border-border bg-card rounded-xl outline-none font-bold uppercase tracking-widest cursor-pointer"
          >
            <option>No</option>
            <option>Yes</option>
          </select>
        </div>

        {canRequest && (
          <div className="p-6 rounded-[24px] border-2 border-primary/20 bg-primary/5 space-y-6 animate-in zoom-in-95 duration-450">
            
            {/* Employee Request Visibility */}
            <div className="space-y-2 pb-4 border-b border-primary/10">
              <label className="text-[10px] font-black text-foreground uppercase tracking-widest">Employee Request Visibility Settings</label>
              <select
                multiple
                value={formData.workflow?.visibilitySegments || ["All Employees"]}
                onChange={(e) => {
                  const opts = Array.from(e.target.selectedOptions, option => option.value);
                  updateNestedField('workflow', 'visibilitySegments', opts);
                }}
                className="flat-input w-full text-xs p-2 border border-border bg-card rounded-xl outline-none min-h-[80px]"
              >
                {VISIBILITY_SEGMENTS.map(seg => <option key={seg} value={seg}>{seg}</option>)}
              </select>
              <p className="text-[9px] text-muted-foreground italic">Hold Ctrl (or Cmd) to select multiple target categories of employees.</p>
            </div>

            {/* Auto Approval Check */}
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                 <h4 className="text-xs font-black uppercase tracking-widest flex items-center gap-1.5">
                   Auto Approval
                 </h4>
                 <p className="text-[10px] text-muted-foreground font-semibold">Generate letters instantly without HR or Manager approval</p>
              </div>
              <input 
                type="checkbox" 
                checked={autoApproval}
                onChange={(e) => updateNestedField('workflow', 'autoApproval', e.target.checked)}
                className="rounded border-border focus:ring-0 w-4 h-4 cursor-pointer"
              />
            </div>

            {/* Approval workflow section */}
            {!autoApproval && (
              <div className="space-y-3 pt-4 border-t border-primary/10 animate-in slide-in-from-top-3 duration-300">
                <p className="text-[9px] font-black text-primary uppercase tracking-widest mb-2">Configure Approval Workflow Chain</p>
                
                <div className="flex items-center justify-between p-4 rounded-xl bg-card border border-border shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center font-black text-xs">1</div>
                    <span className="text-xs font-bold uppercase tracking-wider">Reporting Manager Approval</span>
                  </div>
                  <input 
                    type="checkbox" 
                    checked={formData.workflow?.managerApproval ?? false}
                    onChange={(e) => updateNestedField('workflow', 'managerApproval', e.target.checked)}
                    className="rounded border-border focus:ring-0 w-4 h-4 cursor-pointer"
                  />
                </div>

                <div className="flex items-center justify-between p-4 rounded-xl bg-card border border-border shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center font-black text-xs">2</div>
                    <span className="text-xs font-bold uppercase tracking-wider">HR Business Partner Approval</span>
                  </div>
                  <input 
                    type="checkbox" 
                    checked={formData.workflow?.hrApproval ?? false}
                    onChange={(e) => updateNestedField('workflow', 'hrApproval', e.target.checked)}
                    className="rounded border-border focus:ring-0 w-4 h-4 cursor-pointer"
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function CustomFieldBuilder({ fields, onUpdate }: any) {
  const addField = () => {
    const newField: CustomField = {
      id: `f-${Date.now()}`,
      name: "",
      label: "",
      type: "Text",
      required: false,
      listValues: [],
      allowEmployeeEdit: false
    };
    onUpdate([...fields, newField]);
  };

  const updateField = (id: string, key: string, val: any) => {
    onUpdate(fields.map((f: any) => f.id === id ? { ...f, [key]: val } : f));
  };

  const removeField = (id: string) => {
    onUpdate(fields.filter((f: any) => f.id !== id));
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
         <h4 className="text-xs font-black uppercase tracking-widest flex items-center gap-2">
           <Layers size={14} className="text-primary" />
           Dynamic Custom Input Fields
         </h4>
         <button 
          onClick={addField}
          type="button"
          className="text-[10px] font-black text-primary uppercase tracking-widest hover:underline flex items-center gap-1"
         >
           <Plus size={12} strokeWidth={3} /> Add Field
         </button>
      </div>

      <div className="space-y-3">
        {fields.map((f: any, i: number) => (
          <div key={f.id} className="p-5 rounded-2xl bg-secondary/5 border border-border space-y-4 animate-in slide-in-from-left-4 duration-300">
             <div className="flex items-center justify-between">
               <div className="flex items-center gap-2">
                 <div className="w-6 h-6 rounded bg-secondary flex items-center justify-center text-[10px] font-black text-muted-foreground">{i + 1}</div>
                 <span className="text-[10px] font-black uppercase tracking-wider text-muted-foreground">Field Configuration</span>
               </div>
               <button 
                 onClick={() => removeField(f.id)}
                 type="button"
                 className="text-red-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 p-1.5 rounded-lg transition-all"
               >
                 <Trash2 size={14} />
               </button>
             </div>

             <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
               <div className="space-y-1">
                 <span className="text-[8px] font-black text-muted-foreground uppercase">Field Label *</span>
                 <input 
                  type="text" 
                  value={f.label}
                  onChange={(e) => {
                    const label = e.target.value;
                    const name = label.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
                    updateField(f.id, 'label', label);
                    updateField(f.id, 'name', name);
                  }}
                  className="flat-input h-8 w-full text-xs px-2 border border-border bg-card rounded-lg" 
                  placeholder="e.g. Work Location"
                 />
               </div>
               
               <div className="space-y-1">
                 <span className="text-[8px] font-black text-muted-foreground uppercase">Field Name / Key *</span>
                 <input 
                  type="text" 
                  value={f.name}
                  onChange={(e) => updateField(f.id, 'name', e.target.value)}
                  className="flat-input h-8 w-full text-xs px-2 border border-border bg-card rounded-lg font-mono" 
                  placeholder="e.g. work_location"
                 />
               </div>

               <div className="space-y-1">
                 <span className="text-[8px] font-black text-muted-foreground uppercase">Input Type</span>
                 <select 
                  value={f.type}
                  onChange={(e) => updateField(f.id, 'type', e.target.value)}
                  className="flat-input h-8 w-full text-xs px-2 border border-border bg-card rounded-lg outline-none cursor-pointer"
                 >
                   {["Text", "Number", "Date", "Dropdown", "Textarea", "Checkbox"].map(t => <option key={t}>{t}</option>)}
                 </select>
               </div>
             </div>

             {f.type === "Dropdown" && (
               <div className="space-y-1 animate-in slide-in-from-top-2 duration-200">
                 <span className="text-[8px] font-black text-muted-foreground uppercase">List Values (Comma-separated) *</span>
                 <input 
                  type="text" 
                  value={f.listValues ? f.listValues.join(', ') : ""}
                  onChange={(e) => {
                    const vals = e.target.value.split(',').map(v => v.trim()).filter(Boolean);
                    updateField(f.id, 'listValues', vals);
                  }}
                  className="flat-input h-8 w-full text-xs px-2 border border-border bg-card rounded-lg" 
                  placeholder="e.g. Bangalore, Mumbai, Delhi"
                 />
               </div>
             )}

             <div className="flex items-center gap-6 pt-2 border-t border-border/40">
                <label className="flex items-center gap-2 cursor-pointer select-none">
                  <input 
                    type="checkbox" 
                    checked={f.required}
                    onChange={(e) => updateField(f.id, 'required', e.target.checked)}
                    className="rounded border-border focus:ring-0 w-3.5 h-3.5 cursor-pointer"
                  />
                  <span className="text-[9px] font-black text-foreground uppercase tracking-widest">Required Field</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer select-none">
                  <input 
                    type="checkbox" 
                    checked={f.allowEmployeeEdit}
                    onChange={(e) => updateField(f.id, 'allowEmployeeEdit', e.target.checked)}
                    className="rounded border-border focus:ring-0 w-3.5 h-3.5 cursor-pointer"
                  />
                  <span className="text-[9px] font-black text-foreground uppercase tracking-widest">Allow Employee Edit</span>
                </label>
             </div>
          </div>
        ))}
        {fields.length === 0 && (
          <div className="p-8 text-center border-2 border-dashed border-border rounded-[24px] bg-secondary/5">
             <p className="text-[11px] font-bold text-muted-foreground">No custom fields defined. Templates will use standard placeholders only.</p>
          </div>
        )}
      </div>
    </div>
  );
}
