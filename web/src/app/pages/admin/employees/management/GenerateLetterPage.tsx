import React, { useState } from "react";
import { 
  FileText, 
  History, 
  Plus, 
  Send, 
  CheckCircle2,
  Clock,
  AlertCircle,
  X
} from "lucide-react";
import { cn } from "../../../../components/ui/utils";
import { LetterWizard } from "./LetterManagement/LetterWizard";
import { LetterHistory } from "./LetterManagement/LetterHistory";
import { LetterDetails } from "./LetterManagement/LetterDetails";
import { LetterTemplatePanel } from "./LetterManagement/LetterTemplatePanel";
import { LetterBatch } from "./LetterManagement/types";
import { MOCK_HISTORY } from "./LetterManagement/mockData";
import { Button } from "../../../../components/ui/button";
import { toast } from "sonner";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../../components/ui/select";
import { employees } from "../../../../components/employees/mockData";
import { MOCK_TEMPLATES } from "./LetterManagement/mockData";

type ViewMode = "wizard" | "history" | "details";

export function GenerateLetterPage() {
  const [batches, setBatches] = useState<LetterBatch[]>(() => {
    const saved = localStorage.getItem("hrms_letter_batches");
    return saved ? JSON.parse(saved) : MOCK_HISTORY;
  });
  
  const [activeTab, setActiveTab] = useState<"generated" | "templates">("generated");
  const [view, setView] = useState<ViewMode>("history");
  const [wizardStep, setWizardStep] = useState(1);
  const [selectedBatch, setSelectedBatch] = useState<LetterBatch | null>(null);
  const [initialData, setInitialData] = useState<Partial<LetterBatch> | undefined>(undefined);
  const [isPreviewing, setIsPreviewing] = useState(false);

  const persistBatches = (newBatches: LetterBatch[]) => {
    setBatches(newBatches);
    localStorage.setItem("hrms_letter_batches", JSON.stringify(newBatches));
  };

  const handleCreateNew = () => {
    setInitialData(undefined);
    setWizardStep(1);
    setView("wizard");
  };

  const handleRepublish = (batch: LetterBatch) => {
    setInitialData({ ...batch, status: "Draft" });
    setWizardStep(3); // Start at preview step
    setView("wizard");
  };

  const handleDuplicate = (batch: LetterBatch) => {
    setInitialData({ ...batch, id: "", status: "Draft" });
    setWizardStep(1); // Start at configuration step
    setView("wizard");
  };

  const handleDeleteBatch = (id: string) => {
    if (confirm("Are you sure you want to delete this letter batch permanently?")) {
      const updated = batches.filter(b => b.id !== id);
      persistBatches(updated);
      toast.success("Letter batch deleted successfully.");
    }
  };

  const handleEditBatch = (batch: LetterBatch) => {
    setInitialData({ ...batch });
    setWizardStep(batch.currentStep && batch.currentStep > 1 ? batch.currentStep : 1);
    setView("wizard");
  };

  const handleUpdateBatch = (updatedBatch: LetterBatch) => {
    const updated = batches.map(b => b.id === updatedBatch.id ? { ...b, ...updatedBatch } : b);
    persistBatches(updated);
    setSelectedBatch(updatedBatch);
  };

  const handlePreview = (batch: LetterBatch) => {
    setSelectedBatch(batch);
    setIsPreviewing(true);
  };

  const handleViewDetails = (batch: LetterBatch) => {
    setSelectedBatch(batch);
    setView("details");
  };

  const handleSaveDraft = (batch: Partial<LetterBatch>, currentStep: number) => {
    const newBatch: LetterBatch = {
      ...batch,
      id: batch.id || `BATCH-${Math.floor(Math.random() * 10000)}`,
      status: "Draft",
      currentStep,
      createdBy: batch.createdBy || "Admin User",
      createdAt: batch.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString()
    } as LetterBatch;

    const exists = batches.find(b => b.id === newBatch.id);
    const updatedBatches = exists 
      ? batches.map(b => b.id === newBatch.id ? newBatch : b)
      : [newBatch, ...batches];

    persistBatches(updatedBatches);
    setView("history");
  };

  const handleWizardComplete = (batch: LetterBatch) => {
    const finalBatch: LetterBatch = {
      ...batch,
      id: batch.id || `BATCH-${Math.floor(Math.random() * 10000)}`,
      status: batch.approvalWorkflow === "No Approval Required" ? "Published" : "Pending Approval",
      publishedAt: batch.approvalWorkflow === "No Approval Required" ? new Date().toISOString() : undefined,
      updatedAt: new Date().toISOString()
    };

    const exists = batches.find(b => b.id === finalBatch.id);
    const updatedBatches = exists 
      ? batches.map(b => b.id === finalBatch.id ? finalBatch : b)
      : [finalBatch, ...batches];

    persistBatches(updatedBatches);
    setView("history");
  };

  const handleWizardCancel = () => {
    setView("history");
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Top Main Tab Bar Switcher (Hidden during letter wizard) */}
      {view !== "wizard" && (
        <div className="bg-card border-b border-border px-8 py-3 flex items-center gap-4 sticky top-0 z-30">
          <button
            onClick={() => { setActiveTab("generated"); setView("history"); }}
            className={cn(
              "px-4 py-2 text-xs font-black uppercase tracking-widest rounded-xl transition-all",
              activeTab === "generated" ? "bg-secondary text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
            )}
          >
            Generated Letters
          </button>
          <button
            onClick={() => setActiveTab("templates")}
            className={cn(
              "px-4 py-2 text-xs font-black uppercase tracking-widest rounded-xl transition-all",
              activeTab === "templates" ? "bg-secondary text-foreground shadow-sm" : "text-muted-foreground hover:text-foreground hover:bg-secondary/40"
            )}
          >
            Letter Templates
          </button>
        </div>
      )}

      {/* Dynamic Header based on view */}
      {view !== "wizard" && activeTab === "generated" && (
        <div className="px-8 py-6 border-b border-border bg-card/50 backdrop-blur-md flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* <div className="space-y-1">
            <h1 className="text-xl font-black text-foreground tracking-tight uppercase flex items-center gap-2">
              {view === "history" ? <History className="w-5 h-5 text-primary" /> : <FileText className="w-5 h-5 text-primary" />}
              {view === "history" ? "Letter Generation History" : "Batch Details"}
            </h1>
            <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest opacity-60">
              {view === "history" 
                ? "View and manage all generated official documents" 
                : "Comprehensive breakdown of the selected document batch"}
            </p>
          </div> */}
          
          <div className="flex items-center gap-3">
            {view === "history" && (
              <Button 
                onClick={handleCreateNew}
                className="h-11 px-6 rounded-2xl bg-primary text-white hover:bg-primary/90 text-xs font-black uppercase tracking-widest shadow-lg shadow-primary/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                <Plus className="w-4 h-4 mr-2" />
                Generate New Letter
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto bg-background/50 relative">
        <div className={cn("h-full", view !== "wizard" ? "p-8 max-w-[1600px] mx-auto" : "")}>
          {view === "wizard" && activeTab === "generated" && (
            <LetterWizard 
              onCancel={handleWizardCancel} 
              onComplete={handleWizardComplete} 
              onSaveDraft={handleSaveDraft}
              initialData={initialData}
              initialStep={wizardStep}
            />
          )}

          {view === "history" && activeTab === "generated" && (
            <LetterHistory 
              onViewDetails={handleViewDetails} 
              onPreview={handlePreview}
              onRepublish={handleRepublish}
              onDuplicate={handleDuplicate}
              onDeleteBatch={handleDeleteBatch}
              onEditBatch={handleEditBatch}
              batches={batches}
            />
          )}

          {view === "details" && selectedBatch && activeTab === "generated" && (
            <LetterDetails 
              batch={selectedBatch} 
              onBack={() => setView("history")} 
              onUpdateBatch={handleUpdateBatch}
              onDeleteBatch={handleDeleteBatch}
            />
          )}

          {activeTab === "templates" && (
            <LetterTemplatePanel />
          )}
        </div>
      </div>

      {/* Preview Modal */}
      {isPreviewing && selectedBatch && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-8 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-background w-full max-w-6xl max-h-full overflow-hidden rounded-[2.5rem] shadow-2xl border border-border flex flex-col">
            <div className="px-8 py-6 border-b border-border flex items-center justify-between bg-card">
              <div>
                <h3 className="text-xl font-black text-foreground uppercase tracking-tight">Letter Preview</h3>
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest opacity-60">
                  Reviewing {selectedBatch.letterType} for {selectedBatch.selectedEmployeeIds.length} recipients
                </p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsPreviewing(false)} className="rounded-xl">
                <X size={20} />
              </Button>
            </div>
            <div className="flex-1 overflow-y-auto p-8">
              <LetterPreviewContent batch={selectedBatch} />
            </div>
            <div className="px-8 py-4 border-t border-border bg-card flex justify-end gap-3">
              <Button variant="outline" onClick={() => setIsPreviewing(false)} className="rounded-xl px-6 h-11 text-xs font-black uppercase tracking-widest">
                Close
              </Button>
              <Button 
                variant="outline" 
                onClick={() => {
                  const printContent = document.getElementById('modal-letter-preview');
                  if (printContent) {
                    const win = window.open('', '_blank');
                    win?.document.write(`<html><head><title>Print</title></head><body>${printContent.innerHTML}<script>window.print();window.close();</script></body></html>`);
                    win?.document.close();
                  }
                }}
                className="rounded-xl px-6 h-11 text-xs font-black uppercase tracking-widest"
              >
                <Printer className="w-4 h-4 mr-2" /> Print
              </Button>
              <Button className="rounded-xl px-8 h-11 bg-primary text-white text-xs font-black uppercase tracking-widest shadow-lg shadow-primary/20">
                <Download className="w-4 h-4 mr-2" /> Download All
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Sub-component to handle preview content with employee switcher
function LetterPreviewContent({ batch }: { batch: LetterBatch }) {
  const [previewId, setPreviewId] = useState(batch.selectedEmployeeIds[0]);
  const template = MOCK_TEMPLATES.find(t => t.id === batch.templateId);
  const employee = employees.find(e => e.id === previewId);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4 bg-secondary/30 p-4 rounded-2xl border border-border/50">
        <span className="text-xs font-black text-muted-foreground uppercase tracking-widest">Recipient:</span>
        <Select value={previewId} onValueChange={setPreviewId}>
          <SelectTrigger className="h-10 bg-background rounded-xl w-64">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {batch.selectedEmployeeIds.map(id => (
              <SelectItem key={id} value={id}>
                {employees.find(e => e.id === id)?.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div 
        id="modal-letter-preview"
        className="bg-white dark:bg-slate-950 border border-border shadow-inner rounded-[1.5rem] p-12 min-h-[600px] overflow-auto mx-auto max-w-4xl text-slate-900 dark:text-slate-100"
      >
        {template && employee ? (
          <div 
            dangerouslySetInnerHTML={{ 
              __html: template.content
                .replace(/{{employee_name}}/g, employee.name)
                .replace(/{{employee_id}}/g, employee.employeeId)
                .replace(/{{designation}}/g, employee.designation)
                .replace(/{{department}}/g, employee.department)
                .replace(/{{joining_date}}/g, employee.joiningDate)
                .replace(/{{effective_date}}/g, batch.effectiveDate)
                .replace(/{{salary}}/g, "₹ 8,45,000")
                .replace(/{{current_date}}/g, new Date().toLocaleDateString())
            }} 
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-96 text-muted-foreground opacity-50">
            <AlertCircle size={48} className="mb-4" />
            <p className="text-sm font-black uppercase tracking-widest text-center">
              Template or Employee data missing.<br/>Preview unavailable.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

