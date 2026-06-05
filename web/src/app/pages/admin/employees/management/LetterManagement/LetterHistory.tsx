import React, { useState, useMemo } from "react";
import { 
  FileText, 
  Search, 
  Filter, 
  Eye, 
  Pencil,
  Archive,
  FileArchive,
  Users,
  Trash2,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle
} from "lucide-react";
import { Button } from "../../../../../components/ui/button";
import { Input } from "../../../../../components/ui/input";
import { Badge } from "../../../../../components/ui/badge";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "../../../../../components/ui/table";
import { LetterBatch, LetterStatus } from "./types";
import { format } from "date-fns";
import { cn } from "../../../../../components/ui/utils";

interface LetterHistoryProps {
  onViewDetails: (batch: LetterBatch) => void;
  onPreview: (batch: LetterBatch) => void;
  onRepublish: (batch: LetterBatch) => void;
  onDuplicate: (batch: LetterBatch) => void;
  onDeleteBatch?: (id: string) => void;
  onEditBatch?: (batch: LetterBatch) => void;
  batches: LetterBatch[];
}

export function LetterHistory({ onViewDetails, onDeleteBatch, onEditBatch, batches }: LetterHistoryProps) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<LetterStatus | "All">("All");

  const statusConfig: Record<LetterStatus, { color: string, bg: string, icon: any }> = {
    "Draft": { color: "text-slate-400", bg: "bg-slate-400/10", icon: Archive },
    "Pending Approval": { color: "text-amber-500", bg: "bg-amber-500/10", icon: Clock },
    "Approved": { color: "text-indigo-500", bg: "bg-indigo-500/10", icon: CheckCircle2 },
    "Rejected": { color: "text-rose-500", bg: "bg-rose-500/10", icon: XCircle },
    "Published": { color: "text-emerald-500", bg: "bg-emerald-500/10", icon: CheckCircle2 },
    "Cancelled": { color: "text-slate-500", bg: "bg-slate-500/10", icon: AlertCircle }
  };

  const safeFormatDate = (dateString: string | undefined | null, formatStr: string) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return "Invalid Date";
    return format(date, formatStr);
  };

  const filteredHistory = useMemo(() => {
    return batches.filter(item => {
      const searchLower = search.toLowerCase();
      const matchesSearch = 
        item.id.toLowerCase().includes(searchLower) ||
        item.subject.toLowerCase().includes(searchLower) || 
        item.letterType.toLowerCase().includes(searchLower) ||
        item.templateName?.toLowerCase().includes(searchLower) ||
        item.createdBy.toLowerCase().includes(searchLower) ||
        item.status.toLowerCase().includes(searchLower);
        
      const matchesStatus = statusFilter === "All" || item.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [search, statusFilter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-foreground">Generated Letter History</h3>
          <p className="text-xs font-medium text-muted-foreground">Manage and track all previously generated employee letters.</p>
        </div>
        <div className="flex items-center gap-2 w-full md:w-auto">
          <div className="relative flex-1 md:w-80">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input 
              placeholder="Search letters, subjects..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 h-10 bg-card rounded-xl" 
            />
          </div>
          <Button variant="outline" size="icon" className="h-10 w-10 rounded-xl">
            <Filter className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="bg-card border border-border rounded-[2.5rem] overflow-hidden shadow-sm">
        <Table>
          <TableHeader className="bg-muted/30">
            <TableRow className="hover:bg-transparent border-border">
              <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground pl-8">Batch Details</TableHead>
              <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground text-center">Recipients</TableHead>
              <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Effective Date</TableHead>
              <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Approval Status</TableHead>
              <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Published By</TableHead>
              <TableHead className="text-[10px] font-black uppercase tracking-widest text-muted-foreground pr-8 text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredHistory.map((batch) => {
              const config = statusConfig[batch.status];
              const StatusIcon = config.icon;

              return (
                <TableRow
                  key={batch.id}
                  onClick={() => onViewDetails(batch)}
                  className="border-border/50 group hover:bg-secondary/30 transition-colors cursor-pointer"
                >
                  <TableCell className="pl-8 py-5">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-xl bg-primary/5 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                        <FileText size={20} />
                      </div>
                      <div>
                        <p className="text-sm font-black text-foreground">{batch.subject}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">{batch.letterType}</span>
                          <span className="w-1 h-1 rounded-full bg-border" />
                          <span className="text-[10px] font-medium text-muted-foreground">{safeFormatDate(batch.createdAt, "dd MMM yyyy")}</span>
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-center">
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-secondary rounded-full border border-border">
                      <Users size={12} className="text-muted-foreground" />
                      <span className="text-xs font-black">{batch.selectedEmployeeIds.length}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="text-xs font-bold text-foreground">{safeFormatDate(batch.effectiveDate, "dd MMM yyyy")}</span>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={cn("text-[9px] font-black uppercase tracking-widest rounded-md border-transparent px-2 py-1 flex items-center gap-1.5 w-fit", config.bg, config.color)}>
                      <StatusIcon size={10} />
                      {batch.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-indigo-500 flex items-center justify-center text-[8px] font-black text-white">SC</div>
                      <span className="text-xs font-bold text-muted-foreground">{batch.createdBy}</span>
                    </div>
                  </TableCell>
                  <TableCell
                    className="pr-8 text-right"
                    onClick={(e) => e.stopPropagation()}
                    onPointerDown={(e) => e.stopPropagation()}
                  >
                    <div className="flex items-center justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        title="View"
                        aria-label={`View ${batch.subject}`}
                        onClick={() => onViewDetails(batch)}
                        className="h-8 w-8 rounded-lg text-muted-foreground hover:bg-primary/10 hover:text-primary"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>

                      {onEditBatch && (
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Edit"
                          aria-label={`Edit ${batch.subject}`}
                          onClick={() => onEditBatch(batch)}
                          className="h-8 w-8 rounded-lg text-muted-foreground hover:bg-amber-500/10 hover:text-amber-600"
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                      )}

                      {onDeleteBatch && (
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Delete"
                          aria-label={`Delete ${batch.subject}`}
                          onClick={() => onDeleteBatch(batch.id)}
                          className="h-8 w-8 rounded-lg text-muted-foreground hover:bg-rose-500/10 hover:text-rose-600"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {filteredHistory.length === 0 && (
        <div className="py-24 text-center bg-card/30 rounded-[3rem] border-2 border-dashed border-border/50 backdrop-blur-sm">
          <div className="w-20 h-20 bg-secondary/50 rounded-full flex items-center justify-center mx-auto mb-6 shadow-inner">
            <FileArchive className="w-10 h-10 text-muted-foreground/30" />
          </div>
          <h3 className="text-xl font-black text-foreground mb-2">No letters found</h3>
          <p className="text-sm font-medium text-muted-foreground max-w-xs mx-auto">Try adjusting your filters or search terms to find what you're looking for.</p>
        </div>
      )}
    </div>
  );
}
