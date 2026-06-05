import React, { useState } from "react";
import { X, Download, FileText, Printer, Building2, ShieldCheck, User } from "lucide-react";
import { LetterTemplate } from "@/store/slices/letterSlice";
import { Button } from "@/app/components/ui/button";
import { employees } from "../../../../../components/employees/mockData";

interface TemplatePreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  template: LetterTemplate | null;
}

export function TemplatePreviewModal({ isOpen, onClose, template }: TemplatePreviewModalProps) {
  const [selectedEmpId, setSelectedEmpId] = useState(employees[0]?.id || "");

  if (!isOpen || !template) return null;

  const currentEmployee = employees.find(e => e.id === selectedEmpId) || employees[0];

  const currentDate = new Date().toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  });

  // Calculate Reference Number
  const prefix = template.numberSeries?.prefix || "REF";
  const startNum = template.numberSeries?.startNumber || "001";
  const suffix = template.numberSeries?.suffix || "2026";
  const refNumber = `${prefix}/${startNum}/${suffix}`;

  // Company Details
  const companyName = "Ampcus Tech Pvt Ltd";
  const authSignatoryName = "Priya Nair";
  const authDesignation = "HR Manager";

  // Address details helper
  const addr = currentEmployee?.currentAddress || {
    addressLine1: "123 Business Avenue",
    addressLine2: "Tech Park Phase II",
    landmark: "Electronic City",
    city: "Bangalore",
    state: "Karnataka",
    country: "India",
    pincode: "560100"
  };

  const employeeName = currentEmployee?.name || "John Doe";
  const employeeNumber = currentEmployee?.employeeId || "EMP-001";
  const designation = currentEmployee?.designation || "Software Engineer";
  const joiningDate = currentEmployee?.joiningDate 
    ? new Date(currentEmployee.joiningDate).toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' })
    : "01 June 2024";

  // Placeholder replacer helper
  const renderContent = () => {
    let text = template.description || `This serves as official correspondence regarding ${template.name}.`;
    
    // Auto-replace common placeholders
    text = text
      .replace(/{{employee_name}}/g, employeeName)
      .replace(/{{employee_number}}/g, employeeNumber)
      .replace(/{{employee_id}}/g, employeeNumber)
      .replace(/{{designation}}/g, designation)
      .replace(/{{company_name}}/g, companyName)
      .replace(/{{joining_date}}/g, joiningDate)
      .replace(/{{date}}/g, currentDate)
      .replace(/{{ref_number}}/g, refNumber);

    return text;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-white dark:bg-slate-950 w-full max-w-4xl h-[90vh] rounded-3xl border border-border shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-300">
        
        {/* Header Controls */}
        <div className="px-8 py-5 border-b border-border flex items-center justify-between bg-slate-50 dark:bg-slate-900/50">
          <div className="flex items-center gap-4">
             <div className="w-10 h-10 rounded-xl bg-foreground text-primary-foreground flex items-center justify-center shadow-md shadow-foreground/10">
                <FileText size={20} />
             </div>
             <div>
                <h2 className="text-sm font-black text-foreground uppercase tracking-tight">{template.name}</h2>
                <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">Template Preview Mode</p>
             </div>
          </div>
          <div className="flex items-center gap-3">
             <Button 
               variant="outline" 
               className="h-9 gap-2 text-[10px] font-black uppercase rounded-xl border-border hover:bg-secondary"
               onClick={() => window.print()}
             >
                <Printer size={14} /> Print
             </Button>
             <Button className="h-9 gap-2 text-[10px] font-black uppercase rounded-xl bg-foreground text-primary-foreground hover:bg-foreground/90">
                <Download size={14} /> Export PDF
             </Button>
             <div className="w-px h-6 bg-border mx-2" />
             <button onClick={onClose} className="w-9 h-9 rounded-full border border-border flex items-center justify-center hover:bg-secondary transition-all">
                <X size={16} />
             </button>
          </div>
        </div>

        {/* Dynamic Employee Selector */}
        <div className="px-8 py-3 bg-secondary/30 border-b border-border flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-[10px] font-black text-muted-foreground uppercase tracking-wider">Preview Employee:</span>
            <select
              value={selectedEmpId}
              onChange={(e) => setSelectedEmpId(e.target.value)}
              className="text-xs font-bold uppercase py-1 px-3 border border-border bg-card rounded-xl outline-none cursor-pointer"
            >
              {employees.map(emp => (
                <option key={emp.id} value={emp.id}>{emp.name} ({emp.designation})</option>
              ))}
            </select>
          </div>
          <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
            Digital Signature: {template.enableDigitalSignature ? "ENABLED (PFX)" : "DISABLED"}
          </div>
        </div>

        {/* Document Content */}
        <div className="flex-1 overflow-y-auto p-12 bg-secondary/5 no-scrollbar">
           <div className="max-w-[760px] mx-auto bg-white dark:bg-slate-900 shadow-2xl border border-border p-16 space-y-12 min-h-[960px] relative overflow-hidden text-slate-800 dark:text-slate-200">
              
              {/* Watermark for preview */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.02] rotate-[-45deg]">
                 <span className="text-8xl font-black uppercase tracking-[0.4em] select-none">PREVIEW</span>
              </div>

              {/* Company Header / Header Fields */}
              <div className="flex justify-between items-start">
                 <div className="space-y-3">
                    <div className="w-14 h-14 bg-slate-100 dark:bg-slate-800 rounded-2xl flex items-center justify-center">
                       <Building2 size={28} className="text-slate-400" />
                    </div>
                    <div className="space-y-0.5">
                       <h3 className="text-sm font-black text-foreground uppercase tracking-tight">{companyName}</h3>
                       <p className="text-[9px] text-muted-foreground font-bold leading-normal max-w-[200px]">
                          123 Business Avenue, Tech Park Phase II, <br />
                          Electronic City, Bangalore - 560100
                       </p>
                    </div>
                 </div>
                 <div className="text-right space-y-1">
                    <p className="text-[10px] font-black text-foreground uppercase tracking-widest">Ref: {refNumber}</p>
                    <p className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest">Date: {currentDate}</p>
                 </div>
              </div>

              {/* Document Title */}
              <div className="text-center py-4">
                 <h1 className="text-lg font-black text-foreground uppercase tracking-[0.25em] border-b-2 border-foreground/15 pb-3 inline-block px-10">
                   {template.name}
                 </h1>
              </div>

              {/* Address Details (Formatted) */}
              <div className="space-y-1 text-[11px] leading-normal border-l-2 border-slate-200 dark:border-slate-700 pl-4 py-1">
                 <p className="font-black text-foreground uppercase tracking-wide">To,</p>
                 <p className="font-bold">{employeeName}</p>
                 <p>{addr.addressLine1 || "Flat / House No. 42"}</p>
                 <p>{addr.addressLine2 || "Koramangala 5th Block"}</p>
                 {addr.landmark && <p>{addr.landmark}</p>}
                 <p>{addr.city || "Bangalore"} - {addr.pincode || "560095"}</p>
                 <p>{addr.state || "Karnataka"}, {addr.country || "India"}</p>
              </div>

              {/* Salutation */}
              <div className="pt-2 text-[12px]">
                 <p className="font-bold">Dear <span className="font-black text-primary">{employeeName}</span>,</p>
              </div>

              {/* Employee Details and Body */}
              <div className="space-y-6 text-[12px] leading-relaxed text-slate-800 dark:text-slate-200">
                 
                 {/* Styled Employee Details Table */}
                 <div className="bg-slate-50 dark:bg-slate-800/40 border border-border/80 rounded-2xl p-5 space-y-3">
                   <p className="text-[9px] font-black text-muted-foreground uppercase tracking-widest border-b border-border pb-1.5">Employment Profile</p>
                   <div className="grid grid-cols-2 gap-y-2 gap-x-4">
                     <div className="flex justify-between border-b border-border/40 pb-1">
                       <span className="text-muted-foreground">Employee Name:</span>
                       <span className="font-bold text-foreground">{employeeName}</span>
                     </div>
                     <div className="flex justify-between border-b border-border/40 pb-1">
                       <span className="text-muted-foreground">Employee Number:</span>
                       <span className="font-mono font-bold text-foreground">{employeeNumber}</span>
                     </div>
                     <div className="flex justify-between border-b border-border/40 pb-1">
                       <span className="text-muted-foreground">Designation:</span>
                       <span className="font-bold text-foreground">{designation}</span>
                     </div>
                     <div className="flex justify-between border-b border-border/40 pb-1">
                       <span className="text-muted-foreground">Company Name:</span>
                       <span className="font-bold text-foreground">{companyName}</span>
                     </div>
                     <div className="flex justify-between col-span-2 pt-1">
                       <span className="text-muted-foreground">Employment Start Date:</span>
                       <span className="font-bold text-foreground">{joiningDate}</span>
                     </div>
                   </div>
                 </div>

                 {/* Dynamic Letter Body */}
                 <div className="space-y-4 pt-2">
                   <p>
                     With reference to your employment with <strong>{companyName}</strong>, we are pleased to present this document as confirmation. Below is the custom detailed layout and template information:
                   </p>

                   <div className="p-5 bg-primary/5 rounded-2xl border border-primary/10 italic text-slate-700 dark:text-slate-300">
                     {renderContent()}
                   </div>

                   {/* Custom field rendering */}
                   {template.customFields && template.customFields.length > 0 && (
                     <div className="space-y-3 pt-4">
                       <p className="font-black text-[10px] text-muted-foreground uppercase tracking-widest">Additional Dynamic Placeholders:</p>
                       <div className="grid grid-cols-2 gap-4">
                         {template.customFields.map(cf => (
                           <div key={cf.id} className="p-3 bg-secondary/20 rounded-xl border border-border flex flex-col">
                             <span className="text-[9px] text-muted-foreground uppercase font-bold">{cf.label} (<code>{"{{"}{cf.name || cf.label.toLowerCase().replace(/\s+/g, '_')}{"}}"}</code>)</span>
                             <span className="text-xs font-bold mt-1">
                               {cf.type === 'Dropdown' ? (cf.listValues?.[0] || 'Selected Value') : 
                                cf.type === 'Checkbox' ? 'True / Checked' : 
                                cf.type === 'Date' ? '2026-05-19' : 
                                cf.type === 'Number' ? '12345' : 'Sample Value'}
                             </span>
                           </div>
                         ))}
                       </div>
                     </div>
                   )}
                 </div>

                 <p className="pt-4">
                   Should you have any questions or require modifications, please contact the HR Operations desk or route a request via your Employee Self Service (ESS) dashboard.
                 </p>
              </div>

              {/* Authorization Details / Signatory */}
              <div className="pt-8 flex justify-between items-end">
                 <div className="space-y-4">
                    <div className="space-y-1">
                       <p className="text-[10px] font-black text-foreground uppercase tracking-widest">Authorized Signatory</p>
                       <p className="text-xs font-bold text-foreground font-black">{authSignatoryName}</p>
                       <p className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider">{authDesignation} · {companyName}</p>
                    </div>
                    {template.enableDigitalSignature && (
                      <div className="flex items-center gap-2 py-1.5 px-3 rounded-lg border border-emerald-500/20 bg-emerald-500/5 text-emerald-600 w-fit">
                         <ShieldCheck size={14} />
                         <span className="text-[9px] font-black uppercase tracking-widest">PFX Digitally Signed</span>
                      </div>
                    )}
                 </div>
                 <div className="text-center space-y-1 pb-2">
                   <div className="w-36 h-px bg-slate-300 dark:bg-slate-700 mx-auto" />
                   <p className="text-[9px] text-muted-foreground italic">Signature Signature</p>
                 </div>
              </div>

              {/* Footer */}
              <div className="pt-12 text-center border-t border-slate-100 dark:border-slate-800">
                 <p className="text-[8px] font-bold text-muted-foreground uppercase tracking-[0.2em]">
                   This is a system-generated document based on company records and does not require physical validation.
                 </p>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
