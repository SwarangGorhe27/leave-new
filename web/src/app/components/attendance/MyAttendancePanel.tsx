import { MyAttendanceModule } from "./my-attendance/MyAttendanceModule";

export function MyAttendancePanel({ employeeId }: { employeeId: string }) {
  return (
    <div className="attendance-liquid p-4 md:p-6 min-h-screen attendance-theme-neutral">
      <div className="attendance-ambient relative">
        <div className="relative z-10 max-w-[1600px] mx-auto">
          <MyAttendanceModule employeeId={employeeId || "EMP001"} />
        </div>
      </div>
    </div>
  );
}

