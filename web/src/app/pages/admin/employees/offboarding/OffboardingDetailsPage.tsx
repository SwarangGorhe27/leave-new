import { useState, useEffect } from "react";
import { 
  X, 
  ChevronRight, 
  FileText, 
  ShieldCheck, 
  Wallet, 
  MessageSquare, 
  History,
  Info,
  Calendar,
  User,
  CheckCircle2,
  Clock,
  AlertCircle,
  Download,
  Eye,
  Briefcase,
  DollarSign,
  FileCheck
} from "lucide-react";
import { useOffboardingDetails } from "./useOffboardingDetails";
import { OffboardingData, OffboardingRecord } from "./types";

interface Props {
  onClose: () => void;
  record: OffboardingRecord;
}

export function OffboardingDetailsPage({ onClose, record }: Props) {
  const [activeTab, setActiveTab] = useState("Overview");
  const { data: offboardingData, loading } = useOffboardingDetails(record.id);

  const tabs = [
    { name: "Overview", icon: Info },
    { name: "Resignation/Approval", icon: FileText },
    { name: "Clearance", icon: ShieldCheck },
    { name: "Finance", icon: Wallet },
    { name: "Exit Interview", icon: MessageSquare },
    { name: "Documents", icon: FileCheck },
    { name: "Activity Logs", icon: History },
  ];

  // Build workflow based on completed steps
  const getWorkflow = () => {
    if (!offboardingData) return [];
    
    const steps = [
      { name: "Employee Selected", status: offboardingData.completedSteps?.includes(1) ? "completed" : "pending", date: "Initiated" },
      { name: "Resignation Details", status: offboardingData.completedSteps?.includes(2) ? "completed" : "pending", date: offboardingData.resignationDate || "Pending" },
      { name: "Manager Approval", status: offboardingData.completedSteps?.includes(3) && offboardingData.approvalWorkflow.reportingManagerApproval === "Approved" ? "completed" : "current", date: offboardingData.approvalWorkflow.reportingManagerApprovedAt || "Pending" },
      { name: "Notice Period", status: offboardingData.completedSteps?.includes(4) ? "completed" : "pending", date: offboardingData.noticeDetails.noticeStartDate || "Pending" },
      { name: "Clearance Process", status: offboardingData.completedSteps?.includes(5) ? "completed" : "pending", date: "In Progress" },
      { name: "Financial Settlement", status: offboardingData.completedSteps?.includes(6) ? "completed" : "pending", date: offboardingData.financialSettlement.paymentDate || "Pending" },
      { name: "Exit Interview", status: offboardingData.completedSteps?.includes(7) ? "completed" : "pending", date: offboardingData.exitInterview.exitInterviewDate || "Pending" },
    ];
    return steps;
  };

  const workflow = getWorkflow();

  if (loading) {
    return (
      <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <div className="bg-card p-8 rounded-2xl">
          <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full" />
        </div>
      </div>
    );
  }

  if (!offboardingData) {
    return (
      <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
        <div className="bg-card p-8 rounded-2xl max-w-md text-center">
          <AlertCircle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
          <h3 className="text-lg font-black tracking-tight mb-2">Data Not Found</h3>
          <p className="text-sm text-muted-foreground mb-6">
            The offboarding data for {record.name} could not be loaded.
          </p>
          <button 
            onClick={onClose}
            className="px-6 py-2 bg-primary text-white rounded-lg font-bold text-sm"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-end bg-black/40 backdrop-blur-sm">
      <div className="bg-background w-full max-w-6xl h-full shadow-2xl flex flex-col border-l border-border animate-in slide-in-from-right duration-500">
        
        {/* Header */}
        <div className="px-8 py-4 border-b border-border flex items-center justify-between bg-card">
          <div className="flex items-center gap-2 text-xs font-bold text-muted-foreground uppercase tracking-widest">
            <span>Offboarding</span>
            <ChevronRight className="w-3 h-3" />
            <span className="text-foreground">Details</span>
            <ChevronRight className="w-3 h-3" />
            <span className="text-primary">{offboardingData.name}</span>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-secondary rounded-xl transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex-1 flex overflow-hidden">
          
          {/* Left Profile Panel */}
          <div className="w-80 bg-secondary/20 border-r border-border p-8 flex flex-col gap-8 overflow-y-auto">
            <div className="flex flex-col items-center text-center gap-4">
              <div 
                className="w-32 h-32 rounded-3xl flex items-center justify-center text-white font-black text-4xl border-4 border-card shadow-2xl"
                style={{ backgroundColor: offboardingData.avatarColor }}
              >
                {offboardingData.initials}
              </div>
              <div>
                <h3 className="text-xl font-black tracking-tight">{offboardingData.name}</h3>
                <p className="text-sm font-bold text-muted-foreground">{offboardingData.employeeId}</p>
              </div>
              <span className="text-[10px] px-3 py-1 bg-purple-500/10 text-purple-500 border border-purple-500/20 rounded-full font-black uppercase tracking-widest">
                {record.exitStatus}
              </span>
            </div>

            <div className="space-y-6">
              {[
                { label: "Department", value: offboardingData.department, icon: User },
                { label: "Designation", value: offboardingData.designation, icon: Briefcase },
                { label: "Joining Date", value: "2020-01-15", icon: Calendar },
                { label: "Last Working Day", value: offboardingData.lastWorkingDay, icon: Clock },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-card border border-border flex items-center justify-center">
                    <item.icon className="w-4 h-4 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">{item.label}</p>
                    <p className="text-sm font-bold">{item.value}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-auto p-4 bg-primary/5 border border-primary/10 rounded-2xl">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-4 h-4 text-primary" />
                <p className="text-xs font-black text-primary uppercase tracking-widest">Status Summary</p>
              </div>
              <p className="text-xs font-medium text-foreground/80 leading-relaxed">
                {getStatusSummary(offboardingData)}
              </p>
            </div>
          </div>

          {/* Right Content Area */}
          <div className="flex-1 flex flex-col overflow-hidden bg-background">
            
            {/* Workflow Tracker */}
            <div className="px-8 py-6 border-b border-border bg-card/50 overflow-x-auto">
              <div className="flex items-center min-w-max">
                {workflow.map((step, idx) => (
                  <div key={step.name} className="flex items-center">
                    <div className="flex flex-col items-center gap-2 relative">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all ${
                        step.status === "completed" 
                          ? "bg-green-500 border-green-500 text-white" 
                          : step.status === "current"
                          ? "bg-primary/10 border-primary text-primary"
                          : "bg-secondary border-border text-muted-foreground"
                      }`}>
                        {step.status === "completed" ? <CheckCircle2 className="w-5 h-5" /> : <span className="text-xs font-bold">{idx + 1}</span>}
                      </div>
                      <div className="absolute top-10 flex flex-col items-center min-w-[100px] text-center">
                        <p className={`text-[10px] font-black uppercase tracking-tight ${step.status === "pending" ? "text-muted-foreground" : "text-foreground"}`}>
                          {step.name}
                        </p>
                        <p className="text-[9px] font-bold text-muted-foreground">{step.date}</p>
                      </div>
                    </div>
                    {idx < workflow.length - 1 && (
                      <div className={`h-0.5 w-16 mx-2 ${step.status === "completed" ? "bg-green-500" : "bg-border"}`} />
                    )}
                  </div>
                ))}
              </div>
              <div className="h-10" />
            </div>

            {/* Tabs Navigation */}
            <div className="px-8 flex items-center gap-8 border-b border-border bg-card overflow-x-auto">
              {tabs.map((tab) => (
                <button
                  key={tab.name}
                  onClick={() => setActiveTab(tab.name)}
                  className={`relative py-4 text-xs font-black uppercase tracking-widest transition-all flex items-center gap-2 whitespace-nowrap ${
                    activeTab === tab.name ? "text-primary" : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <tab.icon className="w-3.5 h-3.5" />
                  {tab.name}
                  {activeTab === tab.name && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-primary rounded-t-full" />
                  )}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-y-auto p-8">
              <div className="max-w-4xl space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                {renderTabContent(activeTab, offboardingData)}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper function to get status summary
function getStatusSummary(data: OffboardingData): string {
  const clearanceProgress = data.clearanceChecklist.clearanceProgress;
  const daysRemaining = Math.ceil(
    (new Date(data.noticeDetails.noticeEndDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
  );

  if (daysRemaining < 0) {
    return `Notice period completed. Clearance at ${clearanceProgress}%. Financial settlement: ${data.financialSettlement.paymentStatus}`;
  }
  return `${daysRemaining} days remaining. Clearance at ${clearanceProgress}%. Documents uploaded: ${Object.keys(data.documents).length}`;
}

// Render tab content based on active tab
function renderTabContent(activeTab: string, data: OffboardingData) {
  switch (activeTab) {
    case "Overview":
      return <OverviewTab data={data} />;
    case "Resignation/Approval":
      return <ResignationApprovalTab data={data} />;
    case "Clearance":
      return <ClearanceTab data={data} />;
    case "Finance":
      return <FinanceTab data={data} />;
    case "Exit Interview":
      return <ExitInterviewTab data={data} />;
    case "Documents":
      return <DocumentsTab data={data} />;
    case "Activity Logs":
      return <ActivityLogsTab data={data} />;
    default:
      return <EmptyState activeTab={activeTab} />;
  }
}

// ============ TAB COMPONENTS ============

function OverviewTab({ data }: { data: OffboardingData }) {
  const daysRemaining = Math.ceil(
    (new Date(data.noticeDetails.noticeEndDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="flat-card bg-card p-6 space-y-4 col-span-full">
        <h4 className="text-sm font-black uppercase tracking-widest text-primary">Resignation Summary</h4>
        <p className="text-base font-medium leading-relaxed">
          {data.name} has submitted their resignation on {formatDate(data.resignationDate)} 
          due to {data.reason || "not specified"}. 
          The notice period started on {formatDate(data.noticeDetails.noticeStartDate)} 
          and will end on {formatDate(data.noticeDetails.noticeEndDate)} 
          ({data.noticeDetails.noticeDays} days). 
          {data.noticeDetails.earlyReleaseApproved && " Early release has been approved."}
        </p>
      </div>

      <div className="flat-card bg-card p-6 space-y-4">
        <h4 className="text-sm font-black uppercase tracking-widest text-primary">Notice Period Status</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b border-border last:border-0">
            <span className="text-sm font-bold">Start Date</span>
            <span className="text-sm font-bold text-foreground">{formatDate(data.noticeDetails.noticeStartDate)}</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-border last:border-0">
            <span className="text-sm font-bold">End Date</span>
            <span className="text-sm font-bold text-foreground">{formatDate(data.noticeDetails.noticeEndDate)}</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-border last:border-0">
            <span className="text-sm font-bold">Days Remaining</span>
            <span className={`text-sm font-bold ${daysRemaining > 0 ? "text-amber-500" : "text-green-500"}`}>
              {daysRemaining > 0 ? `${daysRemaining} days` : "Completed"}
            </span>
          </div>
          <div className="flex items-center justify-between py-2 border-b border-border last:border-0">
            <span className="text-sm font-bold">Buyout Required</span>
            <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase"
                  style={{backgroundColor: data.noticeDetails.buyoutRequired ? "rgb(239 68 68 / 0.1)" : "rgb(34 197 94 / 0.1)", 
                          color: data.noticeDetails.buyoutRequired ? "rgb(220 38 38)" : "rgb(22 163 74)"}}>
              {data.noticeDetails.buyoutRequired ? "Yes" : "No"}
            </span>
          </div>
        </div>
      </div>

      <div className="flat-card bg-card p-6 space-y-4">
        <h4 className="text-sm font-black uppercase tracking-widest text-primary">Clearance Progress</h4>
        <div className="space-y-3">
          <div className="relative pt-2">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-black uppercase tracking-widest text-muted-foreground">Overall Progress</span>
              <span className="text-sm font-black text-primary">{data.clearanceChecklist.clearanceProgress}%</span>
            </div>
            <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
              <div 
                className="h-full bg-primary rounded-full transition-all"
                style={{ width: `${data.clearanceChecklist.clearanceProgress}%` }}
              />
            </div>
          </div>
          <div className="space-y-2 mt-4">
            {[
              { label: "Laptop Returned", done: data.clearanceChecklist.laptopReturned },
              { label: "ID Card Returned", done: data.clearanceChecklist.idCardReturned },
              { label: "Knowledge Transfer", done: data.clearanceChecklist.knowledgeTransferDone },
              { label: "Email Access Disabled", done: data.clearanceChecklist.emailAccessDisabled },
              { label: "Assets Cleared", done: data.clearanceChecklist.assetsCleared },
            ].map(item => (
              <div key={item.label} className="flex items-center gap-2">
                <div className={`w-4 h-4 rounded border-2 ${item.done ? "bg-green-500 border-green-500" : "border-border"}`}>
                  {item.done && <CheckCircle2 className="w-3 h-3 text-white" />}
                </div>
                <span className="text-sm font-bold flex-1">{item.label}</span>
                {item.done && <span className="text-[10px] px-2 py-0.5 bg-green-500/10 text-green-600 font-bold rounded">Done</span>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function ResignationApprovalTab({ data }: { data: OffboardingData }) {
  return (
    <div className="space-y-6">
      <div className="flat-card bg-card p-6 space-y-6">
        <h4 className="text-sm font-black uppercase tracking-widest text-primary">Approval Workflow Status</h4>
        
        {[
          { title: "Reporting Manager Approval", status: data.approvalWorkflow.reportingManagerApproval, date: data.approvalWorkflow.reportingManagerApprovedAt, remarks: data.approvalWorkflow.reportingManagerRemarks },
          { title: "HR Approval", status: data.approvalWorkflow.hrApproval, date: data.approvalWorkflow.hrApprovedAt, remarks: data.approvalWorkflow.hrRemarks },
          { title: "IT Clearance Approval", status: data.approvalWorkflow.itClearanceApproval, date: data.approvalWorkflow.itApprovedAt, remarks: data.approvalWorkflow.itRemarks },
        ].map((approval, idx) => (
          <div key={idx} className="p-4 border border-border rounded-xl bg-secondary/20">
            <div className="flex items-center justify-between mb-3">
              <h5 className="text-sm font-bold">{approval.title}</h5>
              <StatusBadge status={approval.status} />
            </div>
            {approval.date && (
              <p className="text-xs text-muted-foreground mb-2">
                {approval.status === "Approved" ? "Approved on: " : "Status updated: "}{formatDate(approval.date)}
              </p>
            )}
            {approval.remarks && (
              <p className="text-sm text-foreground/80 border-t border-border pt-3 mt-3">{approval.remarks}</p>
            )}
          </div>
        ))}

        {data.approvalWorkflow.finalApprovalRemarks && (
          <div className="p-4 bg-primary/10 border border-primary/20 rounded-xl">
            <h5 className="text-sm font-bold mb-2 text-primary">Final Approval Remarks</h5>
            <p className="text-sm text-foreground/80">{data.approvalWorkflow.finalApprovalRemarks}</p>
          </div>
        )}
      </div>

      {!data.approvalWorkflow.finalApprovalRemarks && (
        <div className="p-6 bg-amber-500/5 border border-amber-500/20 rounded-xl">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
            <div>
              <h5 className="text-sm font-bold text-amber-900">Pending Approvals</h5>
              <p className="text-xs text-amber-800 mt-1">Awaiting final approval remarks from HR department.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ClearanceTab({ data }: { data: OffboardingData }) {
  const items = [
    { label: "Laptop Returned", done: data.clearanceChecklist.laptopReturned, date: data.clearanceChecklist.laptopReturnedDate },
    { label: "ID Card Returned", done: data.clearanceChecklist.idCardReturned, date: data.clearanceChecklist.idCardReturnedDate },
    { label: "Knowledge Transfer Done", done: data.clearanceChecklist.knowledgeTransferDone, date: data.clearanceChecklist.knowledgeTransferDate },
    { label: "Email Access Disabled", done: data.clearanceChecklist.emailAccessDisabled, date: data.clearanceChecklist.emailDisabledDate },
    { label: "Assets Cleared", done: data.clearanceChecklist.assetsCleared, date: data.clearanceChecklist.assetsReturnedDate },
  ];

  return (
    <div className="space-y-6">
      <div className="flat-card bg-card p-6">
        <h4 className="text-sm font-black uppercase tracking-widest text-primary mb-6">Clearance Checklist</h4>
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.label} className="flex items-center justify-between p-4 border border-border rounded-xl">
              <div className="flex items-center gap-3">
                <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                  item.done ? "bg-green-500 border-green-500" : "border-border bg-transparent"
                }`}>
                  {item.done && <CheckCircle2 className="w-4 h-4 text-white" />}
                </div>
                <div>
                  <p className="text-sm font-bold">{item.label}</p>
                  {item.date && <p className="text-xs text-muted-foreground">{formatDate(item.date)}</p>}
                </div>
              </div>
              <span className={`text-[10px] px-3 py-1 rounded-full font-black uppercase tracking-widest ${
                item.done 
                  ? "bg-green-500/10 text-green-600" 
                  : "bg-amber-500/10 text-amber-600"
              }`}>
                {item.done ? "Completed" : "Pending"}
              </span>
            </div>
          ))}
        </div>
      </div>

      {data.clearanceChecklist.clearanceRemarks && (
        <div className="flat-card bg-card p-6">
          <h5 className="text-sm font-black uppercase tracking-widest text-primary mb-3">Clearance Remarks</h5>
          <p className="text-sm text-foreground/80 whitespace-pre-wrap">{data.clearanceChecklist.clearanceRemarks}</p>
        </div>
      )}
    </div>
  );
}

function FinanceTab({ data }: { data: OffboardingData }) {
  return (
    <div className="space-y-6">
      <div className="flat-card bg-card p-6 space-y-6">
        <h4 className="text-sm font-black uppercase tracking-widest text-primary">Financial Settlement</h4>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 border border-border rounded-xl bg-secondary/20">
            <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-1">Leave Encashment</p>
            <p className="text-2xl font-black text-foreground">₹{(data.financialSettlement.leaveEncashment || 0).toLocaleString()}</p>
          </div>
          <div className="p-4 border border-border rounded-xl bg-secondary/20">
            <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-1">Deductions</p>
            <p className="text-2xl font-black text-red-500">₹{(data.financialSettlement.deductions || 0).toLocaleString()}</p>
          </div>
        </div>

        <div className="p-6 bg-primary/10 border border-primary/20 rounded-2xl">
          <p className="text-xs font-bold text-primary uppercase tracking-widest mb-2">Final Settlement Amount</p>
          <p className="text-3xl font-black text-primary">₹{(data.financialSettlement.finalSettlementAmount || 0).toLocaleString()}</p>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 border border-border rounded-xl">
            <span className="text-sm font-bold">Payment Status</span>
            <StatusBadge status={data.financialSettlement.paymentStatus} />
          </div>
          {data.financialSettlement.paymentDate && (
            <div className="flex items-center justify-between p-4 border border-border rounded-xl">
              <span className="text-sm font-bold">Payment Date</span>
              <span className="text-sm font-bold text-foreground">{formatDate(data.financialSettlement.paymentDate)}</span>
            </div>
          )}
          {data.financialSettlement.paymentMethod && (
            <div className="flex items-center justify-between p-4 border border-border rounded-xl">
              <span className="text-sm font-bold">Payment Method</span>
              <span className="text-sm font-bold text-foreground">{data.financialSettlement.paymentMethod}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ExitInterviewTab({ data }: { data: OffboardingData }) {
  return (
    <div className="space-y-6">
      {data.exitInterview.exitInterviewDate ? (
        <>
          <div className="flat-card bg-card p-6 space-y-4">
            <h4 className="text-sm font-black uppercase tracking-widest text-primary">Exit Interview Details</h4>
            
            <div className="space-y-3">
              <div className="p-4 border border-border rounded-xl bg-secondary/20">
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-1">Interview Date</p>
                <p className="text-sm font-bold">{formatDate(data.exitInterview.exitInterviewDate)}</p>
              </div>
              
              <div className="p-4 border border-border rounded-xl bg-secondary/20">
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-1">Reason for Leaving</p>
                <p className="text-sm font-bold">{data.exitInterview.exitReason}</p>
              </div>
              
              <div className="p-4 border border-border rounded-xl bg-secondary/20">
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mb-1">Would Rejoin Company</p>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
                  data.exitInterview.wouldRejoin 
                    ? "bg-green-500/10 text-green-600" 
                    : "bg-red-500/10 text-red-600"
                }`}>
                  {data.exitInterview.wouldRejoin ? "Yes" : "No"}
                </span>
              </div>
            </div>
          </div>

          {data.exitInterview.employeeFeedback && (
            <div className="flat-card bg-card p-6">
              <h5 className="text-sm font-black uppercase tracking-widest text-primary mb-3">Employee Feedback</h5>
              <p className="text-sm text-foreground/80 whitespace-pre-wrap">{data.exitInterview.employeeFeedback}</p>
            </div>
          )}
        </>
      ) : (
        <div className="p-6 bg-amber-500/5 border border-amber-500/20 rounded-xl text-center">
          <MessageSquare className="w-12 h-12 text-amber-500 mx-auto mb-3 opacity-50" />
          <h5 className="text-sm font-bold text-amber-900 mb-1">Exit Interview Not Conducted</h5>
          <p className="text-xs text-amber-800">The exit interview is pending. Please schedule it at your earliest convenience.</p>
        </div>
      )}
    </div>
  );
}

function DocumentsTab({ data }: { data: OffboardingData }) {
  const documents = Object.entries(data.documents || {});

  if (documents.length === 0) {
    return (
      <div className="p-6 bg-amber-500/5 border border-amber-500/20 rounded-xl text-center">
        <FileText className="w-12 h-12 text-amber-500 mx-auto mb-3 opacity-50" />
        <h5 className="text-sm font-bold text-amber-900 mb-1">No Documents Uploaded</h5>
        <p className="text-xs text-amber-800">Please upload all required offboarding documents.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flat-card bg-card p-6">
        <h4 className="text-sm font-black uppercase tracking-widest text-primary mb-6">Uploaded Documents</h4>
        <div className="space-y-3">
          {documents.map(([key, doc]) => (
            <div key={key} className="p-4 border border-border rounded-xl bg-secondary/20 hover:bg-secondary/30 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-5 h-5 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-sm font-bold truncate">{doc.name}</p>
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-500/10 text-green-600 text-[10px] font-black uppercase tracking-widest rounded-full border border-green-500/20 flex-shrink-0">
                        <CheckCircle2 className="w-3 h-3" />
                        {doc.uploadStatus}
                      </span>
                    </div>
                    <div className="text-xs text-muted-foreground space-x-2">
                      <span>{doc.fileName}</span>
                      <span>•</span>
                      <span>{formatFileSize(doc.fileSize)}</span>
                      <span>•</span>
                      <span>{doc.uploadedAt}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                  <button className="p-2 hover:bg-primary/10 rounded-lg transition-colors text-primary text-xs font-bold uppercase tracking-widest">
                    <Eye className="w-4 h-4" />
                  </button>
                  <button className="p-2 hover:bg-primary/10 rounded-lg transition-colors text-primary text-xs font-bold uppercase tracking-widest">
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ActivityLogsTab({ data }: { data: OffboardingData }) {
  return (
    <div className="flat-card bg-card p-6">
      <h4 className="text-sm font-black uppercase tracking-widest text-primary mb-6">Activity Timeline</h4>
      <div className="space-y-4">
        <div className="flex gap-4">
          <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
          <div>
            <p className="text-sm font-bold">Offboarding Created</p>
            <p className="text-xs text-muted-foreground">{formatDate(data.createdAt)}</p>
          </div>
        </div>
        {data.completedSteps?.includes(2) && (
          <div className="flex gap-4">
            <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
            <div>
              <p className="text-sm font-bold">Resignation Details Submitted</p>
              <p className="text-xs text-muted-foreground">{formatDate(data.resignationDate)}</p>
            </div>
          </div>
        )}
        {data.completedSteps?.includes(3) && (
          <div className="flex gap-4">
            <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
            <div>
              <p className="text-sm font-bold">Approvals Processed</p>
              <p className="text-xs text-muted-foreground">Manager, HR, and IT approvals received</p>
            </div>
          </div>
        )}
        <div className="flex gap-4">
          <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
          <div>
            <p className="text-sm font-bold">Last Updated</p>
            <p className="text-xs text-muted-foreground">{formatDate(data.updatedAt)}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function EmptyState({ activeTab }: { activeTab: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center opacity-40">
      <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center mb-4">
        <Clock className="w-8 h-8" />
      </div>
      <h3 className="text-lg font-black uppercase tracking-tighter">{activeTab} Details</h3>
      <p className="text-sm font-medium">Detailed data view for {activeTab} is being loaded...</p>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const statusConfig: Record<string, { bg: string; text: string; color: string }> = {
    "Pending": { bg: "bg-amber-500/10", text: "text-amber-600", color: "border-amber-500/20" },
    "Approved": { bg: "bg-green-500/10", text: "text-green-600", color: "border-green-500/20" },
    "Rejected": { bg: "bg-red-500/10", text: "text-red-600", color: "border-red-500/20" },
    "Processed": { bg: "bg-blue-500/10", text: "text-blue-600", color: "border-blue-500/20" },
    "Completed": { bg: "bg-green-500/10", text: "text-green-600", color: "border-green-500/20" },
  };

  const config = statusConfig[status] || statusConfig["Pending"];

  return (
    <span className={`text-[10px] px-3 py-1 rounded-full font-black uppercase tracking-widest border ${config.bg} ${config.text} ${config.color}`}>
      {status}
    </span>
  );
}

// Utility functions
function formatDate(dateString: string | undefined): string {
  if (!dateString) return "N/A";
  try {
    return new Date(dateString).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric"
    });
  } catch {
    return dateString;
  }
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}
