import { useState, useRef } from "react";
import { 
  X, 
  ChevronRight, 
  ChevronLeft, 
  Upload, 
  Plus, 
  Trash2, 
  Check, 
  AlertCircle, 
  FileText, 
  Download,
  Info,
  Settings,
  Shield,
  Layers,
  Search
} from "lucide-react";
import { useDispatch } from "react-redux";
import { addTemplate, updateTemplate, LetterTemplate, CustomField } from "@/store/slices/letterSlice";
import { addNotification } from "@/store/slices/notificationSlice";
import { Button } from "@/app/components/ui/button";
import { MasterSelect } from "@/app/components/ui/MasterSelect";

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

export function TemplateWizard({ isOpen, onClose, editingTemplate }: TemplateWizardProps) {
  const dispatch = useDispatch();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<Partial<LetterTemplate>>(
    editingTemplate || {
      name: "",
      category: "",
      description: "",
      enabled: true,
      owner: [],
      suppressZeroPayroll: false,
      enforceLetter: "Not Required",
      numberSeries: { type: "Default Serial Number" },
      mailTemplate: "None",
      enableDigitalSignature: false,
      customFields: [],
      workflow: { canRequest: false, autoApproval: false, hrApproval: true, managerApproval: false }
    }
  );

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

  const handleSave = () => {
    if (!formData.name) {
      dispatch(addNotification({ type: "error", message: "Template name is required" }));
      return;
    }

    const template: LetterTemplate = {
      ...(formData as LetterTemplate),
      id: formData.id || `tpl-${Date.now()}`,
      lastModified: new Date().toISOString().split('T')[0]
    };

    if (editingTemplate) {
      dispatch(updateTemplate(template));
      dispatch(addNotification({ type: "success", message: "Template updated successfully" }));
    } else {
      dispatch(addTemplate(template));
      dispatch(addNotification({ type: "success", message: "Template created successfully" }));
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-card w-full max-w-4xl max-h-[90vh] rounded-3xl border border-border shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-300">
        
        {/* Header */}
        <div className="px-8 py-6 border-b border-border flex items-center justify-between bg-secondary/20">
          <div>
            <h2 className="text-xl font-black text-foreground uppercase tracking-tight">
              {editingTemplate ? "Edit Letter Template" : "Create New Template"}
            </h2>
            <p className="text-xs text-muted-foreground font-bold uppercase tracking-widest mt-1">Wizard Step {step} of 3</p>
          </div>
          <button onClick={onClose} className="w-10 h-10 rounded-full border border-border flex items-center justify-center hover:bg-secondary transition-all">
            <X size={18} />
          </button>
        </div>

        {/* Stepper */}
        <div className="px-8 py-4 bg-secondary/10 border-b border-border flex items-center justify-between">
          {STEPS.map((s, i) => (
            <div key={s.id} className="flex items-center flex-1 last:flex-none">
              <div className={`flex items-center gap-3 transition-all ${step >= s.id ? "text-foreground" : "text-muted-foreground"}`}>
                <div className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs border-2 transition-all ${
                  step === s.id ? "bg-foreground text-primary-foreground border-foreground shadow-lg shadow-foreground/20" : 
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

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-8 space-y-8 no-scrollbar">
          {step === 1 && <Step1 formData={formData} updateField={updateField} updateNestedField={updateNestedField} />}
          {step === 2 && <Step2 formData={formData} updateField={updateField} fileInputRef={fileInputRef} />}
          {step === 3 && <Step3 formData={formData} updateNestedField={updateNestedField} />}
        </div>

        {/* Footer */}
        <div className="px-8 py-6 border-t border-border bg-secondary/10 flex items-center justify-between">
          <Button variant="outline" onClick={step === 1 ? onClose : prev} className="h-10 px-6 rounded-xl font-bold text-xs uppercase tracking-widest gap-2">
            <ChevronLeft size={14} />
            {step === 1 ? "Cancel" : "Previous"}
          </Button>
          
          <div className="flex items-center gap-3">
            <Button variant="ghost" onClick={handleSave} className="h-10 px-6 rounded-xl font-bold text-xs uppercase tracking-widest">
              Save Draft
            </Button>
            {step < 3 ? (
              <Button onClick={next} className="h-10 px-8 rounded-xl font-bold text-xs uppercase tracking-widest gap-2 bg-foreground text-primary-foreground hover:bg-accent">
                Next Step
                <ChevronRight size={14} />
              </Button>
            ) : (
              <Button onClick={handleSave} className="h-10 px-8 rounded-xl font-bold text-xs uppercase tracking-widest gap-2 bg-foreground text-primary-foreground hover:bg-accent shadow-xl shadow-foreground/10">
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
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-in slide-in-from-right-4 duration-500">
      <div className="space-y-6">
        <div className="space-y-2">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Template Title</label>
          <input 
            type="text" 
            value={formData.name}
            onChange={(e) => updateField('name', e.target.value)}
            className="flat-input h-10 w-full text-sm px-4" 
            placeholder="e.g. Standard Offer Letter" 
          />
        </div>

        <div className="space-y-2">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Category</label>
          <MasterSelect
            masterName="LetterCategory"
            value={formData.category}
            onChange={(v) => updateField('category', v)}
          />
        </div>

        <div className="space-y-2">
          <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Description</label>
          <textarea 
            value={formData.description}
            onChange={(e) => updateField('description', e.target.value)}
            className="flat-input min-h-[80px] w-full text-sm px-4 py-2" 
            placeholder="Brief description of the template purpose..." 
          />
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Enforce Letter</label>
            <select 
              value={formData.enforceLetter}
              onChange={(e) => updateField('enforceLetter', e.target.value)}
              className="flat-input h-10 w-full text-sm px-3"
            >
              {ENFORCE_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Mail Template</label>
            <select 
              value={formData.mailTemplate}
              onChange={(e) => updateField('mailTemplate', e.target.value)}
              className="flat-input h-10 w-full text-sm px-3"
            >
              {MAIL_TEMPLATES.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="p-5 rounded-2xl border border-border bg-secondary/20 space-y-4">
           <div className="flex items-center justify-between">
              <span className="text-[10px] font-black text-foreground uppercase tracking-widest">Number Series</span>
              <select 
                value={formData.numberSeries?.type}
                onChange={(e) => updateNestedField('numberSeries', 'type', e.target.value)}
                className="bg-transparent text-[10px] font-bold text-primary uppercase tracking-tighter outline-none cursor-pointer"
              >
                <option value="Default Serial Number">Default</option>
                <option value="Custom Series">Custom</option>
              </select>
           </div>
           
           {formData.numberSeries?.type === "Custom Series" ? (
             <div className="grid grid-cols-3 gap-3">
               <div className="space-y-1">
                 <span className="text-[8px] font-black text-muted-foreground uppercase">Prefix</span>
                 <input 
                  type="text" 
                  value={formData.numberSeries.prefix}
                  onChange={(e) => updateNestedField('numberSeries', 'prefix', e.target.value)}
                  className="flat-input h-8 w-full text-[10px] px-2" 
                 />
               </div>
               <div className="space-y-1">
                 <span className="text-[8px] font-black text-muted-foreground uppercase">Start</span>
                 <input 
                  type="text" 
                  value={formData.numberSeries.startNumber}
                  onChange={(e) => updateNestedField('numberSeries', 'startNumber', e.target.value)}
                  className="flat-input h-8 w-full text-[10px] px-2" 
                 />
               </div>
               <div className="space-y-1">
                 <span className="text-[8px] font-black text-muted-foreground uppercase">Suffix</span>
                 <input 
                  type="text" 
                  value={formData.numberSeries.suffix}
                  onChange={(e) => updateNestedField('numberSeries', 'suffix', e.target.value)}
                  className="flat-input h-8 w-full text-[10px] px-2" 
                 />
               </div>
             </div>
           ) : (
             <p className="text-[11px] text-muted-foreground italic">System will automatically assign next available serial number.</p>
           )}
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
             <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Template Owners</label>
             <span className="text-[9px] font-bold text-primary">Multi-select</span>
          </div>
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
                  className={`px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider border transition-all ${
                    isSelected ? "bg-foreground text-primary-foreground border-foreground shadow-md" : "bg-card border-border text-muted-foreground hover:border-muted"
                  }`}
                >
                  {owner}
                </button>
              );
            })}
          </div>
        </div>

        <div className="space-y-3 pt-2">
          <div className="flex items-center gap-3">
             <input 
              type="checkbox" 
              checked={formData.enabled}
              onChange={(e) => updateField('enabled', e.target.checked)}
              id="enabled"
             />
             <label htmlFor="enabled" className="text-xs font-bold text-foreground cursor-pointer">Enabled Status</label>
          </div>
          <div className="flex items-center gap-3">
             <input 
              type="checkbox" 
              checked={formData.suppressZeroPayroll}
              onChange={(e) => updateField('suppressZeroPayroll', e.target.checked)}
              id="suppress"
             />
             <label htmlFor="suppress" className="text-xs font-bold text-foreground cursor-pointer">Suppress Zero Payroll Values</label>
          </div>
          <div className="flex items-center gap-3">
             <input 
              type="checkbox" 
              checked={formData.enableDigitalSignature}
              onChange={(e) => updateField('enableDigitalSignature', e.target.checked)}
              id="digisign"
             />
             <label htmlFor="digisign" className="text-xs font-bold text-foreground cursor-pointer">Enable Digital Signature (PFX)</label>
          </div>
        </div>
      </div>

      {/* Custom Fields Builder */}
      <div className="md:col-span-2 pt-4 border-t border-border mt-4">
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

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in slide-in-from-right-4 duration-500">
      <div className="text-center space-y-2">
        <h3 className="text-lg font-black text-foreground uppercase tracking-tight">Upload Document Template</h3>
        <p className="text-xs text-muted-foreground max-w-md mx-auto">
          Upload your standardized letter template in Microsoft Word format (.doc or .docx). 
          Ensure all placeholders like {"{{employee_name}}"} are correctly used.
        </p>
      </div>

      {!formData.templateFile ? (
        <div 
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => { e.preventDefault(); setIsDragging(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
          className={`border-3 border-dashed rounded-3xl p-12 text-center cursor-pointer transition-all ${
            isDragging ? "border-foreground bg-secondary/50 scale-[0.98]" : "border-border hover:border-muted hover:bg-secondary/20"
          }`}
        >
          <input 
            ref={fileInputRef}
            type="file" 
            className="hidden" 
            accept=".doc,.docx"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
          />
          <div className="w-20 h-20 rounded-2xl bg-secondary flex items-center justify-center mx-auto mb-6">
            <Upload size={32} className="text-muted-foreground" />
          </div>
          <p className="text-base font-bold text-foreground uppercase tracking-wide">Drag & Drop Template here</p>
          <p className="text-xs text-muted-foreground mt-2">Or click to browse from your device</p>
          <div className="mt-8 flex items-center justify-center gap-4">
             <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest bg-secondary px-3 py-1 rounded-full border border-border flex items-center gap-2">
               <FileText size={12} /> .DOC / .DOCX
             </span>
             <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest bg-secondary px-3 py-1 rounded-full border border-border flex items-center gap-2">
               <Check size={12} /> MAX 5MB
             </span>
          </div>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-3xl p-6 flex items-center justify-between shadow-xl animate-in zoom-in-95 duration-300">
          <div className="flex items-center gap-6">
            <div className="w-14 h-14 rounded-2xl bg-foreground text-primary-foreground flex items-center justify-center shadow-lg shadow-foreground/20">
              <FileText size={24} />
            </div>
            <div>
              <p className="text-sm font-black text-foreground truncate max-w-xs">{formData.templateFile.name}</p>
              <p className="text-[10px] font-bold text-green-500 uppercase tracking-widest flex items-center gap-1.5 mt-1">
                <Check size={10} strokeWidth={3} />
                {(formData.templateFile.size / 1024).toFixed(1)} KB · Ready to Publish
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => updateField('templateFile', null)}
              className="w-10 h-10 rounded-xl border border-border flex items-center justify-center hover:bg-red-50 hover:text-red-500 transition-all group"
              title="Remove template"
            >
              <Trash2 size={16} />
            </button>
            <button className="h-10 px-4 rounded-xl bg-secondary text-foreground text-[10px] font-black uppercase tracking-widest hover:bg-border transition-all">
               Replace
            </button>
          </div>
        </div>
      )}

      {/* Template Preview Mini-Guide */}
      <div className="bg-blue-50/50 border border-blue-100 rounded-2xl p-4 flex gap-4">
        <Info className="text-blue-500 shrink-0 mt-0.5" size={16} />
        <div className="space-y-1">
          <h4 className="text-xs font-bold text-blue-900 uppercase tracking-wider">Formatting Instructions</h4>
          <p className="text-[11px] text-blue-800/70 leading-relaxed">
            Ensure your document contains no macros. All dynamic fields should be enclosed in double curly braces, 
            matching the available placeholders in the side panel.
          </p>
        </div>
      </div>
    </div>
  );
}

function Step3({ formData, updateNestedField }: any) {
  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in slide-in-from-right-4 duration-500">
      <div className="text-center space-y-2">
        <h3 className="text-lg font-black text-foreground uppercase tracking-tight">Workflow & Approvals</h3>
        <p className="text-xs text-muted-foreground">Configure who can request this letter and the approval chain required for issuance.</p>
      </div>

      <div className="space-y-6">
        <div className="flex items-center justify-between p-6 rounded-3xl border border-border bg-secondary/10">
          <div className="space-y-1">
             <h4 className="text-sm font-bold text-foreground uppercase tracking-tight">Employee Requests</h4>
             <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-widest">Can employees request for this letter via ESS portal?</p>
          </div>
          <select 
            value={formData.workflow?.canRequest ? "Yes" : "No"}
            onChange={(e) => updateNestedField('workflow', 'canRequest', e.target.value === "Yes")}
            className="flat-input h-10 w-24 text-xs px-3 font-bold uppercase tracking-widest"
          >
            <option>No</option>
            <option>Yes</option>
          </select>
        </div>

        {formData.workflow?.canRequest && (
          <div className="p-8 rounded-3xl border-2 border-primary/20 bg-primary/5 space-y-8 animate-in zoom-in-95 duration-500">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                 <h4 className="text-xs font-black text-foreground uppercase tracking-widest flex items-center gap-2">
                   <CheckCircle size={14} className="text-green-500" />
                   Auto Approval
                 </h4>
                 <p className="text-[10px] text-muted-foreground font-medium">Letters will be generated immediately without approval</p>
              </div>
              <input 
                type="checkbox" 
                checked={formData.workflow?.autoApproval}
                onChange={(e) => updateNestedField('workflow', 'autoApproval', e.target.checked)}
                className="w-10 h-6 rounded-full appearance-none bg-border checked:bg-green-500 relative transition-all cursor-pointer before:content-[''] before:absolute before:w-4 before:h-4 before:bg-white before:rounded-full before:top-1 before:left-1 checked:before:left-5 before:transition-all"
              />
            </div>

            {!formData.workflow?.autoApproval && (
              <div className="space-y-4 pt-4 border-t border-primary/10">
                <p className="text-[10px] font-black text-primary uppercase tracking-[0.2em] mb-4">Approval Chain</p>
                
                <div className="flex items-center justify-between p-4 rounded-2xl bg-card border border-border">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center text-foreground font-black text-xs">01</div>
                    <span className="text-xs font-bold text-foreground uppercase tracking-wider">Reporting Manager Approval</span>
                  </div>
                  <input 
                    type="checkbox" 
                    checked={formData.workflow?.managerApproval}
                    onChange={(e) => updateNestedField('workflow', 'managerApproval', e.target.checked)}
                  />
                </div>

                <div className="flex items-center justify-between p-4 rounded-2xl bg-card border border-border">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center text-foreground font-black text-xs">02</div>
                    <span className="text-xs font-bold text-foreground uppercase tracking-wider">HR Business Partner Approval</span>
                  </div>
                  <input 
                    type="checkbox" 
                    checked={formData.workflow?.hrApproval}
                    onChange={(e) => updateNestedField('workflow', 'hrApproval', e.target.checked)}
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
         <h4 className="text-xs font-black text-foreground uppercase tracking-widest flex items-center gap-2">
           <Layers size={14} className="text-primary" />
           Custom Input Fields
         </h4>
         <button 
          onClick={addField}
          className="text-[10px] font-black text-primary uppercase tracking-widest hover:underline flex items-center gap-1"
         >
           <Plus size={12} /> Add Field
         </button>
      </div>

      <div className="space-y-3">
        {fields.map((f: any, i: number) => (
          <div key={f.id} className="p-4 rounded-2xl bg-secondary/10 border border-border flex items-start gap-4 animate-in slide-in-from-left-4 duration-300">
             <div className="w-6 h-6 rounded bg-foreground/5 flex items-center justify-center text-[10px] font-black text-muted-foreground shrink-0 mt-1">{i + 1}</div>
             <div className="flex-1 grid grid-cols-1 sm:grid-cols-4 gap-4">
               <div className="sm:col-span-1 space-y-1">
                 <span className="text-[8px] font-black text-muted-foreground uppercase">Field Label</span>
                 <input 
                  type="text" 
                  value={f.label}
                  onChange={(e) => updateField(f.id, 'label', e.target.value)}
                  className="flat-input h-8 w-full text-xs px-2" 
                  placeholder="e.g. Reason"
                 />
               </div>
               <div className="sm:col-span-1 space-y-1">
                 <span className="text-[8px] font-black text-muted-foreground uppercase">Input Type</span>
                 <select 
                  value={f.type}
                  onChange={(e) => updateField(f.id, 'type', e.target.value)}
                  className="flat-input h-8 w-full text-xs px-2"
                 >
                   {["Text", "Number", "Date", "Dropdown", "Textarea", "Checkbox", "File Upload"].map(t => <option key={t}>{t}</option>)}
                 </select>
               </div>
               <div className="sm:col-span-1 flex items-end pb-2 gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={f.required}
                      onChange={(e) => updateField(f.id, 'required', e.target.checked)}
                    />
                    <span className="text-[9px] font-black text-foreground uppercase tracking-widest">Req.</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={f.allowEmployeeEdit}
                      onChange={(e) => updateField(f.id, 'allowEmployeeEdit', e.target.checked)}
                    />
                    <span className="text-[9px] font-black text-foreground uppercase tracking-widest">Emp Edit</span>
                  </label>
               </div>
               <div className="sm:col-span-1 flex items-end justify-end pb-1.5">
                  <button 
                    onClick={() => removeField(f.id)}
                    className="text-red-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
               </div>
             </div>
          </div>
        ))}
        {fields.length === 0 && (
          <div className="p-8 text-center border-2 border-dashed border-border rounded-3xl">
             <p className="text-[11px] font-bold text-muted-foreground">No custom fields defined. Templates will use standard placeholders only.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function CheckCircle({ size, className, strokeWidth }: any) {
  return <Check size={size} className={className} strokeWidth={strokeWidth} />;
}
