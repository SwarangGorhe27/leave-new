import { useMemo } from "react";
import { 
  MoreVertical, 
  ArrowRightLeft, 
  MapPin, 
  Cpu, 
  ShieldCheck, 
  Clock, 
  AlertTriangle,
  UserCheck,
  Smartphone,
  Globe,
  Monitor,
  Eye,
  Edit,
  Trash2,
  Download
} from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "../../ui/avatar";
import { cn } from "../../ui/utils";
import { SwipeLog } from "../../../modules/attendance/types";
import { KebabMenu, KebabMenuItem } from "../../ui/KebabMenu";
import { toast } from "sonner";

interface SwipeLogsTableProps {
  logs: SwipeLog[];
  onSelectSwipe: (swipe: SwipeLog) => void;
  isLoading?: boolean;
  sortField?: string;
  sortOrder?: "asc" | "desc";
  onSort?: (field: string) => void;
  currentPage?: number;
  setCurrentPage?: (page: number) => void;
  pageSize?: number;
  setPageSize?: (size: number) => void;
  totalRecords?: number;
}

export function SwipeLogsTable({ 
  logs, 
  onSelectSwipe,
  isLoading,
  sortField,
  sortOrder,
  onSort,
  currentPage,
  setCurrentPage,
  pageSize,
  setPageSize,
  totalRecords
}: SwipeLogsTableProps) {
  const getDeviceIcon = (type: string) => {
    switch (type) {
      case "Biometric Device": return <Cpu className="w-3 h-3" />;
      case "Mobile App": return <Smartphone className="w-3 h-3" />;
      case "Web Login": return <Monitor className="w-3 h-3" />;
      default: return <Globe className="w-3 h-3" />;
    }
  };

  return (
    <div className="overflow-x-auto relative">
      <table className="w-full text-left border-collapse min-w-[900px]">
        <thead>
          <tr className="bg-slate-50/50 dark:bg-slate-800/30 border-b border-slate-100 dark:border-slate-800">
            <th className="px-4 py-2 text-[9px] font-bold text-slate-400 uppercase tracking-widest cursor-pointer hover:bg-slate-100/50 dark:hover:bg-slate-800/50" onClick={() => onSort?.("employeeName")}>Employee</th>
            <th className="px-4 py-2 text-[9px] font-bold text-slate-400 uppercase tracking-widest cursor-pointer hover:bg-slate-100/50 dark:hover:bg-slate-800/50" onClick={() => onSort?.("swipeTime")}>Swipe Intelligence</th>
            <th className="px-4 py-2 text-[9px] font-bold text-slate-400 uppercase tracking-widest cursor-pointer hover:bg-slate-100/50 dark:hover:bg-slate-800/50" onClick={() => onSort?.("deviceName")}>Device & Source</th>
            <th className="px-4 py-2 text-[9px] font-bold text-slate-400 uppercase tracking-widest cursor-pointer hover:bg-slate-100/50 dark:hover:bg-slate-800/50" onClick={() => onSort?.("branch")}>Location</th>
            <th className="px-4 py-2"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-50 dark:divide-slate-800/50">
          {logs.map((log) => (
            <tr 
              key={log.id} 
              className="group hover:bg-slate-50/50 dark:hover:bg-white/[0.02] transition-colors cursor-pointer"
              onClick={() => onSelectSwipe(log)}
            >
              {/* Employee Info */}
              <td className="px-4 py-2.5">
                <div className="flex items-center gap-2.5">
                  <Avatar className="h-8 w-8 border border-white dark:border-slate-800 shadow-sm shrink-0">
                    <AvatarImage src={log.avatar} />
                    <AvatarFallback className="bg-emerald-500/10 text-emerald-600 text-[10px] font-bold">
                      {log.employeeName.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col min-w-0">
                    <span className="text-[11px] font-bold text-slate-900 dark:text-slate-100 truncate group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                      {log.employeeName}
                    </span>
                    <div className="flex items-center gap-1 mt-0.5">
                      <span className="text-[9px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-tight">{log.employeeCode}</span>
                      <span className="text-[9px] text-slate-300">•</span>
                      <span className="text-[9px] font-medium text-slate-500 dark:text-slate-400 truncate">{log.department}</span>
                    </div>
                  </div>
                </div>
              </td>

              {/* Swipe Intel */}
              <td className="px-4 py-2.5">
                <div className="flex items-center gap-2.5">
                  <div className={cn(
                    "w-7 h-7 rounded-lg flex items-center justify-center shrink-0",
                    log.type === "IN" ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10" : "bg-purple-50 text-purple-600 dark:bg-purple-500/10"
                  )}>
                    <ArrowRightLeft className={cn("w-3 h-3", log.type === "OUT" && "rotate-180")} />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-bold text-slate-900 dark:text-slate-100">{log.swipeTime}</span>
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">{log.type} • {log.swipeDate}</span>
                  </div>
                </div>
              </td>

              {/* Device Info */}
              <td className="px-4 py-2.5">
                <div className="flex flex-col gap-0.5">
                  <div className="flex items-center gap-1.5">
                    <div className="p-1 rounded bg-slate-100 dark:bg-slate-800 text-slate-500">
                      {getDeviceIcon(log.deviceType)}
                    </div>
                    <span className="text-[10px] font-bold text-slate-700 dark:text-slate-300">{log.deviceName}</span>
                  </div>
                  <span className="text-[9px] font-medium text-slate-500 ml-6">{log.deviceType}</span>
                </div>
              </td>

              {/* Location */}
              <td className="px-4 py-2.5">
                <div className="flex flex-col gap-0.5">
                  <div className="flex items-center gap-1.5">
                    <MapPin className="w-3 h-3 text-slate-400" />
                    <span className="text-[10px] font-bold text-slate-700 dark:text-slate-300">{log.branch}</span>
                  </div>
                  <span className="text-[9px] font-medium text-slate-500 truncate max-w-[150px]">{log.doorName}</span>
                </div>
              </td>

              {/* Actions */}
              <td className="px-4 py-2.5 text-right" onClick={(e) => e.stopPropagation()}>
                <KebabMenu 
                  size="sm"
                  items={[
                    { label: "View Details", icon: Eye, onClick: () => onSelectSwipe(log) },
                    { label: "Manual Override", icon: Edit, onClick: () => toast.info(`Manual override for ${log.employeeName}`) },
                    { label: "Download Log", icon: Download, onClick: () => toast.success("Log downloaded") },
                    { label: "Delete Log", icon: Trash2, variant: "destructive", separator: true, onClick: () => {
                      if (confirm("Delete this swipe log?")) toast.success("Log deleted");
                    }},
                  ]}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
