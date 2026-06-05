import { Badge, Button } from '@components/ui';
import type { Employee } from '@/types/employee';

interface EmployeeLifecycleTabProps {
  employee: Employee;
}

export function EmployeeLifecycleTab({ employee }: EmployeeLifecycleTabProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-surface-900 dark:text-white">Lifecycle events</h3>
          <p className="text-sm text-surface-600 dark:text-white/55">Track changes across joining, confirmation, promotion, and compensation updates.</p>
        </div>
        <Button>Add event</Button>
      </div>
      <div className="space-y-4">
        {employee.lifecycle.map((event) => (
          <article key={event.id} className="surface-card flex gap-4 p-5">
            <div className="flex flex-col items-center">
              <Badge variant="brand">{event.date}</Badge>
              <span className="mt-3 h-full w-px bg-surface-300 dark:bg-white/10" />
            </div>
            <div className="pb-4">
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-semibold text-surface-900 dark:text-white">{event.title}</h4>
                <Badge variant="neutral">{event.type}</Badge>
              </div>
              <p className="mt-2 text-sm text-surface-600 dark:text-white/55">{event.details}</p>
              <p className="mt-3 text-xs text-surface-500 dark:text-white/35">Recorded by {event.actor}</p>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
