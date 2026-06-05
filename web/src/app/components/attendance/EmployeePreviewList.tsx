import { Card, CardContent } from "../ui/card";
import { Button } from "../ui/button";
import { ChevronRight } from "lucide-react";
import { Badge } from "../ui/badge";

interface EmployeePreview {
  id: string;
  name: string;
  department: string;
  loginTime: string;
  status: "On Time" | "Late In" | "Not Yet In";
}

interface EmployeePreviewListProps {
  employees: EmployeePreview[];
}

export function EmployeePreviewList({ employees }: EmployeePreviewListProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "On Time": return "bg-green-500/10 text-green-600 border-green-500/20";
      case "Late In": return "bg-amber-500/10 text-amber-600 border-amber-500/20";
      case "Not Yet In": return "bg-red-500/10 text-red-600 border-red-500/20";
      default: return "bg-gray-500/10 text-gray-600 border-gray-500/20";
    }
  };

  return (
    <div className="mt-6">
      <div className="flex items-center justify-between mb-4 px-2">
        <h4 className="text-sm font-bold text-foreground">Employee Presence</h4>
        <Button variant="ghost" size="sm" className="text-xs h-8 text-muted-foreground hover:text-foreground">
          View All <ChevronRight className="ml-1 w-3 h-3" />
        </Button>
      </div>

      <div className="space-y-2">
        {employees.length > 0 ? (
          employees.map((emp) => (
            <div 
              key={emp.id} 
              className="flex items-center justify-between p-3 rounded-xl border border-border bg-card hover:bg-secondary/20 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-foreground/5 flex items-center justify-center text-xs font-bold text-foreground">
                  {emp.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <p className="text-sm font-semibold leading-none">{emp.name}</p>
                  <p className="text-[11px] text-muted-foreground mt-1">{emp.department}</p>
                </div>
              </div>

              <div className="flex items-center gap-4 text-right">
                <div className="hidden sm:block">
                  <p className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider">Login</p>
                  <p className="text-xs font-medium">{emp.loginTime || "--:--"}</p>
                </div>
                <Badge variant="outline" className={getStatusColor(emp.status)}>
                  {emp.status}
                </Badge>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-muted-foreground text-sm border border-dashed border-border rounded-xl">
            No employees found for the selected criteria.
          </div>
        )}
      </div>
    </div>
  );
}
