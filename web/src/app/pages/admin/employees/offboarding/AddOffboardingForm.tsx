import { useState, useRef, useEffect } from "react";
import { 
  User, 
  FileText, 
  CheckSquare, 
  Clock, 
  ClipboardCheck, 
  Wallet, 
  MessageSquare, 
  Upload,
  X,
  ChevronRight,
  ChevronLeft,
  CheckCircle2,
  Eye,
  RotateCcw,
  Trash2,
  Check
} from "lucide-react";
import { employees } from "../../../../components/employees/mockData";
import { OffboardingData, DocumentFile } from "./types";

const flatInputClass = "w-full px-4 py-3 text-sm font-bold border border-border rounded-xl bg-card focus:outline-none focus:ring-2 focus:ring-primary";

interface UploadedDocument extends DocumentFile {}

interface Props {
  onClose: () => void;
  onSave: (data: OffboardingData) => void;
}

export function AddOffboardingForm({ onClose, onSave }: Props) {
  const [currentStep, setCurrentStep] = useState(1);
  const fileInputRefs = useRef<Record<string, HTMLInputElement>>({});
  const [uploadedDocuments, setUploadedDocuments] = useState<Record<string, UploadedDocument>>({});
  
  // Initialize with structured form data
  const [formData, setFormData] = useState({
    // Basic employee info
    employeeId: "",
    resignationDate: "",
    lastWorkingDay: "",
    noticePeriod: "",
    type: "Voluntary" as const,
    reason: "",
    
    // Step 3 - Approval Workflow
    reportingManagerApproval: "Pending" as const,
    reportingManagerRemarks: "",
    hrApproval: "Pending" as const,
    hrRemarks: "",
    itClearanceApproval: "Pending" as const,
    itRemarks: "",
    finalApprovalRemarks: "",
    
    // Step 4 - Notice Period
    noticeStartDate: "",
    noticeEndDate: "",
    buyoutRequired: false,
    buyoutAmount: 0,
    earlyReleaseApproved: false,
    
    // Step 5 - Clearance Checklist
    laptopReturned: false,
    idCardReturned: false,
    knowledgeTransferDone: false,
    emailAccessDisabled: false,
    assetsCleared: false,
    clearanceRemarks: "",
    
    // Step 6 - Financial Settlement
    leaveEncashment: 0,
    deductions: 0,
    paymentStatus: "Pending" as const,
    paymentMethod: "",
    
    // Step 7 - Exit Interview
    exitInterviewDate: "",
    exitReason: "",
    employeeFeedback: "",
    wouldRejoin: false,
  });
  const totalSteps = 8;

  const [draftMeta, setDraftMeta] = useState<{ savedAt?: string; completedSteps?: number[] } | null>(null);
  const [autoSaved, setAutoSaved] = useState(false);
  const initialLoadRef = useRef(true);

  const selectedEmployee = employees.find(e => e.id === formData.employeeId);

  const steps = [
    { id: 1, title: "Employee Information", icon: User },
    { id: 2, title: "Resignation Details", icon: FileText },
    { id: 3, title: "Approval Workflow", icon: CheckSquare },
    { id: 4, title: "Notice Period", icon: Clock },
    { id: 5, title: "Clearance Checklist", icon: ClipboardCheck },
    { id: 6, title: "Financial Settlement", icon: Wallet },
    { id: 7, title: "Exit Interview", icon: MessageSquare },
    { id: 8, title: "Documents", icon: Upload },
  ];

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }));
  };

  const handleToggle = (field: string) => {
    setFormData((prev: any) => ({ ...prev, [field]: !prev[field] }));
  };

  const calculateNoticeDays = () => {
    if (formData.noticeStartDate && formData.noticeEndDate) {
      const start = new Date(formData.noticeStartDate);
      const end = new Date(formData.noticeEndDate);
      const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
      return Math.max(0, days);
    }
    return 0;
  };

  const nextStep = () => currentStep < totalSteps && setCurrentStep(currentStep + 1);
  const prevStep = () => currentStep > 1 && setCurrentStep(currentStep - 1);

  // Document upload handlers
  const requiredDocuments = [
    "Resignation Letter",
    "Clearance Form",
    "Relieving Letter",
    "Experience Letter",
    "Settlement Copy"
  ];

  const handleDocumentUpload = (docName: string, file: File) => {
    const uploadedAt = new Date().toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });

    setUploadedDocuments(prev => ({
      ...prev,
      [docName]: {
        name: docName,
        fileName: file.name,
        fileSize: file.size,
        uploadedAt,
        file,
        url: URL.createObjectURL(file)
      }
    }));
  };

  const handleViewDocument = (docName: string) => {
    const doc = uploadedDocuments[docName];
    if (doc?.url) {
      window.open(doc.url, '_blank');
    }
  };

  const handleReplaceDocument = (docName: string) => {
    fileInputRefs.current[docName]?.click();
  };

  const handleDeleteDocument = (docName: string) => {
    setUploadedDocuments(prev => {
      const newDocs = { ...prev };
      delete newDocs[docName];
      return newDocs;
    });
  };

  const handleFileInputChange = (docName: string, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleDocumentUpload(docName, file);
    }
    event.target.value = '';
  };

  const allMandatoryUploaded = requiredDocuments.every(doc => uploadedDocuments[doc]);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const handleSave = () => {
    if (!selectedEmployee) {
      alert("Please select an employee first.");
      setCurrentStep(1);
      return;
    }
    if (!allMandatoryUploaded) {
      alert("Please upload all required documents.");
      return;
    }

    // Calculate notice days
    const noticeStartDate = new Date(formData.noticeStartDate);
    const noticeEndDate = new Date(formData.noticeEndDate);
    const noticeDays = Math.ceil(
      (noticeEndDate.getTime() - noticeStartDate.getTime()) / (1000 * 60 * 60 * 24)
    );

    // Calculate clearance progress
    const clearanceItems = [
      formData.laptopReturned,
      formData.idCardReturned,
      formData.knowledgeTransferDone,
      formData.emailAccessDisabled,
      formData.assetsCleared
    ];
    const clearanceProgress = Math.round((clearanceItems.filter(Boolean).length / clearanceItems.length) * 100);

    // Calculate financial settlement
    const finalSettlementAmount = (formData.leaveEncashment || 0) - (formData.deductions || 0);

    // Convert uploaded documents to DocumentFile format
    const documentsRecord: Record<string, DocumentFile> = {};
    Object.entries(uploadedDocuments).forEach(([key, doc]) => {
      documentsRecord[key] = {
        name: doc.name,
        fileName: doc.fileName,
        fileSize: doc.fileSize,
        uploadedAt: doc.uploadedAt,
        uploadStatus: "Uploaded Successfully"
      };
    });

    // Create structured offboarding data
    const offboardingId = `OFF_${selectedEmployee.id}_${Date.now()}`;
    const now = new Date().toISOString();
    const completedSteps = calculateCompletedSteps();

    const offboardingData: OffboardingData = {
      // Basic Info
      offboardingId,
      employeeId: selectedEmployee.id,
      name: selectedEmployee.name,
      initials: selectedEmployee.initials,
      avatarColor: selectedEmployee.avatarColor,
      department: selectedEmployee.department,
      designation: selectedEmployee.designation,
      reportingManager: selectedEmployee.reportingTo || "HR Manager",
      reportingTo: selectedEmployee.reportingTo,

      // Resignation Info
      resignationDate: formData.resignationDate,
      lastWorkingDay: formData.lastWorkingDay,
      noticePeriod: parseInt(formData.noticePeriod) || 0,
      type: formData.type as "Voluntary" | "Involuntary" | "Contractual",
      reason: formData.reason,

      // Step 3: Approval Workflow
      approvalWorkflow: {
        reportingManagerApproval: formData.reportingManagerApproval,
        reportingManagerRemarks: formData.reportingManagerRemarks,
        hrApproval: formData.hrApproval,
        hrRemarks: formData.hrRemarks,
        itClearanceApproval: formData.itClearanceApproval,
        itRemarks: formData.itRemarks,
        finalApprovalRemarks: formData.finalApprovalRemarks,
      },

      // Step 4: Notice Period
      noticeDetails: {
        noticeStartDate: formData.noticeStartDate,
        noticeEndDate: formData.noticeEndDate,
        noticeDays,
        buyoutRequired: formData.buyoutRequired,
        buyoutAmount: formData.buyoutAmount || 0,
        earlyReleaseApproved: formData.earlyReleaseApproved,
      },

      // Step 5: Clearance Checklist
      clearanceChecklist: {
        laptopReturned: formData.laptopReturned,
        idCardReturned: formData.idCardReturned,
        knowledgeTransferDone: formData.knowledgeTransferDone,
        emailAccessDisabled: formData.emailAccessDisabled,
        assetsCleared: formData.assetsCleared,
        clearanceRemarks: formData.clearanceRemarks,
        clearanceProgress,
      },

      // Step 6: Financial Settlement
      financialSettlement: {
        leaveEncashment: formData.leaveEncashment || 0,
        deductions: formData.deductions || 0,
        finalSettlementAmount,
        paymentStatus: formData.paymentStatus,
        paymentMethod: formData.paymentMethod,
      },

      // Step 7: Exit Interview
      exitInterview: {
        exitInterviewDate: formData.exitInterviewDate,
        exitReason: formData.exitReason,
        employeeFeedback: formData.employeeFeedback,
        wouldRejoin: formData.wouldRejoin,
      },

      // Step 8: Documents
      documents: documentsRecord,

      // Metadata
      createdAt: now,
      updatedAt: now,
      status: "In Progress",
      completedSteps,
    };

    // Save to localStorage (simulate API)
    localStorage.setItem(`offboarding-data-${offboardingId}`, JSON.stringify(offboardingData));
    // Clear any draft for this employee since final record saved
    if (selectedEmployee) {
      localStorage.removeItem(`offboarding-draft-${selectedEmployee.id}`);
    }
    onSave(offboardingData);
  };

  // Draft persistence: save/load partial form per employee so they can continue later
  const saveDraft = (employeeId: string) => {
    if (!employeeId) return;
    const completed = calculateCompletedStepsFromData(formData, uploadedDocuments);
    const savedAt = new Date().toISOString();
    const draft = {
      formData,
      uploadedDocuments,
      savedAt,
      completedSteps: completed
    };
    try {
      localStorage.setItem(`offboarding-draft-${employeeId}`, JSON.stringify(draft));
      setDraftMeta({ savedAt, completedSteps: completed });
      // transient UI feedback for autosave
      setAutoSaved(true);
      window.setTimeout(() => setAutoSaved(false), 1400);
      // Also upsert a lightweight record into offboarding-records so the list updates dynamically
      try {
        const RECORDS_KEY = "offboarding-records";
        const raw = localStorage.getItem(RECORDS_KEY);
        const records = raw ? JSON.parse(raw) : [];

        const noticeStatus = (formData.noticeStartDate && formData.noticeEndDate) ? (new Date() > new Date(formData.noticeEndDate) ? "Completed" : "In Notice") : "In Notice";

        const clearanceStatus = (() => {
          const items = [formData.laptopReturned, formData.idCardReturned, formData.knowledgeTransferDone, formData.emailAccessDisabled, formData.assetsCleared];
          const completedCount = items.filter(Boolean).length;
          if (completedCount === 0) return "Pending";
          if (completedCount === items.length) return "Completed";
          return "Partially Completed";
        })();

        const draftExitStatus = (() => {
          // Use completed steps length to decide
          if (completed.length >= 8) return "Completed";
          if (completed.includes(4)) return "In Notice Period";
          if (completed.includes(5) && clearanceStatus !== "Completed") return "Clearance Pending";
          if (completed.includes(3)) return "Approved";
          return "Pending";
        })();

        const recordId = `DRAFT_${employeeId}`;
        const record = {
          id: recordId,
          employeeId,
          name: selectedEmployee?.name || "",
          initials: selectedEmployee?.initials || "",
          avatarColor: selectedEmployee?.avatarColor || "#999",
          department: selectedEmployee?.department || "",
          designation: selectedEmployee?.designation || "",
          reportingManager: selectedEmployee?.reportingTo || "",
          resignationDate: formData.resignationDate || "",
          lastWorkingDay: formData.lastWorkingDay || "",
          noticeStatus,
          exitStatus: draftExitStatus,
          clearanceStatus,
        };

        const idx = records.findIndex((r: any) => r.employeeId === employeeId || r.id === recordId);
        if (idx >= 0) records[idx] = record;
        else records.unshift(record);
        localStorage.setItem(RECORDS_KEY, JSON.stringify(records));
      } catch (err) {
        console.warn('Failed to upsert draft record', err);
      }
    } catch (err) {
      console.warn("Failed to save draft", err);
    }
  };

  const loadDraft = (employeeId: string) => {
    if (!employeeId) return;
    try {
      const raw = localStorage.getItem(`offboarding-draft-${employeeId}`);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (parsed?.formData) setFormData((prev: any) => ({ ...prev, ...parsed.formData }));
      if (parsed?.uploadedDocuments) setUploadedDocuments(parsed.uploadedDocuments);
      // Set draft metadata and move to next incomplete step
      const comp = parsed.completedSteps || calculateCompletedStepsFromData(parsed.formData || {}, parsed.uploadedDocuments || {});
      setDraftMeta({ savedAt: parsed.savedAt, completedSteps: comp });
      const next = Math.min(totalSteps, Math.max(1, (comp?.length || 0) + 1));
      setCurrentStep(next);
    } catch (err) {
      console.warn("Failed to load draft", err);
    }
  };

  const calculateCompletedStepsFromData = (data: any, docs: Record<string, UploadedDocument>) => {
    const completed: number[] = [];
    if (data && data.employeeId) completed.push(1);
    if (data && data.resignationDate && data.lastWorkingDay) completed.push(2);
    if (data && (data.reportingManagerApproval || data.hrApproval || data.itClearanceApproval)) completed.push(3);
    if (data && data.noticeStartDate && data.noticeEndDate) completed.push(4);
    if (data && (data.laptopReturned || data.idCardReturned || data.knowledgeTransferDone || data.emailAccessDisabled || data.assetsCleared)) completed.push(5);
    if (data && (data.leaveEncashment || data.deductions)) completed.push(6);
    if (data && (data.exitInterviewDate || data.exitReason)) completed.push(7);
    const allDocs = requiredDocuments.every(d => docs && docs[d]);
    if (allDocs) completed.push(8);
    return completed;
  };

  // Save current step as draft
  const handleSaveSection = () => {
    if (!selectedEmployee) {
      alert("Please select an employee before saving this section.");
      setCurrentStep(1);
      return;
    }
    saveDraft(selectedEmployee.id);
  };

  const isFinalReady = () => {
    // Require employee selected, resignation + LWD, notice start/end and all documents
    if (!selectedEmployee) return false;
    if (!formData.resignationDate || !formData.lastWorkingDay) return false;
    if (!formData.noticeStartDate || !formData.noticeEndDate) return false;
    if (!allMandatoryUploaded) return false;
    return true;
  };

  // Calculate which steps are completed
  const calculateCompletedSteps = (): number[] => {
    const completed: number[] = [];
    if (selectedEmployee) completed.push(1); // Employee info always complete when selected
    if (formData.resignationDate && formData.lastWorkingDay) completed.push(2);
    if (
      formData.reportingManagerApproval ||
      formData.hrApproval ||
      formData.itClearanceApproval
    ) completed.push(3);
    if (formData.noticeStartDate && formData.noticeEndDate) completed.push(4);
    if (
      formData.laptopReturned ||
      formData.idCardReturned ||
      formData.knowledgeTransferDone ||
      formData.emailAccessDisabled ||
      formData.assetsCleared
    ) completed.push(5);
    if (formData.leaveEncashment || formData.deductions) completed.push(6);
    if (formData.exitInterviewDate || formData.exitReason) completed.push(7);
    if (allMandatoryUploaded) completed.push(8);
    return completed;
  };

  // Load draft when employee selection changes
  useEffect(() => {
    if (formData.employeeId) {
      loadDraft(formData.employeeId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData.employeeId]);

  // Auto-save draft when user navigates between steps (skip initial load)
  useEffect(() => {
    if (!formData.employeeId) return;
    if (initialLoadRef.current) {
      initialLoadRef.current = false;
      return;
    }
    // save silently
    saveDraft(formData.employeeId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentStep]);

  // Save draft on unload to avoid losing progress
  useEffect(() => {
    const handler = () => {
      if (formData.employeeId) saveDraft(formData.employeeId);
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData]);

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 sm:p-6">
      <style>{`
        .flat-input {
          @apply w-full px-4 py-3 text-sm font-bold border border-border rounded-xl bg-card focus:outline-none focus:ring-2 focus:ring-primary;
        }
      `}</style>
      <div className="bg-card w-full max-w-5xl max-h-[90vh] rounded-3xl shadow-2xl flex flex-col overflow-hidden border border-white/10 animate-in fade-in zoom-in duration-300">
        
        {/* Header */}
        <div className="px-8 py-6 border-b border-border flex items-center justify-between bg-secondary/30">
          <div>
            <h2 className="text-2xl font-black tracking-tight">Add New Offboarding</h2>
            <p className="text-sm text-muted-foreground font-medium mt-1">Fill in the details to initiate the employee exit process.</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-secondary rounded-xl transition-colors text-muted-foreground hover:text-foreground"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar Steps */}
          <div className="w-72 bg-secondary/20 border-r border-border p-6 hidden lg:block overflow-y-auto">
            <div className="space-y-2">
              {steps.map((step) => (
                <div 
                  key={step.id}
                  className={`flex items-center gap-3 p-3 rounded-xl transition-all ${
                    currentStep === step.id 
                      ? "bg-primary text-white shadow-lg shadow-primary/20 scale-[1.02]" 
                      : currentStep > step.id
                      ? "text-green-500 bg-green-500/5"
                      : "text-muted-foreground hover:bg-secondary/50"
                  }`}
                >
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center border ${
                    currentStep === step.id ? "border-white/20 bg-white/10" : "border-current opacity-60"
                  }`}>
                    {(() => {
                      const completedFromDraft = draftMeta?.completedSteps?.includes(step.id);
                      const Icon = (currentStep > step.id || completedFromDraft) ? CheckCircle2 : step.icon;
                      return <Icon className={currentStep > step.id || completedFromDraft ? "w-5 h-5" : "w-4 h-4"} />;
                    })()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-[10px] font-black uppercase tracking-widest opacity-60">Step {step.id}</p>
                    <p className="text-sm font-bold truncate">{step.title}</p>
                  </div>
                  <div className="flex-shrink-0">
                    {draftMeta?.completedSteps && draftMeta.completedSteps.includes(step.id) ? (
                      <span className="text-[10px] font-black text-green-600">Saved</span>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Form Content */}
          <div className="flex-1 overflow-y-auto p-8 bg-card/50">
            <div className="max-w-2xl mx-auto space-y-8">
              
              {/* Progress for Mobile */}
              <div className="lg:hidden flex items-center justify-between mb-6">
                <span className="text-xs font-black uppercase tracking-widest text-primary">Step {currentStep} of {totalSteps}</span>
                <span className="text-sm font-bold">{steps[currentStep-1].title}</span>
              </div>

              {/* Step 1: Employee Information */}
              {currentStep === 1 && (
                <div className="space-y-6 animate-in slide-in-from-right duration-300">
                  <h3 className="text-xl font-black tracking-tight flex items-center gap-2">
                    <User className="w-5 h-5 text-primary" />
                    Employee Information
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Employee Name</label>
                      <select 
                        value={formData.employeeId}
                        onChange={(e) => handleInputChange("employeeId", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold"
                      >
                        <option value="">Select Employee</option>
                        {employees.map(emp => (
                          <option key={emp.id} value={emp.id}>{emp.name}</option>
                        ))}
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Employee ID</label>
                      <input type="text" readOnly className="flat-input w-full px-4 py-3 text-sm font-bold bg-secondary/50" value={selectedEmployee?.employeeId || ""} placeholder="Auto-filled" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Department</label>
                      <input type="text" readOnly className="flat-input w-full px-4 py-3 text-sm font-bold bg-secondary/50" value={selectedEmployee?.department || ""} placeholder="Auto-filled" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Designation</label>
                      <input type="text" readOnly className="flat-input w-full px-4 py-3 text-sm font-bold bg-secondary/50" value={selectedEmployee?.designation || ""} placeholder="Auto-filled" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Reporting Manager</label>
                      <input type="text" readOnly className="flat-input w-full px-4 py-3 text-sm font-bold bg-secondary/50" value={selectedEmployee?.reportingTo || "HR Manager"} placeholder="Auto-filled" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Date of Joining</label>
                      <input type="text" readOnly className="flat-input w-full px-4 py-3 text-sm font-bold bg-secondary/50" value={selectedEmployee?.joiningDate || ""} placeholder="Auto-filled" />
                    </div>
                  </div>
                </div>
              )}

              {/* Step 2: Resignation Details */}
              {currentStep === 2 && (
                <div className="space-y-6 animate-in slide-in-from-right duration-300">
                  <h3 className="text-xl font-black tracking-tight flex items-center gap-2">
                    <FileText className="w-5 h-5 text-primary" />
                    Resignation Details
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Resignation Date</label>
                      <input 
                        type="date" 
                        value={formData.resignationDate}
                        onChange={(e) => handleInputChange("resignationDate", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold" 
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Last Working Day</label>
                      <input 
                        type="date" 
                        value={formData.lastWorkingDay}
                        onChange={(e) => handleInputChange("lastWorkingDay", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold" 
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Notice Period Days</label>
                      <input 
                        type="number" 
                        value={formData.noticePeriod}
                        onChange={(e) => handleInputChange("noticePeriod", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold" 
                        placeholder="e.g. 30" 
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Resignation Type</label>
                      <select 
                        value={formData.type}
                        onChange={(e) => handleInputChange("type", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold"
                      >
                        <option value="Voluntary">Voluntary</option>
                        <option value="Termination">Termination</option>
                        <option value="Retirement">Retirement</option>
                        <option value="Contract End">Contract End</option>
                      </select>
                    </div>
                    <div className="col-span-full space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Reason for Leaving</label>
                      <textarea 
                        value={formData.reason}
                        onChange={(e) => handleInputChange("reason", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold min-h-[100px]" 
                        placeholder="Detailed reason..."
                      ></textarea>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 3: Approval Workflow */}
              {currentStep === 3 && (
                <div className="space-y-6 animate-in slide-in-from-right duration-300">
                  <h3 className="text-xl font-black tracking-tight">Approval Workflow</h3>
                  <div className="grid grid-cols-1 gap-4">
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Reporting Manager Approval</label>
                      <select 
                        value={formData.reportingManagerApproval || "Pending"}
                        onChange={(e) => handleInputChange("reportingManagerApproval", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold"
                      >
                        <option value="Pending">Pending</option>
                        <option value="Approved">Approved</option>
                        <option value="Rejected">Rejected</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">HR Approval</label>
                      <select 
                        value={formData.hrApproval || "Pending"}
                        onChange={(e) => handleInputChange("hrApproval", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold"
                      >
                        <option value="Pending">Pending</option>
                        <option value="Approved">Approved</option>
                        <option value="Rejected">Rejected</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">IT Clearance Approval</label>
                      <select 
                        value={formData.itClearanceApproval || "Pending"}
                        onChange={(e) => handleInputChange("itClearanceApproval", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold"
                      >
                        <option value="Pending">Pending</option>
                        <option value="Approved">Approved</option>
                        <option value="Rejected">Rejected</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Final Approval Remarks</label>
                      <textarea 
                        value={formData.approvalRemarks || ""}
                        onChange={(e) => handleInputChange("approvalRemarks", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold min-h-[80px]"
                        placeholder="Add any final remarks..."
                      ></textarea>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 4: Notice Period */}
              {currentStep === 4 && (
                <div className="space-y-6 animate-in slide-in-from-right duration-300">
                  <h3 className="text-xl font-black tracking-tight">Notice Period</h3>
                  <div className="grid grid-cols-1 gap-4">
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Notice Start Date</label>
                      <input 
                        type="date"
                        value={formData.noticeStartDate || ""}
                        onChange={(e) => handleInputChange("noticeStartDate", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Notice End Date</label>
                      <input 
                        type="date"
                        value={formData.noticeEndDate || ""}
                        onChange={(e) => handleInputChange("noticeEndDate", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold"
                      />
                    </div>
                    <div className="p-4 bg-primary/10 rounded-xl border border-primary/20">
                      <p className="text-sm font-black text-primary">Notice Period: <span className="text-lg">{calculateNoticeDays()} days</span></p>
                    </div>
                    <div className="space-y-3">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input 
                          type="checkbox"
                          checked={formData.buyoutRequired || false}
                          onChange={() => handleToggle("buyoutRequired")}
                          className="w-5 h-5 rounded border-2 border-border accent-primary"
                        />
                        <span className="text-sm font-bold">Buyout Required</span>
                      </label>
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input 
                          type="checkbox"
                          checked={formData.earlyReleaseApproved || false}
                          onChange={() => handleToggle("earlyReleaseApproved")}
                          className="w-5 h-5 rounded border-2 border-border accent-primary"
                        />
                        <span className="text-sm font-bold">Early Release Approved</span>
                      </label>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 5: Clearance Checklist */}
              {currentStep === 5 && (
                <div className="space-y-6 animate-in slide-in-from-right duration-300">
                  <h3 className="text-xl font-black tracking-tight">Clearance Checklist</h3>
                  <div className="grid grid-cols-1 gap-3">
                    {[
                      { key: "laptopReturned", label: "Laptop Returned" },
                      { key: "idCardReturned", label: "ID Card Returned" },
                      { key: "knowledgeTransferDone", label: "Knowledge Transfer Done" },
                      { key: "emailAccessDisabled", label: "Email Access Disabled" },
                      { key: "assetsCleared", label: "Assets Cleared" }
                    ].map((item) => (
                      <label key={item.key} className="flex items-center gap-3 p-3 rounded-xl bg-secondary/20 border border-border cursor-pointer hover:bg-secondary/40 transition-colors">
                        <input 
                          type="checkbox"
                          checked={formData[item.key] || false}
                          onChange={() => handleToggle(item.key)}
                          className="w-5 h-5 rounded border-2 border-border accent-primary"
                        />
                        <span className="text-sm font-bold flex-1">{item.label}</span>
                        {formData[item.key] && <CheckCircle2 className="w-5 h-5 text-emerald-500" />}
                      </label>
                    ))}
                  </div>
                  <div className="space-y-2">
                    <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Clearance Remarks</label>
                    <textarea 
                      value={formData.clearanceRemarks || ""}
                      onChange={(e) => handleInputChange("clearanceRemarks", e.target.value)}
                      className="flat-input w-full px-4 py-3 text-sm font-bold min-h-[80px]"
                      placeholder="Add clearance remarks..."
                    ></textarea>
                  </div>
                </div>
              )}

              {/* Step 6: Financial Settlement */}
              {currentStep === 6 && (
                <div className="space-y-6 animate-in slide-in-from-right duration-300">
                  <h3 className="text-xl font-black tracking-tight">Financial Settlement</h3>
                  <div className="grid grid-cols-1 gap-4">
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Leave Encashment (₹)</label>
                      <input 
                        type="number"
                        value={formData.leaveEncashment || 0}
                        onChange={(e) => handleInputChange("leaveEncashment", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold"
                        placeholder="0"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Deductions (₹)</label>
                      <input 
                        type="number"
                        value={formData.deductions || 0}
                        onChange={(e) => handleInputChange("deductions", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold"
                        placeholder="0"
                      />
                    </div>
                    <div className="p-4 bg-primary/10 rounded-xl border border-primary/20">
                      <p className="text-sm font-black text-primary">Final Settlement Amount: <span className="text-lg">₹ {((formData.leaveEncashment || 0) - (formData.deductions || 0)).toLocaleString()}</span></p>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Payment Status</label>
                      <select 
                        value={formData.paymentStatus || "Pending"}
                        onChange={(e) => handleInputChange("paymentStatus", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold"
                      >
                        <option value="Pending">Pending</option>
                        <option value="Processed">Processed</option>
                        <option value="Completed">Completed</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 7: Exit Interview */}
              {currentStep === 7 && (
                <div className="space-y-6 animate-in slide-in-from-right duration-300">
                  <h3 className="text-xl font-black tracking-tight">Exit Interview</h3>
                  <div className="grid grid-cols-1 gap-4">
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Exit Interview Date</label>
                      <input 
                        type="date"
                        value={formData.exitInterviewDate || ""}
                        onChange={(e) => handleInputChange("exitInterviewDate", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Reason for Leaving</label>
                      <select 
                        value={formData.exitReason || ""}
                        onChange={(e) => handleInputChange("exitReason", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold"
                      >
                        <option value="">Select reason</option>
                        <option value="Better Opportunity">Better Opportunity</option>
                        <option value="Salary">Salary</option>
                        <option value="Work-Life Balance">Work-Life Balance</option>
                        <option value="Career Growth">Career Growth</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black uppercase tracking-widest text-muted-foreground">Employee Feedback</label>
                      <textarea 
                        value={formData.employeeFeedback || ""}
                        onChange={(e) => handleInputChange("employeeFeedback", e.target.value)}
                        className="flat-input w-full px-4 py-3 text-sm font-bold min-h-[100px]"
                        placeholder="Detailed feedback..."
                      ></textarea>
                    </div>
                    <div className="space-y-3">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input 
                          type="checkbox"
                          checked={formData.wouldRejoin || false}
                          onChange={() => handleToggle("wouldRejoin")}
                          className="w-5 h-5 rounded border-2 border-border accent-primary"
                        />
                        <span className="text-sm font-bold">Would Rejoin Company?</span>
                      </label>
                    </div>
                  </div>
                </div>
              )}

              {/* Step 8: Documents */}
              {currentStep === 8 && (
                <div className="space-y-6 animate-in slide-in-from-right duration-300">
                  <div>
                    <h3 className="text-xl font-black tracking-tight flex items-center gap-2 mb-2">
                      <Upload className="w-5 h-5 text-primary" />
                      Required Documents
                    </h3>
                    <p className="text-sm text-muted-foreground">Upload all mandatory documents to proceed with offboarding process</p>
                  </div>
                  
                  <div className="grid grid-cols-1 gap-4">
                    {requiredDocuments.map((doc) => {
                      const uploaded = uploadedDocuments[doc];
                      const isUploaded = !!uploaded;

                      return (
                        <div key={doc} className={`transition-all ${isUploaded ? "bg-green-500/5 border border-green-500/20" : "bg-secondary/30 border border-dashed border-border hover:border-primary/50"} rounded-2xl overflow-hidden`}>
                          <div className="p-4 space-y-3">
                            {/* Document Header */}
                            <div className="flex items-start justify-between">
                              <div className="flex items-center gap-3 flex-1">
                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${isUploaded ? "bg-green-500/10" : "bg-card"}`}>
                                  <FileText className={`w-5 h-5 ${isUploaded ? "text-green-500" : "text-muted-foreground"}`} />
                                </div>
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm font-bold flex items-center gap-2">
                                    {doc}
                                    {isUploaded && (
                                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-500/10 text-green-600 text-[10px] font-black uppercase tracking-widest rounded-full border border-green-500/20">
                                        <Check className="w-3 h-3" />
                                        Completed
                                      </span>
                                    )}
                                  </p>
                                  <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mt-1">
                                    {isUploaded ? "PDF, JPG up to 10MB" : "PDF, JPG up to 10MB"}
                                  </p>
                                </div>
                              </div>
                            </div>

                            {/* Uploaded State */}
                            {isUploaded && uploaded ? (
                              <div className="space-y-3 pl-12">
                                {/* File Info */}
                                <div className="bg-card/50 rounded-xl p-3 space-y-2">
                                  <div className="flex items-center justify-between gap-2">
                                    <div className="min-w-0 flex-1">
                                      <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">File Name</p>
                                      <p className="text-sm font-bold text-foreground truncate">{uploaded.fileName}</p>
                                    </div>
                                    <div className="text-right flex-shrink-0">
                                      <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Size</p>
                                      <p className="text-sm font-bold text-foreground">{formatFileSize(uploaded.fileSize)}</p>
                                    </div>
                                  </div>
                                  <div className="flex items-center justify-between gap-2 pt-2 border-t border-border">
                                    <div>
                                      <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Uploaded</p>
                                      <p className="text-sm font-bold text-foreground">{uploaded.uploadedAt}</p>
                                    </div>
                                    <div className="flex items-center gap-1.5 px-2.5 py-1 bg-green-500/10 text-green-600 text-[10px] font-black uppercase tracking-widest rounded-full border border-green-500/20">
                                      <Check className="w-3.5 h-3.5" />
                                      Uploaded
                                    </div>
                                  </div>
                                </div>

                                {/* Action Buttons */}
                                <div className="flex items-center gap-2 justify-between">
                                  <div className="flex items-center gap-2">
                                    <button
                                      onClick={() => handleViewDocument(doc)}
                                      className="flex items-center gap-1.5 px-3 py-2 text-xs font-bold uppercase tracking-widest text-primary hover:bg-primary/10 rounded-lg transition-all border border-primary/20"
                                    >
                                      <Eye className="w-3.5 h-3.5" />
                                      View
                                    </button>
                                    <button
                                      onClick={() => handleReplaceDocument(doc)}
                                      className="flex items-center gap-1.5 px-3 py-2 text-xs font-bold uppercase tracking-widest text-foreground hover:bg-secondary rounded-lg transition-all border border-border"
                                    >
                                      <RotateCcw className="w-3.5 h-3.5" />
                                      Replace
                                    </button>
                                  </div>
                                  <button
                                    onClick={() => handleDeleteDocument(doc)}
                                    className="flex items-center gap-1.5 px-3 py-2 text-xs font-bold uppercase tracking-widest text-red-600 hover:bg-red-500/10 rounded-lg transition-all border border-red-500/20"
                                  >
                                    <Trash2 className="w-3.5 h-3.5" />
                                    Delete
                                  </button>
                                </div>

                                {/* Hidden File Input for Replace */}
                                <input
                                  ref={(el) => {
                                    if (el) fileInputRefs.current[doc] = el;
                                  }}
                                  type="file"
                                  accept=".pdf,.jpg,.jpeg"
                                  className="hidden"
                                  onChange={(e) => handleFileInputChange(doc, e)}
                                />
                              </div>
                            ) : (
                              <div className="pl-12">
                                {/* Upload Area */}
                                <label className="flex items-center justify-center p-4 bg-card/50 border-2 border-dashed border-border rounded-xl hover:border-primary/50 hover:bg-primary/5 transition-all cursor-pointer group">
                                  <input
                                    type="file"
                                    accept=".pdf,.jpg,.jpeg"
                                    className="hidden"
                                    onChange={(e) => handleFileInputChange(doc, e)}
                                  />
                                  <div className="flex items-center gap-2 text-primary group-hover:scale-105 transition-transform">
                                    <Upload className="w-4 h-4" />
                                    <span className="text-xs font-black uppercase tracking-widest">Upload</span>
                                  </div>
                                </label>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Summary */}
                  {!allMandatoryUploaded && (
                    <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-4">
                      <p className="text-sm font-bold text-amber-700 dark:text-amber-400">
                        ⚠️ {requiredDocuments.length - Object.keys(uploadedDocuments).length} more document{requiredDocuments.length - Object.keys(uploadedDocuments).length !== 1 ? "s" : ""} required to proceed
                      </p>
                    </div>
                  )}
                  
                  {allMandatoryUploaded && (
                    <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-4 flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
                      <p className="text-sm font-bold text-green-700 dark:text-green-400">
                        All required documents uploaded. You can now proceed with offboarding.
                      </p>
                    </div>
                  )}
                </div>
              )}

            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-8 py-6 border-t border-border flex items-center justify-between bg-secondary/10">
          <button 
            onClick={prevStep}
            disabled={currentStep === 1}
            className="flex items-center gap-2 px-6 py-3 text-sm font-black uppercase tracking-widest text-foreground bg-card border border-border rounded-xl hover:bg-secondary transition-all disabled:opacity-0"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </button>
          
            <div className="flex items-center gap-3">
            <button 
              onClick={onClose}
              className="px-6 py-3 text-sm font-black uppercase tracking-widest text-muted-foreground hover:text-foreground transition-all"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveSection}
              className="px-6 py-3 text-sm font-black uppercase tracking-widest rounded-xl border border-border bg-card hover:bg-secondary transition-all"
            >
              Save Section
            </button>
            <button 
              onClick={currentStep === totalSteps ? handleSave : nextStep}
              disabled={currentStep === totalSteps && !isFinalReady()}
              className={`flex items-center gap-2 px-8 py-3 text-sm font-black uppercase tracking-widest rounded-xl shadow-lg transition-all ${
                currentStep === totalSteps && !isFinalReady()
                  ? "bg-muted text-muted-foreground cursor-not-allowed opacity-50"
                  : "text-white bg-primary shadow-primary/20 hover:scale-[1.02] active:scale-[0.98]"
              }`}
            >
              {currentStep === totalSteps ? "Finish & Save" : "Next Step"}
              {currentStep !== totalSteps && <ChevronRight className="w-4 h-4" />}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
