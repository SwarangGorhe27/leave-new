import { attendanceDataset, useAttendanceStore } from "../../modules/attendance/store";

export function AttendanceFilters() {
  const { filters, setFilter } = useAttendanceStore();
  const departments = Array.from(new Set(attendanceDataset.employees.map((e) => e.department)));
  const locations = Array.from(new Set(attendanceDataset.employees.map((e) => e.location)));

  return (
    <div className="flat-card bg-card p-2 px-3 grid grid-cols-1 md:grid-cols-3 xl:grid-cols-9 gap-1.5 items-center">
      <select value={filters.employeeId} onChange={(e) => setFilter("employeeId", e.target.value)} className="flat-input h-7 px-2 text-[11px]">
        <option value="all">All Employees</option>
        {attendanceDataset.employees.map((employee) => (
          <option key={employee.id} value={employee.id}>{employee.name}</option>
        ))}
      </select>
      <select value={filters.department} onChange={(e) => setFilter("department", e.target.value)} className="flat-input h-7 px-2 text-[11px]">
        <option value="all">All Departments</option>
        {departments.map((department) => <option key={department}>{department}</option>)}
      </select>
      <select value={filters.location} onChange={(e) => setFilter("location", e.target.value)} className="flat-input h-7 px-2 text-[11px]">
        <option value="all">All Locations</option>
        {locations.map((location) => <option key={location}>{location}</option>)}
      </select>
      <select value={filters.status} onChange={(e) => setFilter("status", e.target.value)} className="flat-input h-7 px-2 text-[11px]">
        <option value="all">All Status</option>
        {["Present", "Absent", "Half Day", "Leave", "Holiday", "Week Off"].map((status) => <option key={status}>{status}</option>)}
      </select>
      <select value={filters.workMode} onChange={(e) => setFilter("workMode", e.target.value)} className="flat-input h-7 px-2 text-[11px]">
        <option value="all">All Work Modes</option>
        {["WFO", "WFH", "Field"].map((mode) => <option key={mode}>{mode}</option>)}
      </select>
      <select value={filters.shift} onChange={(e) => setFilter("shift", e.target.value)} className="flat-input h-7 px-2 text-[11px]">
        <option value="all">All Shifts</option>
        {["General", "Night"].map((shift) => <option key={shift}>{shift}</option>)}
      </select>
      <select value={filters.exceptionType} onChange={(e) => setFilter("exceptionType", e.target.value)} className="flat-input h-7 px-2 text-[11px]">
        <option value="all">All Exceptions</option>
        {["Missing Punch", "Late Cycle Trigger", "Short Hours"].map((type) => <option key={type}>{type}</option>)}
      </select>
      <input type="date" value={filters.from} onChange={(e) => setFilter("from", e.target.value)} className="flat-input h-7 px-2 text-[11px]" />
      <input type="date" value={filters.to} onChange={(e) => setFilter("to", e.target.value)} className="flat-input h-7 px-2 text-[11px]" />
    </div>
  );
}
