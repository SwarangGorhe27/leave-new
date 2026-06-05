import { Mail, Briefcase, Building2, Hash, ArrowRight } from 'lucide-react';
import type { EmployeeListItem } from '@hooks/useEmployees';
import { cn } from '@utils/utils';

interface EmployeeCardProps {
  employee: EmployeeListItem;
  onClick?: () => void;
}

export function EmployeeCard({ employee, onClick }: EmployeeCardProps) {
  return (
    <div 
      className={cn(
        "surface-card group relative overflow-hidden p-5 transition-all duration-300 hover:shadow-xl dark:hover:shadow-brand-500/10",
        onClick && "cursor-pointer"
      )}
      onClick={onClick}
    >
      {/* Background Decorative Element */}
      <div className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-brand-500/5 transition-transform duration-500 group-hover:scale-150" />
      
      <div className="relative space-y-4">
        {/* Avatar & Basic Info */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-brand-100 text-lg font-bold text-brand-700 dark:bg-brand-500/20 dark:text-brand-300">
              {employee.first_name[0]}{employee.last_name[0]}
            </div>
            <div>
              <h4 className="font-bold text-text-primary group-hover:text-brand-500 transition-colors">
                {employee.full_name}
              </h4>
              <div className="flex items-center gap-1.5 text-xs text-text-tertiary">
                <Hash className="h-3 w-3" />
                {employee.employee_code}
              </div>
            </div>
          </div>
          
          {/* Status Badge */}
          {employee.status_detail && (
            <div 
              className="flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider"
              style={{ 
                backgroundColor: `${employee.status_detail.color_code}15`,
                color: employee.status_detail.color_code 
              }}
            >
              <span 
                className="h-1.5 w-1.5 rounded-full" 
                style={{ backgroundColor: employee.status_detail.color_code }} 
              />
              {employee.status_detail.name}
            </div>
          )}
        </div>

        {/* Roles & Dept */}
        <div className="grid grid-cols-2 gap-3 pt-2">
          <div className="space-y-1">
            <p className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-text-tertiary">
              <Briefcase className="h-3 w-3" />
              Designation
            </p>
            <p className="truncate text-xs font-medium text-text-secondary">
              {employee.designation}
            </p>
          </div>
          <div className="space-y-1">
            <p className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-text-tertiary">
              <Building2 className="h-3 w-3" />
              Department
            </p>
            <p className="truncate text-xs font-medium text-text-secondary">
              {employee.department}
            </p>
          </div>
        </div>

        {/* Contact info footer */}
        <div className="flex items-center justify-between border-t border-surface-100 pt-4 dark:border-white/5">
          <div className="flex items-center gap-2 text-xs text-text-tertiary">
            <Mail className="h-3.5 w-3.5" />
            <span className="truncate max-w-[140px]">{employee.work_email}</span>
          </div>
          <button className="flex h-8 w-8 items-center justify-center rounded-lg bg-surface-50 text-text-tertiary transition-all hover:bg-brand-500 hover:text-white dark:bg-white/5">
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
