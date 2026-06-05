import { useCallback, useEffect, useState } from 'react';
import {
  fetchManagerTeam,
  fetchTeamMemberAttendance,
  ManagerAttendanceApiError,
} from '../../api/managerAttendanceClient';
import type { TeamAttendanceMember } from '../../api/managerAttendanceTypes';
import {
  mapTeamMemberToTodayRecord,
  mapTeamRecordToDaily,
  teamMemberAvatar,
  teamMemberDisplayId,
  teamStatusLabel,
} from '../modules/manager-attendance/mappers';
import type { DailyAttendance } from '../modules/attendance/types';

export interface TeamMemberViewModel {
  id: string;
  displayId: string;
  name: string;
  department: string;
  designation: string;
  avatar: string;
  today?: DailyAttendance;
  raw: TeamAttendanceMember;
}

export function useManagerTeamAttendance() {
  const [members, setMembers] = useState<TeamMemberViewModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const team = await fetchManagerTeam();
      setMembers(
        team.map((member) => ({
          id: member.id,
          displayId: teamMemberDisplayId(member),
          name: member.name,
          department: member.department ?? '—',
          designation: member.role,
          avatar: teamMemberAvatar(member),
          today: mapTeamMemberToTodayRecord(member),
          raw: member,
        })),
      );
    } catch (err) {
      const message =
        err instanceof ManagerAttendanceApiError
          ? err.message
          : 'Failed to load team attendance.';
      setError(message);
      setMembers([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return { members, loading, error, reload: load, teamStatusLabel };
}

export function useTeamMemberAttendanceHistory(
  employeeId: string | null,
  monthDate: Date,
  meta: { name: string; department: string; designation: string },
) {
  const [records, setRecords] = useState<DailyAttendance[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const month = monthDate.getMonth() + 1;
  const year = monthDate.getFullYear();

  useEffect(() => {
    if (!employeeId) {
      setRecords([]);
      return;
    }

    let cancelled = false;
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchTeamMemberAttendance(employeeId, { month, year });
        if (cancelled) return;
        const mapped = data.records.map((record) =>
          mapTeamRecordToDaily(record, {
            employeeId,
            employeeName: meta.name,
            department: meta.department,
            designation: meta.designation,
          }),
        );
        setRecords(mapped);
      } catch (err) {
        if (cancelled) return;
        const message =
          err instanceof ManagerAttendanceApiError
            ? err.message
            : 'Failed to load member attendance.';
        setError(message);
        setRecords([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void run();
    return () => {
      cancelled = true;
    };
  }, [employeeId, month, year, meta.name, meta.department, meta.designation]);

  return { records, loading, error };
}
