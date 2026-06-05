import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchMatrixGrid,
  fetchEmployeeDayDetail,
  updateEmployeeDayStatus,
  fetchEntityAuditHistory,
} from '../app/modules/attendance/api';
import { unwrapList } from '../app/modules/attendance/mappers';
import type { MatrixRowApi } from '../app/modules/attendance/apiTypes';

const STATUS_FROM_CELL: Record<string, string> = {
  P: 'PRESENT',
  A: 'ABSENT',
  L: 'LEAVE',
  H: 'HOLIDAY',
  HO: 'HOLIDAY',
  W: 'WEEK_OFF',
  WO: 'WEEK_OFF',
  HD: 'HALF_DAY',
  WFH: 'PRESENT',
};

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

export interface AdminAttendanceRecord {
  id: string;
  employee: string;
  employee_code: string;
  employee_name: string;
  date: string;
  shift: string | null;
  shift_name: string;
  first_in: string | null;
  last_out: string | null;
  effective_hours: string | null;
  late_mins: number;
  early_leave_mins: number;
  overtime_mins: number;
  status: string;
  is_regularized: boolean;
  remarks: string;
  is_admin_edited: boolean;
  admin_edit_reason: string;
  admin_edited_at: string | null;
  original_first_in: string | null;
  original_last_out: string | null;
  original_status: string;
  last_changed_by_source: string;
  regularization_ref: string | null;
}

export interface AttendanceEditLogEntry {
  id: string;
  attendance_record: string;
  employee: string;
  date: string;
  field_changed: string;
  old_value: string;
  new_value: string;
  change_source: string;
  changed_by: string;
  changed_by_name: string;
  changed_by_code: string;
  reason: string;
  regularization_request: string | null;
  ip_address: string | null;
  created_at: string;
}

export interface OverridePayload {
  first_in?: string | null;
  last_out?: string | null;
  status?: string;
  reason: string;
}

function mapGridRowsToRecords(rows: MatrixRowApi[]): AdminAttendanceRecord[] {
  const records: AdminAttendanceRecord[] = [];
  for (const row of rows) {
    for (const cell of row.days ?? []) {
      const code = cell.cell_code ?? cell.status_code ?? '';
      const status = STATUS_FROM_CELL[code] ?? (cell.status_code ?? 'ABSENT');
      records.push({
        id: `${row.employee_id}-${cell.date}`,
        employee: row.employee_id,
        employee_code: row.employee_code,
        employee_name: row.full_name,
        date: cell.date,
        shift: null,
        shift_name: '—',
        first_in: null,
        last_out: null,
        effective_hours: null,
        late_mins: 0,
        early_leave_mins: 0,
        overtime_mins: 0,
        status,
        is_regularized: false,
        remarks: '',
        is_admin_edited: false,
        admin_edit_reason: '',
        admin_edited_at: null,
        original_first_in: null,
        original_last_out: null,
        original_status: status,
        last_changed_by_source: 'SYSTEM',
        regularization_ref: null,
      });
    }
  }
  return records;
}

async function fetchAdminRecords(params: Record<string, string>): Promise<AdminAttendanceRecord[]> {
  if (params._skip) return [];

  const month = Number(params.month ?? new Date().getMonth() + 1);
  const year = Number(params.year ?? new Date().getFullYear());
  const grid = await fetchMatrixGrid({
    year,
    month,
    page: 1,
    page_size: 100,
    department_id: params.department_id,
    search: params.search,
  });
  return mapGridRowsToRecords(grid.rows ?? []);
}

function parseRecordId(recordId: string): { employeeId: string; date: string } | null {
  const match = recordId.match(/^(.+)-(\d{4}-\d{2}-\d{2})$/);
  if (!match) return null;
  return { employeeId: match[1], date: match[2] };
}

async function fetchAuditLog(recordId: string): Promise<AttendanceEditLogEntry[]> {
  const parsed = parseRecordId(recordId);
  if (!parsed) return [];
  const { employeeId, date } = parsed;

  try {
    const res = await fetchEntityAuditHistory({
      entity_type: 'daily_attendance',
      entity_id: employeeId,
      date_from: date,
      date_to: date,
    });
    const rows = unwrapList(res as { results?: unknown[] }) as Array<Record<string, unknown>>;
    return rows.map((row, index) => ({
      id: String(row.id ?? index),
      attendance_record: recordId,
      employee: employeeId,
      date,
      field_changed: String(row.field_name ?? row.field_changed ?? 'status'),
      old_value: String(row.old_value ?? ''),
      new_value: String(row.new_value ?? ''),
      change_source: String(row.change_source ?? row.source ?? 'SYSTEM'),
      changed_by: String(row.changed_by ?? ''),
      changed_by_name: String(row.changed_by_name ?? '—'),
      changed_by_code: String(row.changed_by_code ?? '—'),
      reason: String(row.reason ?? ''),
      regularization_request: null,
      ip_address: null,
      created_at: String(row.created_at ?? new Date().toISOString()),
    }));
  } catch {
    return [];
  }
}

export function useAdminAttendanceRecords(filters: Record<string, string>) {
  return useQuery({
    queryKey: ['admin-attendance-records', filters],
    queryFn: () => fetchAdminRecords(filters),
    staleTime: 30_000,
    enabled: !filters._skip,
  });
}

export function useAttendanceAuditLog(recordId: string | null) {
  return useQuery({
    queryKey: ['attendance-audit-log', recordId],
    queryFn: () => fetchAuditLog(recordId!),
    enabled: !!recordId,
    staleTime: 10_000,
  });
}

export function useAttendanceOverride() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ recordId, payload }: { recordId: string; payload: OverridePayload }) => {
      const parsed = parseRecordId(recordId);
      if (!parsed) {
        throw new Error('Invalid attendance record id');
      }
      const { employeeId, date } = parsed;

      if (payload.status) {
        await updateEmployeeDayStatus(employeeId, {
          date,
          status_code: payload.status,
        });
      }

      const detail = await fetchEmployeeDayDetail(employeeId, date);
      const d = detail as Record<string, unknown>;
      return {
        id: recordId,
        employee: employeeId,
        employee_code: '',
        employee_name: '',
        date,
        shift: null,
        shift_name: String(d.shift_name ?? '—'),
        first_in: (payload.first_in ?? d.first_in ?? null) as string | null,
        last_out: (payload.last_out ?? d.last_out ?? null) as string | null,
        effective_hours: null,
        late_mins: Number(d.late_in_mins ?? 0),
        early_leave_mins: Number(d.early_exit_mins ?? 0),
        overtime_mins: Number(d.ot_mins ?? 0),
        status: String(payload.status ?? d.status_code ?? 'PRESENT'),
        is_regularized: !!d.regularization,
        remarks: payload.reason,
        is_admin_edited: true,
        admin_edit_reason: payload.reason,
        admin_edited_at: new Date().toISOString(),
        original_first_in: (d.first_in ?? null) as string | null,
        original_last_out: (d.last_out ?? null) as string | null,
        original_status: String(d.status_code ?? ''),
        last_changed_by_source: 'ADMIN_OVERRIDE',
        regularization_ref: null,
      } satisfies AdminAttendanceRecord;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin-attendance-records'] });
      qc.invalidateQueries({ queryKey: ['attendance-audit-log'] });
    },
  });
}
