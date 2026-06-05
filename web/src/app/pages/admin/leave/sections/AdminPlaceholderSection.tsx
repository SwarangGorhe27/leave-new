import { Construction } from "lucide-react";

export function AdminPlaceholderSection({ title }: { title: string }) {
  return (
    <div className="flat-card bg-card p-8">
      <div className="flex flex-col md:flex-row md:items-center gap-4 justify-between">
        <div>
          <h2 className="text-base font-semibold text-foreground">{title}</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Enterprise-grade UI scaffold is ready. Next step is wiring data + flows for this section.
          </p>
        </div>
        <div className="w-11 h-11 rounded-lg bg-secondary border border-border flex items-center justify-center flex-shrink-0">
          <Construction className="w-5 h-5 text-muted-foreground" />
        </div>
      </div>
    </div>
  );
}

