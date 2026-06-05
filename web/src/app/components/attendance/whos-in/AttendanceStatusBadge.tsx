import { Badge } from "../../ui/badge";
import { cn } from "../../ui/utils";

interface AttendanceStatusBadgeProps {
  status: string;
  className?: string;
}

export function AttendanceStatusBadge({ status, className }: AttendanceStatusBadgeProps) {
  const getStatusStyles = (status: string) => {
    switch (status.toLowerCase()) {
      case "on time":
      case "present":
        return "bg-green-500/10 text-green-600 border-green-500/20";
      case "late in":
      case "late arrivals":
        return "bg-amber-500/10 text-amber-600 border-amber-500/20";
      case "not yet in":
      case "absent":
        return "bg-red-500/10 text-red-600 border-red-500/20";
      case "on leave":
      case "leave":
        return "bg-purple-500/10 text-purple-600 border-purple-500/20";
      case "holiday":
        return "bg-blue-500/10 text-blue-600 border-blue-500/20";
      case "week off":
        return "bg-slate-500/10 text-slate-600 border-slate-500/20";
      case "wfh":
        return "bg-indigo-500/10 text-indigo-600 border-indigo-500/20";
      case "field duty":
      case "on duty":
        return "bg-cyan-500/10 text-cyan-600 border-cyan-500/20";
      default:
        return "bg-gray-500/10 text-gray-600 border-gray-500/20";
    }
  };

  return (
    <Badge variant="outline" className={cn("px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider", getStatusStyles(status), className)}>
      {status}
    </Badge>
  );
}
