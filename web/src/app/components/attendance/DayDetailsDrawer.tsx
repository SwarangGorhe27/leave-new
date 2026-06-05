import { Loader2 } from 'lucide-react';
import { useAttendanceStore } from '../../modules/attendance/store';
import { useEmployeeDayDetail } from '../../modules/attendance/hooks';

export function DayDetailsDrawer({ employeeId }: { employeeId?: string }) {
  const { selectedDate, setSelectedDate } = useAttendanceStore();
  const date = selectedDate ? new Date(selectedDate) : undefined;

  const { data: detail, isLoading, isError } = useEmployeeDayDetail(employeeId, date);

  if (!selectedDate) return null;

  const punches = (detail as { punches?: Array<{ punch_time: string; punch_type: string; punch_source: string }> })?.punches ?? [];

  return (
    <div className="fixed inset-0 z-50 bg-black/30 flex justify-end">
      <div className="w-full max-w-md h-full bg-card border-l border-border p-5 overflow-y-auto glassmorph-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-foreground">Day Details</h3>
          <button onClick={() => setSelectedDate(null)} className="text-sm border border-border rounded px-2 py-1">Close</button>
        </div>
        <p className="text-sm text-muted-foreground mb-3">{selectedDate}</p>

        {isLoading && (
          <div className="flex items-center gap-2 text-muted-foreground text-sm py-8">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading day details…
          </div>
        )}

        {isError && (
          <p className="text-sm text-red-600">Failed to load attendance details for this date.</p>
        )}

        {!isLoading && !isError && detail && (
          <div className="space-y-3 text-sm">
            <div className="rounded-lg border border-border p-3">
              <p>Status: <span className="font-semibold">{String((detail as { status_code?: string }).status_code ?? '—')}</span></p>
              <p>First In: {String((detail as { first_in?: string }).first_in ?? '—')}</p>
              <p>Last Out: {String((detail as { last_out?: string }).last_out ?? '—')}</p>
              <p>
                Work Minutes: {(detail as { actual_work_mins?: number }).actual_work_mins ?? 0}
                {' '}| OT: {(detail as { ot_mins?: number }).ot_mins ?? 0}m
              </p>
              <p>
                Late: {(detail as { late_in_mins?: number }).late_in_mins ?? 0}m
                {' '}| Early Exit: {(detail as { early_exit_mins?: number }).early_exit_mins ?? 0}m
              </p>
              <p>Shift: {(detail as { shift_name?: string }).shift_name ?? '—'}</p>
              <p>Payroll Lock: {(detail as { is_locked?: boolean }).is_locked ? 'Locked' : 'Open'}</p>
            </div>
            <div className="rounded-lg border border-border p-3">
              <p className="font-semibold mb-2">Punch Logs</p>
              <div className="space-y-2">
                {punches.length === 0 && <p className="text-muted-foreground">No punch logs for this date.</p>}
                {punches.map((log, index) => (
                  <p key={`${log.punch_time}-${index}`} className="text-xs">
                    {log.punch_time} — {log.punch_type} ({log.punch_source})
                  </p>
                ))}
              </div>
            </div>
            {(detail as { regularization?: unknown }).regularization && (
              <div className="rounded-lg border border-border p-3">
                <p className="font-semibold mb-2">Regularization</p>
                <p className="text-xs text-muted-foreground">A regularization request exists for this day.</p>
              </div>
            )}
            {(detail as { leave?: unknown }).leave && (
              <div className="rounded-lg border border-border p-3">
                <p className="font-semibold mb-2">Leave</p>
                <p className="text-xs text-muted-foreground">Leave applied on this date.</p>
              </div>
            )}
          </div>
        )}

        {!isLoading && !isError && !detail && (
          <p className="text-sm text-muted-foreground">No attendance data found for selected date.</p>
        )}
      </div>
    </div>
  );
}
