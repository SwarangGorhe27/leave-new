import React, { useState, useMemo } from "react";
import { 
  FileText, 
  Users, 
  Eye, 
  Send, 
  ChevronRight, 
  ChevronLeft, 
  Search, 
  Filter, 
  Calendar,
  CheckCircle2,
  Clock,
  Shield,
  Download,
  Trash2,
  Paperclip,
  Plus,
  X,
  RefreshCw,
  Printer,
  Archive,
  Check,
  AlertCircle,
  File,
  Loader2,
  User
} from "lucide-react";
import { MasterSelect } from "../../../../../components/ui/MasterSelect";
import { SearchableSelect } from "../../../../../components/ui/SearchableSelect";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "../../../../../components/ui/button";
import { Input } from "../../../../../components/ui/input";
import { Badge } from "../../../../../components/ui/badge";
import { Checkbox } from "../../../../../components/ui/checkbox";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "../../../../../components/ui/select";
import { Textarea } from "../../../../../components/ui/textarea";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "../../../../../components/ui/table";
import { employees } from "../../../../../components/employees/mockData";
import { LetterBatch, LetterType, ApprovalWorkflow, LetterTemplate } from "./types";
import { MOCK_TEMPLATES } from "./mockData";
import { cn } from "../../../../../components/ui/utils";

interface LetterWizardProps {
  onCancel: () => void;
  onComplete: (batch: LetterBatch) => void;
  onSaveDraft: (batch: Partial<LetterBatch>, currentStep: number) => void;
  initialData?: Partial<LetterBatch>;
  initialStep?: number;
}

export function LetterWizard({ onCancel, onComplete, onSaveDraft, initialData, initialStep }: LetterWizardProps) {
  const [step, setStep] = useState(initialStep || 1);
  const [formData, setFormData] = useState<Partial<LetterBatch>>(initialData || {
    letterType: "Offer Letter",
    approvalWorkflow: "No Approval Required",
    effectiveDate: new Date().toISOString().split('T')[0],
    publishDate: new Date().toISOString().split('T')[0],
    selectedEmployeeIds: [],
    attachmentUrls: [],
    status: "Draft",
    remarks: "",
    authorisedSignatory: "",
    purpose: "",
    generationMode: "Multiple",
    employeeType: "All Employees"
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  const [searchQuery, setSearchQuery] = useState("");
  const [templateSearch, setTemplateSearch] = useState("");
  const [filters, setFilters] = useState({
    department: "All",
    designation: "All",
    location: "All",
    status: "All",
    employeeType: "All"
  });
  const [previewEmployeeId, setPreviewEmployeeId] = useState<string>("");
  const [uploadingFile, setUploadingFile] = useState(false);

  const filteredTemplates = useMemo(() => {
    let filtered = MOCK_TEMPLATES;
    if (formData.letterType) {
      filtered = filtered.filter(t => t.type === formData.letterType);
    }
    if (templateSearch) {
      const s = templateSearch.toLowerCase();
      filtered = filtered.filter(t => 
        t.name.toLowerCase().includes(s) || 
        t.type.toLowerCase().includes(s)
      );
    }
    return filtered;
  }, [formData.letterType, templateSearch]);

  const currentTemplate = useMemo(() => 
    MOCK_TEMPLATES.find(t => t.id === formData.templateId),
  [formData.templateId]);

  const filteredEmployees = useMemo(() => {
    return employees.filter(emp => {
      const matchesSearch = 
        emp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        emp.employeeId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        emp.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
        emp.designation.toLowerCase().includes(searchQuery.toLowerCase()) ||
        emp.email.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesDept = filters.department === "All" || emp.department === filters.department;
      const matchesDesig = filters.designation === "All" || emp.designation === filters.designation;
      const matchesLoc = filters.location === "All" || emp.location === filters.location;
      const matchesStatus = filters.status === "All" || emp.status === filters.status;

      let matchesType = true;
      if (formData.employeeType === "Current Employees") {
        matchesType = emp.status === "Active" || emp.status === "On Leave";
      } else if (formData.employeeType === "Resigned Employees") {
        matchesType = emp.status === "Inactive";
      }
      
      return matchesSearch && matchesDept && matchesDesig && matchesLoc && matchesStatus && matchesType;
    });
  }, [searchQuery, filters, formData.employeeType]);

  // Set default preview employee when entering step 3
  useMemo(() => {
    if (step === 3 && !previewEmployeeId && formData.selectedEmployeeIds?.length) {
      setPreviewEmployeeId(formData.selectedEmployeeIds[0]);
    }
  }, [step, formData.selectedEmployeeIds, previewEmployeeId]);

  const canGoNext = () => {
    if (step === 1) return formData.letterType && formData.templateId && formData.approvalWorkflow && formData.effectiveDate;
    if (step === 2) return (formData.selectedEmployeeIds?.length ?? 0) > 0;
    if (step === 3) return true;
    return true;
  };

  const handleSaveDraft = () => {
    // Validation
    if (!formData.letterType || !formData.templateId) {
      alert("Please select at least a Letter Type and Template to save a draft.");
      return;
    }

    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      onSaveDraft({
        ...formData,
        status: "Draft",
        updatedAt: new Date().toISOString()
      }, step);
      alert("Draft saved successfully.");
    }, 1000);
  };

  const nextStep = () => {
    if (step === 2) {
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        setStep(step + 1);
      }, 800);
    } else if (step === 4) {
      // Handled by publish button
    } else {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
      return;
    }

    onCancel();
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Stepper Header */}
      <div className="bg-card/50 backdrop-blur-md border-b border-border px-8 py-4 sticky top-0 z-30">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-8">
            <StepItem n={1} label="Configuration" active={step === 1} completed={step > 1} Icon={FileText} />
            <div className="h-px w-8 bg-border" />
            <StepItem n={2} label="Employees" active={step === 2} completed={step > 2} Icon={Users} />
            <div className="h-px w-8 bg-border" />
            <StepItem n={3} label="Preview" active={step === 3} completed={step > 3} Icon={Eye} />
            <div className="h-px w-8 bg-border" />
            <StepItem n={4} label="Publish" active={step === 4} completed={step > 4} Icon={Send} />
          </div>
          <Button variant="ghost" size="sm" onClick={onCancel} className="text-muted-foreground hover:text-foreground">
            <X className="w-4 h-4 mr-2" />
            Cancel
          </Button>
        </div>
      </div>

      {/* Step Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto p-8">
          <AnimatePresence mode="wait">
            {step === 1 && (
              <motion.div 
                key="step1" 
                initial={{ opacity: 0, x: 20 }} 
                animate={{ opacity: 1, x: 0 }} 
                exit={{ opacity: 0, x: -20 }}
                className="space-y-8"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <h3 className="text-lg font-bold text-foreground">Letter Configuration</h3>
                    
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Letter Type *</label>
                      <Select 
                        value={formData.letterType} 
                        onValueChange={(v) => setFormData(prev => ({ ...prev, letterType: v as LetterType, templateId: undefined }))}
                      >
                        <SelectTrigger className="h-12 bg-card rounded-xl">
                          <SelectValue placeholder="Select Letter Type" />
                        </SelectTrigger>
                        <SelectContent>
                          {[
                            "Offer Letter", "Appointment Letter", "Confirmation Letter", "Promotion Letter", 
                            "Salary Revision Letter", "Increment Letter", "Transfer Letter", "Experience Letter", 
                            "Relieving Letter", "Warning Letter", "Appreciation Letter", "Custom Template"
                          ].map(t => (
                            <SelectItem key={t} value={t}>{t}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Select Template *</label>
                      <Select 
                        value={formData.templateId} 
                        onValueChange={(v) => setFormData(prev => ({ ...prev, templateId: v }))}
                      >
                        <SelectTrigger className="h-12 bg-card rounded-xl">
                          <SelectValue placeholder="Select Template" />
                        </SelectTrigger>
                        <SelectContent className="max-h-80">
                          <div className="p-2 sticky top-0 bg-background z-10 border-b border-border mb-2">
                            <div className="relative">
                              <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                              <Input 
                                placeholder="Search templates..." 
                                value={templateSearch}
                                onChange={(e) => setTemplateSearch(e.target.value)}
                                className="h-8 pl-8 text-xs bg-muted/50 rounded-lg border-none focus-visible:ring-1 focus-visible:ring-primary"
                                onClick={(e) => e.stopPropagation()}
                              />
                            </div>
                          </div>
                          {filteredTemplates.length > 0 ? (
                            filteredTemplates.map(t => (
                              <SelectItem key={t.id} value={t.id}>
                                <div className="flex flex-col py-1">
                                  <span className="font-bold text-xs">{t.name}</span>
                                  <span className="text-[9px] text-muted-foreground uppercase tracking-widest">{t.type}</span>
                                </div>
                              </SelectItem>
                            ))
                          ) : (
                            <div className="p-4 text-center text-xs text-muted-foreground italic">No templates available.</div>
                          )}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Approval Workflow *</label>
                      <Select 
                        value={formData.approvalWorkflow} 
                        onValueChange={(v) => setFormData(prev => ({ ...prev, approvalWorkflow: v as ApprovalWorkflow }))}
                      >
                        <SelectTrigger className="h-12 bg-card rounded-xl">
                          <SelectValue placeholder="Select Workflow" />
                        </SelectTrigger>
                        <SelectContent>
                          {["No Approval Required", "Reporting Manager", "HR Manager", "Department Head", "Custom Approval Chain"].map(w => (
                            <SelectItem key={w} value={w}>{w}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-6">
                    <h3 className="text-lg font-bold text-foreground">Timeline & Metadata</h3>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Effective Date *</label>
                        <Input 
                          type="date" 
                          value={formData.effectiveDate} 
                          onChange={(e) => setFormData(prev => ({ ...prev, effectiveDate: e.target.value }))}
                          className="h-12 bg-card rounded-xl px-4"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Publish Date</label>
                        <Input 
                          type="date" 
                          value={formData.publishDate} 
                          onChange={(e) => setFormData(prev => ({ ...prev, publishDate: e.target.value }))}
                          className="h-12 bg-card rounded-xl px-4"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Subject Line</label>
                      <Input 
                        placeholder="Letter Subject..." 
                        value={formData.subject}
                        onChange={(e) => setFormData(prev => ({ ...prev, subject: e.target.value }))}
                        className="h-12 bg-card rounded-xl px-4"
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Remarks / Internal Notes</label>
                      <Textarea 
                        placeholder="Add notes for approvers or record..." 
                        value={formData.remarks}
                        onChange={(e) => setFormData(prev => ({ ...prev, remarks: e.target.value }))}
                        className="rounded-xl min-h-[100px] bg-card p-4 resize-none"
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-secondary/20 p-6 rounded-[2rem] border border-border/50">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-sm font-bold text-foreground flex items-center gap-2">
                      <Paperclip className="w-4 h-4 text-primary" />
                      Supporting Documents (Optional)
                    </h4>
                    <div className="relative">
                      <input 
                        type="file" 
                        id="letter-attachments" 
                        multiple 
                        className="hidden" 
                        onChange={(e) => {
                          if (e.target.files) {
                            setUploadingFile(true);
                            setTimeout(() => {
                              const newFiles = Array.from(e.target.files!).map(f => ({
                                name: f.name,
                                size: (f.size / 1024).toFixed(1) + " KB",
                                type: f.type,
                                url: URL.createObjectURL(f)
                              }));
                              setFormData(prev => ({ 
                                ...prev, 
                                attachmentUrls: [...(prev.attachmentUrls || []), ...newFiles.map(nf => nf.name)] 
                              }));
                              setUploadingFile(false);
                            }, 1500);
                          }
                        }}
                      />
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="rounded-lg text-[10px] font-black uppercase tracking-widest"
                        disabled={uploadingFile}
                        onClick={() => document.getElementById('letter-attachments')?.click()}
                      >
                        {uploadingFile ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : <Plus className="w-3 h-3 mr-1" />}
                        {uploadingFile ? "Uploading..." : "Add File"}
                      </Button>
                    </div>
                  </div>
                  
                  {formData.attachmentUrls && formData.attachmentUrls.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
                      {formData.attachmentUrls.map((fileName, idx) => (
                        <div key={idx} className="flex items-center justify-between p-3 bg-card border border-border rounded-xl group">
                          <div className="flex items-center gap-3 overflow-hidden">
                            <File className="w-4 h-4 text-primary shrink-0" />
                            <span className="text-[11px] font-bold text-foreground truncate">{fileName}</span>
                          </div>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="h-6 w-6 rounded-md text-rose-500 hover:bg-rose-50 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={() => setFormData(prev => ({ 
                              ...prev, 
                              attachmentUrls: prev.attachmentUrls?.filter((_, i) => i !== idx) 
                            }))}
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-[11px] text-muted-foreground mb-4">Upload any documents that should be sent along with the letter (e.g., Annexure, Policy docs).</p>
                  )}
                  
                  <div className="flex items-center gap-2 px-3 py-2 bg-primary/5 rounded-lg border border-primary/10">
                    <AlertCircle className="w-3 h-3 text-primary" />
                    <span className="text-[10px] font-bold text-primary">Max size 10MB per file. Formats: PDF, DOCX, XLSX, PNG, JPG.</span>
                  </div>
                </div>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div 
                key="step2" 
                initial={{ opacity: 0, x: 20 }} 
                animate={{ opacity: 1, x: 0 }} 
                exit={{ opacity: 0, x: -20 }}
                className="space-y-8"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 bg-secondary/10 p-6 rounded-[2rem] border border-border/50">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Authorised Signatory *</label>
                    <MasterSelect 
                      masterName="AuthorizedSignatory" 
                      value={formData.authorisedSignatory || ""} 
                      onChange={(v) => setFormData(prev => ({ ...prev, authorisedSignatory: v }))}
                      placeholder="Select Signatory"
                    />
                  </div>

                  <div className="space-y-2 md:col-span-1">
                    <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Generate Letter *</label>
                    <Select 
                      value={formData.generationMode} 
                      onValueChange={(v) => {
                        setFormData(prev => ({ 
                          ...prev, 
                          generationMode: v as "Single" | "Multiple",
                          selectedEmployeeIds: [] // Reset selection on mode change
                        }));
                      }}
                    >
                      <SelectTrigger className="h-11 bg-card rounded-xl">
                        <SelectValue placeholder="Select Mode" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Single">Single</SelectItem>
                        <SelectItem value="Multiple">Multiple</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Employee Type *</label>
                    <Select 
                      value={formData.employeeType} 
                      onValueChange={(v) => setFormData(prev => ({ ...prev, employeeType: v as any }))}
                    >
                      <SelectTrigger className="h-11 bg-card rounded-xl">
                        <SelectValue placeholder="Select Type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="All Employees">All Employees</SelectItem>
                        <SelectItem value="Current Employees">Current Employees</SelectItem>
                        <SelectItem value="Resigned Employees">Resigned Employees</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2 md:col-span-2 lg:col-span-1">
                    <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Purpose *</label>
                    <Textarea 
                      placeholder="Enter purpose/remarks..." 
                      value={formData.purpose}
                      onChange={(e) => setFormData(prev => ({ ...prev, purpose: e.target.value }))}
                      className="h-11 min-h-[44px] bg-card rounded-xl py-2 px-3 resize-none text-xs font-medium"
                    />
                  </div>
                </div>

                {formData.generationMode === "Single" ? (
                  <div className="space-y-6">
                    <div className="max-w-2xl mx-auto space-y-4">
                      <div className="text-center space-y-2">
                        <h4 className="text-lg font-bold text-foreground">Employee Search</h4>
                        <p className="text-xs text-muted-foreground">Search by Name, ID, or Email to generate a single letter.</p>
                      </div>
                      <SearchableSelect 
                        value={formData.selectedEmployeeIds?.[0] || ""} 
                        onChange={(v) => setFormData(prev => ({ ...prev, selectedEmployeeIds: [v] }))}
                        placeholder="Search employee..."
                        options={filteredEmployees.map(emp => ({
                          value: emp.id,
                          label: `${emp.name} (${emp.employeeId}) - ${emp.email}`
                        }))}
                      />
                      
                      {formData.selectedEmployeeIds && formData.selectedEmployeeIds.length > 0 && (
                        <div className="bg-primary/5 border border-primary/10 rounded-2xl p-6 flex items-center gap-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
                          {(() => {
                            const emp = employees.find(e => e.id === formData.selectedEmployeeIds?.[0]);
                            return emp ? (
                              <>
                                <div className={cn("w-12 h-12 rounded-2xl flex items-center justify-center text-sm font-bold text-white shadow-lg", emp.avatarColor)}>
                                  {emp.initials}
                                </div>
                                <div className="flex-1">
                                  <p className="text-sm font-black text-foreground">{emp.name}</p>
                                  <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">{emp.designation} • {emp.department}</p>
                                </div>
                                <Button 
                                  variant="ghost" 
                                  size="icon" 
                                  onClick={() => setFormData(prev => ({ ...prev, selectedEmployeeIds: [] }))}
                                  className="text-rose-500 hover:bg-rose-50 rounded-xl"
                                >
                                  <X size={18} />
                                </Button>
                              </>
                            ) : null;
                          })()}
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                      <h3 className="text-lg font-bold text-foreground">Select Employees</h3>
                      <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
                        <div className="relative flex-1 md:w-64">
                          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                          <Input 
                            placeholder="Search name, ID, department..." 
                            className="pl-10 h-10 bg-card rounded-xl" 
                            value={searchQuery}
                            onChange={(e) => {
                              setSearchQuery(e.target.value);
                              setIsLoading(true);
                              setTimeout(() => setIsLoading(false), 300);
                            }}
                          />
                        </div>
                        
                        <Select value={filters.department} onValueChange={(v) => setFilters(f => ({ ...f, department: v }))}>
                          <SelectTrigger className="h-10 bg-card rounded-xl w-32 text-[10px] font-bold">
                            <SelectValue placeholder="Dept" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="All">All Depts</SelectItem>
                            {Array.from(new Set(employees.map(e => e.department))).map(d => (
                              <SelectItem key={d} value={d}>{d}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>

                        <Select value={filters.location} onValueChange={(v) => setFilters(f => ({ ...f, location: v }))}>
                          <SelectTrigger className="h-10 bg-card rounded-xl w-32 text-[10px] font-bold">
                            <SelectValue placeholder="Location" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="All">All Locations</SelectItem>
                            {Array.from(new Set(employees.map(e => e.location))).map(l => (
                              <SelectItem key={l} value={l}>{l}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>

                        <Button 
                          variant="outline" 
                          size="icon" 
                          className="h-10 w-10 rounded-xl"
                          onClick={() => {
                            setSearchQuery("");
                            setFilters({ department: "All", designation: "All", location: "All", status: "All", employeeType: "All" });
                          }}
                        >
                          <RefreshCw className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="bg-card border border-border rounded-[2rem] overflow-hidden shadow-sm">
                      <Table>
                        <TableHeader className="bg-muted/30">
                          <TableRow className="hover:bg-transparent border-border">
                            <TableHead className="w-[50px]">
                              <Checkbox 
                                checked={formData.selectedEmployeeIds?.length === filteredEmployees.length && filteredEmployees.length > 0}
                                onCheckedChange={(checked) => {
                                  if (checked) {
                                    const newIds = Array.from(new Set([...(formData.selectedEmployeeIds || []), ...filteredEmployees.map(e => e.id)]));
                                    setFormData(prev => ({ ...prev, selectedEmployeeIds: newIds }));
                                  } else {
                                    const remainingIds = (formData.selectedEmployeeIds || []).filter(id => !filteredEmployees.find(fe => fe.id === id));
                                    setFormData(prev => ({ ...prev, selectedEmployeeIds: remainingIds }));
                                  }
                                }}
                              />
                            </TableHead>
                            <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Employee</TableHead>
                            <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Department</TableHead>
                            <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Designation</TableHead>
                            <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Location</TableHead>
                            <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Status</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {isLoading ? (
                            <TableRow>
                              <TableCell colSpan={6} className="h-64">
                                <div className="flex flex-col items-center justify-center space-y-4">
                                  <RefreshCw className="w-8 h-8 text-primary animate-spin" />
                                  <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground animate-pulse">Searching Employees...</p>
                                </div>
                              </TableCell>
                            </TableRow>
                          ) : filteredEmployees.length > 0 ? (
                            filteredEmployees.map((emp) => (
                              <TableRow key={emp.id} className="border-border/50 group hover:bg-secondary/30 transition-colors">
                                <TableCell>
                                  <Checkbox 
                                    checked={formData.selectedEmployeeIds?.includes(emp.id)}
                                    onCheckedChange={(checked) => {
                                      if (checked) setFormData(prev => ({ ...prev, selectedEmployeeIds: [...(prev.selectedEmployeeIds || []), emp.id] }));
                                      else setFormData(prev => ({ ...prev, selectedEmployeeIds: (prev.selectedEmployeeIds || []).filter(id => id !== emp.id) }));
                                    }}
                                  />
                                </TableCell>
                                <TableCell>
                                  <div className="flex items-center gap-3">
                                    <div className={cn("w-8 h-8 rounded-lg flex items-center justify-center text-[10px] font-bold text-white shadow-sm", emp.avatarColor)}>
                                      {emp.initials}
                                    </div>
                                    <div>
                                      <p className="text-sm font-bold text-foreground">{emp.name}</p>
                                      <p className="text-[10px] font-medium text-muted-foreground font-mono uppercase tracking-tighter">{emp.employeeId}</p>
                                    </div>
                                  </div>
                                </TableCell>
                                <TableCell className="text-xs font-semibold text-muted-foreground">{emp.department}</TableCell>
                                <TableCell className="text-xs font-semibold text-muted-foreground">{emp.designation}</TableCell>
                                <TableCell className="text-xs font-semibold text-muted-foreground">{emp.location}</TableCell>
                                <TableCell>
                                  <Badge variant="outline" className="text-[9px] font-black uppercase tracking-widest rounded-md bg-emerald-500/5 text-emerald-500 border-emerald-500/10">
                                    {emp.status}
                                  </Badge>
                                </TableCell>
                              </TableRow>
                            ))
                          ) : (
                            <TableRow>
                              <TableCell colSpan={6} className="h-32 text-center text-xs text-muted-foreground italic uppercase tracking-widest opacity-60">
                                No employees found matching your criteria.
                              </TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 bg-secondary/20 rounded-2xl border border-border/50 text-xs font-bold text-muted-foreground">
                      <p>{formData.selectedEmployeeIds?.length || 0} employees selected</p>
                      <Button variant="ghost" size="sm" onClick={() => setFormData(prev => ({ ...prev, selectedEmployeeIds: [] }))} className="h-8 text-rose-500 hover:text-rose-600 hover:bg-rose-50">
                        Clear Selection
                      </Button>
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {step === 3 && (
              <motion.div 
                key="step3" 
                initial={{ opacity: 0, x: 20 }} 
                animate={{ opacity: 1, x: 0 }} 
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between gap-4">
                  <h3 className="text-lg font-bold text-foreground">Preview & Review</h3>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Previewing for:</span>
                    <Select 
                      value={previewEmployeeId} 
                      onValueChange={(v) => {
                        setIsPreviewLoading(true);
                        setPreviewEmployeeId(v);
                        setTimeout(() => setIsPreviewLoading(false), 500);
                      }}
                    >
                      <SelectTrigger className="h-10 bg-card rounded-xl w-60">
                        <SelectValue placeholder="Select Employee" />
                      </SelectTrigger>
                      <SelectContent>
                        {formData.selectedEmployeeIds?.map(id => {
                          const emp = employees.find(e => e.id === id);
                          return <SelectItem key={id} value={id}>{emp?.name}</SelectItem>
                        })}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  {/* Letter Preview */}
                  <div className="lg:col-span-2 bg-white dark:bg-slate-900 border border-border shadow-2xl rounded-[1.5rem] p-12 min-h-[800px] aspect-[1/1.414] overflow-auto relative">
                    <div className="absolute top-4 right-4 flex gap-2">
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-8 w-8 rounded-lg" 
                        title="Print Preview"
                        onClick={() => {
                          const printContent = document.getElementById('letter-preview-content');
                          if (printContent) {
                            const win = window.open('', '_blank');
                            win?.document.write(`
                              <html>
                                <head>
                                  <title>Print Letter</title>
                                  <style>
                                    body { font-family: sans-serif; padding: 40px; }
                                    @media print { body { padding: 0; } }
                                  </style>
                                </head>
                                <body>
                                  ${printContent.innerHTML}
                                  <script>window.print(); window.close();</script>
                                </body>
                              </html>
                            `);
                            win?.document.close();
                          }
                        }}
                      >
                        <Printer size={14} />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-8 w-8 rounded-lg" 
                        title="Download Sample"
                        onClick={() => {
                          setIsPreviewLoading(true);
                          setTimeout(() => {
                            setIsPreviewLoading(false);
                            alert("Document generated and downloaded as PDF.");
                          }, 1500);
                        }}
                      >
                        <Download size={14} />
                      </Button>
                    </div>

                    {isPreviewLoading ? (
                      <div className="h-full flex flex-col items-center justify-center space-y-4">
                        <RefreshCw className="w-10 h-10 text-primary/20 animate-spin" />
                        <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/40 animate-pulse">Rendering Document...</p>
                      </div>
                    ) : currentTemplate ? (
                      <div 
                        id="letter-preview-content"
                        dangerouslySetInnerHTML={{ 
                          __html: currentTemplate.content
                            .replace(/{{employee_name}}/g, employees.find(e => e.id === previewEmployeeId)?.name || "Employee Name")
                            .replace(/{{employee_id}}/g, employees.find(e => e.id === previewEmployeeId)?.employeeId || "Employee ID")
                            .replace(/{{designation}}/g, employees.find(e => e.id === previewEmployeeId)?.designation || "Designation")
                            .replace(/{{department}}/g, employees.find(e => e.id === previewEmployeeId)?.department || "Department")
                            .replace(/{{joining_date}}/g, employees.find(e => e.id === previewEmployeeId)?.joiningDate || "Joining Date")
                            .replace(/{{effective_date}}/g, formData.effectiveDate || "Effective Date")
                            .replace(/{{salary}}/g, "₹ 8,45,000")
                            .replace(/{{current_date}}/g, new Date().toLocaleDateString())
                        }} 
                      />
                    ) : (
                      <div className="h-full flex flex-col items-center justify-center text-muted-foreground space-y-4 opacity-50">
                        <FileText size={48} />
                        <p className="text-sm font-bold uppercase tracking-widest">No Template Loaded</p>
                      </div>
                    )}
                  </div>

                  {/* Metadata Sidebar */}
                  <div className="space-y-6">
                    <div className="bg-card border border-border rounded-[2rem] p-6 space-y-6">
                      <h4 className="text-[10px] font-black text-muted-foreground uppercase tracking-[0.2em] mb-4">Summary</h4>
                      
                      <PreviewMeta label="Letter Type" value={formData.letterType} />
                      <PreviewMeta label="Workflow" value={formData.approvalWorkflow} />
                      <PreviewMeta label="Employees" value={`${formData.selectedEmployeeIds?.length || 0} Selected`} />
                      <PreviewMeta label="Effective Date" value={formData.effectiveDate} />
                      <PreviewMeta label="Publish Date" value={formData.publishDate} />
                      
                      <div className="pt-4 border-t border-border/50">
                        <p className="text-[10px] font-black text-muted-foreground uppercase tracking-widest mb-2 opacity-60">Internal Remarks</p>
                        <p className="text-xs font-bold text-foreground leading-relaxed italic">
                          "{formData.remarks || "No remarks provided"}"
                        </p>
                      </div>
                    </div>

                    <div className="p-6 rounded-[2rem] bg-amber-500/5 border border-amber-500/10 flex gap-4 items-start">
                      <AlertCircle className="w-5 h-5 text-amber-500 shrink-0" />
                      <p className="text-[11px] font-medium text-amber-600 leading-relaxed">
                        Merge fields have been automatically resolved using the selected employee's data. Please verify all details before publishing.
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {step === 4 && (
              <motion.div 
                key="step4" 
                initial={{ opacity: 0, x: 20 }} 
                animate={{ opacity: 1, x: 0 }} 
                exit={{ opacity: 0, x: -20 }}
                className="flex flex-col items-center justify-center text-center py-12 space-y-8"
              >
                <div className="w-24 h-24 rounded-[2.5rem] bg-primary/10 flex items-center justify-center border border-primary/20 shadow-inner group">
                  <CheckCircle2 className="w-12 h-12 text-primary group-hover:scale-110 transition-transform duration-500" />
                </div>
                
                <div className="space-y-2">
                  <h3 className="text-2xl font-black text-foreground tracking-tight uppercase">Ready to Publish</h3>
                  <p className="text-sm font-bold text-muted-foreground max-w-md mx-auto">
                    The {formData.letterType} batch is prepared for {formData.selectedEmployeeIds?.length} employees. 
                    {formData.approvalWorkflow !== "No Approval Required" ? " It will be routed for approval once sent." : " These will be published immediately."}
                  </p>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full max-w-3xl">
                  <FinalCard label="Letter" value={formData.letterType} Icon={FileText} />
                  <FinalCard label="Recipients" value={`${formData.selectedEmployeeIds?.length}`} Icon={Users} />
                  <FinalCard label="Effective" value={formData.effectiveDate} Icon={Calendar} />
                  <FinalCard label="Workflow" value={formData.approvalWorkflow} Icon={Shield} />
                </div>

                <div className="flex gap-4 pt-8">
                  <Button 
                    variant="outline" 
                    size="lg" 
                    onClick={handleSaveDraft}
                    className="h-14 px-8 rounded-2xl text-xs font-black uppercase tracking-widest"
                  >
                    <Archive className="w-4 h-4 mr-2" /> Save Draft
                  </Button>
                  
                  {formData.approvalWorkflow !== "No Approval Required" ? (
                    <Button 
                      size="lg" 
                      onClick={() => onComplete(formData as LetterBatch)}
                      className="h-14 px-10 rounded-2xl text-xs font-black uppercase tracking-widest bg-primary text-white hover:bg-primary/90 shadow-xl shadow-primary/20"
                    >
                      <Send className="w-4 h-4 mr-2" /> Send for Approval
                    </Button>
                  ) : (
                    <Button 
                      size="lg" 
                      onClick={() => onComplete(formData as LetterBatch)}
                      className="h-14 px-10 rounded-2xl text-xs font-black uppercase tracking-widest bg-emerald-500 text-white hover:bg-emerald-600 shadow-xl shadow-emerald-500/20"
                    >
                      <CheckCircle2 className="w-4 h-4 mr-2" /> Publish Now
                    </Button>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Sticky Footer Actions */}
      <div className="bg-card/80 backdrop-blur-md border-t border-border px-8 py-4 sticky bottom-0 z-30">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Button 
            variant="ghost" 
            onClick={handleBack} 
            className="rounded-xl h-12 px-6 text-xs font-black uppercase tracking-widest"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          
          <div className="flex items-center gap-4">
            {step < 4 && (
              <Button 
                variant="ghost" 
                onClick={handleSaveDraft}
                className="h-12 px-6 rounded-xl text-primary hover:bg-primary/5 text-xs font-black uppercase tracking-widest border border-primary/20"
              >
                <Archive className="w-4 h-4 mr-2" />
                Save Draft
              </Button>
            )}
            {step < 4 ? (
              <Button 
                onClick={nextStep} 
                disabled={!canGoNext()}
                className="h-12 px-10 rounded-xl bg-foreground text-background text-xs font-black uppercase tracking-widest hover:opacity-90 shadow-xl"
              >
                Continue
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}

function StepItem({ n, label, active, completed, Icon }: { n: number, label: string, active: boolean, completed: boolean, Icon: any }) {
  return (
    <div className={cn(
      "flex items-center gap-3 transition-all duration-500",
      active ? "scale-110 opacity-100" : completed ? "opacity-70" : "opacity-40"
    )}>
      <div className={cn(
        "w-10 h-10 rounded-xl flex items-center justify-center border-2 transition-all",
        active ? "bg-primary border-primary text-white shadow-lg shadow-primary/20" : 
        completed ? "bg-emerald-500/10 border-emerald-500 text-emerald-500" : "bg-muted border-border text-muted-foreground"
      )}>
        {completed ? <Check size={18} strokeWidth={3} /> : <Icon size={18} />}
      </div>
      <div className="hidden sm:block text-left">
        <p className={cn("text-[9px] font-black uppercase tracking-widest", active ? "text-primary" : "text-muted-foreground")}>Step 0{n}</p>
        <p className={cn("text-xs font-black tracking-tight", active ? "text-foreground" : "text-muted-foreground")}>{label}</p>
      </div>
    </div>
  );
}

function PreviewMeta({ label, value }: { label: string, value?: string }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest opacity-60">{label}</span>
      <span className="text-xs font-black text-foreground">{value || "-"}</span>
    </div>
  );
}

function FinalCard({ label, value, Icon }: { label: string, value: string, Icon: any }) {
  return (
    <div className="bg-card border border-border p-5 rounded-[2rem] text-left space-y-3 shadow-sm hover:border-primary/30 transition-all group">
      <div className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center text-muted-foreground group-hover:text-primary transition-colors">
        <Icon size={18} />
      </div>
      <div>
        <p className="text-[9px] font-black text-muted-foreground uppercase tracking-widest opacity-60 mb-0.5">{label}</p>
        <p className="text-xs font-black text-foreground truncate">{value}</p>
      </div>
    </div>
  );
}
