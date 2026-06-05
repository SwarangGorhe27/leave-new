import { X, Download, FileText, Printer, Calendar, User, Building2, MapPin, ShieldCheck } from "lucide-react";
import { LetterTemplate } from "@/store/slices/letterSlice";
import { Button } from "@/app/components/ui/button";

interface TemplatePreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  template: LetterTemplate | null;
}

export function TemplatePreviewModal({ isOpen, onClose, template }: TemplatePreviewModalProps) {
  if (!isOpen || !template) return null;

  const currentDate = new Date().toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm animate-in fade-in duration-300">
      <div className="bg-white dark:bg-slate-950 w-full max-w-4xl h-[90vh] rounded-3xl border border-border shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-300">
        
        {/* Header Controls */}
        <div className="px-8 py-6 border-b border-border flex items-center justify-between bg-secondary/10">
          <div className="flex items-center gap-4">
             <div className="w-10 h-10 rounded-xl bg-foreground text-primary-foreground flex items-center justify-center">
                <FileText size={20} />
             </div>
             <div>
                <h2 className="text-sm font-black text-foreground uppercase tracking-tight">{template.name}</h2>
                <p className="text-[10px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">Preview Mode · Dynamic View</p>
             </div>
          </div>
          <div className="flex items-center gap-3">
             <Button variant="outline" className="h-9 gap-2 text-[10px] font-black uppercase rounded-xl">
                <Printer size={14} /> Print
             </Button>
             <Button className="h-9 gap-2 text-[10px] font-black uppercase rounded-xl bg-foreground text-primary-foreground">
                <Download size={14} /> Export PDF
             </Button>
             <div className="w-px h-6 bg-border mx-2" />
             <button onClick={onClose} className="w-9 h-9 rounded-full border border-border flex items-center justify-center hover:bg-secondary transition-all">
                <X size={16} />
             </button>
          </div>
        </div>

        {/* Document Content */}
        <div className="flex-1 overflow-y-auto p-12 bg-secondary/5 no-scrollbar">
           <div className="max-w-[800px] mx-auto bg-white dark:bg-slate-900 shadow-2xl border border-border p-16 space-y-12 min-h-[1000px] relative overflow-hidden">
              
              {/* Watermark for preview */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-[0.03] rotate-[-45deg]">
                 <span className="text-9xl font-black uppercase tracking-[0.5em]">PREVIEW</span>
              </div>

              {/* Company Header */}
              <div className="flex justify-between items-start">
                 <div className="space-y-4">
                    <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center">
                       <Building2 size={32} className="text-slate-400" />
                    </div>
                    <div className="space-y-1">
                       <h3 className="text-lg font-black text-foreground uppercase tracking-tight">Ampcus Tech Pvt Ltd</h3>
                       <p className="text-[10px] text-muted-foreground font-bold leading-relaxed max-w-[240px]">
                          123 Business Avenue, Tech Park Phase II, <br />
                          Electronic City, Bangalore - 560100, <br />
                          Karnataka, India
                       </p>
                    </div>
                 </div>
                 <div className="text-right space-y-1">
                    <p className="text-[11px] font-black text-foreground uppercase tracking-widest">{template.numberSeries?.prefix || 'REF'}/2024/{template.numberSeries?.startNumber || '001'}</p>
                    <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">{currentDate}</p>
                 </div>
              </div>

              {/* Title */}
              <div className="text-center py-6">
                 <h1 className="text-xl font-black text-foreground uppercase tracking-[0.3em] border-b-2 border-foreground/10 pb-4 inline-block px-12">
                   {template.name}
                 </h1>
              </div>

              {/* Salutation & Body */}
              <div className="space-y-8 text-[13px] leading-relaxed text-slate-800 dark:text-slate-200">
                 <p className="font-bold">To,</p>
                 <div className="space-y-1">
                    <p className="font-black text-foreground">John Doe</p>
                    <p className="font-bold text-muted-foreground">Software Engineer</p>
                    <p className="text-muted-foreground">EMP-2024-001</p>
                 </div>

                 <p className="pt-4">Dear <span className="font-black text-primary">John Doe</span>,</p>

                 <p>
                    With reference to your employment with <strong>Ampcus Tech Pvt Ltd</strong>, we are pleased to issue this 
                    <strong> {template.name}</strong>. This document serves as an official confirmation of the terms and conditions 
                    associated with your role as a <strong>Software Engineer</strong> within the <strong>Engineering</strong> department.
                 </p>

                 <p>
                    Since your joining date on <strong>01 June 2024</strong>, your contribution to the team has been highly valued. 
                    The company appreciates your dedication and professionalism in handling your responsibilities.
                 </p>

                 {template.description && (
                   <div className="p-6 bg-secondary/20 rounded-2xl border border-border/50 italic">
                      {template.description}
                   </div>
                 )}

                 <p>
                    Please note that this letter is issued based on the records available in the system. Any further adjustments or 
                    requests regarding this document must be routed through the proper HR channels or requested via the ESS portal.
                 </p>

                 <p>
                    We wish you continued success in your journey with us.
                 </p>
              </div>

              {/* Signatory */}
              <div className="pt-12 flex justify-between items-end">
                 <div className="space-y-6">
                    <div className="space-y-1">
                       <p className="text-[11px] font-black text-foreground uppercase tracking-widest">Authorized Signatory</p>
                       <p className="text-xs font-bold text-muted-foreground italic">Digitally Signed by HR Admin</p>
                    </div>
                    <div className="flex items-center gap-3 py-2 px-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5 text-emerald-600">
                       <ShieldCheck size={16} />
                       <span className="text-[10px] font-black uppercase tracking-widest">Verified Signature</span>
                    </div>
                 </div>
                 <div className="w-48 h-px bg-slate-200" />
              </div>

              {/* Footer */}
              <div className="pt-20 text-center border-t border-slate-100">
                 <p className="text-[9px] font-bold text-muted-foreground uppercase tracking-[0.2em]">
                   This is a computer-generated document and does not require a physical signature if digitally verified.
                 </p>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
