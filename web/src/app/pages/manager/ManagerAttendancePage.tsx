import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { MyAttendanceModule } from "../../components/attendance/my-attendance/MyAttendanceModule";
import { useManagerOwnAttendance } from "../../hooks/useManagerOwnAttendance";

export function ManagerAttendancePage() {
  const { user } = useAuth();
  const [periodDate, setPeriodDate] = useState(() => new Date());

  const { records, loading, error } = useManagerOwnAttendance({
    monthDate: periodDate,
    employeeId: user?.employeeId ?? "",
    employeeName: user?.name ?? "Me",
  });

  return (
    <div className="attendance-liquid p-4 md:p-6 min-h-screen attendance-theme-neutral">
      <div className="attendance-ambient relative">
        <div className="relative z-10 max-w-[1600px] mx-auto">
          <MyAttendanceModule
            employeeId={user?.employeeId ?? ""}
            externalRecords={records}
            externalLoading={loading}
            externalError={error}
            onPeriodChange={setPeriodDate}
          />
        </div>
      </div>
    </div>
  );
}
