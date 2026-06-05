import { useCallback, useEffect, useState } from 'react';
import {
  fetchManagerOvertimeRequests,
  fetchManagerRegularizations,
  ManagerAttendanceApiError,
} from '../../api/managerAttendanceClient';
import type { ManagerApprovalListParams } from '../../api/managerAttendanceClient';
import {
  overtimeListToRow,
  regularizationListToRow,
  type UnifiedApprovalRow,
} from '../modules/manager-attendance/approvalsMappers';

export function useManagerApprovals(filters?: ManagerApprovalListParams) {
  const [rows, setRows] = useState<UnifiedApprovalRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [regularizations, overtime] = await Promise.all([
        fetchManagerRegularizations(filters),
        fetchManagerOvertimeRequests(filters),
      ]);
      const merged = [
        ...regularizations.map(regularizationListToRow),
        ...overtime.map(overtimeListToRow),
      ].sort((a, b) => b.submittedOn.localeCompare(a.submittedOn));
      setRows(merged);
    } catch (err) {
      const message =
        err instanceof ManagerAttendanceApiError
          ? err.message
          : 'Failed to load attendance approvals.';
      setError(message);
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, [
    filters?.status,
    filters?.reg_type,
    filters?.date_from,
    filters?.date_to,
    filters?.search,
    filters?.department,
    filters?.page,
    filters?.per_page,
  ]);

  useEffect(() => {
    void load();
  }, [load]);

  return { rows, loading, error, reload: load };
}
