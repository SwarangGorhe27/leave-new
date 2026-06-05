import { FileText, Eye, Plus, Info } from "lucide-react";
import { Button } from "@/app/components/ui/button";

interface TemplateGalleryCardProps {
  name: string;
  description: string;
  onAdd: () => void;
  onPreview: () => void;
}

export function TemplateGalleryCard({ name, description, onAdd, onPreview }: TemplateGalleryCardProps) {
  return (
    <div className="bg-card border border-border rounded-2xl p-5 hover:shadow-xl hover:border-foreground/20 transition-all group flex flex-col h-full">
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 rounded-2xl bg-secondary flex items-center justify-center group-hover:bg-foreground group-hover:text-primary-foreground transition-all duration-300">
           <FileText size={22} />
        </div>
        <button 
          onClick={onPreview}
          className="w-8 h-8 rounded-full border border-border flex items-center justify-center text-muted-foreground hover:bg-secondary transition-all"
        >
           <Eye size={14} />
        </button>
      </div>
      
      <div className="flex-1 space-y-2">
         <h4 className="text-[13px] font-black text-foreground uppercase tracking-tight">{name}</h4>
         <p className="text-[11px] text-muted-foreground leading-relaxed">{description}</p>
      </div>

      <div className="mt-6 pt-4 border-t border-border/50">
         <Button 
          onClick={onAdd}
          className="w-full h-9 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest gap-2 hover:bg-accent transition-all"
         >
            <Plus size={12} strokeWidth={3} />
            Add to My Templates
         </Button>
      </div>
    </div>
  );
}
