import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { MyAttendanceModule } from "../../components/attendance/my-attendance/MyAttendanceModule";
import { useEmployeeAttendance } from "../../hooks/useEmployeeAttendance";

export function EmployeeAttendancePage() {
  const { user } = useAuth();
  const [periodDate, setPeriodDate] = useState(() => new Date());

  const {
    records,
    regularizationRequests,
    metrics,
    loading,
    error,
    fetchPunchDetails,
    submitRegularization,
  } = useEmployeeAttendance({
    monthDate: periodDate,
    employeeId: user?.employeeId ?? user?.employeeCode ?? "",
    employeeName: user?.name ?? "Me",
  });

  return (
    <div className="attendance-liquid p-4 md:p-6 min-h-screen attendance-theme-neutral">
      <div className="attendance-ambient relative">
        <div className="relative z-10 max-w-[1600px] mx-auto">
          <MyAttendanceModule
            employeeId={user?.employeeId ?? user?.employeeCode ?? ""}
            externalRecords={records}
            externalRegularizationRequests={regularizationRequests}
            externalMetrics={metrics ?? undefined}
            externalLoading={loading}
            externalError={error}
            onPeriodChange={setPeriodDate}
            onFetchPunchDetails={fetchPunchDetails}
            onSubmitRegularization={submitRegularization}
          />
        </div>
      </div>
    </div>
  );
}
