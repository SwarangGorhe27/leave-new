import { Pie, PieChart, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { attendanceDataset } from "../../modules/attendance/store";

export function AttendanceChart() {
  const today = "2026-05-06";
  const records = attendanceDataset.records.filter((record) => record.date === today);
  const data = [
    { name: "Present", value: records.filter((record) => record.status === "Present").length, color: "#111827" },
    { name: "Absent", value: records.filter((record) => record.status === "Absent").length, color: "#9CA3AF" },
    { name: "Leave", value: records.filter((record) => record.status === "Leave").length, color: "#D97706" },
    { name: "Half Day", value: records.filter((record) => record.status === "Half Day").length, color: "#2563EB" },
  ];

  return (
    <div className="flat-card bg-card p-4 h-64">
      <p className="text-sm font-semibold text-foreground mb-2">Attendance Distribution</p>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" outerRadius={80}>
            {data.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
