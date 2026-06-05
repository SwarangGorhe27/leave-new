import { useState } from "react";
import { ChevronDown, ChevronUp, Mail, Phone, MapPin, Monitor, User, Calendar, Clock, History, TrendingUp, CheckCircle, Edit, Send, ExternalLink } from "lucide-react";
import { AttendanceStatusBadge } from "./AttendanceStatusBadge";
import { Button } from "../../ui/button";
import { cn } from "../../ui/utils";
import { DailyAttendance } from "../../../modules/attendance/types";
import { useEmployee } from "../../../context/EmployeeContext";

interface EmployeeAttendanceCardProps {
  record: DailyAttendance;
  type: "not-yet-in" | "late" | "on-time" | "ooo" | "absent";
}

export function EmployeeAttendanceCard({ record, type }: EmployeeAttendanceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { selectEmployee } = useEmployee();

  return (
    <div className={cn(
      "group border border-border rounded-xl bg-card transition-all duration-300 glassmorph-card flex flex-col h-full",
      isExpanded ? "shadow-md ring-1 ring-primary/20 scale-[1.02] z-10" : "hover:border-primary/30 hover:shadow-sm"
    )}>
      <div className="p-3 flex flex-col flex-1">
        {/* Header: Avatar + Status */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-secondary/50 flex items-center justify-center text-primary font-bold text-xs border border-border">
              {record.employeeName.split(" ").map(n => n[0]).join("")}
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-bold text-foreground leading-tight group-hover:text-primary transition-colors">{record.employeeName}</span>
              <span className="text-[9px] text-muted-foreground font-medium">{record.employeeId}</span>
            </div>
          </div>
          <AttendanceStatusBadge status={record.status} className="shadow-none scale-90 origin-top-right" />
        </div>

        {/* Info Grid */}
        <div className="grid grid-cols-2 gap-2 mb-3">
          <div className="bg-secondary/20 rounded-md p-1.5 border border-secondary/10">
            <p className="text-[8px] text-muted-foreground uppercase font-bold tracking-wider mb-0.5">
              {type === "not-yet-in" ? "Expected" : (type === "absent" ? "Last Present" : "Login Time")}
            </p>
            <p className={cn(
              "text-[10px] font-bold",
              type === "not-yet-in" || type === "absent" ? "text-red-500" : (type === "late" ? "text-amber-500" : "text-green-500")
            )}>
              {type === "not-yet-in" ? (record.expectedInTime || "09:00 AM") : (type === "absent" ? (record.lastAttendanceDate || "N/A") : record.firstIn)}
            </p>
          </div>
          
          <div className="bg-secondary/20 rounded-md p-1.5 border border-secondary/10">
            <p className="text-[8px] text-muted-foreground uppercase font-bold tracking-wider mb-0.5">Work Mode</p>
            <div className="flex items-center gap-1">
              <Monitor className="w-2.5 h-2.5 text-muted-foreground" />
              <span className="text-[10px] font-bold truncate">{record.workMode}</span>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-1 mb-3 flex-1">
          <div className="flex items-center justify-between text-[10px]">
            <span className="text-muted-foreground font-medium">Department</span>
            <span className="font-bold truncate max-w-[90px]">{record.department}</span>
          </div>
          <div className="flex items-center justify-between text-[10px]">
            <span className="text-muted-foreground font-medium">Shift</span>
            <span className="font-bold">{record.shiftName?.split('(')[1]?.split('-')[0] || "09:00"}</span>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center gap-2 mt-auto pt-2 border-t border-border/50">
          <Button 
            variant="ghost" 
            size="sm" 
            className="flex-1 h-7 text-[10px] font-bold gap-1 glassmorph-button rounded-md"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            {isExpanded ? "Collapse" : "Details"}
          </Button>
          <Button 
            variant="outline" 
            size="icon" 
            className="h-7 w-7 rounded-md shrink-0 glassmorph-button"
            onClick={() => selectEmployee(record.id)}
            title="View Full Profile"
          >
            <ExternalLink className="w-3 h-3" />
          </Button>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="px-3 pb-3 animate-in slide-in-from-top-2 duration-300">
           <div className="bg-secondary/10 rounded-lg p-2.5 space-y-2.5">
              <div className="space-y-1.5 pb-2 border-b border-border/50">
                <div className="flex items-center justify-between">
                  <span className="text-[9px] text-muted-foreground font-bold uppercase">Manager</span>
                  <span className="text-[10px] font-bold">{record.manager || "Rajesh Kumar"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[9px] text-muted-foreground font-bold uppercase">Contact</span>
                  <span className="text-[10px] font-bold text-primary underline underline-offset-2 decoration-primary/30 cursor-pointer">{record.contactNo || "+91 98765 43210"}</span>
                </div>
              </div>

              {type === "absent" ? (
                <div className="p-2 rounded-md bg-red-500/5 border border-red-500/10">
                  <p className="text-[8px] text-red-600 font-bold uppercase">Risk Level</p>
                  <p className="text-[10px] font-bold text-red-700">Critical: {record.lop || 2} Days Streak</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-1.5">
                  <div className="p-1.5 bg-card/50 rounded-md border border-border">
                    <p className="text-[8px] text-muted-foreground font-bold uppercase mb-0.5">Avg Login</p>
                    <p className="text-[10px] font-bold">{record.avgLoginTime || "09:05 AM"}</p>
                  </div>
                  <div className="p-1.5 bg-card/50 rounded-md border border-border">
                    <p className="text-[8px] text-muted-foreground font-bold uppercase mb-0.5">Balance</p>
                    <p className="text-[10px] font-bold">{record.leaveBalance || 15}d</p>
                  </div>
                </div>
              )}

              <div className="flex gap-1.5 pt-0.5">
                <Button variant="outline" size="sm" className="flex-1 h-7 text-[9px] font-bold gap-1 px-1 rounded-md">
                  <CheckCircle className="w-2.5 h-2.5 text-green-500" /> Present
                </Button>
                <Button variant="outline" size="sm" className="flex-1 h-7 text-[9px] font-bold gap-1 px-1 rounded-md">
                  <Edit className="w-2.5 h-2.5 text-blue-500" /> Regularize
                </Button>
                <Button variant="outline" size="sm" className="flex-1 h-7 text-[9px] font-bold gap-1 px-1 rounded-md">
                  <Send className="w-2.5 h-2.5 text-primary" /> Notify
                </Button>
              </div>
           </div>
        </div>
      )}
    </div>
  );
}
